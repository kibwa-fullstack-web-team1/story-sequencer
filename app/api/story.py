from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.common.response import create_response, NotFoundError, BadRequest
from app.helper.story_helper import (
    create_story_helper, get_stories_helper, get_story_helper,
    update_story_helper, delete_story_helper
)
from app.schemas.story import StoryCreate, StoryUpdate, StoryResponse
from app.database import get_db
from app.utils.security import get_current_user_validated
from app.models.story import Story, StorySegment
from app.core.story_service import StoryService
import random

router = APIRouter()
story_service = StoryService()

@router.get("/", description="이야기 목록 조회")
async def get_stories(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """로그인 사용자의 이야기 목록 조회 (시니어는 보호자의 이야기도 포함)"""
    # 사용자 정보 가져오기
    user_response = await get_user_info_from_user_service(user_id)
    user_role = user_response.get('role')
    
    if user_role == 'senior':
        # 시니어인 경우: 자신의 이야기 + 보호자의 이야기
        stories = await get_stories_for_senior(db, user_id)
    else:
        # 보호자인 경우: 자신이 등록한 이야기만
        stories = db.query(Story).filter(Story.user_id == user_id).offset(skip).limit(limit).all()
    
    return create_response([StoryResponse.model_validate(story.__dict__) for story in stories])

async def get_user_info_from_user_service(user_id: int):
    """User Service에서 사용자 정보 가져오기"""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        return {"role": "senior"}  # 기본값

async def get_stories_for_senior(db: Session, senior_id: int):
    """시니어를 위한 이야기 목록 (자신의 이야기 + 보호자의 이야기)"""
    import httpx
    
    # 1. 시니어의 보호자 목록 가져오기
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/users/family-relationships/guardians")
        if response.status_code == 200:
            guardians_data = response.json()
            guardian_ids = [guardian['id'] for guardian in guardians_data.get('guardians', [])]
        else:
            guardian_ids = []
    
    # 2. 자신의 이야기 + 보호자들의 이야기 가져오기
    all_user_ids = [senior_id] + guardian_ids
    stories = db.query(Story).filter(Story.user_id.in_(all_user_ids)).all()
    
    return stories

@router.post("/", status_code=status.HTTP_201_CREATED, description="이야기 생성")
async def create_story(
    request: Request,
    story: StoryCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """로그인 사용자의 이야기 생성 (문장 분할 포함)"""
    try:
        # StoryService를 사용하여 이야기 생성 (문장 분할 포함)
        result = story_service.create_story(db, story, request.app, user_id)
        return create_response(result)
    except Exception as e:
        raise BadRequest(f"이야기 생성에 실패했습니다: {str(e)}")

@router.get("/{story_id}", description="이야기 상세 조회")
async def get_story(
    request: Request,
    story_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    story = db.query(Story).filter(Story.id == story_id, Story.user_id == user_id).first()
    if not story:
        raise NotFoundError("이야기를 찾을 수 없습니다.")
    return create_response(StoryResponse.model_validate(story.__dict__))

@router.get("/{story_id}/segments", description="이야기의 세그먼트 목록 조회")
async def get_story_segments(
    request: Request,
    story_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """특정 이야기의 세그먼트 목록 조회"""
    # 사용자의 이야기인지 확인
    story = db.query(Story).filter(Story.id == story_id, Story.user_id == user_id).first()
    if not story:
        raise NotFoundError("이야기를 찾을 수 없습니다.")
    
    segments = db.query(StorySegment).filter(StorySegment.story_id == story_id).order_by(StorySegment.order).all()
    return create_response([{
        "id": segment.id,
        "order": segment.order,
        "segment_text": segment.segment_text
    } for segment in segments])

@router.get("/segments/random", description="랜덤 세그먼트 조회")
async def get_random_segment(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 모든 이야기에서 랜덤으로 하나의 세그먼트 조회 (시니어는 보호자의 이야기도 포함)"""
    # 사용자 정보 가져오기
    user_response = await get_user_info_from_user_service(user_id)
    user_role = user_response.get('role')
    
    if user_role == 'senior':
        # 시니어인 경우: 자신의 이야기 + 보호자의 이야기
        stories = await get_stories_for_senior(db, user_id)
    else:
        # 보호자인 경우: 자신이 등록한 이야기만
        stories = db.query(Story).filter(Story.user_id == user_id).all()
    
    if not stories:
        raise NotFoundError("사용자의 이야기가 없습니다.")
    
    story_ids = [story.id for story in stories]
    
    # 모든 세그먼트 가져오기
    all_segments = db.query(StorySegment).filter(StorySegment.story_id.in_(story_ids)).all()
    if not all_segments:
        raise NotFoundError("사용할 수 있는 세그먼트가 없습니다.")
    
    # 랜덤으로 하나 선택
    random_segment = random.choice(all_segments)
    
    return create_response({
        "id": random_segment.id,
        "story_id": random_segment.story_id,
        "order": random_segment.order,
        "segment_text": random_segment.segment_text
    })

@router.put("/{story_id}", description="이야기 수정")
async def update_story(
    request: Request,
    story_id: int, 
    story_update: StoryUpdate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    db_story = db.query(Story).filter(Story.id == story_id, Story.user_id == user_id).first()
    if not db_story:
        raise NotFoundError("이야기를 찾을 수 없습니다.")
    update_data = story_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_story, key, value)
    db.commit()
    db.refresh(db_story)
    return create_response(StoryResponse.model_validate(db_story.__dict__))

@router.delete("/{story_id}", description="이야기 삭제")
async def delete_story(
    request: Request,
    story_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    db_story = db.query(Story).filter(Story.id == story_id, Story.user_id == user_id).first()
    if not db_story:
        raise NotFoundError("이야기를 찾을 수 없습니다.")
    db.delete(db_story)
    db.commit()
    return create_response({"msg": "삭제되었습니다."}) 