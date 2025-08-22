from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config.config import config_by_name
from app.utils.logger import Logger
from app.common.response import register_error_handlers
from app.api import router as api_router
from app.api.internal_router import router as internal_api_router # internal_router 임포트
import os

def create_app(config_name):
    app = FastAPI(
        title="Story API Service",
        description="기억의 정원 프로젝트의 이야기 관리 API 서비스",
        version="1.0.0"
    )
    
    # CORS 설정 - 프론트엔드 포트로 통일
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 설정 로드
    config = config_by_name[config_name]()
    app.state.config = config
    
    # Lab environment setup
    if config_name == 'lab_development':
        external_config = None
        app.state.message_queue = None
    else:
        external_config = load_dynamic_config(config)
        app.state.message_queue = None  # 필요시 MessageQueue 구현
    
    Logger.init_app(app)
    
    # Initialize services based on environment
    if config_name == 'lab_development' or not CORE_MODULES_AVAILABLE:
        # Use mocks for lab environment
        from app.lab import MockStoryService, MockOpenAIService
        app.state.story_service = MockStoryService().init_app(app)
        app.state.openai_service = MockOpenAIService().init_app(app)
        app.state.s3_service = None
        app.state.external_config = None
    else:
        # Use real services for other environments
        from app.core.story_service import StoryService
        from app.core.openai_service import OpenAIService
        from app.core.s3_service import S3Service
        app.state.story_service = StoryService().init_app(app)
        app.state.openai_service = OpenAIService().init_app(app)
        app.state.s3_service = S3Service().init_app(app)
        app.state.external_config = external_config

    # 데이터베이스 초기화
    try:
        from app.database import init_db
        init_db()
    except Exception as e:
        print(f"데이터베이스 초기화 실패: {e}")
        print("일부 기능이 제한될 수 있습니다.")
    
    # 정적 파일 서빙 설정 - FastAPI StaticFiles 사용으로 최적화
    static_dir = os.path.join(os.getcwd(), "static")
    print(f"Static directory: {static_dir}")
    print(f"Static directory exists: {os.path.exists(static_dir)}")
    
    if os.path.exists(static_dir):
        # 정적 파일을 FastAPI의 StaticFiles로 서빙
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # 루트 경로에서 정적 파일 서빙
        @app.get("/")
        def serve_root():
            return FileResponse(os.path.join(static_dir, "elderly", "index.html"))
        
        # admin 페이지 서빙
        @app.get("/admin")
        def serve_admin():
            admin_index = os.path.join(static_dir, "admin", "index.html")
            if os.path.exists(admin_index):
                return FileResponse(admin_index)
            return {"error": "Admin page not found"}
    
    # 헬스체크 엔드포인트 추가
    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "story-api", "port": 8011}
    
    app.include_router(api_router, prefix=config.APP_PREFIX)
    app.include_router(internal_api_router) # 내부 API 라우터 포함
    register_error_handlers(app)
    
    return app

def load_dynamic_config(config):
    """동적 설정 로드 로직"""
    try:
        # 환경변수에서 설정 로드
        external_config = {
            'openai_api_key': os.environ.get('OPENAI_API_KEY'),
            'database_url': os.environ.get('DATABASE_URL'),
            'aws_region': os.environ.get('AWS_REGION'),
            's3_bucket': os.environ.get('S3_BUCKET_NAME'),
            'kafka_broker': os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
        }
        
        # 필수 설정 검증
        missing_configs = []
        if not external_config['openai_api_key']:
            missing_configs.append('OPENAI_API_KEY')
        if not external_config['database_url']:
            missing_configs.append('DATABASE_URL')
        
        if missing_configs:
            print(f"Warning: Missing required environment variables: {', '.join(missing_configs)}")
            print("Some features may not work properly.")
            
        # AWS 설정 검증
        if not external_config['aws_region']:
            print("Warning: AWS_REGION not set, S3 service may not work")
        if not external_config['s3_bucket']:
            print("Warning: S3_BUCKET_NAME not set, S3 service may not work")
            
        return external_config
    except Exception as e:
        print(f"Error loading dynamic config: {e}")
        print("Using default configuration")
        return {
            'openai_api_key': None,
            'database_url': None,
            'aws_region': None,
            's3_bucket': None,
            'kafka_broker': 'kafka:9092'
        }

# 환경변수로 CORE_MODULES_AVAILABLE 설정
CORE_MODULES_AVAILABLE = os.getenv('CORE_MODULES_AVAILABLE', 'true').lower() == 'true'