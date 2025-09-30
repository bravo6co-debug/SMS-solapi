#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 회원가입 테스트
print("=== 회원가입 테스트 ===")

signup_data = {
    "username": "testuser",
    "password": "test123456",
    "name": "테스트사용자"
}

try:
    # 회원가입
    signup_response = requests.post("http://localhost:8000/api/auth/signup", json=signup_data)
    print(f"Signup Status: {signup_response.status_code}")
    print(f"Signup Response: {signup_response.text}")
    
    if signup_response.status_code == 200:
        # 로그인
        login_data = {
            "username": "testuser",
            "password": "test123456"
        }
        
        login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        print(f"\nLogin Status: {login_response.status_code}")
        print(f"Login Response: {login_response.text}")
        
        if login_response.status_code == 200:
            # 발송 테스트
            send_data = {
                "template_id": 1,
                "items": [
                    {
                        "company_id": 1,
                        "campaign_name": "API 테스트 캠페인"
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json",
                "Cookie": login_response.headers.get("Set-Cookie", "")
            }
            
            send_response = requests.post("http://localhost:8000/api/send/bulk", json=send_data, headers=headers)
            print(f"\nSend Status: {send_response.status_code}")
            print(f"Send Response: {send_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
