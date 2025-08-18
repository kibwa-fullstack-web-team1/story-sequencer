import jwt
from fastapi import Depends, HTTPException, status, Request
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.story import Story  # 실제 User 모델 import 필요
import os
import httpx
from typing import Optional
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"

# User Service 설정
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8000")

# ... (기존 JWT/해시 함수 생략)

async def validate_user_exists(user_id: int) -> bool:
    """User Service API를 호출하여 사용자 존재 여부 확인"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            return response.status_code == 200
    except Exception as e:
        print(f"User Service 호출 실패: {e}")
        return False

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """현재 사용자 ID 가져오기 (JWT 검증)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization 헤더 형식이 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰에서 사용자 ID를 추출할 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\", error_description=\"expired\""}
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 디코딩에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
        )

async def get_current_user_validated(request: Request, db: Session = Depends(get_db)):
    """사용자 인증 및 존재 여부 검증"""
    user_id = get_current_user(request, db)
    
    # User Service API 호출하여 사용자 존재 여부 확인
    user_exists = await validate_user_exists(user_id)
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="사용자를 찾을 수 없습니다."
        )
    
    return user_id 