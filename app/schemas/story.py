from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StoryBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class StoryCreate(StoryBase):
    pass  # user_id는 API에서 자동 할당

class StoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None

class StorySegmentBase(BaseModel):
    order: int
    segment_text: str

class StorySegmentCreate(StorySegmentBase):
    pass

class StorySegmentResponse(StorySegmentBase):
    id: int
    story_id: int

    class Config:
        from_attributes = True

class StoryResponse(StoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    segments: Optional[List] = None

    class Config:
        orm_mode = True 