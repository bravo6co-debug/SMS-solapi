#!/usr/bin/env python3
"""
Railway 배포용 시작 스크립트
PORT 환경변수를 읽어서 uvicorn 실행
"""
import os
import subprocess
import sys

def main():
    # Railway가 주입하는 PORT 환경변수 읽기 (기본값: 8000)
    port = os.environ.get("PORT", "8000")

    # uvicorn 명령어 구성
    cmd = [
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--timeout-keep-alive", "300",  # Keep-alive 타임아웃 5분
        "--timeout-graceful-shutdown", "60"  # Graceful shutdown 타임아웃 1분
    ]

    print(f"Starting uvicorn on port {port}...")

    # uvicorn 실행
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting uvicorn: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
