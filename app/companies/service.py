from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate
from typing import List, Optional


def get_companies(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Company]:
    """발주사 목록 조회 (검색 포함)"""
    query = db.query(Company)

    if search:
        query = query.filter(
            or_(
                Company.name.ilike(f"%{search}%"),
                Company.company_id.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all()


def get_company_by_id(db: Session, company_id: int) -> Optional[Company]:
    """ID로 발주사 조회"""
    return db.query(Company).filter(Company.id == company_id).first()


def create_company(db: Session, company_data: CompanyCreate) -> Company:
    """발주사 생성"""
    db_company = Company(
        name=company_data.name,
        phone=company_data.phone,
        company_id=company_data.company_id,
        memo=company_data.memo
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def update_company(db: Session, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
    """발주사 수정"""
    db_company = get_company_by_id(db, company_id)
    if not db_company:
        return None

    update_data = company_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    """발주사 삭제"""
    db_company = get_company_by_id(db, company_id)
    if not db_company:
        return False

    db.delete(db_company)
    db.commit()
    return True


def get_companies_count(db: Session) -> int:
    """전체 발주사 수"""
    return db.query(Company).count()