from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import TemplateCreate, TemplateUpdate, TemplateResponse
from app.templates import service
from app.auth.router import get_current_user

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=List[TemplateResponse])
def get_templates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """템플릿 목록 조회"""
    templates = service.get_templates(db)
    return templates


@router.get("/count")
def get_templates_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """전체 템플릿 수"""
    count = service.get_templates_count(db)
    can_create = service.can_create_template(db)
    return {
        "count": count,
        "max": 10,
        "can_create": can_create
    }


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """템플릿 상세 조회"""
    template = service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다"
        )
    return template


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """템플릿 등록"""
    # 최대 10개 제한 체크
    if not service.can_create_template(db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="템플릿은 최대 10개까지만 등록할 수 있습니다"
        )

    template = service.create_template(db, template_data)
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """템플릿 수정"""
    template = service.update_template(db, template_id, template_data)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다"
        )
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """템플릿 삭제"""
    success = service.delete_template(db, template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다"
        )
    return None