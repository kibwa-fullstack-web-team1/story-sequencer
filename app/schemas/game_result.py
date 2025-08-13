from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GameResultBase(BaseModel):
    game_type: str
    story_id: int
    is_correct: bool
    response_time: float
    score: Optional[int] = None

class GameResultCreate(GameResultBase):
    user_id: int

class GameResultResponse(GameResultBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserDifficultyBase(BaseModel):
    current_game_type: str
    success_rate: float
    consecutive_success: int
    consecutive_failure: int

class UserDifficultyResponse(UserDifficultyBase):
    user_id: int
    last_updated: datetime

    class Config:
        from_attributes = True 