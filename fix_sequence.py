#!/usr/bin/env python3
"""
ID 시퀀스 재설정 스크립트
stories 테이블의 id 시퀀스를 현재 최대값 다음부터 시작하도록 설정합니다.
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

def fix_id_sequence():
    """ID 시퀀스 재설정"""
    try:
        print("🔧 ID 시퀀스 재설정 중...")
        
        with engine.connect() as conn:
            # 1. 현재 stories 테이블의 최대 id 확인
            result = conn.execute(text("SELECT MAX(id) FROM stories"))
            max_id = result.fetchone()[0]
            print(f"📊 현재 최대 ID: {max_id}")
            
            if max_id is None:
                print("❌ stories 테이블에 데이터가 없습니다.")
                return
            
            # 2. 시퀀스 이름 확인 (PostgreSQL에서 자동 생성된 시퀀스)
            result = conn.execute(text("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public' 
                AND sequence_name LIKE '%stories%'
            """))
            
            sequences = result.fetchall()
            print(f"🔍 발견된 시퀀스들: {[seq[0] for seq in sequences]}")
            
            # 3. stories_id_seq 시퀀스 재설정
            if sequences:
                sequence_name = sequences[0][0]  # 첫 번째 시퀀스 사용
                print(f"✅ 시퀀스 '{sequence_name}' 재설정 중...")
                
                # 시퀀스를 현재 최대값으로 설정
                conn.execute(text(f"SELECT setval('{sequence_name}', {max_id})"))
                
                # 다음 값 확인
                result = conn.execute(text(f"SELECT nextval('{sequence_name}')"))
                next_id = result.fetchone()[0]
                
                print(f"✅ 시퀀스 재설정 완료!")
                print(f"📊 다음 ID는 {next_id}부터 시작됩니다.")
                
                conn.commit()
            else:
                print("⚠️ stories 테이블과 관련된 시퀀스를 찾을 수 없습니다.")
                print("테이블을 다시 생성해야 할 수 있습니다.")
                
    except Exception as e:
        print(f"❌ 시퀀스 재설정 실패: {e}")
        raise

def verify_fix():
    """수정 결과 확인"""
    try:
        print("\n🔍 수정 결과 확인 중...")
        
        with engine.connect() as conn:
            # 1. 현재 최대 ID 확인
            result = conn.execute(text("SELECT MAX(id) FROM stories"))
            max_id = result.fetchone()[0]
            print(f"📊 stories 테이블 최대 ID: {max_id}")
            
            # 2. 시퀀스 현재 값 확인
            result = conn.execute(text("""
                SELECT sequence_name, last_value, is_called
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public' 
                AND sequence_name LIKE '%stories%'
            """))
            
            sequences = result.fetchall()
            for seq in sequences:
                print(f"🔍 시퀀스 '{seq[0]}': last_value={seq[1]}, is_called={seq[2]}")
            
            # 3. 테스트로 새 ID 생성 시도
            if sequences:
                sequence_name = sequences[0][0]
                result = conn.execute(text(f"SELECT nextval('{sequence_name}')"))
                test_id = result.fetchone()[0]
                print(f"🧪 테스트 - 다음 ID: {test_id}")
                
                if test_id > max_id:
                    print("✅ 시퀀스가 올바르게 설정되었습니다!")
                else:
                    print("❌ 시퀀스 설정에 문제가 있습니다.")
                    
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        raise

def main():
    """메인 함수"""
    try:
        print("🔄 ID 시퀀스 재설정 시작...")
        
        # 1. 시퀀스 재설정
        fix_id_sequence()
        
        # 2. 결과 확인
        verify_fix()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        print("이제 새로운 이야기를 등록할 수 있습니다.")
        
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
