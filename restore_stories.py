#!/usr/bin/env python3
"""
stories 테이블 복구 스크립트
기존 story_segments 데이터를 활용해서 stories 테이블을 복구합니다.
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

def restore_stories():
    """stories 테이블 복구"""
    try:
        print("🔧 stories 테이블 복구 중...")
        
        with engine.connect() as conn:
            # 1. story_segments에서 story_id별로 그룹화하여 이야기 복구
            result = conn.execute(text("""
                SELECT DISTINCT story_id 
                FROM story_segments 
                ORDER BY story_id
            """))
            
            story_ids = [row[0] for row in result.fetchall()]
            print(f"📝 복구할 이야기 개수: {len(story_ids)}")
            
            for story_id in story_ids:
                # 각 story_id에 대한 세그먼트들을 순서대로 가져오기
                result = conn.execute(text("""
                    SELECT segment_text 
                    FROM story_segments 
                    WHERE story_id = :story_id 
                    ORDER BY "order"
                """), {"story_id": story_id})
                
                segments = [row[0] for row in result.fetchall()]
                full_content = " ".join(segments)
                
                # 첫 번째 세그먼트를 제목으로 사용 (간단하게)
                title = segments[0][:30] + "..." if len(segments[0]) > 30 else segments[0]
                
                # stories 테이블에 이야기 추가
                conn.execute(text("""
                    INSERT INTO stories (id, user_id, title, content, image_url) 
                    VALUES (:story_id, 1, :title, :content, NULL)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    "story_id": story_id,
                    "title": title,
                    "content": full_content
                })
                
                print(f"✅ 이야기 {story_id} 복구 완료: {title}")
            
            conn.commit()
            print(f"\n🎉 총 {len(story_ids)}개의 이야기 복구 완료!")
            
    except Exception as e:
        print(f"❌ 이야기 복구 실패: {e}")
        raise

def verify_restoration():
    """복구 결과 확인"""
    try:
        print("\n🔍 복구 결과 확인 중...")
        
        with engine.connect() as conn:
            # 1. stories 테이블 확인
            result = conn.execute(text("SELECT COUNT(*) FROM stories"))
            story_count = result.fetchone()[0]
            print(f"\n📊 stories 테이블 데이터 개수: {story_count}")
            
            if story_count > 0:
                result = conn.execute(text("SELECT id, title, content FROM stories LIMIT 3"))
                stories = result.fetchall()
                print("📝 복구된 이야기:")
                for story in stories:
                    print(f"  - ID: {story[0]}, 제목: {story[1]}")
                    print(f"    내용: {story[2][:100]}...")
            
            # 2. API 테스트용 랜덤 세그먼트 조회
            result = conn.execute(text("""
                SELECT s.id, s.title, ss.segment_text, ss."order"
                FROM stories s
                JOIN story_segments ss ON s.id = ss.story_id
                ORDER BY s.id, ss."order"
                LIMIT 10
            """))
            
            rows = result.fetchall()
            print(f"\n🔗 이야기-세그먼트 연결 확인 (최대 10개):")
            for row in rows:
                print(f"  - 이야기 {row[0]} ({row[1]}): 세그먼트 {row[3]} - {row[2][:50]}...")
            
    except Exception as e:
        print(f"❌ 복구 결과 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        print("🔄 stories 테이블 복구 시작...")
        
        # 1. 이야기 복구
        restore_stories()
        
        # 2. 복구 결과 확인
        verify_restoration()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
