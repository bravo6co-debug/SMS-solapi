from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import CompanyCreate, CompanyUpdate, CompanyResponse
from app.companies import service
from app.auth.router import get_current_user

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=List[CompanyResponse])
def get_companies(
    search: Optional[str] = Query(None, description="검색어 (이름 또는 아이디)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발주사 목록 조회"""
    companies = service.get_companies(db, search=search, skip=skip, limit=limit)
    return companies


@router.get("/count")
def get_companies_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """전체 발주사 수"""
    count = service.get_companies_count(db)
    return {"count": count}


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발주사 상세 조회"""
    company = service.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="발주사를 찾을 수 없습니다"
        )
    return company


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발주사 등록"""
    company = service.create_company(db, company_data)
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발주사 수정"""
    company = service.update_company(db, company_id, company_data)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="발주사를 찾을 수 없습니다"
        )
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """발주사 삭제"""
    success = service.delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="발주사를 찾을 수 없습니다"
        )
    return None