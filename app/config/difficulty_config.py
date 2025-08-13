import os

# 환경변수에서 설정을 가져오거나 기본값 사용
def get_difficulty_thresholds():
    return {
        'EASY_TO_MEDIUM': float(os.getenv('EASY_TO_MEDIUM_THRESHOLD', '0.7')),
        'MEDIUM_TO_HARD': float(os.getenv('MEDIUM_TO_HARD_THRESHOLD', '0.8')),
        'HARD_TO_EASY': float(os.getenv('HARD_TO_EASY_THRESHOLD', '0.3')),
        'MIN_GAMES_FOR_ANALYSIS': int(os.getenv('MIN_GAMES_FOR_ANALYSIS', '5')),
        'CONSECUTIVE_SUCCESS_FOR_INCREASE': int(os.getenv('CONSECUTIVE_SUCCESS_FOR_INCREASE', '5')),
        'CONSECUTIVE_FAILURE_FOR_DECREASE': int(os.getenv('CONSECUTIVE_FAILURE_FOR_DECREASE', '3'))
    }

# 시니어별 맞춤 설정
SENIOR_DIFFICULTY_PROFILES = {
    'BEGINNER': {
        'consecutive_success_for_increase': 3,  # 연속 3번 성공 시 상승
        'consecutive_failure_for_decrease': 2,  # 연속 2번 실패 시 하락
        'easy_to_medium': 0.6,  # 60% 성공률
        'hard_to_easy': 0.4     # 40% 성공률
    },
    'INTERMEDIATE': {
        'consecutive_success_for_increase': 5,  # 연속 5번 성공 시 상승
        'consecutive_failure_for_decrease': 3,  # 연속 3번 실패 시 하락
        'easy_to_medium': 0.7,  # 70% 성공률
        'hard_to_easy': 0.3     # 30% 성공률
    },
    'ADVANCED': {
        'consecutive_success_for_increase': 7,  # 연속 7번 성공 시 상승
        'consecutive_failure_for_decrease': 4,  # 연속 4번 실패 시 하락
        'easy_to_medium': 0.8,  # 80% 성공률
        'hard_to_easy': 0.2     # 20% 성공률
    }
} 