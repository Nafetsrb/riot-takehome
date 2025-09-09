from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class APIError(Exception):
    """Domain-specific API error carrying HTTP status & normalized code."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)

class APIErrorResponse(BaseModel):
    error: str
    code: str

def add_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers (domain & fallback)."""

    @app.exception_handler(APIError)
    async def _handle_api_error(_: Request, exc: APIError):
        return JSONResponse(
            status_code=exc.status_code,
            content=APIErrorResponse(error=exc.message, code=exc.code).model_dump(),
        )

    @app.exception_handler(Exception)
    async def _handle_500(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=APIErrorResponse(error='Internal Server Error', code='internal_error').model_dump(),
        )
