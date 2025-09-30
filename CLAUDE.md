# SOLAPI 문자 발송 시스템 개발 문서

> 📘 **프로젝트 가이드 문서**
>
> 본 문서는 SOLAPI 문자 발송 시스템의 설계 및 구현 가이드입니다.

---

## 1. 프로젝트 개요

### 1.1 목적
SOLAPI를 연동하여 발주사에게 캠페인 진행 상황을 문자로 발송하는 웹 기반 시스템

### 1.2 핵심 기능
- 발주사 관리 (등록, 수정, 삭제, 검색)
- 문자 템플릿 관리 (최대 10개)
- 수동 문자 발송 (템플릿 기반 + 변수 치환)
- 임시저장 기능 (1개)
- 발송 이력 자동 기록
- 발송 실패 시 자동 재발송

### 1.3 사용자
- 관리자 여러 명 (간편 회원가입)
- 발주사 약 200개

---

## 2. 기술 스택

### 2.1 Backend
- **언어**: Python 3.13+
- **프레임워크**: FastAPI
- **데이터베이스**:
  - 로컬 개발: SQLite
  - 프로덕션: PostgreSQL (Vercel PostgreSQL)
- **문자 발송**: solapi SDK (v5.0.2+)

### 2.2 Frontend
- **구조**: 단일 페이지 애플리케이션 (SPA)
- **스타일**: Bootstrap 5
- **스크립트**: Vanilla JavaScript

### 2.3 배포
- **플랫폼**: Vercel (서버리스)
- **서버**: Uvicorn (로컬 개발)
- **접근**: URL만 알면 접근 가능

---

## 3. 데이터베이스 스키마

### 3.1 users (사용자)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 companies (발주사)
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    company_id VARCHAR(50) NOT NULL,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 templates (템플릿)
```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_category CHECK (
        category IN ('검수완료', '진행률50%', '진행률100%', '기타')
    )
);
```
- **변수**: `{발주사명}`, `{캠페인명}`

### 3.4 draft (임시저장)
```sql
CREATE TABLE draft (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    user_id INTEGER,
    template_id INTEGER,
    items TEXT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (template_id) REFERENCES templates(id)
);
```
- **items**: JSON 형식 `[{"company_id": 1, "campaign_name": "봄 프로모션"}, ...]`
- **제약**: 단일 레코드만 존재 (id = 1)

### 3.5 send_history (발송 이력)
```sql
CREATE TABLE send_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    campaign_name VARCHAR(200) NOT NULL,
    message_content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    solapi_message_id VARCHAR(100),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT chk_status CHECK (
        status IN ('성공', '실패', '재발송성공', '재발송실패')
    )
);
```

---

## 4. API 엔드포인트 설계

### 4.1 인증 API
```
POST   /api/auth/signup        회원가입
POST   /api/auth/login         로그인
POST   /api/auth/logout        로그아웃
GET    /api/auth/me            현재 사용자 정보
```

### 4.2 발주사 API
```
GET    /api/companies          발주사 목록 (검색 포함)
POST   /api/companies          발주사 등록
GET    /api/companies/{id}     발주사 상세
PUT    /api/companies/{id}     발주사 수정
DELETE /api/companies/{id}     발주사 삭제
```

### 4.3 템플릿 API
```
GET    /api/templates          템플릿 목록
POST   /api/templates          템플릿 등록
GET    /api/templates/{id}     템플릿 상세
PUT    /api/templates/{id}     템플릿 수정
DELETE /api/templates/{id}     템플릿 삭제
GET    /api/templates/count    템플릿 개수 (10개 제한 체크)
```

### 4.4 발송 API
```
POST   /api/send/preview       미리보기 (변수 치환 결과)
POST   /api/send/bulk          일괄 발송
```

### 4.5 임시저장 API
```
GET    /api/draft              임시저장 불러오기
POST   /api/draft              임시저장 저장
DELETE /api/draft              임시저장 삭제
```

### 4.6 이력 API (참고용)
```
GET    /api/history            발송 이력 목록
```

---

## 5. 주요 기능 상세 설계

### 5.1 회원가입/로그인
- **방식**: 간편 가입 (아이디, 비밀번호, 이름)
- **인증**: Session 기반 (쿠키)
- **비밀번호**: bcrypt 해싱

