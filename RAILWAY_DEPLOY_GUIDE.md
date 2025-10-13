# Railway 배포 가이드

> 🚂 **Railway로 SOLAPI 문자 발송 시스템 배포하기**
>
> Railway는 FastAPI + PostgreSQL 스택에 최적화된 배포 플랫폼입니다.

---

## 📋 배포 전 체크리스트

- [ ] GitHub 계정
- [ ] SOLAPI API 키 (API Key, API Secret, 발신번호)
- [ ] Railway 계정 (GitHub로 로그인 가능)

---

## 🚀 1단계: Railway 프로젝트 생성

### 1.1 Railway 회원가입
1. [Railway.app](https://railway.app) 접속
2. "Start a New Project" 클릭
3. GitHub 계정으로 로그인

### 1.2 PostgreSQL 추가
1. "New Project" → "Provision PostgreSQL" 클릭
2. PostgreSQL 인스턴스가 자동 생성됨
3. `DATABASE_URL` 환경변수가 자동 주입됨

### 1.3 GitHub 레포지토리 연결
1. "New" → "GitHub Repo" 클릭
2. 본 프로젝트 레포지토리 선택
3. `main` 또는 `master` 브랜치 선택

---

## ⚙️ 2단계: 환경변수 설정

Railway 대시보드 → 프로젝트 선택 → "Variables" 탭에서 다음 환경변수를 추가하세요.

### 필수 환경변수

```bash
# SOLAPI 설정
SOLAPI_API_KEY=your_api_key_here
SOLAPI_API_SECRET=your_api_secret_here
SOLAPI_SENDER_PHONE=01012345678

# 세션 보안 (랜덤 문자열 생성 필수!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# 데이터베이스 (Railway가 자동 주입하므로 설정 불필요)
# DATABASE_URL은 PostgreSQL 서비스에서 자동으로 제공됨
```

### SECRET_KEY 생성 방법

#### Python 사용:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 온라인 생성:
- [RandomKeygen.com](https://randomkeygen.com/)
- 256-bit key 사용 권장

---

## 🔧 3단계: 배포 설정

### 3.1 자동 배포 확인
- Railway는 `railway.json` 또는 `railway.toml` 파일을 자동 감지합니다.
- Dockerfile을 자동으로 인식하여 빌드합니다.

### 3.2 배포 시작
1. GitHub에 코드 푸시 → 자동 배포 시작
2. Railway 대시보드에서 배포 로그 확인
3. 빌드 완료 후 URL 자동 생성 (예: `https://your-app.railway.app`)

### 3.3 도메인 설정 (선택)
1. Railway 대시보드 → "Settings" → "Domains"
2. "Generate Domain" 클릭 → 무료 `.railway.app` 도메인 생성
3. 또는 커스텀 도메인 연결 가능

---

## 🗄️ 4단계: 데이터베이스 초기화

Railway는 애플리케이션 시작 시 자동으로 데이터베이스를 초기화합니다.
([main.py:68](main.py#L68)의 `init_database_with_retry()` 함수 참조)

### 수동 초기화가 필요한 경우:
```bash
# Railway CLI 설치
npm i -g @railway/cli

# Railway 로그인
railway login

# 프로젝트 연결
railway link

# 데이터베이스 초기화 스크립트 실행
railway run python init_db.py
```

---

## 🔍 5단계: 배포 확인

### 헬스체크
```bash
curl https://your-app.railway.app/health
# 응답: {"status": "ok"}
```

### API 문서 확인
브라우저에서 다음 URL 접속:
```
https://your-app.railway.app/docs
```

### 메인 페이지 접속
```
https://your-app.railway.app/
```

---

## 🛠️ 트러블슈팅

### 문제 1: 빌드 실패
**증상**: Dockerfile 빌드 중 오류 발생

**해결책**:
- Railway 로그 확인: "Deployments" → 실패한 배포 클릭
- Python 버전 확인 (Dockerfile에서 3.13 사용)
- `requirements.txt` 패키지 버전 호환성 확인

### 문제 2: 데이터베이스 연결 실패
**증상**: `DATABASE_URL` 연결 오류

**해결책**:
```bash
# PostgreSQL 서비스가 프로젝트에 연결되었는지 확인
railway service list

# DATABASE_URL이 자동 주입되는지 확인
railway variables
```

### 문제 3: SOLAPI 발송 실패
**증상**: 문자 발송 시 401/403 오류

**해결책**:
- `SOLAPI_API_KEY`, `SOLAPI_API_SECRET` 환경변수 재확인
- SOLAPI 콘솔에서 API 키 상태 확인
- 발신번호 등록 여부 확인

### 문제 4: 정적 파일 404 오류
**증상**: CSS/JS 파일이 로드되지 않음

**해결책**:
- `static/` 디렉토리가 Git에 포함되어 있는지 확인
- [main.py:33-37](main.py#L33-L37)의 정적 파일 마운트 로직 확인

---

## 💰 비용 안내

### Free Tier (무료)
- **월 500시간** 실행 시간
- **1GB RAM**
- **PostgreSQL 1GB 스토리지**
- **무료 `.railway.app` 도메인**

**예상 비용**: 거의 무료 (500시간 ≈ 20일 24시간 가동)

### Hobby Plan ($5/월)
- **무제한** 실행 시간
- **8GB RAM**
- **PostgreSQL 무제한**
- **커스텀 도메인 지원**

### 실제 예상 비용:
- 소규모 프로젝트: **무료 ~ $1/월**
- 중규모 프로젝트: **$5 ~ $10/월**

---

## 📊 모니터링

### Railway 대시보드
- **Metrics**: CPU, 메모리, 네트워크 사용량
- **Logs**: 실시간 애플리케이션 로그
- **Deployments**: 배포 이력 및 롤백

### 로그 확인
```bash
# Railway CLI로 실시간 로그 보기
railway logs
```

---

## 🔄 CI/CD 자동화

### GitHub Push → 자동 배포
1. 코드 수정 후 `git push`
2. Railway가 자동으로 감지하여 빌드 시작
3. 빌드 성공 시 자동 배포
4. 실패 시 이전 버전 유지 (자동 롤백)

### 브랜치별 배포 (선택)
- `main` 브랜치: 프로덕션 배포
- `dev` 브랜치: 개발 환경 배포 (별도 프로젝트 생성)

---

## 🔐 보안 권장사항

### 1. SECRET_KEY
- 절대 GitHub에 커밋하지 마세요
- 최소 32자 이상 랜덤 문자열 사용
- 주기적으로 변경 (3개월마다 권장)

### 2. SOLAPI API 키
- Railway Variables에만 저장
- 로컬 개발은 `.env` 파일 사용 (`.gitignore`에 추가)

### 3. HTTPS
- Railway는 기본적으로 HTTPS 제공
- [main.py:22](main.py#L22)의 `https_only=False`를 `True`로 변경 권장:
  ```python
  https_only=True  # 프로덕션에서는 True 사용
  ```

### 4. CORS 설정
만약 별도 프론트엔드에서 API 호출 시:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📞 지원

### Railway 공식 문서
- [Railway Docs](https://docs.railway.app/)
- [Dockerfile 배포 가이드](https://docs.railway.app/deploy/dockerfiles)

### Railway 커뮤니티
- [Discord](https://discord.gg/railway)
- [GitHub Discussions](https://github.com/railwayapp/railway/discussions)

### 본 프로젝트 이슈
- [GitHub Issues](https://github.com/your-repo/issues)

---

## ✅ 배포 완료 체크리스트

배포 후 다음 항목들을 확인하세요:

- [ ] 헬스체크 API 응답 확인 (`/health`)
- [ ] API 문서 접속 확인 (`/docs`)
- [ ] 로그인 기능 테스트
- [ ] 발주사 CRUD 테스트
- [ ] 템플릿 CRUD 테스트
- [ ] SOLAPI 문자 발송 테스트 (실제 발송)
- [ ] 임시저장 기능 테스트
- [ ] 발송 이력 기록 확인

---

## 🎉 배포 완료!

Railway 배포가 완료되었습니다!

**다음 단계:**
1. 팀원들에게 URL 공유
2. SOLAPI 크레딧 충전
3. 실제 발주사 데이터 입력
4. 문자 발송 테스트

**추천 다음 작업:**
- 커스텀 도메인 연결
- 모니터링 대시보드 설정
- 정기 백업 자동화
- 성능 모니터링 도구 연동 (예: Sentry)
