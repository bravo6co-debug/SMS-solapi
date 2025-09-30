Signature 생성
import hmac
import hashlib
import secrets
from datetime import datetime, timezone

def generate_signature(api_secret: str, date_time: str, salt: str) -> str:
    """HMAC-SHA256 시그니처 생성"""
    data = date_time + salt
    signature = hmac.new(
        api_secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def create_auth_header(api_key: str, api_secret: str) -> str:
    """Authorization 헤더 생성"""
    date_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    salt = secrets.token_hex(16)
    signature = generate_signature(api_secret, date_time, salt)
    
    return f"HMAC-SHA256 apiKey={api_key}, date={date_time}, salt={salt}, signature={signature}"


API 요청 예제
import requests
from typing import Dict, Any

def send_message(api_key: str, api_secret: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """메시지 전송 API 호출"""
    auth_header = create_auth_header(api_key, api_secret)
    
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'https://api.solapi.com/messages/v4/send-many/detail',
        json=message_data,
        headers=headers
    )
    
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    message_data = {
        "message": {
            "to": "01012345678",
            "from": "01087654321",
            "text": "테스트 메시지입니다."
        }
    }


오류 처리
API 인증 과정에서 발생할 수 있는 오류들과 대응 방법입니다.

Error code	설명	HTTP 상태 코드	해결 방법
InvalidAPIKey
유효하지 않은 API Key
403
API Key 확인 및 재발급
SignatureDoesNotMatch
Signature 불일치
403
Signature 생성 로직 검토
RequestTimeTooSkewed
시간 차이 초과 (±15분)
403
시스템 시간 동기화
DuplicatedSignature
중복된 Signature 사용
403
Salt 값 변경 및 재시도