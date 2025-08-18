from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    game_type = Column(String(50), nullable=False)  # 'SENTENCE_SEQUENCE', 'WORD_SEQUENCE'
    story_id = Column(Integer, ForeignKey("stories.id"))
    is_correct = Column(Boolean, nullable=False)
    response_time = Column(Float, nullable=False)  # 응답 시간 (초)
    score = Column(Integer, nullable=True)  # 점수 (선택사항)
    created_at = Column(DateTime, server_default=func.now())
    
    story = relationship("Story")

class UserDifficulty(Base):
    __tablename__ = "user_difficulties"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    current_game_type = Column(String(50), default='SENTENCE_SEQUENCE')
    success_rate = Column(Float, default=0.0)
    consecutive_success = Column(Integer, default=0)
    consecutive_failure = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now()) 