### 5.2 발주사 관리
- **등록**: 이름, 전화번호, 아이디, 메모(선택)
- **검색**: 이름으로 검색 (LIKE 검색)
- **총 개수**: 약 200개 예상

### 5.3 템플릿 관리
- **카테고리**: 검수완료, 진행률50%, 진행률100%, 기타
- **변수**: `{발주사명}`, `{캠페인명}`
- **제한**: 최대 10개
- **예시**:
  ```
  제목: 검수 완료 알림
  내용: {발주사명}님, {캠페인명} 검수가 완료되었습니다.
  ```

### 5.4 문자 발송 프로세스
```
1. 템플릿 선택
   ↓
2. 발주사 선택 + 캠페인명 입력 (반복 추가)
   - 발주사 검색: 이름으로 검색
   - 중복 체크: 같은 발주사 추가 시 경고
   ↓
3. 발송 목록 확인
   - 미리보기 기능 (변수 치환 결과)
   - 개별 삭제 가능
   ↓
4. 임시저장 (선택)
   - 1개만 저장 가능
   - 이전 저장 내용 덮어쓰기
   ↓
5. 일괄 발송
   - SOLAPI API 호출
   - 발송 실패 시 자동 재발송 (1회)
   - 재발송도 실패 시 실패 이력 기록
```

### 5.5 발송 실패 처리
```python
# 의사코드
def send_message(phone, message):
    try:
        result = solapi.send(phone, message)
        if result.success:
            return "성공"
        else:
            # 1차 실패 -> 재발송
            retry_result = solapi.send(phone, message)
            if retry_result.success:
                return "재발송성공"
            else:
                return "재발송실패"
    except Exception as e:
        return "재발송실패"
```

### 5.6 임시저장
- **개수**: 1개만 저장
- **저장 내용**:
  - 선택한 템플릿 ID
  - 발송 목록 (발주사 ID + 캠페인명)
- **불러오기**: 덮어쓰기 (기존 작업 내용 삭제)

---

## 6. 설정 파일

### 6.1 config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # SOLAPI 설정
    SOLAPI_API_KEY: str = "your_api_key_here"
    SOLAPI_API_SECRET: str = "your_api_secret_here"
    SOLAPI_SENDER_PHONE: str = "01012345678"

    # 데이터베이스 (환경변수로 오버라이드 가능)
    # 로컬: sqlite:///./database.db
    # 배포: postgresql://...
    DATABASE_URL: str = "sqlite:///./database.db"

    # 세션
    SECRET_KEY: str = "your-secret-key-here"
    SESSION_EXPIRE_HOURS: int = 24

    # 템플릿 제한
    MAX_TEMPLATES: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 6.2 환경변수 (.env)
```bash
SOLAPI_API_KEY=your_api_key_here
SOLAPI_API_SECRET=your_api_secret_here
SOLAPI_SENDER_PHONE=01012345678
DATABASE_URL=sqlite:///./database.db
SECRET_KEY=your-secret-key-change-this-in-production
```

---

## 7. 화면 구성

### 7.1 전체 레이아웃
```
┌─────────────────────────────────────────┐
│  📱 문자 발송 시스템        [로그아웃]   │
├─────────────────────────────────────────┤
│ [발주사 관리] [템플릿 관리] [문자발송]  │
├─────────────────────────────────────────┤
│                                          │
│           (컨텐츠 영역)                  │
│                                          │
└─────────────────────────────────────────┘
```

### 7.2 문자 발송 화면
```
┌─────────────────────────────────────────┐
│  1. 템플릿 선택                          │
│  ┌──────────────────────────────────┐  │
│  │ [검수완료 ▼]                      │  │
│  └──────────────────────────────────┘  │
│                                          │
│  2. 발송 대상 추가                       │
│  ┌──────────────────────────────────┐  │
│  │ 발주사: [검색...] 🔍              │  │
│  │         [검색결과 드롭다운]        │  │
│  │ 캠페인명: [____________]          │  │
│  │ [추가하기]                        │  │
│  └──────────────────────────────────┘  │
│                                          │
│  3. 발송 목록 (5건)                      │
│  ┌──────────────────────────────────┐  │
│  │ No │ 발주사 │ 캠페인명 │ 액션    │  │
│  ├────┼────────┼──────────┼─────────┤  │
│  │ 1  │ ABC회사│ 봄프로모션│[보기][X]│  │
│  │ 2  │ XYZ회사│ 여름행사  │[보기][X]│  │
│  └──────────────────────────────────┘  │
│                                          │
│  [임시저장] [불러오기] [일괄발송]        │
│                                          │
└─────────────────────────────────────────┘
```

