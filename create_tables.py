#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db

def main():
    """메인 함수"""
    try:
        print("데이터베이스 테이블 생성 시작...")
        init_db()
        print("✅ 데이터베이스 테이블 생성 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 생성 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
