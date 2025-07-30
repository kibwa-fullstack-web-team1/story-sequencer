from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
# from app.models.user import User  # 실제 User 모델 import 필요 (user-service와 통합 시)

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # 외래키 제약조건 제거
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    segments = relationship("StorySegment", back_populates="story", cascade="all, delete-orphan")
    # user = relationship("User")  # 실제 User 모델과 연결 (user-service와 통합 시)

class StorySegment(Base):
    __tablename__ = "story_segments"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    segment_text = Column(Text, nullable=False)

    story = relationship("Story", back_populates="segments") 