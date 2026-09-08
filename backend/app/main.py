from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.router import router
from app.core.config import get_settings
from app.core.logging import logger
from app.core.error_handlers import register_exception_handlers
from app.core.rate_limiter import (
    get_rate_limiter,
    check_upload_rate_limit,
    check_chat_rate_limit,
    check_search_rate_limit,
    RateLimitExceeded,
)

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        path = request.url.path
        method = request.method

        if method == "OPTIONS":
            return await call_next(request)

        try:
            if path.startswith("/api/documents") and method == "POST":
                await check_upload_rate_limit(client_ip)
            elif path.startswith("/api/chat") and method == "POST":
                await check_chat_rate_limit(client_ip)
            elif path.startswith("/api/search") and method == "POST":
                await check_search_rate_limit(client_ip)
        except RateLimitExceeded as e:
            return Response(
                content=f'{{"detail": "{str(e)}", "error_code": "RATE_LIMIT_EXCEEDED", "retry_after": {e.retry_after}, "limit": {e.limit}, "window_seconds": {e.window_seconds}}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(e.retry_after)},
            )

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        if request.client:
            return request.client.host
        return "unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Embedding provider: {settings.embedding_provider} ({settings.embedding_model})")
    logger.info(f"Generation provider: {settings.generation_provider} ({settings.generation_model})")
    logger.info(f"Reranker provider: {settings.reranker_provider}")
    logger.info(f"Vector storage mode: {'Embedded' if settings.use_embedded_qdrant else 'Remote Qdrant'}")
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title="Document Intelligence & RAG System",
    description="Modular Document Intelligence and RAG platform with provider abstractions and verifiable citations.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
allowed_origins = [settings.frontend_url] if settings.frontend_url else []
if settings.environment == "development":
    allowed_origins.append("http://localhost:5173")
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Register exception handlers
register_exception_handlers(app)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs_url": "/docs",
        "api_prefix": "/api",
        "status": "online",
    }
