from sqlalchemy.orm import Session
from app.helper.game_helper import get_recent_game_results, get_user_difficulty, create_or_update_user_difficulty
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 난이도 조절 기준
DIFFICULTY_THRESHOLDS = {
    'EASY_TO_MEDIUM': 0.7,    # 70% 성공률 달성 시 중간 난이도로 상승
    'MEDIUM_TO_HARD': 0.8,    # 80% 성공률 달성 시 어려운 난이도로 상승
    'HARD_TO_EASY': 0.3,      # 30% 이하 성공률 시 쉬운 난이도로 하락
    'MIN_GAMES_FOR_ANALYSIS': 5,  # 분석을 위한 최소 게임 수
    'CONSECUTIVE_SUCCESS_FOR_INCREASE': 5,  # 연속 5번 성공 시 난이도 상승
    'CONSECUTIVE_FAILURE_FOR_DECREASE': 3   # 연속 3번 실패 시 난이도 하락
}

# 게임 유형 정의
GAME_TYPES = {
    'SENTENCE_SEQUENCE': {
        'level': 'EASY',
        'description': '문장 순서 맞추기',
        'next_level': 'WORD_SEQUENCE'
    },
    'WORD_SEQUENCE': {
        'level': 'MEDIUM', 
        'description': '단어 순서 맞추기',
        'next_level': 'SENTENCE_SEQUENCE'  # 현재는 단어 -> 문장으로 되돌아감
    }
}

