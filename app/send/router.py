from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import SendBulkRequest, PreviewRequest, PreviewResponse, SendHistoryResponse
from app.send import service
from app.templates.service import replace_variables
from app.companies.service import get_company_by_id
from app.templates.service import get_template_by_id
from app.auth.router import get_current_user

router = APIRouter(prefix="/api/send", tags=["send"])


@router.post("/preview", response_model=PreviewResponse)
def preview_message(
    preview_data: PreviewRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """메시지 미리보기 (변수 치환 결과)"""
    # 템플릿 조회
    template = get_template_by_id(db, preview_data.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다"
        )

    # 발주사 조회
    company = get_company_by_id(db, preview_data.company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="발주사를 찾을 수 없습니다"
        )

    # 메시지 내용 생성
    message_content = replace_variables(
        template.content,
        company.name,
        preview_data.campaign_name,
        template.category
    )

    # 추가 메시지가 있으면 붙이기
    if preview_data.additional_message:
        message_content = message_content + "\n\n" + preview_data.additional_message

    # 통계 계산
    stats = service.calculate_message_stats(message_content)

    return PreviewResponse(
        company_name=company.name,
        phone=company.phone,
        message_content=message_content,
        char_count=stats["char_count"],
        byte_count=stats["byte_count"]
    )


@router.post("/bulk")
async def send_bulk_messages(
    send_data: SendBulkRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """일괄 발송 (비동기)"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    results = []

    def send_single_message(item):
        """개별 메시지 발송 (스레드에서 실행)"""
        return service.send_message_with_retry(
            db=db,
            user_id=current_user.id,
            template_id=send_data.template_id,
            company_id=item.company_id,
            campaign_name=item.campaign_name,
            additional_message=send_data.additional_message
        )

    # 병렬 처리 (최대 5개씩 동시 발송)
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = []

        for item in send_data.items:
            task = loop.run_in_executor(executor, send_single_message, item)
            tasks.append((item, task))

        # 모든 작업 완료 대기
        for item, task in tasks:
            try:
                result = await task
                results.append({
                    "company_id": item.company_id,
                    "campaign_name": item.campaign_name,
                    "status": result["status"],
                    "success": result["success"],
                    "message_id": result.get("message_id"),
                    "error": result.get("error")
                })
            except Exception as e:
                results.append({
                    "company_id": item.company_id,
                    "campaign_name": item.campaign_name,
                    "status": "실패",
                    "success": False,
                    "message_id": None,
                    "error": str(e)
                })

    # 성공/실패 통계
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    return {
        "total": len(results),
        "success": success_count,
        "fail": fail_count,
        "results": results
    }


@router.get("/history", response_model=List[SendHistoryResponse])
def get_send_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발송 이력 조회"""
    history = service.get_send_history(db, skip=skip, limit=limit)
    return history