from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.common.response import create_response
from app.helper.story_helper import get_internal_stories_helper # 새로운 헬퍼 함수 임포트
from app.schemas.story import StoryResponse
from app.database import get_db
from app.models.story import Story # Story 모델 임포트
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/internal",
    tags=["Internal Synchronization"]
)

@router.get("/stories", description="내부 서비스용 이야기 목록 조회 (인증 없음)")
async def get_internal_stories(
    request: Request,
    updated_after: Optional[str] = None, # dify-data-sync-service에서 사용할 파라미터
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """인증 없이 내부 서비스가 이야기 목록을 조회합니다."""
    logger.info(f"Internal story fetch triggered. updated_after: {updated_after}")
    
    stories = get_internal_stories_helper(db, skip=skip, limit=limit, updated_after=updated_after)
    
    return create_response([StoryResponse.model_validate(story.__dict__) for story in stories])

@router.get("/story-ids", description="내부 서비스용 모든 이야기 ID 목록 조회 (인증 없음)")
async def get_all_story_ids(
    db: Session = Depends(get_db)
):
    """인증 없이 내부 서비스가 모든 이야기의 ID 목록을 조회합니다."""
    logger.info("Internal story ID fetch triggered.")
    
    story_ids = db.query(Story.id).all()
    return create_response([story_id[0] for story_id in story_ids])
