from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# 연결 풀 설정으로 SSL 연결 문제 해결
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """데이터베이스 테이블 초기화"""
    try:
        # 모든 모델을 import하여 테이블 생성
        from app.models.game_result import GameResult, UserDifficulty
        from app.models.story import Story
        
        print("데이터베이스 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        print("데이터베이스 테이블 생성 완료!")
        
    except Exception as e:
        print(f"데이터베이스 초기화 오류: {e}")
        raise 