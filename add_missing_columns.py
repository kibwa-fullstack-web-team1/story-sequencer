#!/usr/bin/env python3
"""
필요한 컬럼만 추가하는 스크립트
기존 테이블과 데이터를 보존하면서 컬럼을 추가합니다.
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

def add_missing_columns():
    """필요한 컬럼만 추가"""
    try:
        print("🔧 필요한 컬럼 추가 중...")
        
        with engine.connect() as conn:
            # 1. game_results 테이블에 game_type 컬럼이 있는지 확인
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'game_results' AND column_name = 'game_type'
            """))
            
            if result.fetchone():
                print("✅ game_results.game_type 컬럼이 이미 존재합니다.")
            else:
                print("➕ game_results 테이블에 game_type 컬럼 추가 중...")
                conn.execute(text("""
                    ALTER TABLE game_results 
                    ADD COLUMN game_type VARCHAR(50) NOT NULL DEFAULT 'unknown'
                """))
                print("✅ game_results.game_type 컬럼 추가 완료!")
            
            # 2. story_segments 테이블 구조 확인
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'story_segments'
                ORDER BY ordinal_position
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"\n📋 story_segments 테이블 현재 컬럼: {existing_columns}")
            
            # 3. 필요한 컬럼들 추가
            required_columns = {
                'story_id': 'INTEGER REFERENCES stories(id)',
                'segment_order': 'INTEGER NOT NULL',
                'content': 'TEXT NOT NULL',
                'created_at': 'TIMESTAMP DEFAULT NOW()'
            }
            
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    print(f"➕ story_segments 테이블에 {col_name} 컬럼 추가 중...")
                    try:
                        conn.execute(text(f"ALTER TABLE story_segments ADD COLUMN {col_name} {col_def}"))
                        print(f"✅ {col_name} 컬럼 추가 완료!")
                    except Exception as e:
                        print(f"⚠️ {col_name} 컬럼 추가 실패 (이미 존재할 수 있음): {e}")
                else:
                    print(f"✅ {col_name} 컬럼이 이미 존재합니다.")
            
            # 4. 기본 이야기 데이터 추가 (테스트용)
            result = conn.execute(text("SELECT COUNT(*) FROM stories"))
            story_count = result.fetchone()[0]
            
            if story_count == 0:
                print("\n📝 기본 이야기 데이터 추가 중...")
                
                # 기본 이야기 추가
                conn.execute(text("""
                    INSERT INTO stories (user_id, title, content, image_url) 
                    VALUES (1, '할머니와의 추억', '어린 시절 할머니와 함께 정원에서 꽃을 심었던 추억이 아직도 생생합니다.', NULL)
                """))
                
                # 이야기 ID 가져오기
                result = conn.execute(text("SELECT id FROM stories WHERE title = '할머니와의 추억'"))
                story_id = result.fetchone()[0]
                
                # 이야기 세그먼트 추가
                segments = [
                    "어린 시절",
                    "할머니와 함께",
                    "정원에서",
                    "꽃을 심었던",
                    "추억이",
                    "아직도",
                    "생생합니다"
                ]
                
                for i, segment in enumerate(segments):
                    conn.execute(text("""
                        INSERT INTO story_segments (story_id, segment_order, content) 
                        VALUES (:story_id, :segment_order, :content)
                    """), {"story_id": story_id, "segment_order": i + 1, "content": segment})
                
                print(f"✅ 기본 이야기와 {len(segments)}개 세그먼트 추가 완료!")
            else:
                print(f"✅ stories 테이블에 {story_count}개의 이야기가 이미 존재합니다.")
            
            conn.commit()
            
    except Exception as e:
        print(f"❌ 컬럼 추가 실패: {e}")
        raise

def verify_changes():
    """변경사항 확인"""
    try:
        print("\n🔍 변경사항 확인 중...")
        
        with engine.connect() as conn:
            # 1. game_results 테이블 확인
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'game_results' 
                ORDER BY ordinal_position
            """))
            
            print("\n📋 game_results 테이블 최종 구조:")
            for col in result.fetchall():
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[1] == 'YES' else 'NOT NULL'})")
            
            # 2. stories 테이블 데이터 확인
            result = conn.execute(text("SELECT COUNT(*) FROM stories"))
            story_count = result.fetchone()[0]
            print(f"\n📊 stories 테이블 데이터 개수: {story_count}")
            
            if story_count > 0:
                result = conn.execute(text("SELECT id, title FROM stories LIMIT 3"))
                stories = result.fetchall()
                print("📝 등록된 이야기:")
                for story in stories:
                    print(f"  - ID: {story[0]}, 제목: {story[1]}")
            
            # 3. story_segments 테이블 데이터 확인
            result = conn.execute(text("SELECT COUNT(*) FROM story_segments"))
            segment_count = result.fetchone()[0]
            print(f"\n📊 story_segments 테이블 데이터 개수: {segment_count}")
            
    except Exception as e:
        print(f"❌ 변경사항 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        print("🔄 데이터베이스 컬럼 추가 시작...")
        
        # 1. 필요한 컬럼 추가
        add_missing_columns()
        
        # 2. 변경사항 확인
        verify_changes()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