### 7.3 미리보기 모달
```
┌─────────────────────────────────────────┐
│  미리보기                      [닫기 X]  │
├─────────────────────────────────────────┤
│                                          │
│  수신자: ABC회사 (010-1234-5678)         │
│                                          │
│  발송 내용:                              │
│  ┌──────────────────────────────────┐  │
│  │ ABC회사님,                        │  │
│  │ 2025 봄 프로모션 검수가           │  │
│  │ 완료되었습니다.                   │  │
│  │                                   │  │
│  │ 감사합니다.                       │  │
│  └──────────────────────────────────┘  │
│                                          │
│  글자수: 45자 / 90바이트               │
│                                          │
│                       [확인]             │
└─────────────────────────────────────────┘
```

---

## 8. 디렉토리 구조

```
project/
├── main.py                 # FastAPI 애플리케이션 진입점
├── config.py               # 설정 파일
├── requirements.txt        # Python 패키지 목록
├── database.db             # SQLite 데이터베이스
│
├── app/
│   ├── __init__.py
│   ├── database.py         # DB 연결 및 초기화
│   ├── models.py           # SQLAlchemy 모델
│   ├── schemas.py          # Pydantic 스키마
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py       # 인증 라우터
│   │   └── service.py      # 인증 비즈니스 로직
│   │
│   ├── companies/
│   │   ├── __init__.py
│   │   ├── router.py       # 발주사 라우터
│   │   └── service.py      # 발주사 비즈니스 로직
│   │
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── router.py       # 템플릿 라우터
│   │   └── service.py      # 템플릿 비즈니스 로직
│   │
│   ├── send/
│   │   ├── __init__.py
│   │   ├── router.py       # 발송 라우터
│   │   ├── service.py      # 발송 비즈니스 로직
│   │   └── solapi.py       # SOLAPI 연동
│   │
│   └── draft/
│       ├── __init__.py
│       ├── router.py       # 임시저장 라우터
│       └── service.py      # 임시저장 비즈니스 로직
│
└── static/
    ├── index.html          # 단일 페이지
    ├── css/
    │   └── style.css       # 커스텀 스타일
    └── js/
        ├── app.js          # 메인 애플리케이션 로직
        ├── auth.js         # 인증 관련
        ├── companies.js    # 발주사 관리
        ├── templates.js    # 템플릿 관리
        └── send.js         # 문자 발송
```

---

## 9. 개발 순서

### Phase 1: 기본 구조 (1일)
1. FastAPI 프로젝트 초기화
2. SQLite 데이터베이스 생성
3. 기본 HTML 페이지 작성
4. 인증 시스템 구현 (회원가입, 로그인)

### Phase 2: 발주사 & 템플릿 관리 (1일)
1. 발주사 CRUD API 구현
2. 템플릿 CRUD API 구현
3. 프론트엔드 연동

### Phase 3: 문자 발송 (2일)
1. SOLAPI 연동
2. 발송 로직 구현 (재발송 포함)
3. 미리보기 기능
4. 발송 이력 저장

### Phase 4: 임시저장 & 마무리 (1일)
1. 임시저장 기능 구현
2. 중복 체크 로직
3. UI/UX 개선
4. 테스트

**예상 개발 기간: 5일**

---

## 10. 주요 라이브러리

### 10.1 requirements.txt
```
fastapi>=0.115.0
uvicorn>=0.32.0
sqlalchemy>=2.0.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
python-multipart>=0.0.20
bcrypt>=4.2.0
solapi>=5.0.2
python-dotenv>=1.0.0
psycopg2-binary>=2.9.10
itsdangerous>=2.2.0
```

