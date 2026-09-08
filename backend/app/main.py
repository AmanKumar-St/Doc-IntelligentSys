from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

app = FastAPI(
    title="Document Intelligence & RAG System",
    description="Modular Document Intelligence and RAG platform with provider abstractions and verifiable citations.",
    version="0.1.0",
)

# CORS configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"Embedding provider: {settings.embedding_provider} ({settings.embedding_model})")
    logger.info(f"Generation provider: {settings.generation_provider} ({settings.generation_model})")
    logger.info(f"Reranker provider: {settings.reranker_provider}")
    logger.info(f"Vector storage mode: {'Embedded' if settings.use_embedded_qdrant else 'Remote Qdrant'}")
