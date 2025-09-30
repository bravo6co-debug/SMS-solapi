from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # SOLAPI 설정 (환경 변수에서 가져옴)
    SOLAPI_API_KEY: str
    SOLAPI_API_SECRET: str
    SOLAPI_SENDER_PHONE: str

    # 데이터베이스 (로컬: SQLite, Vercel: PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

    # 세션
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SESSION_EXPIRE_HOURS: int = 24

    # 템플릿 제한
    MAX_TEMPLATES: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()