**주요 변경사항:**
- Python 3.13 호환성을 위해 최신 버전 사용
- solapi SDK 5.x 버전으로 업그레이드
- PostgreSQL 지원을 위한 psycopg2-binary 추가
- 세션 미들웨어를 위한 itsdangerous 추가
- pydantic-settings 분리 패키지 추가

---

## 11. 보안 고려사항

### 11.1 비밀번호
- bcrypt 해싱 사용
- 최소 8자 이상

### 11.2 세션
- HTTPOnly 쿠키
- 24시간 만료

### 11.3 SOLAPI 키
- config.py에 저장 (Git에 업로드 금지)
- 환경변수 사용 권장

### 11.4 SQL Injection
- SQLAlchemy ORM 사용으로 방지

---

## 12. 테스트 시나리오

### 12.1 발주사 관리
- [ ] 발주사 등록 (정상)
- [ ] 발주사 검색 (이름으로)
- [ ] 발주사 수정
- [ ] 발주사 삭제

### 12.2 템플릿 관리
- [ ] 템플릿 등록 (10개 제한 확인)
- [ ] 변수 치환 테스트 ({발주사명}, {캠페인명})
- [ ] 템플릿 수정/삭제

### 12.3 문자 발송
- [ ] 템플릿 선택
- [ ] 발주사 추가 (검색)
- [ ] 중복 체크 (같은 발주사 추가 시 경고)
- [ ] 미리보기
- [ ] 임시저장 (1개만)
- [ ] 임시저장 불러오기 (덮어쓰기)
- [ ] 일괄 발송 (성공)
- [ ] 발송 실패 시 재발송
- [ ] 발송 이력 확인

### 12.4 인증
- [ ] 회원가입
- [ ] 로그인/로그아웃
- [ ] 세션 유지

---

## 13. 배포 가이드

### 13.1 로컬 실행
```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 설정 파일 작성
# config.py에 SOLAPI 키 입력

# 4. 데이터베이스 초기화
python -c "from app.database import init_db; init_db()"

# 5. 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 13.2 접속
```
http://localhost:8000
```

### 13.3 Vercel 배포
```bash
# 1. GitHub 저장소 생성 및 푸시
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main

# 2. Vercel 프로젝트 연결
# - Vercel 대시보드에서 GitHub 저장소 연결
# - 환경변수 설정:
#   DATABASE_URL=<Vercel PostgreSQL URL>
#   SOLAPI_API_KEY=<your-api-key>
#   SOLAPI_API_SECRET=<your-api-secret>
#   SOLAPI_SENDER_PHONE=<your-phone>
#   SECRET_KEY=<random-secret-key>

# 3. 자동 배포
# - main 브랜치에 푸시할 때마다 자동 배포
```

**배포 파일:** `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

---

## 14. 향후 개선 사항 (Optional)

### 14.1 현재 포기한 기능
- ~~엑셀 업로드~~ (개별 추가로 충분)

### 14.2 추가 고려 사항
- 발송 이력 조회 UI (현재는 DB에만 기록)
- 대시보드 (발송 통계)
- 발주사 그룹 기능
- 예약 발송
- 대량 발주사 등록 (CSV)

---

## 15. 문의 및 지원

- 개발 중 이슈가 발생하면 이 문서를 기준으로 논의
- 기능 변경은 별도 문서로 관리

---

## 16. 개발 현황

### 완료된 작업
- ✅ Phase 1: 기본 구조 및 인증 시스템
  - FastAPI 프로젝트 초기화
  - 데이터베이스 모델 및 스키마
  - 회원가입/로그인/로그아웃 API
  - 기본 HTML 페이지
  - 개발 서버 구동 성공

### 진행 예정
- ⏳ Phase 2: 발주사 & 템플릿 관리
- ⏳ Phase 3: 문자 발송 기능
- ⏳ Phase 4: 임시저장 및 마무리
- ⏳ GitHub 연동 및 Vercel 배포

---

**문서 버전**: 2.0
**최종 수정일**: 2025-09-30
**작성자**: Claude

---

> 📝 **변경 이력**
> - v2.0 (2025-09-30): 실제 구현 내용 반영 (Python 3.13, PostgreSQL, Vercel 배포)
> - v1.0 (2025-09-30): 초기 설계 문서
