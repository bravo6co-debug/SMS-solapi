from sqlalchemy.orm import Session
from app.models import SendHistory, Company, Template
from app.send.solapi import solapi_client
from app.templates.service import replace_variables
from typing import Dict, Any, Optional


def send_message_with_retry(
    db: Session,
    user_id: int,
    template_id: int,
    company_id: int,
    campaign_name: str
) -> Dict[str, Any]:
    """
    문자 발송 (재발송 포함)

    Returns:
        {
            "success": bool,
            "status": str,  # "성공", "재발송성공", "재발송실패"
            "message_id": str,
            "error": str (optional)
        }
    """
    # 발주사 정보 조회
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return {
            "success": False,
            "status": "실패",
            "error": "발주사를 찾을 수 없습니다",
            "message_id": None
        }

    # 템플릿 조회
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return {
            "success": False,
            "status": "실패",
            "error": "템플릿을 찾을 수 없습니다",
            "message_id": None
        }

    # 메시지 내용 생성 (변수 치환)
    message_content = replace_variables(
        template.content,
        company.name,
        campaign_name
    )

    # 1차 발송 시도
    result = solapi_client.send_message(company.phone, message_content)

    if result["success"]:
        # 발송 성공
        save_send_history(
            db, user_id, template_id, company_id,
            campaign_name, message_content, "성공", result["message_id"]
        )
        return {
            "success": True,
            "status": "성공",
            "message_id": result["message_id"]
        }
    else:
        # 1차 실패 -> 재발송 시도
        retry_result = solapi_client.send_message(company.phone, message_content)

        if retry_result["success"]:
            # 재발송 성공
            save_send_history(
                db, user_id, template_id, company_id,
                campaign_name, message_content, "재발송성공", retry_result["message_id"]
            )
            return {
                "success": True,
                "status": "재발송성공",
                "message_id": retry_result["message_id"]
            }
        else:
            # 재발송 실패
            save_send_history(
                db, user_id, template_id, company_id,
                campaign_name, message_content, "재발송실패", None
            )
            return {
                "success": False,
                "status": "재발송실패",
                "error": retry_result.get("error", "알 수 없는 오류"),
                "message_id": None
            }


def save_send_history(
    db: Session,
    user_id: int,
    template_id: int,
    company_id: int,
    campaign_name: str,
    message_content: str,
    status: str,
    solapi_message_id: Optional[str]
):
    """발송 이력 저장"""
    history = SendHistory(
        user_id=user_id,
        template_id=template_id,
        company_id=company_id,
        campaign_name=campaign_name,
        message_content=message_content,
        status=status,
        solapi_message_id=solapi_message_id
    )
    db.add(history)
    db.commit()


def get_send_history(db: Session, skip: int = 0, limit: int = 100):
    """발송 이력 조회"""
    return db.query(SendHistory).order_by(SendHistory.sent_at.desc()).offset(skip).limit(limit).all()


def calculate_message_stats(message: str) -> Dict[str, int]:
    """메시지 통계 (글자수, 바이트수)"""
    char_count = len(message)
    byte_count = len(message.encode('utf-8'))
    return {
        "char_count": char_count,
        "byte_count": byte_count
    }