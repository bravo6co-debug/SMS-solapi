# 데이터베이스 마이그레이션 가이드

## 개요

발주사 삭제 시 발송 이력도 함께 삭제되도록 외래 키 제약 조건을 CASCADE로 변경하는 마이그레이션입니다.

**변경 내용**: `send_history.company_id` 외래 키 제약 조건을 `RESTRICT` → `CASCADE`로 변경

---

## 실행 방법

### 방법 1: Railway CLI 사용 (권장)

```bash
# Railway에 로그인
railway login

# 프로젝트 연결 (처음 한 번만)
railway link

# 마이그레이션 실행
railway run python run_migration.py
```

### 방법 2: Railway 대시보드에서 직접 실행

1. Railway 대시보드 접속
2. 프로젝트 선택
3. PostgreSQL 서비스 선택
4. "Connect" 탭에서 데이터베이스 접속 정보 확인
5. PostgreSQL 클라이언트(psql, DBeaver 등)로 접속
6. `migrations/migrate_cascade.sql` 파일 내용 복사하여 실행

---

## 실행 전 체크리스트

- [ ] Railway CLI 설치 확인 (`railway --version`)
- [ ] Railway에 로그인 (`railway login`)
- [ ] 프로젝트가 연결되어 있는지 확인 (`railway status`)
- [ ] (선택) 데이터베이스 백업 (Railway 대시보드에서 스냅샷 생성)

---

## 실행 예시

```bash
$ railway run python run_migration.py

============================================================
🔧 Database Migration Tool
============================================================
📄 Loading migration script: migrations/migrate_cascade.sql
🔗 Connecting to database...
✅ Connected to database
🚀 Executing migration...

✅ Migration completed successfully!

📊 Verification:
============================================================
Constraint Name: send_history_company_id_fkey
Table Name: send_history
Column Name: company_id
Delete Rule: CASCADE

✅ Foreign key constraint successfully changed to CASCADE!
============================================================
```

---

## 트러블슈팅

### 에러: `DATABASE_URL environment variable not set`

**원인**: 환경변수가 설정되지 않음

**해결**:
```bash
# Railway CLI로 실행 (자동으로 환경변수 주입)
railway run python run_migration.py
```

### 에러: `Migration file not found`

**원인**: 잘못된 경로에서 실행

**해결**: 프로젝트 루트 디렉토리에서 실행
```bash
cd c:\Users\admin\Dev_Project\sms-solapi
railway run python run_migration.py
```

### 에러: `psycopg2 module not found`

**원인**: psycopg2 패키지가 설치되지 않음

**해결**:
```bash
pip install psycopg2-binary
```

---

## 마이그레이션 확인

마이그레이션 후 다음 명령어로 제약 조건이 올바르게 변경되었는지 확인할 수 있습니다:

```sql
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'send_history'
    AND kcu.column_name = 'company_id';
```

**예상 결과**:
```
constraint_name              | send_history_company_id_fkey
table_name                   | send_history
column_name                  | company_id
delete_rule                  | CASCADE
```

---

## 마이그레이션 롤백 (필요한 경우)

CASCADE에서 RESTRICT로 되돌리려면:

```sql
BEGIN;

ALTER TABLE send_history
DROP CONSTRAINT send_history_company_id_fkey;

ALTER TABLE send_history
ADD CONSTRAINT send_history_company_id_fkey
    FOREIGN KEY (company_id)
    REFERENCES companies(id)
    ON DELETE RESTRICT;

COMMIT;
```

---

## 주의사항

⚠️ **이 마이그레이션 후 발주사를 삭제하면 관련된 모든 발송 이력도 함께 삭제됩니다.**

- 데이터를 복구할 수 없으므로 신중하게 삭제하세요
- 중요한 데이터는 정기적으로 백업하세요
- 가능하면 Railway 대시보드에서 스냅샷을 생성하세요

---

## 문의

마이그레이션 관련 문제가 발생하면:

1. 에러 메시지 전체 복사
2. Railway 로그 확인 (`railway logs`)
3. GitHub Issues에 문의
