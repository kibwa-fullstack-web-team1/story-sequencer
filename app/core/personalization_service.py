from sqlalchemy.orm import Session
from app.helper.game_helper import get_recent_game_results, get_user_difficulty
from app.core.difficulty_service import DifficultyService
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PersonalizationService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.difficulty_service = DifficultyService()

    def init_app(self, app):
        """앱 초기화"""
        self.logger.info("PersonalizationService initialized")
        return self

    def get_personalized_recommendation(self, db: Session, user_id: int) -> Dict[str, Any]:
        """사용자 개인화된 게임 추천"""
        try:
            # 사용자 난이도 정보 조회
            user_difficulty = get_user_difficulty(db, user_id)
            
            if not user_difficulty:
                # 신규 사용자
                return self._get_new_user_recommendation()
            
            # 기존 사용자 개인화 추천
            return self._get_existing_user_recommendation(db, user_id, user_difficulty)
            
        except Exception as e:
            self.logger.error(f"Error getting personalized recommendation: {e}")
            return self._get_fallback_recommendation()

    def _get_new_user_recommendation(self) -> Dict[str, Any]:
        """신규 사용자 추천"""
        return {
            "recommended_game_type": "SENTENCE_SEQUENCE",
            "difficulty_level": "BEGINNER",
            "message": "문장 순서 맞추기부터 시작해보세요!",
            "reason": "신규 사용자",
            "estimated_duration": "5-10분",
            "tips": [
                "천천히 문장을 읽어보세요",
                "순서를 기억해두세요",
                "틀려도 괜찮아요, 연습이 중요해요"
            ]
        }

    def _get_existing_user_recommendation(self, db: Session, user_id: int, user_difficulty) -> Dict[str, Any]:
        """기존 사용자 개인화 추천"""
        try:
            # 최근 게임 패턴 분석
            recent_patterns = self._analyze_recent_patterns(db, user_id)
            
            # 시간대별 성과 분석
            time_based_performance = self._analyze_time_based_performance(db, user_id)
            
            # 추천 게임 유형 결정
            recommended_game_type = self.difficulty_service.determine_next_game_type(
                db, user_id, user_difficulty.current_game_type
            )
            
            # 개인화된 메시지 생성
            message, tips = self._generate_personalized_message(
                user_difficulty, recent_patterns, time_based_performance
            )
            
            return {
                "recommended_game_type": recommended_game_type,
                "difficulty_level": self._get_difficulty_level(user_difficulty.success_rate),
                "message": message,
                "reason": self._get_recommendation_reason(user_difficulty, recent_patterns),
                "estimated_duration": self._estimate_duration(user_difficulty, recent_patterns),
                "tips": tips,
                "performance_insights": {
                    "success_rate": user_difficulty.success_rate,
                    "consecutive_success": user_difficulty.consecutive_success,
                    "consecutive_failure": user_difficulty.consecutive_failure,
                    "best_time_of_day": time_based_performance.get('best_time', '오전'),
                    "improvement_trend": recent_patterns.get('trend', 'stable')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting existing user recommendation: {e}")
            return self._get_fallback_recommendation()

    def _analyze_recent_patterns(self, db: Session, user_id: int) -> Dict[str, Any]:
        """최근 게임 패턴 분석"""
        try:
            # 최근 20게임 분석
            recent_results = get_recent_game_results(db, user_id, 'SENTENCE_SEQUENCE', 20)
            recent_results.extend(get_recent_game_results(db, user_id, 'WORD_SEQUENCE', 20))
            
            if not recent_results:
                return {"trend": "stable", "consistency": "unknown"}
            
            # 성과 트렌드 분석
            recent_10 = recent_results[:10]
            older_10 = recent_results[10:20] if len(recent_results) >= 20 else []
            
            recent_success_rate = sum(1 for r in recent_10 if r.is_correct) / len(recent_10)
            older_success_rate = sum(1 for r in older_10 if r.is_correct) / len(older_10) if older_10 else recent_success_rate
            
            # 트렌드 판단
            if recent_success_rate > older_success_rate + 0.1:
                trend = "improving"
            elif recent_success_rate < older_success_rate - 0.1:
                trend = "declining"
            else:
                trend = "stable"
            
            # 일관성 분석
            response_times = [r.response_time for r in recent_results]
            avg_time = sum(response_times) / len(response_times)
            time_variance = sum((t - avg_time) ** 2 for t in response_times) / len(response_times)
            
            if time_variance < 100:  # 응답 시간이 일정함
                consistency = "high"
            elif time_variance < 400:
                consistency = "medium"
            else:
                consistency = "low"
            
            return {
                "trend": trend,
                "consistency": consistency,
                "recent_success_rate": recent_success_rate,
                "avg_response_time": avg_time
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing recent patterns: {e}")
            return {"trend": "stable", "consistency": "unknown"}

    def _analyze_time_based_performance(self, db: Session, user_id: int) -> Dict[str, Any]:
        """시간대별 성과 분석"""
        try:
            recent_results = get_recent_game_results(db, user_id, 'SENTENCE_SEQUENCE', 50)
            recent_results.extend(get_recent_game_results(db, user_id, 'WORD_SEQUENCE', 50))
            
            if not recent_results:
                return {"best_time": "오전", "performance_by_time": {}}
            
            # 시간대별 성과 분석
            morning_results = []
            afternoon_results = []
            evening_results = []
            
            for result in recent_results:
                hour = result.created_at.hour
                if 6 <= hour < 12:
                    morning_results.append(result)
                elif 12 <= hour < 18:
                    afternoon_results.append(result)
                else:
                    evening_results.append(result)
            
            # 각 시간대별 성공률 계산
            performance_by_time = {}
            for time_period, results in [("오전", morning_results), ("오후", afternoon_results), ("저녁", evening_results)]:
                if results:
                    success_rate = sum(1 for r in results if r.is_correct) / len(results)
                    performance_by_time[time_period] = success_rate
            
            # 최고 성과 시간대 찾기
            best_time = max(performance_by_time.items(), key=lambda x: x[1])[0] if performance_by_time else "오전"
            
            return {
                "best_time": best_time,
                "performance_by_time": performance_by_time
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing time-based performance: {e}")
            return {"best_time": "오전", "performance_by_time": {}}

    def _generate_personalized_message(self, user_difficulty, recent_patterns, time_based_performance) -> tuple[str, List[str]]:
        """개인화된 메시지와 팁 생성"""
        message = ""
        tips = []
        
        # 성공률 기반 메시지
        if user_difficulty.success_rate >= 0.8:
            message = "훌륭한 성과를 보이고 계세요! 더 어려운 도전을 해보세요."
            tips.append("이제 단어 순서 맞추기에 도전해보세요")
        elif user_difficulty.success_rate >= 0.6:
            message = "잘 하고 계세요! 조금 더 연습하면 더 좋은 결과를 얻을 수 있어요."
            tips.append("천천히 꼼꼼히 확인해보세요")
        elif user_difficulty.success_rate >= 0.4:
            message = "꾸준히 연습하고 계시네요. 조금 더 천천히 해보세요."
            tips.append("틀린 부분을 다시 한번 확인해보세요")
        else:
            message = "천천히 다시 시작해보세요. 연습이 중요해요."
            tips.append("문장을 다시 한번 읽어보세요")
        
        # 연속 성공/실패 기반 팁
        if user_difficulty.consecutive_success >= 3:
            tips.append("연속으로 잘하고 계세요! 계속 이어가세요")
        elif user_difficulty.consecutive_failure >= 2:
            tips.append("잠시 쉬었다가 다시 시도해보세요")
        
        # 시간대별 팁
        best_time = time_based_performance.get('best_time', '오전')
        tips.append(f"{best_time}에 게임하시면 더 좋은 결과를 얻을 수 있어요")
        
        # 트렌드 기반 팁
        trend = recent_patterns.get('trend', 'stable')
        if trend == 'improving':
            tips.append("점점 더 잘하고 계세요! 계속 이어가세요")
        elif trend == 'declining':
            tips.append("조금 쉬었다가 다시 시작해보세요")
        
        return message, tips

    def _get_difficulty_level(self, success_rate: float) -> str:
        """성공률 기반 난이도 레벨"""
        if success_rate >= 0.8:
            return "ADVANCED"
        elif success_rate >= 0.6:
            return "INTERMEDIATE"
        elif success_rate >= 0.4:
            return "BEGINNER"
        else:
            return "NOVICE"

    def _get_recommendation_reason(self, user_difficulty, recent_patterns) -> str:
        """추천 이유"""
        if user_difficulty.consecutive_success >= 5:
            return "연속 성공으로 난이도 상승"
        elif user_difficulty.consecutive_failure >= 3:
            return "연속 실패로 난이도 조정"
        elif recent_patterns.get('trend') == 'improving':
            return "성과 향상으로 난이도 상승"
        else:
            return "현재 난이도 유지"

    def _estimate_duration(self, user_difficulty, recent_patterns) -> str:
        """예상 소요 시간"""
        avg_time = recent_patterns.get('avg_response_time', 30)
        
        if avg_time < 20:
            return "3-5분"
        elif avg_time < 40:
            return "5-8분"
        else:
            return "8-12분"

    def _get_fallback_recommendation(self) -> Dict[str, Any]:
        """기본 추천"""
        return {
            "recommended_game_type": "SENTENCE_SEQUENCE",
            "difficulty_level": "BEGINNER",
            "message": "문장 순서 맞추기부터 시작해보세요!",
            "reason": "기본 추천",
            "estimated_duration": "5-10분",
            "tips": [
                "천천히 문장을 읽어보세요",
                "순서를 기억해두세요"
            ]
        } 