from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from app.database import init_db
from app.auth.router import router as auth_router
from app.companies.router import router as companies_router
from app.templates.router import router as templates_router
from app.send.router import router as send_router
from app.draft.router import router as draft_router
import os

app = FastAPI(title="SOLAPI 문자 발송 시스템")

# 세션 미들웨어
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=86400,  # 24시간 (초 단위)
    same_site="lax",  # CSRF 방어
    https_only=False  # 로컬/도커: False, 프로덕션 HTTPS: True
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(templates_router)
app.include_router(send_router)
app.include_router(draft_router)

# 정적 파일 (CSS, JS) - 로컬 개발 환경에서만
if not os.getenv("VERCEL"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    # Docker 환경에서도 정적 파일 제공
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 환경변수 검증 (개발 환경에서는 경고만)
required_env_vars = ["SOLAPI_API_KEY", "SOLAPI_API_SECRET", "SOLAPI_SENDER_PHONE"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"⚠️ 필수 환경변수가 누락되었습니다: {missing_vars}")
    print("💡 테스트용 기본값을 사용합니다.")
    # 테스트용 기본값 설정
    os.environ.setdefault("SOLAPI_API_KEY", "test_api_key")
    os.environ.setdefault("SOLAPI_API_SECRET", "test_api_secret")
    os.environ.setdefault("SOLAPI_SENDER_PHONE", "01012345678")
else:
    print("✅ 모든 필수 환경변수가 설정되었습니다")

# 데이터베이스 초기화 (재시도 로직 포함)
def init_database_with_retry(max_retries=5):
    for attempt in range(max_retries):
        try:
            init_db()
            print("✅ 데이터베이스 초기화 완료")
            return True
        except Exception as e:
            print(f"⚠️ 데이터베이스 초기화 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
            else:
                print("❌ 데이터베이스 초기화 최종 실패")
                return False

init_database_with_retry()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # 정적 파일이 없는 경우 기본 페이지 제공
        return """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SOLAPI 문자 발송 시스템</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .links { text-align: center; margin-top: 30px; }
                .links a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .links a:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 SOLAPI 문자 발송 시스템</h1>
                <div class="status">
                    ✅ 시스템이 정상적으로 작동하고 있습니다!
                </div>
                <p>이 시스템은 Docker 컨테이너에서 실행되고 있습니다.</p>
                <div class="links">
                    <a href="/health">헬스체크</a>
                    <a href="/docs">API 문서</a>
                    <a href="/static/">정적 파일</a>
                </div>
            </div>
        </body>
        </html>
        """


@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)