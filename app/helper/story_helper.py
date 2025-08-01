from app.schemas.story import StoryCreate, StoryUpdate
from app.utils.functions import validate_story_content, validate_story_title
from app.common.response import ValidationError
from fastapi import Request
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.story import Story # Story 모델 임포트

logger = logging.getLogger(__name__)

def create_story_helper(request: Request, data):
    """이야기 생성 헬퍼"""
    try:
        # 데이터 검증
        if not data.get('title') or not data.get('content'):
            raise ValidationError("제목과 내용은 필수입니다.")
        
        if not validate_story_title(data['title']):
            raise ValidationError("제목은 2자 이상 255자 이하여야 합니다.")
        
        if not validate_story_content(data['content']):
            raise ValidationError("내용은 10자 이상이어야 합니다.")
        
        # 스키마 생성
        story_create = StoryCreate(
            title=data['title'],
            content=data['content'],
            image_url=data.get('image_url')
        )
        
        # 서비스 호출
        return request.app.state.story_service.create_story(request.app.state.db, story_create, request.app)
        
    except Exception as e:
        logger.error(f"Error in create_story_helper: {e}")
        raise

def get_stories_helper(request: Request, args):
    """이야기 목록 조회 헬퍼"""
    try:
        skip = args.get('skip', 0)
        limit = args.get('limit', 100)
        
        return request.app.state.story_service.get_stories(request.app.state.db, skip=skip, limit=limit)
        
    except Exception as e:
        logger.error(f"Error in get_stories_helper: {e}")
        raise

def get_story_helper(request: Request, story_id):
    """이야기 상세 조회 헬퍼"""
    try:
        return request.app.state.story_service.get_story(request.app.state.db, story_id)
        
    except Exception as e:
        logger.error(f"Error in get_story_helper: {e}")
        raise

def update_story_helper(request: Request, story_id, data):
    """이야기 수정 헬퍼"""
    try:
        # 데이터 검증
        if 'title' in data and not validate_story_title(data['title']):
            raise ValidationError("제목은 2자 이상 255자 이하여야 합니다.")
        
        if 'content' in data and not validate_story_content(data['content']):
            raise ValidationError("내용은 10자 이상이어야 합니다.")
        
        # 스키마 생성
        story_update = StoryUpdate(
            title=data.get('title'),
            content=data.get('content'),
            image_url=data.get('image_url')
        )
        
        # 서비스 호출
        return request.app.state.story_service.update_story(request.app.state.db, story_id, story_update)
        
    except Exception as e:
        logger.error(f"Error in update_story_helper: {e}")
        raise

def delete_story_helper(request: Request, story_id):
    """이야기 삭제 헬퍼"""
    try:
        return request.app.state.story_service.delete_story(request.app.state.db, story_id)
        
    except Exception as e:
        logger.error(f"Error in delete_story_helper: {e}")
        raise

def get_internal_stories_helper(db: Session, skip: int = 0, limit: int = 100, updated_after: str = None):
    """내부 서비스용 이야기 목록 조회 헬퍼 (updated_after 필터링 포함)"""
    try:
        query = db.query(Story)
        if updated_after:
            updated_after_dt = datetime.fromisoformat(updated_after)
            query = query.filter(Story.updated_at >= updated_after_dt)
        
        return query.offset(skip).limit(limit).all()
        
    except Exception as e:
        logger.error(f"Error in get_internal_stories_helper: {e}")
        raise