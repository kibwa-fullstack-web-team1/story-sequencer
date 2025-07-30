import os
import logging
from typing import Optional

class Config(object):
    PHASE = 'default'
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    APP_NAME = 'story-api'
    APP_PREFIX = '/api/v0'

    # 환경변수에서 로드
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    STORY_DATABASE_URL = os.environ.get(
        'DATABASE_URL'
    )

    # 로깅 설정
    LOG_LEVEL = logging.INFO
    LOG_PATH = '/var/log/story-api'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class ProductionConfig(Config):
    PHASE = 'production'
    LOG_LEVEL = logging.INFO
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    PHASE = 'development'
    LOG_LEVEL = logging.DEBUG
    LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

    def __init__(self):
        """Apply lab environment settings if detected"""
        if is_lab_environment():
            self.PHASE = 'lab_development'
            self.DUMMY_DATA_ENABLED = True
            # 랩 환경 전용 설정 오버라이드
            self.OPENAI_API_KEY = 'mock_key'
            self.STORY_DATABASE_URL = 'sqlite:///test.db'

class TestingConfig(Config):
    TESTING = True
    PHASE = 'testing'
    LOG_LEVEL = logging.DEBUG
    LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    STORY_DATABASE_URL = 'sqlite:///test.db'

def is_lab_environment():
    return os.getenv('SERVICE_LAB_MODE', '').lower() == 'true'

config_by_name = dict(
    development=DevelopmentConfig,
    test=TestingConfig,
    production=ProductionConfig,
    lab_development=DevelopmentConfig
) 