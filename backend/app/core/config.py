from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "document-intelligence"
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_storage_path: str = "./data/qdrant_db"
    qdrant_collection: str = "documents"
    use_embedded_qdrant: bool = True

    # Storage Paths
    upload_dir: str = "./data/uploads"
    markdown_dir: str = "./data/markdown"

    # Embeddings
    embedding_provider: str = "openrouter"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Reranker
    reranker_provider: str = "openrouter"
    reranker_model: str = "mistralai/mistral-7b-instruct:free"

    # Generation
    generation_provider: str = "openrouter"
    generation_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    generation_fallback_provider: str | None = "codecraft"
    generation_fallback_model: str | None = "gpt-4o-mini"

    # API Keys with alias support for multiple casing formats
    codecraft_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CODECRAFT_API_KEY", "CODE_CRAFT_KEY", "CODE-CRAFT-KEY"),
    )
    codecraft_base_url: str = "https://codecraftapi.com/v1"

    openrouter_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENROUTER_API_KEY", "OPENROUTER_KEY", "OPENROUTER-KEY"),
    )
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    unorouter_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("UNOROUTER_API_KEY", "UNOROUTER_KEY", "UNOROUTER-KEY"),
    )
    unorouter_base_url: str = "https://api.unorouter.ai/v1"

    # RAG Parameters
    top_k: int = 20
    rerank_top_k: int = 6
    max_context_chunks: int = 6
    chunk_size: int = 1000
    chunk_overlap: int = 150
    temperature: float = 0.1
    max_output_tokens: int = 1500

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
