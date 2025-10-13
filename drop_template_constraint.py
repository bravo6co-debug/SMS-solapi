#!/usr/bin/env python3
"""
템플릿 테이블의 CheckConstraint 제거 스크립트
Railway PostgreSQL에서 실행하여 제약 조건을 삭제합니다.
"""
from sqlalchemy import create_engine, text
from config import settings
import sys

def drop_constraint():
    """템플릿 체크 제약 조건 삭제"""
    try:
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # 기존 제약 조건 확인
            result = conn.execute(text("""
                SELECT conname
                FROM pg_constraint
                WHERE conrelid = 'templates'::regclass
                AND conname = 'chk_category'
            """))

            constraint_exists = result.fetchone()

            if constraint_exists:
                print("✅ 'chk_category' 제약 조건이 존재합니다. 삭제를 시작합니다...")

                # 제약 조건 삭제
                conn.execute(text("""
                    ALTER TABLE templates DROP CONSTRAINT IF EXISTS chk_category
                """))
                conn.commit()

                print("✅ 'chk_category' 제약 조건이 성공적으로 삭제되었습니다!")
            else:
                print("ℹ️  'chk_category' 제약 조건이 존재하지 않습니다. (이미 삭제되었거나 없음)")

            # 현재 템플릿 확인
            result = conn.execute(text("SELECT COUNT(*) FROM templates"))
            count = result.fetchone()[0]
            print(f"📊 현재 템플릿 개수: {count}개")

            return True

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("템플릿 CheckConstraint 제거 스크립트")
    print("=" * 60)
    print(f"DATABASE_URL: {settings.DATABASE_URL[:30]}...")
    print()

    success = drop_constraint()

    if success:
        print()
        print("=" * 60)
        print("✅ 작업이 완료되었습니다!")
        print("이제 Railway 앱을 재시작하면 템플릿 등록이 정상적으로 작동합니다.")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("❌ 작업 실패. 위 오류를 확인하세요.")
        print("=" * 60)
        sys.exit(1)
