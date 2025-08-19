#!/usr/bin/env python3
"""
story_segments 테이블 구조와 데이터 확인 스크립트
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

def check_story_segments():
    """story_segments 테이블 확인"""
    try:
        print("🔍 story_segments 테이블 확인 중...")
        
        with engine.connect() as conn:
            # 1. 테이블 구조 확인
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'story_segments' 
                ORDER BY ordinal_position
            """))
            
            print("\n📋 story_segments 테이블 구조:")
            for col in result.fetchall():
                default = col[3] if col[3] else 'NULL'
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}) [기본값: {default}]")
            
            # 2. 데이터 개수 확인
            result = conn.execute(text("SELECT COUNT(*) FROM story_segments"))
            count = result.fetchone()[0]
            print(f"\n📊 story_segments 테이블 데이터 개수: {count}")
            
            # 3. 샘플 데이터 확인
            if count > 0:
                result = conn.execute(text("SELECT * FROM story_segments LIMIT 5"))
                rows = result.fetchall()
                print(f"\n📝 story_segments 샘플 데이터 (최대 5개):")
                for i, row in enumerate(rows):
                    print(f"  {i+1}. {row}")
            
            # 4. stories 테이블 확인
            result = conn.execute(text("SELECT COUNT(*) FROM stories"))
            story_count = result.fetchone()[0]
            print(f"\n📊 stories 테이블 데이터 개수: {story_count}")
            
            if story_count > 0:
                result = conn.execute(text("SELECT id, title, content FROM stories LIMIT 3"))
                stories = result.fetchall()
                print("📝 등록된 이야기:")
                for story in stories:
                    print(f"  - ID: {story[0]}, 제목: {story[1]}")
                    print(f"    내용: {story[2][:100]}...")
            
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        check_story_segments()
        print("\n✅ 확인 완료!")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
