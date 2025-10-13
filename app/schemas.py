from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    name: str = Field(..., max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# Company Schemas
class CompanyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    company_id: str = Field(..., max_length=50)
    memo: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company_id: Optional[str] = Field(None, max_length=50)
    memo: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    phone: str
    company_id: str
    memo: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkUploadError(BaseModel):
    row: int
    name: Optional[str]
    phone: Optional[str]
    company_id: Optional[str]
    error: str


class CompanyBulkUploadResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[BulkUploadError]


# Template Schemas
class TemplateCreate(BaseModel):
    category: str = Field(..., pattern="^(검수완료|진행률50%|진행률100%|기타|기타\\(캠페인명사용\\))$")
    title: str = Field(..., max_length=100)
    content: str


class TemplateUpdate(BaseModel):
    category: Optional[str] = Field(None, pattern="^(검수완료|진행률50%|진행률100%|기타|기타\\(캠페인명사용\\))$")
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None


class TemplateResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Draft Schemas
class DraftItem(BaseModel):
    company_id: int
    campaign_name: str


class DraftSave(BaseModel):
    template_id: int
    items: List[DraftItem]


class DraftResponse(BaseModel):
    id: int
    user_id: Optional[int]
    template_id: Optional[int]
    items: str
    saved_at: datetime

    class Config:
        from_attributes = True


# Send Schemas
class SendItem(BaseModel):
    company_id: int
    campaign_name: str


class SendBulkRequest(BaseModel):
    template_id: int
    items: List[SendItem]
    additional_message: Optional[str] = None


class PreviewRequest(BaseModel):
    template_id: int
    company_id: int
    campaign_name: str
    additional_message: Optional[str] = None


class PreviewResponse(BaseModel):
    company_name: str
    phone: str
    message_content: str
    char_count: int
    byte_count: int


# History Schemas
class SendHistoryResponse(BaseModel):
    id: int
    user_id: int
    template_id: int
    company_id: int
    campaign_name: str
    message_content: str
    status: str
    solapi_message_id: Optional[str]
    sent_at: datetime

    class Config:
        from_attributes = True