import hmac
import hashlib
import secrets
import requests
from datetime import datetime, timezone
from config import settings
from typing import Dict, Any


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


class SolapiClient:
    """SOLAPI 클라이언트"""

    def __init__(self):
        self.api_key = settings.SOLAPI_API_KEY
        self.api_secret = settings.SOLAPI_API_SECRET
        self.sender_phone = settings.SOLAPI_SENDER_PHONE
        self.api_url = "https://api.solapi.com/messages/v4/send"

    def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        문자 발송

        Args:
            to: 수신 번호
            message: 발송 내용

        Returns:
            발송 결과 딕셔너리
        """
        try:
            auth_header = create_auth_header(self.api_key, self.api_secret)

            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/json'
            }

            message_data = {
                "message": {
                    "to": to,
                    "from": self.sender_phone,
                    "text": message
                }
            }

            response = requests.post(
                self.api_url,
                json=message_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("messageId"),
                    "status": result.get("statusCode"),
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "message_id": None
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "요청 시간 초과",
                "message_id": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"네트워크 오류: {str(e)}",
                "message_id": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"알 수 없는 오류: {str(e)}",
                "message_id": None
            }


# 싱글톤 인스턴스
solapi_client = SolapiClient()