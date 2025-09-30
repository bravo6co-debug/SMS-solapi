from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse
from app.auth import service
from datetime import datetime, timedelta
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


# 세션 관리
SESSION_KEY = "user_id"


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """현재 로그인한 사용자 가져오기"""
    user_id = request.session.get(SESSION_KEY)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다"
        )
    user = service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )
    return user


@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    # 중복 체크
    existing_user = service.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명입니다"
        )

    # 사용자 생성
    user = service.create_user(db, user_data)
    return user


@router.post("/login")
def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """로그인"""
    user = service.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다"
        )

    # 세션 저장
    request.session[SESSION_KEY] = user.id

    return {
        "message": "로그인 성공",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name
        }
    }


@router.post("/logout")
def logout(request: Request):
    """로그아웃"""
    request.session.clear()
    return {"message": "로그아웃 성공"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """현재 사용자 정보"""
    return current_user