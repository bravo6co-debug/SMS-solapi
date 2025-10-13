# Railway 배포 빠른 시작 가이드 (5분 완성)

> ⚡ **5분 안에 Railway에 배포하기**

---

## 🎯 준비물

1. **GitHub 계정**
2. **SOLAPI API 키** ([SOLAPI 콘솔](https://console.solapi.com/)에서 발급)
   - API Key
   - API Secret
   - 발신번호 (등록된 전화번호)

---

## 🚀 1단계: Railway 프로젝트 생성 (2분)

### 1. Railway 가입
```
https://railway.app → "Start a New Project" → GitHub 로그인
```

### 2. 서비스 추가
Railway 대시보드에서:

#### (1) PostgreSQL 추가
```
"+ New" → "Database" → "Add PostgreSQL"
```
✅ `DATABASE_URL` 자동 생성됨

#### (2) GitHub 레포지토리 연결
```
"+ New" → "GitHub Repo" → 본 프로젝트 선택
```
✅ 자동으로 Dockerfile 감지 후 빌드 시작

---

## ⚙️ 2단계: 환경변수 설정 (2분)

Railway 대시보드 → 앱 서비스 클릭 → "Variables" 탭

### 필수 3개 + 1개 추가

```bash
# SOLAPI 설정 (필수)
SOLAPI_API_KEY=NCS...YOUR_KEY
SOLAPI_API_SECRET=YOUR_SECRET
SOLAPI_SENDER_PHONE=01012345678

# 보안 키 생성 (필수)
SECRET_KEY=생성한_랜덤_문자열
```

### SECRET_KEY 생성 방법

#### Windows (PowerShell):
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 복사할 키 예시:
```
Xg9vK2mN8pQ4wR7tY1uI5oP3aS6dF0jH2kL4zX8cV9bN
```

---

## 🔗 3단계: 도메인 생성 (30초)

Railway 대시보드 → "Settings" → "Networking"

```
"Generate Domain" 클릭
```

✅ `https://your-app-name.up.railway.app` 자동 생성

---

## ✅ 4단계: 배포 확인 (30초)

### 헬스체크
브라우저에서 접속:
```
https://your-app-name.up.railway.app/health
```

응답:
```json
{"status": "ok"}
```

### API 문서
```
https://your-app-name.up.railway.app/docs
```

### 메인 페이지
```
https://your-app-name.up.railway.app/
```

---

## 🎉 배포 완료!

**총 소요 시간: 약 5분**

---

## 📊 다음 단계

### 1. 초기 데이터 입력
로그인 후:
- [ ] 관리자 계정 생성
- [ ] 발주사 등록
- [ ] 템플릿 등록

### 2. 문자 발송 테스트
- [ ] SOLAPI 크레딧 충전
- [ ] 테스트 발송 (본인 번호로)
- [ ] 실제 발주사에게 발송

### 3. 모니터링
Railway 대시보드에서:
- [ ] "Metrics" 탭 → CPU/메모리 사용량 확인
- [ ] "Logs" 탭 → 실시간 로그 확인

---

## 🛠️ 트러블슈팅

### 빌드 실패 시
```bash
# Railway 로그 확인
Railway 대시보드 → "Deployments" → 실패한 배포 클릭 → 로그 확인
```

### 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스가 연결되었는지 확인
Railway 대시보드 → PostgreSQL 서비스 → "Variables" → DATABASE_URL 확인
```

### 환경변수 오류
```bash
# Variables 탭에서 다음 항목 재확인:
✅ SOLAPI_API_KEY
✅ SOLAPI_API_SECRET
✅ SOLAPI_SENDER_PHONE
✅ SECRET_KEY
```

---

## 💰 비용 안내

### Free Tier
- **월 500시간** (약 20일 24시간 가동)
- **무료 PostgreSQL 1GB**
- **예상 비용: $0 ~ $1/월**

### Hobby Plan ($5/월)
- **무제한 실행**
- **PostgreSQL 무제한**

---

## 📚 상세 가이드

더 자세한 정보는 [RAILWAY_DEPLOY_GUIDE.md](RAILWAY_DEPLOY_GUIDE.md) 참조

---

## 🔒 보안 팁

### 1. SECRET_KEY 보안
- ❌ GitHub에 커밋하지 마세요
- ✅ Railway Variables에만 저장
- ✅ 주기적으로 변경 (3개월)

### 2. SOLAPI API 키
- ✅ SOLAPI 콘솔에서 IP 제한 설정 권장
- ✅ 사용하지 않는 키는 삭제

### 3. HTTPS 강제
[main.py:22](main.py#L22) 수정:
```python
https_only=True  # 프로덕션 배포 시 True 사용
```

---

## 📞 지원

- **상세 가이드**: [RAILWAY_DEPLOY_GUIDE.md](RAILWAY_DEPLOY_GUIDE.md)
- **Railway 문서**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway

---

**Happy Deploying! 🚂🚀**
