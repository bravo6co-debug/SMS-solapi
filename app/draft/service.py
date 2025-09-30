from sqlalchemy.orm import Session
from app.models import Draft
from app.schemas import DraftSave
import json
from typing import Optional


def get_draft(db: Session, user_id: int) -> Optional[Draft]:
    """임시저장 불러오기 (사용자별 단일 레코드)"""
    return db.query(Draft).filter(Draft.id == 1).first()


def save_draft(db: Session, user_id: int, draft_data: DraftSave) -> Draft:
    """임시저장 저장 (덮어쓰기)"""
    # 기존 임시저장 확인
    existing_draft = db.query(Draft).filter(Draft.id == 1).first()

    # items를 JSON 문자열로 변환
    items_json = json.dumps(
        [item.model_dump() for item in draft_data.items],
        ensure_ascii=False
    )

    if existing_draft:
        # 기존 레코드 업데이트
        existing_draft.user_id = user_id
        existing_draft.template_id = draft_data.template_id
        existing_draft.items = items_json
    else:
        # 새로운 레코드 생성 (id=1 고정)
        existing_draft = Draft(
            id=1,
            user_id=user_id,
            template_id=draft_data.template_id,
            items=items_json
        )
        db.add(existing_draft)

    db.commit()
    db.refresh(existing_draft)
    return existing_draft


def delete_draft(db: Session) -> bool:
    """임시저장 삭제"""
    draft = db.query(Draft).filter(Draft.id == 1).first()
    if not draft:
        return False

    db.delete(draft)
    db.commit()
    return True