class DifficultyService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def init_app(self, app):
        """앱 초기화"""
        self.logger.info("DifficultyService initialized")
        return self

    def calculate_success_rate(self, db: Session, user_id: int, game_type: str, recent_games: int = 10) -> float:
        """최근 N게임의 성공률 계산"""
        try:
            recent_results = get_recent_game_results(db, user_id, game_type, recent_games)
            
            if not recent_results:
                return 0.0
            
            success_count = sum(1 for result in recent_results if result.is_correct)
            success_rate = success_count / len(recent_results)
            
            self.logger.info(f"Success rate for user {user_id}, game_type {game_type}: {success_rate:.2f}")
            return success_rate
            
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {e}")
            return 0.0

    def calculate_difficulty_score(self, db: Session, user_id: int, game_type: str) -> float:
        """응답 시간과 정확도를 종합한 난이도 점수 계산"""
        try:
            recent_results = get_recent_game_results(db, user_id, game_type, 10)
            
            if not recent_results:
                return 0.0
            
            # 평균 응답 시간 (초)
            avg_response_time = sum(result.response_time for result in recent_results) / len(recent_results)
            
            # 성공률
            success_rate = self.calculate_success_rate(db, user_id, game_type)
            
            # 난이도 점수 계산 (응답 시간이 빠르고 성공률이 높을수록 높은 점수)
            # 응답 시간은 60초를 최대값으로 정규화
            time_score = max(0, 1 - (avg_response_time / 60))
            difficulty_score = (success_rate * 0.7) + (time_score * 0.3)
            
            self.logger.info(f"Difficulty score for user {user_id}, game_type {game_type}: "
                           f"success_rate={success_rate:.2f}, avg_time={avg_response_time:.2f}s, "
                           f"score={difficulty_score:.2f}")
            
            return difficulty_score
            
        except Exception as e:
            self.logger.error(f"Error calculating difficulty score: {e}")
            return 0.0

    def determine_next_game_type(self, db: Session, user_id: int, current_game_type: str) -> str:
        """사용자의 성과를 바탕으로 다음 게임 유형 결정"""
        try:
            # 최소 게임 수 확인
            recent_results = get_recent_game_results(db, user_id, current_game_type, DIFFICULTY_THRESHOLDS['MIN_GAMES_FOR_ANALYSIS'])
            if len(recent_results) < DIFFICULTY_THRESHOLDS['MIN_GAMES_FOR_ANALYSIS']:
                self.logger.info(f"Not enough games for analysis: {len(recent_results)}")
                return current_game_type
            
            # 성공률과 난이도 점수 계산
            success_rate = self.calculate_success_rate(db, user_id, current_game_type)
            difficulty_score = self.calculate_difficulty_score(db, user_id, current_game_type)
            
            # 개선된 난이도 판단 로직
            should_increase = self._should_increase_difficulty(db, user_id, current_game_type, recent_results)
            should_decrease = self._should_decrease_difficulty(db, user_id, current_game_type, recent_results)
            
            # 상세 로그 추가
            self.logger.info(f"Difficulty analysis for user {user_id}: "
                           f"current_type={current_game_type}, "
                           f"success_rate={success_rate:.2f}, "
                           f"difficulty_score={difficulty_score:.2f}, "
                           f"should_increase={should_increase}, "
                           f"should_decrease={should_decrease}")
            
            # 난이도 상승 조건
            if current_game_type == 'SENTENCE_SEQUENCE' and should_increase:
                self.logger.info(f"User {user_id} ready for difficulty increase: SENTENCE_SEQUENCE -> WORD_SEQUENCE")
                return 'WORD_SEQUENCE'
            
            # 난이도 하락 조건
            elif current_game_type == 'WORD_SEQUENCE' and should_decrease:
                self.logger.info(f"User {user_id} needs difficulty decrease: WORD_SEQUENCE -> SENTENCE_SEQUENCE")
                return 'SENTENCE_SEQUENCE'
            
            # 현재 난이도 유지
            self.logger.info(f"User {user_id} maintaining current difficulty: {current_game_type}")
            return current_game_type
            
        except Exception as e:
            self.logger.error(f"Error determining next game type: {e}")
            return current_game_type

    def _should_increase_difficulty(self, db: Session, user_id: int, game_type: str, recent_results: list) -> bool:
        """난이도 상승 여부 판단 (개선된 로직)"""
        if not recent_results:
            return False
        
        # 1. 전체 성공률 조건
        success_rate = self.calculate_success_rate(db, user_id, game_type)
        if success_rate < DIFFICULTY_THRESHOLDS['EASY_TO_MEDIUM']:
            self.logger.info(f"User {user_id} failed success rate check: {success_rate:.2f} < {DIFFICULTY_THRESHOLDS['EASY_TO_MEDIUM']}")
            return False
        
        # 2. 난이도 점수 조건
        difficulty_score = self.calculate_difficulty_score(db, user_id, game_type)
        if difficulty_score < 0.6:
            self.logger.info(f"User {user_id} failed difficulty score check: {difficulty_score:.2f} < 0.6")
            return False
        
        # 3. 최근 성과 조건 (연속성 대신 최근 성과 중시)
        recent_5_games = recent_results[:5]
        recent_success_count = sum(1 for r in recent_5_games if r.is_correct)
        
        # 최근 5게임 중 3게임 이상 성공하면 상승
        if recent_success_count >= 3:
            self.logger.info(f"User {user_id} passed recent performance check: {recent_success_count}/5 games successful")
            return True
        
        # 4. 연속 성공 조건 (기존 로직 유지)
        consecutive_success, _ = self._calculate_consecutive_results(db, user_id, game_type)
        if consecutive_success >= DIFFICULTY_THRESHOLDS['CONSECUTIVE_SUCCESS_FOR_INCREASE']:
            self.logger.info(f"User {user_id} passed consecutive success check: {consecutive_success} consecutive successes")
            return True
        
        self.logger.info(f"User {user_id} failed all difficulty increase checks")
        return False

    def _should_decrease_difficulty(self, db: Session, user_id: int, game_type: str, recent_results: list) -> bool:
        """난이도 하락 여부 판단 (개선된 로직)"""
        if not recent_results:
            return False
        
        # 1. 전체 성공률 조건
        success_rate = self.calculate_success_rate(db, user_id, game_type)
        if success_rate <= DIFFICULTY_THRESHOLDS['HARD_TO_EASY']:
            return True
        
        # 2. 난이도 점수 조건
        difficulty_score = self.calculate_difficulty_score(db, user_id, game_type)
        if difficulty_score <= 0.3:
            return True
        
        # 3. 최근 성과 조건
        recent_5_games = recent_results[:5]
        recent_success_count = sum(1 for r in recent_5_games if r.is_correct)
        
        # 최근 5게임 중 1게임 이하 성공하면 하락
        if recent_success_count <= 1:
            return True
        
        # 4. 연속 실패 조건 (기존 로직 유지)
        _, consecutive_failure = self._calculate_consecutive_results(db, user_id, game_type)
        if consecutive_failure >= DIFFICULTY_THRESHOLDS['CONSECUTIVE_FAILURE_FOR_DECREASE']:
            return True
        
        return False

    def update_user_difficulty(self, db: Session, user_id: int, game_type: str) -> Dict[str, Any]:
        """사용자 난이도 정보 업데이트"""
        try:
            # 성공률 계산
            success_rate = self.calculate_success_rate(db, user_id, game_type)
            
            # 연속 성공/실패 계산
            consecutive_success, consecutive_failure = self._calculate_consecutive_results(db, user_id, game_type)
            
            # 최근 게임 분석
            recent_results = get_recent_game_results(db, user_id, game_type, 5)
            recent_success_count = sum(1 for r in recent_results if r.is_correct)
            
            # 난이도 점수 계산
            difficulty_score = self.calculate_difficulty_score(db, user_id, game_type)
            
            # 사용자 난이도 정보 업데이트
            difficulty = create_or_update_user_difficulty(
                db, user_id, game_type, success_rate, consecutive_success, consecutive_failure
            )
            
            # 다음 추천 게임 유형 결정
            recommended_game_type = self.determine_next_game_type(db, user_id, game_type)
            
            # 상승/하락 이유 결정
            reason = self._get_difficulty_change_reason(
                game_type, recommended_game_type, success_rate, 
                difficulty_score, recent_success_count, consecutive_success, consecutive_failure
            )
            
            return {
                "current_game_type": game_type,
                "recommended_game_type": recommended_game_type,
                "success_rate": success_rate,
                "difficulty_score": difficulty_score,
                "consecutive_success": consecutive_success,
                "consecutive_failure": consecutive_failure,
                "recent_performance": {
                    "recent_5_games": len(recent_results),
                    "recent_success_count": recent_success_count,
                    "recent_success_rate": recent_success_count / len(recent_results) if recent_results else 0
                },
                "difficulty_changed": game_type != recommended_game_type,
                "reason": reason
            }
            
        except Exception as e:
            self.logger.error(f"Error updating user difficulty: {e}")
            return {
                "current_game_type": game_type,
                "recommended_game_type": game_type,
                "success_rate": 0.0,
                "consecutive_success": 0,
                "consecutive_failure": 0,
                "difficulty_changed": False
            }

    def _calculate_consecutive_results(self, db: Session, user_id: int, game_type: str) -> tuple[int, int]:
        """연속 성공/실패 횟수 계산"""
        try:
            recent_results = get_recent_game_results(db, user_id, game_type, 10)
            
            if not recent_results:
                return 0, 0
            
            consecutive_success = 0
            consecutive_failure = 0
            
            # 최신 결과부터 역순으로 확인
            for result in recent_results:
                if result.is_correct:
                    consecutive_success += 1
                    consecutive_failure = 0  # 성공하면 실패 카운트 리셋
                else:
                    consecutive_failure += 1
                    consecutive_success = 0  # 실패하면 성공 카운트 리셋
                    
                    # 연속 실패가 3번 이상이면 더 이상 확인하지 않음
                    if consecutive_failure >= 3:
                        break
            
            return consecutive_success, consecutive_failure
            
        except Exception as e:
            self.logger.error(f"Error calculating consecutive results: {e}")
            return 0, 0

    def _get_difficulty_change_reason(self, current_type: str, recommended_type: str, 
                                    success_rate: float, difficulty_score: float,
                                    recent_success_count: int, consecutive_success: int, 
                                    consecutive_failure: int) -> str:
        """난이도 변화 이유 결정"""
        
        if current_type == recommended_type:
            return "현재 난이도 유지"
        
        if current_type == 'SENTENCE_SEQUENCE' and recommended_type == 'WORD_SEQUENCE':
            # 난이도 상승 이유
            if recent_success_count >= 3:
                return f"최근 5게임 중 {recent_success_count}게임 성공"
            elif consecutive_success >= 5:
                return f"연속 {consecutive_success}회 성공"
            elif success_rate >= 0.7:
                return f"전체 성공률 {success_rate:.1%} 달성"
            elif difficulty_score >= 0.6:
                return f"난이도 점수 {difficulty_score:.1f} 달성"
            else:
                return "종합적 성과 우수"
        
        elif current_type == 'WORD_SEQUENCE' and recommended_type == 'SENTENCE_SEQUENCE':
            # 난이도 하락 이유
            if recent_success_count <= 1:
                return f"최근 5게임 중 {recent_success_count}게임만 성공"
            elif consecutive_failure >= 3:
                return f"연속 {consecutive_failure}회 실패"
            elif success_rate <= 0.3:
                return f"전체 성공률 {success_rate:.1%} 미달"
            elif difficulty_score <= 0.3:
                return f"난이도 점수 {difficulty_score:.1f} 미달"
            else:
                return "성과 개선 필요"
        
        return "기타 사유"

    def get_difficulty_message(self, current_type: str, recommended_type: str) -> str:
        """사용자에게 난이도 변화 알림 메시지 생성"""
        if current_type != recommended_type:
            if recommended_type == 'WORD_SEQUENCE':
                return "축하합니다! 단어 순서 맞추기로 도전해보세요."
            elif recommended_type == 'SENTENCE_SEQUENCE':
                return "천천히 다시 문장 순서 맞추기부터 시작해보세요."
        
        return "현재 난이도에서 계속 연습해보세요." 