#!/usr/bin/env python3
"""
데이터베이스 테이블 재생성 스크립트
기존 테이블을 삭제하고 새로 생성합니다.
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from sqlalchemy import text

def drop_tables():
    """기존 테이블 삭제"""
    try:
        print("기존 테이블 삭제 중...")
        
        # 기존 테이블 삭제
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS game_results CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS user_difficulties CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS stories CASCADE"))
            conn.commit()
        
        print("✅ 기존 테이블 삭제 완료!")
        
    except Exception as e:
        print(f"❌ 테이블 삭제 실패: {e}")
        raise

def create_tables():
    """새 테이블 생성"""
    try:
        print("새 테이블 생성 중...")
        
        # 모든 모델을 import하여 테이블 생성
        from app.models.game_result import GameResult, UserDifficulty
        from app.models.story import Story
        
        Base.metadata.create_all(bind=engine)
        print("✅ 새 테이블 생성 완료!")
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        raise

def verify_tables():
    """테이블 생성 확인"""
    try:
        print("테이블 생성 확인 중...")
        
        with engine.connect() as conn:
            # game_results 테이블 구조 확인
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'game_results' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("\n📋 game_results 테이블 구조:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 테이블 개수 확인
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.fetchone()[0]
            print(f"\n📊 총 테이블 개수: {table_count}")
            
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        print("🔄 데이터베이스 테이블 재생성 시작...")
        
        # 1. 기존 테이블 삭제
        drop_tables()
        
        # 2. 새 테이블 생성
        create_tables()
        
        # 3. 테이블 생성 확인
        verify_tables()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
