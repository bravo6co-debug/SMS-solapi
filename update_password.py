#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

# 비밀번호 해시 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == 'admin').first()
        if user:
            # 새 비밀번호 설정
            new_password = "admin123"
            user.password_hash = pwd_context.hash(new_password)
            db.commit()
            print(f"Password updated for user: {user.username}")
            print(f"New password: {new_password}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    update_password()
