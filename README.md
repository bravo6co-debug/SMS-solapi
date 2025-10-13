# 📱 SOLAPI 문자 발송 시스템

> FastAPI + PostgreSQL + SOLAPI를 활용한 캠페인 문자 발송 관리 시스템

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app/)

---

## 🎯 주요 기능

- ✅ **발주사 관리**: 약 200개 발주사 정보 관리 (CRUD)
- ✅ **템플릿 관리**: 최대 10개 문자 템플릿 (변수 치환 지원)
- ✅ **일괄 발송**: SOLAPI 연동 문자 발송 + 자동 재발송
- ✅ **임시저장**: 발송 목록 1개 임시저장
- ✅ **발송 이력**: 모든 발송 기록 자동 저장
- ✅ **간편 인증**: 세션 기반 로그인/회원가입

---

## 🚀 빠른 시작

### 방법 1: Railway 배포 (추천) - 5분 완성
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

📖 **가이드**: [QUICK_START_RAILWAY.md](QUICK_START_RAILWAY.md)

### 방법 2: Docker로 로컬 실행
```bash
# 1. 환경변수 설정
cp env.local.example .env.local
# .env.local 파일 수정 (SOLAPI API 키 입력)

# 2. Docker 실행
docker-compose up -d

# 3. 브라우저에서 접속
http://localhost:8000
```

### 방법 3: Python 가상환경
```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp env.local.example .env

# 4. 서버 실행
uvicorn main:app --reload

# 5. 브라우저에서 접속
http://localhost:8000
```

---

## 📦 기술 스택

### Backend
- **Python 3.13** - 최신 Python 버전
- **FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy** - ORM
- **PostgreSQL** - 프로덕션 DB
- **SQLite** - 로컬 개발 DB

### Frontend
- **Vanilla JavaScript** - 프레임워크 없는 순수 JS
- **Bootstrap 5** - 반응형 UI

### 외부 서비스
- **SOLAPI** - 문자 발송 API
- **Railway** - 배포 플랫폼

---

## 📁 프로젝트 구조

```
sms-solapi/
├── main.py                    # FastAPI 진입점
├── config.py                  # 환경 설정
├── requirements.txt           # Python 패키지
├── Dockerfile                 # Docker 이미지
├── docker-compose.yml         # Docker Compose 설정
│
├── app/                       # 백엔드 애플리케이션
│   ├── database.py            # DB 연결
│   ├── models.py              # SQLAlchemy 모델
│   ├── schemas.py             # Pydantic 스키마
│   │
│   ├── auth/                  # 인증
│   ├── companies/             # 발주사 관리
│   ├── templates/             # 템플릿 관리
│   ├── send/                  # 문자 발송
│   └── draft/                 # 임시저장
│
└── static/                    # 프론트엔드
    ├── index.html             # 메인 페이지
    ├── css/
    └── js/
```

---

## 🗄️ 데이터베이스 스키마

### 주요 테이블
- **users** - 관리자 계정
- **companies** - 발주사 정보
- **templates** - 문자 템플릿
- **draft** - 임시저장 (단일 레코드)
- **send_history** - 발송 이력

📖 상세 스키마: [CLAUDE.md](CLAUDE.md#3-데이터베이스-스키마)

---

## 🔧 환경변수 설정

### Railway 배포 시
```bash
SOLAPI_API_KEY=your_api_key
SOLAPI_API_SECRET=your_api_secret
SOLAPI_SENDER_PHONE=01012345678
SECRET_KEY=generated_random_string
```

### 로컬 개발 시
`.env` 파일 생성:
```bash
SOLAPI_API_KEY=your_api_key
SOLAPI_API_SECRET=your_api_secret
SOLAPI_SENDER_PHONE=01012345678
DATABASE_URL=sqlite:///./database.db
SECRET_KEY=dev-secret-key
```

---

## 📚 문서

- **개발 가이드**: [CLAUDE.md](CLAUDE.md) - 전체 설계 및 구현 명세
- **Railway 배포**: [RAILWAY_DEPLOY_GUIDE.md](RAILWAY_DEPLOY_GUIDE.md) - 상세 배포 가이드
- **빠른 시작**: [QUICK_START_RAILWAY.md](QUICK_START_RAILWAY.md) - 5분 배포 가이드
- **Docker 가이드**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 사용법

---

## 🔒 보안

### 프로덕션 체크리스트
- [ ] `SECRET_KEY` 32자 이상 랜덤 문자열로 변경
- [ ] `https_only=True` 설정 (main.py:22)
- [ ] SOLAPI IP 제한 설정
- [ ] 환경변수 절대 GitHub 커밋 금지
- [ ] 정기적인 비밀번호 변경 정책

---

## 🧪 테스트

### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# API 문서 (Swagger UI)
http://localhost:8000/docs
```

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f

# Railway 로그
railway logs
```

---

## 🛠️ 트러블슈팅

### Docker 빌드 실패
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache
docker-compose up -d
```

### 데이터베이스 초기화
```bash
# 로컬
python init_db.py

# Railway
railway run python init_db.py
```

### SOLAPI 발송 실패
- SOLAPI 콘솔에서 API 키 상태 확인
- 발신번호 등록 여부 확인
- 크레딧 잔액 확인

---

## 💰 비용 안내

### 무료로 시작
- **Railway Free Tier**: 월 500시간 (약 $0-1)
- **SOLAPI**: 가입 시 무료 크레딧 제공

### 예상 운영 비용
- **Railway Hobby**: $5/월 (무제한 실행)
- **SOLAPI 문자**: 건당 약 15-20원
- **총 예상 비용**: $5-10/월 + 문자 발송 비용

---

## 🤝 기여

이슈 및 풀 리퀘스트를 환영합니다!

### 개발 환경 설정
```bash
git clone https://github.com/your-repo/sms-solapi.git
cd sms-solapi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📄 라이선스

MIT License

---

## 📞 지원

- **이슈 등록**: [GitHub Issues](https://github.com/your-repo/issues)
- **Railway 지원**: [Railway Discord](https://discord.gg/railway)
- **SOLAPI 지원**: [SOLAPI 헬프센터](https://docs.solapi.com/)

---

## 🌟 특징

- ⚡ **빠른 배포**: Railway로 5분 만에 배포
- 🔄 **자동 재발송**: 실패 시 1회 자동 재시도
- 📊 **완전한 이력**: 모든 발송 기록 추적
- 🎨 **직관적 UI**: Bootstrap 기반 반응형 디자인
- 🔐 **보안**: 세션 기반 인증 + bcrypt 해싱

---

**Made with ❤️ using FastAPI & Railway**
