from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # "postgresql://neondb_owner:npg_JmHTASslW8B6@ep-summer-frost-a1ojuc9i.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    # "postgresql://neondb_owner:npg_JmHTASslW8B6@ep-summer-frost-a1ojuc9i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
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