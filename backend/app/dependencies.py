from functools import lru_cache
from app.core.config import Settings, get_settings
from app.ingestion.service import IngestionService
from app.retrieval.service import RetrievalService
from app.generation.service import GenerationService
from app.storage.files import FileStorage
from app.storage.qdrant import QdrantStorage


@lru_cache
def get_file_storage() -> FileStorage:
    return FileStorage(get_settings())


@lru_cache
def get_qdrant_storage() -> QdrantStorage:
    return QdrantStorage(get_settings())


@lru_cache
def get_ingestion_service() -> IngestionService:
    settings = get_settings()
    return IngestionService(
        settings=settings,
        qdrant=get_qdrant_storage(),
        files=get_file_storage(),
    )


@lru_cache
def get_retrieval_service() -> RetrievalService:
    settings = get_settings()
    return RetrievalService(
        settings=settings,
        qdrant=get_qdrant_storage(),
    )


@lru_cache
def get_generation_service() -> GenerationService:
    return GenerationService(get_settings())
