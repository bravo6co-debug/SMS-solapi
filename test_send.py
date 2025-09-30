#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.send.service import send_message_with_retry
from app.database import SessionLocal

# 실제 발송 테스트
print("=== 실제 발송 테스트 ===")
db = SessionLocal()

try:
    result = send_message_with_retry(db, 1, 1, 1, '테스트 캠페인')
    
    print(f"Success: {result['success']}")
    print(f"Status: {result['status']}")
    print(f"Message ID: {result.get('message_id', 'None')}")
    print(f"Error: {result.get('error', 'None')}")
    
finally:
    db.close()
