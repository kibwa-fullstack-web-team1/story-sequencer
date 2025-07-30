from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
import os
from typing import List

router = APIRouter()

@router.post("/image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """이미지 업로드"""
    try:
        # 파일 타입 검증
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
        # 파일 크기 검증 (5MB 제한)
        file_size = 0
        file_content = b""
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > 5 * 1024 * 1024:  # 5MB
                raise HTTPException(status_code=400, detail="파일 크기는 5MB를 초과할 수 없습니다.")
            file_content += chunk
        
        # 파일 확장자 추출
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다.")
        
        # S3 서비스가 있는지 확인
        if not hasattr(request.app.state, 's3_service') or request.app.state.s3_service is None:
            raise HTTPException(status_code=500, detail="S3 서비스가 설정되지 않았습니다.")
        
        # S3에 업로드
        s3_url = request.app.state.s3_service.upload_image(file_content, file_extension)
        
        if not s3_url:
            raise HTTPException(status_code=500, detail="이미지 업로드에 실패했습니다.")
        
        return JSONResponse(content={
            "results": {
                "image_url": s3_url,
                "filename": file.filename,
                "size": file_size
            },
            "error": None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 중 오류가 발생했습니다: {str(e)}")

@router.delete("/image")
async def delete_image(request: Request, image_url: str):
    """이미지 삭제"""
    try:
        # S3 서비스가 있는지 확인
        if not hasattr(request.app.state, 's3_service') or request.app.state.s3_service is None:
            raise HTTPException(status_code=500, detail="S3 서비스가 설정되지 않았습니다.")
        
        # S3에서 삭제
        success = request.app.state.s3_service.delete_image(image_url)
        
        if not success:
            raise HTTPException(status_code=500, detail="이미지 삭제에 실패했습니다.")
        
        return JSONResponse(content={
            "results": {"message": "이미지가 성공적으로 삭제되었습니다."},
            "error": None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"삭제 중 오류가 발생했습니다: {str(e)}") 