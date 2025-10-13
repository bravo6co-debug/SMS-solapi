from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import os

# 데이터베이스 URL 설정 (환경변수 우선)
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# 데이터베이스 연결 설정
if DATABASE_URL.startswith("sqlite"):
    # SQLite 연결 설정
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # 디버깅 시 True로 변경
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL 연결 설정
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
        max_overflow=0,
        echo=False,  # 디버깅 시 True로 변경
        pool_size=10,  # 연결 풀 크기 증가
        connect_args={
            "options": "-c timezone=Asia/Seoul"  # 타임존 설정
        }
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 테이블 생성"""
    from app import models
    Base.metadata.create_all(bind=engine)