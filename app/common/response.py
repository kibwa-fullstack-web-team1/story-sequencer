from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
import logging
from typing import Any, Dict, Optional

class ErrorBase(Exception):
    def __init__(self, message="에러가 발생하였습니다.", status_code=HTTPStatus.INTERNAL_SERVER_ERROR):
        self.method = self._get_calling_method()
        self.message = message
        self._status_code = status_code

    def status_code(self):
        return self._status_code

    def get_message(self):
        return self.message
    
    def _get_calling_method(self):
        import traceback
        try:
            return traceback.extract_stack()[-2][2]
        except:
            return "unknown"

class NotFoundError(ErrorBase):
    def __init__(self, message="결과가 없습니다."):
        super().__init__(message, HTTPStatus.NOT_FOUND)

class BadRequest(ErrorBase):
    def __init__(self, message="잘못된 요청입니다. 확인 후 다시 시도해주세요."):
        super().__init__(message, HTTPStatus.BAD_REQUEST)

class ValidationError(ErrorBase):
    def __init__(self, message="입력 데이터가 올바르지 않습니다."):
        super().__init__(message, HTTPStatus.BAD_REQUEST)

class OpenAIServiceError(ErrorBase):
    def __init__(self, message="AI 서비스 처리 중 오류가 발생했습니다."):
        super().__init__(message, HTTPStatus.INTERNAL_SERVER_ERROR)

def create_response(data: Any = None, error: Optional[str] = None, status: int = 200) -> Dict[str, Any]:
    """표준화된 응답 형식 생성"""
    if isinstance(data, ErrorBase):
        response_data = {
            'results': None,
            'error': data.get_message()
        }
        status = data.status_code()
    else:
        response_data = {
            'results': data,
            'error': str(error) if error else None
        }

    return response_data

def register_error_handlers(app):
    @app.exception_handler(ErrorBase)
    async def handle_custom_error(request: Request, exc: ErrorBase):
        logging.error(f"Custom error in {exc.method}: {exc.get_message()}")
        return JSONResponse(
            status_code=exc.status_code(),
            content=create_response(error=exc.get_message())
        )

    @app.exception_handler(404)
    async def handle_not_found(request: Request, exc: HTTPException):
        logging.error(f"Not found: {exc}")
        return JSONResponse(
            status_code=404,
            content=create_response(error="요청한 리소스를 찾을 수 없습니다.")
        )

    @app.exception_handler(500)
    async def handle_internal_error(request: Request, exc: HTTPException):
        logging.error(f"Internal server error: {exc}")
        return JSONResponse(
            status_code=500,
            content=create_response(error="내부 서버 오류가 발생했습니다.")
        )

    @app.exception_handler(Exception)
    async def handle_generic_error(request: Request, exc: Exception):
        logging.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=create_response(error="예상치 못한 오류가 발생했습니다.")
        ) 