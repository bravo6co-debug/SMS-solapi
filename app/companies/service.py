from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate, BulkUploadError
from typing import List, Optional, Tuple
import re


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


def validate_phone_number(phone: str) -> bool:
    """전화번호 유효성 검사 (01X-XXXX-XXXX 또는 01XXXXXXXXX 형식)"""
    # 하이픈 제거
    phone_clean = phone.replace("-", "").replace(" ", "")
    # 010, 011, 016, 017, 018, 019로 시작하는 10-11자리 숫자
    pattern = r'^01[0-9]{8,9}$'
    return bool(re.match(pattern, phone_clean))


def create_companies_bulk(db: Session, companies_data: List[dict]) -> Tuple[int, List[BulkUploadError]]:
    """
    발주사 대량 등록

    Args:
        db: 데이터베이스 세션
        companies_data: 발주사 데이터 리스트 [{"name": "", "phone": "", "company_id": "", "memo": ""}, ...]

    Returns:
        (성공 건수, 에러 리스트)
    """
    success_count = 0
    errors = []
    
    print(f"[DEBUG] 대량 업로드 시작: {len(companies_data)}개 데이터 처리")

    try:
        # 기존 발주사명, 전화번호 목록 조회 (중복 체크용)
        existing_names = {c.name for c in db.query(Company.name).all()}
        existing_phones = {c.phone for c in db.query(Company.phone).all()}
        existing_company_ids = {c.company_id for c in db.query(Company.company_id).all()}
        
        print(f"[DEBUG] 기존 데이터 수: 이름={len(existing_names)}, 전화번호={len(existing_phones)}, 아이디={len(existing_company_ids)}")

        # 유효한 데이터만 저장할 리스트
        valid_companies = []

        for idx, data in enumerate(companies_data):
            row_num = idx + 2  # 엑셀 행 번호 (헤더 1행 + 1부터 시작)

            try:
                # 필수 항목 체크
                name = data.get("name", "").strip()
                phone = data.get("phone", "").strip()
                company_id = data.get("company_id", "").strip()
                memo = data.get("memo", "").strip() if data.get("memo") else None

                if not name:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error="발주사명은 필수입니다"
                    ))
                    continue

                if not phone:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error="전화번호는 필수입니다"
                    ))
                    continue

                if not company_id:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error="발주사 아이디는 필수입니다"
                    ))
                    continue

                # 전화번호 형식 검사
                if not validate_phone_number(phone):
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error="전화번호 형식이 올바르지 않습니다 (예: 01012345678)"
                    ))
                    continue

                # 중복 체크
                if name in existing_names:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error=f"이미 등록된 발주사명입니다: {name}"
                    ))
                    continue

                if phone in existing_phones:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error=f"이미 등록된 전화번호입니다: {phone}"
                    ))
                    continue

                if company_id in existing_company_ids:
                    errors.append(BulkUploadError(
                        row=row_num,
                        name=name,
                        phone=phone,
                        company_id=company_id,
                        error=f"이미 등록된 발주사 아이디입니다: {company_id}"
                    ))
                    continue

                # 유효한 데이터로 추가
                valid_companies.append({
                    "name": name,
                    "phone": phone,
                    "company_id": company_id,
                    "memo": memo
                })

                # 중복 방지를 위해 추가
                existing_names.add(name)
                existing_phones.add(phone)
                existing_company_ids.add(company_id)

                success_count += 1

            except Exception as e:
                print(f"[ERROR] 행 {row_num} 처리 중 오류: {str(e)}")
                errors.append(BulkUploadError(
                    row=row_num,
                    name=data.get("name", ""),
                    phone=data.get("phone", ""),
                    company_id=data.get("company_id", ""),
                    error=f"처리 중 오류 발생: {str(e)}"
                ))

        print(f"[DEBUG] 유효한 데이터: {len(valid_companies)}개, 에러: {len(errors)}개")

        # 유효한 데이터가 있으면 일괄 저장
        if valid_companies:
            try:
                # 배치 삽입을 위한 객체 생성
                companies_to_add = []
                for data in valid_companies:
                    company = Company(
                        name=data["name"],
                        phone=data["phone"],
                        company_id=data["company_id"],
                        memo=data["memo"]
                    )
                    companies_to_add.append(company)

                # 모든 객체를 세션에 추가
                db.add_all(companies_to_add)
                
                # 커밋 실행
                db.commit()
                print(f"[DEBUG] 데이터베이스 커밋 성공: {len(companies_to_add)}개 저장")
                
            except Exception as e:
                print(f"[ERROR] 데이터베이스 저장 실패: {str(e)}")
                db.rollback()
                # 모든 항목을 에러로 처리
                errors = [BulkUploadError(
                    row=0,
                    name="",
                    phone="",
                    company_id="",
                    error=f"데이터베이스 저장 실패: {str(e)}"
                )]
                success_count = 0

    except Exception as e:
        print(f"[ERROR] 대량 업로드 전체 실패: {str(e)}")
        db.rollback()
        errors = [BulkUploadError(
            row=0,
            name="",
            phone="",
            company_id="",
            error=f"시스템 오류: {str(e)}"
        )]
        success_count = 0

    print(f"[DEBUG] 최종 결과: 성공={success_count}, 에러={len(errors)}")
    return success_count, errors