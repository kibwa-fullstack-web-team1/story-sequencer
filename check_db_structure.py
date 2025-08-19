#!/usr/bin/env python3
"""
데이터베이스 구조 확인 스크립트
테이블을 삭제하지 않고 현재 상태를 확인합니다.
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def check_database_structure():
    """데이터베이스 구조 확인"""
    try:
        print("🔍 데이터베이스 구조 확인 중...")
        
        with engine.connect() as conn:
            # 1. 모든 테이블 목록 확인
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            print(f"\n📊 총 테이블 개수: {len(tables)}")
            print("📋 테이블 목록:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 2. game_results 테이블 구조 확인
            if any('game_results' in table[0] for table in tables):
                print("\n📋 game_results 테이블 구조:")
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'game_results' 
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                for col in columns:
                    default = col[3] if col[3] else 'NULL'
                    print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}) [기본값: {default}]")
            else:
                print("\n❌ game_results 테이블이 존재하지 않습니다.")
            
            # 3. stories 테이블 구조 확인
            if any('stories' in table[0] for table in tables):
                print("\n📋 stories 테이블 구조:")
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'stories' 
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                for col in columns:
                    default = col[3] if col[3] else 'NULL'
                    print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}) [기본값: {default}]")
            else:
                print("\n❌ stories 테이블이 존재하지 않습니다.")
            
            # 4. 데이터 개수 확인
            for table_name in ['stories', 'game_results']:
                if any(table_name in table[0] for table in tables):
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"\n📊 {table_name} 테이블 데이터 개수: {count}")
                    
                    if count > 0:
                        # 샘플 데이터 확인
                        result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
                        rows = result.fetchall()
                        print(f"  📝 {table_name} 샘플 데이터 (최대 3개):")
                        for i, row in enumerate(rows):
                            print(f"    {i+1}. {row}")
            
    except Exception as e:
        print(f"❌ 데이터베이스 구조 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        check_database_structure()
        print("\n✅ 데이터베이스 구조 확인 완료!")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
