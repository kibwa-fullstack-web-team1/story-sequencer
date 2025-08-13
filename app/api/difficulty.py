from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.difficulty_service import DifficultyService
from app.utils.security import get_current_user_validated
from app.common.response import create_response
import logging

router = APIRouter()
difficulty_service = DifficultyService()
logger = logging.getLogger(__name__)

@router.post("/submit-result-with-difficulty", description="게임 결과 제출 및 난이도 조절")
async def submit_game_result_with_difficulty(
    request: Request,
    game_result: dict,  # GameResultCreate 스키마 대신 dict 사용
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """게임 결과를 제출하고 난이도를 자동으로 조절합니다."""
    try:
        # 사용자 ID 검증
        if game_result.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="자신의 게임 결과만 제출할 수 있습니다.")
        
        # 게임 결과 저장
        from app.helper.game_helper import save_game_result
        from app.schemas.game_result import GameResultCreate
        
        result_create = GameResultCreate(
            user_id=game_result['user_id'],
            game_type=game_result['game_type'],
            story_id=game_result['story_id'],
            is_correct=game_result['is_correct'],
            response_time=game_result['response_time'],
            score=None  # 점수는 사용하지 않음
        )
        
        saved_result = save_game_result(db, result_create)
        
        # 난이도 조절
        difficulty_info = difficulty_service.update_user_difficulty(
            db, user_id, game_result['game_type']
        )
        
        # 사용자에게 메시지 생성
        message = difficulty_service.get_difficulty_message(
            game_result['game_type'], 
            difficulty_info['recommended_game_type']
        )
        
        logger.info(f"Game result submitted with difficulty adjustment: user_id={user_id}, "
                   f"game_type={game_result['game_type']}, correct={game_result['is_correct']}")
        
        return create_response({
            "message": "게임 결과가 성공적으로 저장되었습니다.",
            "result_id": saved_result.id,
            "difficulty_info": difficulty_info,
            "user_message": message
        })
        
    except Exception as e:
        logger.error(f"Error submitting game result with difficulty: {e}")
        raise HTTPException(status_code=500, detail=f"게임 결과 저장에 실패했습니다: {str(e)}")

@router.get("/recommendation", description="사용자에게 추천할 게임 유형 조회")
async def get_game_recommendation(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 성과를 바탕으로 추천할 게임 유형을 조회합니다."""
    try:
        # 사용자의 현재 난이도 정보 조회
        from app.helper.game_helper import get_user_difficulty
        
        user_difficulty = get_user_difficulty(db, user_id)
        
        if not user_difficulty:
            # 처음 플레이하는 사용자는 문장 순서 맞추기부터 시작
            recommended_game_type = 'SENTENCE_SEQUENCE'
            message = "문장 순서 맞추기부터 시작해보세요!"
        else:
            # 기존 사용자는 성과를 바탕으로 추천
            recommended_game_type = difficulty_service.determine_next_game_type(
                db, user_id, user_difficulty.current_game_type
            )
            message = difficulty_service.get_difficulty_message(
                user_difficulty.current_game_type, recommended_game_type
            )
        
        return create_response({
            "recommended_game_type": recommended_game_type,
            "current_difficulty": user_difficulty.current_game_type if user_difficulty else 'SENTENCE_SEQUENCE',
            "success_rate": user_difficulty.success_rate if user_difficulty else 0.0,
            "message": message
        })
        
    except Exception as e:
        logger.error(f"Error getting game recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"게임 추천 조회에 실패했습니다: {str(e)}")

@router.get("/stats", description="사용자의 게임 통계 조회")
async def get_user_game_stats(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 게임 통계를 조회합니다."""
    try:
        from app.helper.game_helper import get_user_difficulty, get_recent_game_results
        
        user_difficulty = get_user_difficulty(db, user_id)
        
        if not user_difficulty:
            return create_response({
                "message": "아직 게임 기록이 없습니다.",
                "stats": {
                    "total_games": 0,
                    "success_rate": 0.0,
                    "current_game_type": "SENTENCE_SEQUENCE"
                }
            })
        
        # 각 게임 유형별 통계
        sentence_results = get_recent_game_results(db, user_id, 'SENTENCE_SEQUENCE', 50)
        word_results = get_recent_game_results(db, user_id, 'WORD_SEQUENCE', 50)
        
        sentence_success_rate = difficulty_service.calculate_success_rate(db, user_id, 'SENTENCE_SEQUENCE')
        word_success_rate = difficulty_service.calculate_success_rate(db, user_id, 'WORD_SEQUENCE')
        
        return create_response({
            "stats": {
                "current_game_type": user_difficulty.current_game_type,
                "success_rate": user_difficulty.success_rate,
                "consecutive_success": user_difficulty.consecutive_success,
                "consecutive_failure": user_difficulty.consecutive_failure,
                "sentence_sequence": {
                    "total_games": len(sentence_results),
                    "success_rate": sentence_success_rate
                },
                "word_sequence": {
                    "total_games": len(word_results),
                    "success_rate": word_success_rate
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user game stats: {e}")
        raise HTTPException(status_code=500, detail=f"게임 통계 조회에 실패했습니다: {str(e)}") 

@router.put("/settings", description="난이도 조절 설정 변경")
async def update_difficulty_settings(
    request: Request,
    settings: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자별 난이도 조절 설정을 변경합니다."""
    try:
        # 관리자 권한 확인 (예시)
        # if not is_admin(user_id):
        #     raise HTTPException(status_code=403, detail="관리자만 설정을 변경할 수 있습니다.")
        
        # 설정 유효성 검사
        valid_settings = {
            'consecutive_success_for_increase': int,
            'consecutive_failure_for_decrease': int,
            'easy_to_medium_threshold': float,
            'hard_to_easy_threshold': float,
            'min_games_for_analysis': int
        }
        
        for key, value_type in valid_settings.items():
            if key in settings:
                try:
                    settings[key] = value_type(settings[key])
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"잘못된 설정값: {key}")
        
        # 설정 저장 (예: Redis, DB, 환경변수 등)
        # 여기서는 간단히 로그만 남김
        logger.info(f"Difficulty settings updated by user {user_id}: {settings}")
        
        return create_response({
            "message": "난이도 조절 설정이 업데이트되었습니다.",
            "settings": settings
        })
        
    except Exception as e:
        logger.error(f"Error updating difficulty settings: {e}")
        raise HTTPException(status_code=500, detail=f"설정 변경에 실패했습니다: {str(e)}")

@router.get("/settings", description="현재 난이도 조절 설정 조회")
async def get_difficulty_settings(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """현재 난이도 조절 설정을 조회합니다."""
    try:
        from app.config.difficulty_config import get_difficulty_thresholds
        
        current_settings = get_difficulty_thresholds()
        
        return create_response({
            "settings": current_settings,
            "description": {
                "CONSECUTIVE_SUCCESS_FOR_INCREASE": "연속 성공 시 난이도 상승 횟수",
                "CONSECUTIVE_FAILURE_FOR_DECREASE": "연속 실패 시 난이도 하락 횟수",
                "EASY_TO_MEDIUM_THRESHOLD": "쉬운 난이도에서 중간 난이도로 상승하는 성공률",
                "HARD_TO_EASY_THRESHOLD": "어려운 난이도에서 쉬운 난이도로 하락하는 성공률",
                "MIN_GAMES_FOR_ANALYSIS": "난이도 분석을 위한 최소 게임 수"
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting difficulty settings: {e}")
        raise HTTPException(status_code=500, detail=f"설정 조회에 실패했습니다: {str(e)}") 