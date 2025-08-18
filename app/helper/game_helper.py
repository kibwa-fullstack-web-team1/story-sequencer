from sqlalchemy.orm import Session
from app.models.game_result import GameResult, UserDifficulty
from app.schemas.game_result import GameResultCreate, UserDifficultyResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def save_game_result(db: Session, game_result: GameResultCreate) -> GameResult:
    """게임 결과 저장"""
    try:
        db_result = GameResult(
            user_id=game_result.user_id,
            game_type=game_result.game_type,
            story_id=game_result.story_id,
            is_correct=game_result.is_correct,
            response_time=game_result.response_time,
            score=game_result.score
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        logger.info(f"Game result saved for user {game_result.user_id}, type: {game_result.game_type}")
        return db_result
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving game result: {e}")
        raise

def get_recent_game_results(db: Session, user_id: int, game_type: str, limit: int = 10) -> List[GameResult]:
    """최근 게임 결과 조회"""
    try:
        results = db.query(GameResult).filter(
            GameResult.user_id == user_id,
            GameResult.game_type == game_type
        ).order_by(GameResult.created_at.desc()).limit(limit).all()
        
        return results
    except Exception as e:
        logger.error(f"Error getting recent game results: {e}")
        return []

def get_user_difficulty(db: Session, user_id: int) -> Optional[UserDifficulty]:
    """사용자 난이도 정보 조회"""
    try:
        difficulty = db.query(UserDifficulty).filter(UserDifficulty.user_id == user_id).first()
        return difficulty
    except Exception as e:
        logger.error(f"Error getting user difficulty: {e}")
        return None

def create_or_update_user_difficulty(db: Session, user_id: int, game_type: str, 
                                   success_rate: float, consecutive_success: int, 
                                   consecutive_failure: int) -> UserDifficulty:
    """사용자 난이도 정보 생성 또는 업데이트"""
    try:
        difficulty = db.query(UserDifficulty).filter(UserDifficulty.user_id == user_id).first()
        
        if difficulty:
            # 기존 정보 업데이트
            difficulty.current_game_type = game_type
            difficulty.success_rate = success_rate
            difficulty.consecutive_success = consecutive_success
            difficulty.consecutive_failure = consecutive_failure
        else:
            # 새로 생성
            difficulty = UserDifficulty(
                user_id=user_id,
                current_game_type=game_type,
                success_rate=success_rate,
                consecutive_success=consecutive_success,
                consecutive_failure=consecutive_failure
            )
            db.add(difficulty)
        
        db.commit()
        db.refresh(difficulty)
        
        logger.info(f"User difficulty updated for user {user_id}: {game_type}")
        return difficulty
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user difficulty: {e}")
        raise 