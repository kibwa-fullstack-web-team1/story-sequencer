from sqlalchemy.orm import Session
from app.models.story import Story, StorySegment
from app.schemas.story import StoryCreate, StoryUpdate, StoryResponse
from app.common.response import NotFoundError, ValidationError
from typing import List, Optional
import logging

class StoryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def init_app(self, app):
        """앱 초기화"""
        self.logger.info("StoryService initialized")
        return self

    def create_story(self, db: Session, story_create: StoryCreate, app=None, user_id: int = None) -> StoryResponse:
        """이야기 생성"""
        try:
            # 유효성 검사
            if not story_create.title or not story_create.content:
                raise ValidationError("제목과 내용은 필수입니다.")
            
            # 이야기 생성
            db_story = Story(
                user_id=user_id,  # user_id 추가
                title=story_create.title,
                content=story_create.content,
                image_url=story_create.image_url
            )
            db.add(db_story)
            db.commit()
            db.refresh(db_story)
            
            self.logger.info(f"Story created with ID: {db_story.id}")
            
            # OpenAI로 문장 분리 (app.state.openai_service 사용)
            segments = []
            if app and hasattr(app, 'state') and hasattr(app.state, 'openai_service'):
                self.logger.info("Using OpenAI service for sentence splitting")
                segments = app.state.openai_service.split_story_into_segments(db_story.content)
            else:
                # fallback: 기본 분리
                self.logger.warning("OpenAI service not available, using fallback method")
                segments = [s.strip() for s in db_story.content.split('.') if s.strip()]
            
            self.logger.info(f"Split story into {len(segments)} segments")
            
            # 세그먼트 저장
            for idx, segment_text in enumerate(segments, start=1):
                if segment_text.strip():  # 빈 문자열이 아닌 경우만 저장
                    db_segment = StorySegment(
                        story_id=db_story.id,
                        order=idx,
                        segment_text=segment_text.strip()
                    )
                    db.add(db_segment)
                    self.logger.debug(f"Added segment {idx}: {segment_text[:50]}...")
            
            db.commit()
            db.refresh(db_story)
            
            self.logger.info(f"Successfully created story with {len(segments)} segments")
            return StoryResponse.model_validate(db_story.__dict__)
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating story: {e}")
            raise

    def get_story(self, db: Session, story_id: int) -> Optional[StoryResponse]:
        """이야기 조회"""
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            return None
        return StoryResponse.model_validate(story)

    def get_stories(self, db: Session, skip: int = 0, limit: int = 100) -> List[StoryResponse]:
        """이야기 목록 조회"""
        stories = db.query(Story).offset(skip).limit(limit).all()
        return [StoryResponse.model_validate(story) for story in stories]

    def update_story(self, db: Session, story_id: int, story_update: StoryUpdate) -> Optional[StoryResponse]:
        """이야기 수정"""
        try:
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                return None
            
            # 업데이트할 필드만 수정
            update_data = story_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(story, key, value)
            
            db.commit()
            db.refresh(story)
            return StoryResponse.model_validate(story)
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating story: {e}")
            raise

    def delete_story(self, db: Session, story_id: int) -> bool:
        """이야기 삭제"""
        try:
            story = db.query(Story).filter(Story.id == story_id).first()
            if not story:
                return False
            
            db.delete(story)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting story: {e}")
            raise

 