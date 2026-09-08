from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import (
    DocumentIntelligenceException,
    DocumentParsingError,
    VectorStorageError,
    ProviderError,
)
from app.core.rate_limiter import RateLimitExceeded
from app.core.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
        logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": str(exc),
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": exc.retry_after,
                "limit": exc.limit,
                "window_seconds": exc.window_seconds,
            },
            headers={"Retry-After": str(exc.retry_after)},
        )

    @app.exception_handler(DocumentParsingError)
    async def document_parsing_exception_handler(request: Request, exc: DocumentParsingError):
        logger.error(f"Document parsing error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": f"Failed to parse document: {str(exc)}",
                "error_code": "DOCUMENT_PARSING_ERROR",
            },
        )

    @app.exception_handler(VectorStorageError)
    async def vector_storage_exception_handler(request: Request, exc: VectorStorageError):
        logger.error(f"Vector storage error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Vector storage temporarily unavailable. Please try again later.",
                "error_code": "VECTOR_STORAGE_ERROR",
            },
        )

    @app.exception_handler(ProviderError)
    async def provider_exception_handler(request: Request, exc: ProviderError):
        logger.error(f"Provider error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "AI provider temporarily unavailable. Please try again later.",
                "error_code": "PROVIDER_ERROR",
            },
        )

    @app.exception_handler(DocumentIntelligenceException)
    async def document_intelligence_exception_handler(request: Request, exc: DocumentIntelligenceException):
        logger.error(f"Document intelligence error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal error occurred.",
                "error_code": "INTERNAL_ERROR",
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": f"HTTP_{exc.status_code}"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred.",
                "error_code": "INTERNAL_SERVER_ERROR",
            },
        )