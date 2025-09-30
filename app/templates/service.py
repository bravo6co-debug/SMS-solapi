from sqlalchemy.orm import Session
from app.models import Template
from app.schemas import TemplateCreate, TemplateUpdate
from typing import List, Optional
from config import settings


def get_templates(db: Session) -> List[Template]:
    """템플릿 목록 조회"""
    return db.query(Template).all()


def get_template_by_id(db: Session, template_id: int) -> Optional[Template]:
    """ID로 템플릿 조회"""
    return db.query(Template).filter(Template.id == template_id).first()


def get_templates_count(db: Session) -> int:
    """전체 템플릿 수"""
    return db.query(Template).count()


def can_create_template(db: Session) -> bool:
    """템플릿 생성 가능 여부 (최대 10개 제한)"""
    count = get_templates_count(db)
    return count < settings.MAX_TEMPLATES


def create_template(db: Session, template_data: TemplateCreate) -> Template:
    """템플릿 생성"""
    db_template = Template(
        category=template_data.category,
        title=template_data.title,
        content=template_data.content
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_template(db: Session, template_id: int, template_data: TemplateUpdate) -> Optional[Template]:
    """템플릿 수정"""
    db_template = get_template_by_id(db, template_id)
    if not db_template:
        return None

    update_data = template_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)

    db.commit()
    db.refresh(db_template)
    return db_template


def delete_template(db: Session, template_id: int) -> bool:
    """템플릿 삭제"""
    db_template = get_template_by_id(db, template_id)
    if not db_template:
        return False

    db.delete(db_template)
    db.commit()
    return True


def replace_variables(content: str, company_name: str, campaign_name: str) -> str:
    """템플릿 변수 치환"""
    result = content.replace("{발주사명}", company_name)
    result = result.replace("{캠페인명}", campaign_name)
    return result