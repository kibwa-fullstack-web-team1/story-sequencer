from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config.config import config_by_name
from app.utils.logger import Logger
from app.common.response import register_error_handlers
from app.api import router as api_router
import os

def create_app(config_name):
    app = FastAPI(
        title="Story API Service",
        description="기억의 정원 프로젝트의 이야기 관리 API 서비스",
        version="1.0.0"
    )
    
    # CORS 설정 - 더 구체적으로 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],
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
    
    # 정적 파일 서빙 설정 - 모든 파일을 직접 라우트로 처리
    static_dir = os.path.join(os.getcwd(), "static")
    print(f"Static directory: {static_dir}")
    print(f"Static directory exists: {os.path.exists(static_dir)}")
    
    @app.get("/static/admin/")
    def serve_admin():
        admin_index = os.path.join(static_dir, "admin", "index.html")
        if os.path.exists(admin_index):
            return FileResponse(admin_index)
        return {"error": "Admin page not found"}
    
    @app.get("/static/elderly/")
    def serve_elderly():
        elderly_index = os.path.join(static_dir, "elderly", "index.html")
        if os.path.exists(elderly_index):
            return FileResponse(elderly_index)
        return {"error": "Elderly page not found"}
    
    @app.get("/static/admin/{file_path:path}")
    def serve_admin_static(file_path: str):
        file_path = os.path.join(static_dir, "admin", file_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return {"error": f"File not found: {file_path}"}
    
    @app.get("/static/elderly/{file_path:path}")
    def serve_elderly_static(file_path: str):
        file_path = os.path.join(static_dir, "elderly", file_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return {"error": f"File not found: {file_path}"}
    
    # 헬스체크 엔드포인트 추가
    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "story-api", "port": 8011}
    
    app.include_router(api_router, prefix=config.APP_PREFIX)
    register_error_handlers(app)
    
    return app

def load_dynamic_config(config):
    # 동적 설정 로드 로직 (필요시 구현)
    return None

# 환경변수로 CORE_MODULES_AVAILABLE 설정
CORE_MODULES_AVAILABLE = os.getenv('CORE_MODULES_AVAILABLE', 'true').lower() == 'true' 