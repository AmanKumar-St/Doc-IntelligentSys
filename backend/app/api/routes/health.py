from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "embedding_provider": settings.embedding_provider,
        "generation_provider": settings.generation_provider,
        "reranker_provider": settings.reranker_provider,
        "storage_mode": "embedded" if settings.use_embedded_qdrant else "remote",
    }
