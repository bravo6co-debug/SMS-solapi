#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# API 테스트
print("=== API 발송 테스트 ===")

# 로그인 먼저
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    # 로그인
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
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
        print(f"Send Status: {send_response.status_code}")
        print(f"Send Response: {send_response.text}")
        
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")