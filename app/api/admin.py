from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
async def admin_panel():
    """Admin panel 메인 페이지"""
    return FileResponse("static/admin/index.html") 