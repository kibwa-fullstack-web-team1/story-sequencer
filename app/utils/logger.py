import logging
import os
from logging.handlers import RotatingFileHandler

class Logger:
    @staticmethod
    def init_app(app):
        # 로그 디렉토리 생성
        log_path = app.state.config.LOG_PATH
        os.makedirs(log_path, exist_ok=True)
        
        # 로그 레벨 설정
        log_level = app.state.config.LOG_LEVEL
        
        # 로그 포맷 설정
        log_format = app.state.config.LOG_FORMAT
        formatter = logging.Formatter(log_format)
        
        # 파일 핸들러 설정
        file_handler = RotatingFileHandler(
            os.path.join(log_path, 'story-api.log'),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logging.info(f"Logger initialized for {app.state.config.PHASE} environment") 