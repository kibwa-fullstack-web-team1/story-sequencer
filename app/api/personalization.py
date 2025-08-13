from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.personalization_service import PersonalizationService
from app.utils.security import get_current_user_validated
from app.common.response import create_response
import logging

router = APIRouter()
personalization_service = PersonalizationService()
logger = logging.getLogger(__name__)

@router.get("/personalized-recommendation", description="개인화된 게임 추천")
async def get_personalized_recommendation(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 성과를 바탕으로 개인화된 게임 추천을 제공합니다."""
    try:
        recommendation = personalization_service.get_personalized_recommendation(db, user_id)
        
        logger.info(f"Personalized recommendation generated for user {user_id}: {recommendation['recommended_game_type']}")
        
        return create_response(recommendation)
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"개인화된 추천 조회에 실패했습니다: {str(e)}")

@router.get("/learning-progress", description="학습 진행도 조회")
async def get_learning_progress(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 학습 진행도를 조회합니다."""
    try:
        from app.helper.game_helper import get_user_difficulty, get_recent_game_results
        
        user_difficulty = get_user_difficulty(db, user_id)
        
        if not user_difficulty:
            return create_response({
                "message": "아직 학습 기록이 없습니다.",
                "progress": {
                    "level": "BEGINNER",
                    "total_games": 0,
                    "current_streak": 0,
                    "best_streak": 0,
                    "improvement_rate": 0.0
                }
            })
        
        # 최근 게임 결과 분석
        recent_results = get_recent_game_results(db, user_id, 'SENTENCE_SEQUENCE', 50)
        recent_results.extend(get_recent_game_results(db, user_id, 'WORD_SEQUENCE', 50))
        
        # 현재 연속 성공 횟수
        current_streak = user_difficulty.consecutive_success
        
        # 최고 연속 성공 횟수 계산
        best_streak = 0
        temp_streak = 0
        for result in recent_results:
            if result.is_correct:
                temp_streak += 1
                best_streak = max(best_streak, temp_streak)
            else:
                temp_streak = 0
        
        # 개선률 계산 (최근 10게임 vs 이전 10게임)
        if len(recent_results) >= 20:
            recent_10 = recent_results[:10]
            older_10 = recent_results[10:20]
            
            recent_success_rate = sum(1 for r in recent_10 if r.is_correct) / len(recent_10)
            older_success_rate = sum(1 for r in older_10 if r.is_correct) / len(older_10)
            
            improvement_rate = recent_success_rate - older_success_rate
        else:
            improvement_rate = 0.0
        
        # 레벨 결정
        level = personalization_service._get_difficulty_level(user_difficulty.success_rate)
        
        return create_response({
            "progress": {
                "level": level,
                "total_games": len(recent_results),
                "current_streak": current_streak,
                "best_streak": best_streak,
                "improvement_rate": improvement_rate,
                "success_rate": user_difficulty.success_rate,
                "current_game_type": user_difficulty.current_game_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting learning progress: {e}")
        raise HTTPException(status_code=500, detail=f"학습 진행도 조회에 실패했습니다: {str(e)}")

@router.get("/performance-insights", description="성과 인사이트 조회")
async def get_performance_insights(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_validated)
):
    """사용자의 성과 인사이트를 제공합니다."""
    try:
        from app.helper.game_helper import get_recent_game_results
        
        # 최근 게임 결과 분석
        sentence_results = get_recent_game_results(db, user_id, 'SENTENCE_SEQUENCE', 30)
        word_results = get_recent_game_results(db, user_id, 'WORD_SEQUENCE', 30)
        
        # 문장 순서 맞추기 분석
        sentence_insights = {
            "total_games": len(sentence_results),
            "success_rate": sum(1 for r in sentence_results if r.is_correct) / len(sentence_results) if sentence_results else 0.0,
            "avg_response_time": sum(r.response_time for r in sentence_results) / len(sentence_results) if sentence_results else 0.0,
            "best_time": "오전"  # 기본값
        }
        
        # 단어 순서 맞추기 분석
        word_insights = {
            "total_games": len(word_results),
            "success_rate": sum(1 for r in word_results if r.is_correct) / len(word_results) if word_results else 0.0,
            "avg_response_time": sum(r.response_time for r in word_results) / len(word_results) if word_results else 0.0,
            "best_time": "오전"  # 기본값
        }
        
        # 시간대별 성과 분석
        all_results = sentence_results + word_results
        time_analysis = personalization_service._analyze_time_based_performance(db, user_id)
        
        # 패턴 분석
        pattern_analysis = personalization_service._analyze_recent_patterns(db, user_id)
        
        return create_response({
            "insights": {
                "sentence_sequence": sentence_insights,
                "word_sequence": word_insights,
                "time_analysis": time_analysis,
                "pattern_analysis": pattern_analysis,
                "recommendations": [
                    "꾸준한 연습이 중요해요",
                    "틀린 부분을 다시 한번 확인해보세요",
                    "천천히 꼼꼼히 해보세요"
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting performance insights: {e}")
        raise HTTPException(status_code=500, detail=f"성과 인사이트 조회에 실패했습니다: {str(e)}") 