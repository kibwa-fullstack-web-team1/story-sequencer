from fastapi import APIRouter
from app.api.story import router as story_router
from app.api.admin import router as admin_router
from app.api.upload import router as upload_router
from app.api.activity import router as activity_router

# 메인 API 라우터 생성
router = APIRouter()

# 모든 서브 라우터 등록
router.include_router(story_router, prefix="/stories", tags=["stories"])
router.include_router(admin_router, prefix="/admin", tags=["admin"])
router.include_router(upload_router, prefix="/upload", tags=["upload"])
router.include_router(activity_router, prefix="", tags=["activity"]) 