from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.story import Story, StorySegment
import random

router = APIRouter()

@router.get("/activity/story-sequence/{story_id}")
def get_story_sequence(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    segments = db.query(StorySegment).filter(StorySegment.story_id == story_id).order_by(StorySegment.order).all()
    segment_texts = [s.segment_text for s in segments]
    shuffled = segment_texts.copy()
    random.shuffle(shuffled)
    return {
        "id": story.id,
        "title": story.title,
        "description": story.content,
        "image_url": story.image_url,
        "segments": segment_texts,
        "shuffled": shuffled
    }

@router.get("/activity/word-sequence/{story_id}")
def get_word_sequence(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    segments = db.query(StorySegment).filter(StorySegment.story_id == story_id).order_by(StorySegment.order).all()
    if not segments:
        raise HTTPException(status_code=404, detail="No segments found for this story")
    # 랜덤 문장 선택
    segment = random.choice(segments).segment_text
    # 띄어쓰기 기준 어절 분리 (더 똑똑한 분리는 추후 개선)
    words = segment.strip().split()
    shuffled = words.copy()
    random.shuffle(shuffled)
    return {
        "story_id": story.id,
        "segment": segment,
        "words": words,
        "shuffled": shuffled
    } 