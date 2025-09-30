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

app = FastAPI(title="SOLAPI 문자 발송 시스템")

# 세션 미들웨어
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# 라우터 등록
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(templates_router)
app.include_router(send_router)
app.include_router(draft_router)

# 정적 파일 (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 초기화"""
    init_db()
    print("✅ 데이터베이스 초기화 완료")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health_check():
    """헬스체크"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)