from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.helper.game_helper import save_game_result
from app.schemas.game_result import GameResultCreate, GameResultResponse
from app.utils.security import get_current_user_validated
from app.common.response import create_response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/submit-result", description="게임 결과 제출")
async def submit_game_result(
    request: Request,
    game_result: GameResultCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """게임 결과를 제출하고 저장합니다."""
    try:
        # 사용자 ID 검증
        if game_result.user_id != user_id:
            raise HTTPException(status_code=403, detail="자신의 게임 결과만 제출할 수 있습니다.")
        
        # 게임 결과 저장
        saved_result = save_game_result(db, game_result)
        
        logger.info(f"Game result submitted: user_id={user_id}, game_type={game_result.game_type}, correct={game_result.is_correct}")
        
        return create_response({
            "message": "게임 결과가 성공적으로 저장되었습니다.",
            "result_id": saved_result.id
        })
        
    except Exception as e:
        logger.error(f"Error submitting game result: {e}")
        raise HTTPException(status_code=500, detail=f"게임 결과 저장에 실패했습니다: {str(e)}")

@router.get("/results/{game_type}", description="사용자의 게임 결과 조회")
async def get_user_game_results(
    request: Request,
    game_type: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 특정 게임 유형 결과를 조회합니다."""
    try:
        from app.helper.game_helper import get_recent_game_results
        
        results = get_recent_game_results(db, user_id, game_type, limit)
        
        return create_response({
            "game_type": game_type,
            "total_results": len(results),
            "results": [
                {
                    "id": result.id,
                    "story_id": result.story_id,
                    "is_correct": result.is_correct,
                    "response_time": result.response_time,
                    "score": result.score,
                    "created_at": result.created_at
                }
                for result in results
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting user game results: {e}")
        raise HTTPException(status_code=500, detail=f"게임 결과 조회에 실패했습니다: {str(e)}") 