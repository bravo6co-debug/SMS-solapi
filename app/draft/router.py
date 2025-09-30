from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import DraftSave, DraftResponse
from app.draft import service
from app.auth.router import get_current_user

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.get("", response_model=DraftResponse)
def get_draft(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """임시저장 불러오기"""
    draft = service.get_draft(db, current_user.id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="저장된 임시 데이터가 없습니다"
        )
    return draft


@router.post("", response_model=DraftResponse)
def save_draft(
    draft_data: DraftSave,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """임시저장 (덮어쓰기)"""
    draft = service.save_draft(db, current_user.id, draft_data)
    return draft


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_draft(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """임시저장 삭제"""
    success = service.delete_draft(db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="저장된 임시 데이터가 없습니다"
        )
    return None