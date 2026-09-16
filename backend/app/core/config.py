from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "document-intelligence"
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    frontend_url: str = "*"
    cors_origins: str = "*"

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_storage_path: str = "./data/qdrant_db"
    qdrant_collection: str = "documents"
    use_embedded_qdrant: bool = True

    # Storage Paths
    upload_dir: str = "./data/uploads"
    markdown_dir: str = "./data/markdown"

    # File Upload Limits
    max_upload_size_mb: int = 10
    allowed_file_extensions: str = ".pdf,.docx,.doc,.txt,.md,.markdown,.xlsx,.xls,.pptx,.ppt,.csv,.json,.html,.htm,.xml,.rtf,.odt,.ods,.odp"

    # Request Body Limits
    max_query_length: int = 2000
    max_chat_message_length: int = 4000

    # Rate Limiting
    rate_limit_enabled: bool = True
    upload_rate_limit: int = 5
    upload_rate_window_seconds: int = 3600
    chat_rate_limit: int = 30
    chat_rate_window_seconds: int = 3600
    search_rate_limit: int = 60
    search_rate_window_seconds: int = 3600

    # Embeddings
    embedding_provider: str = "openrouter"
    embedding_model: str = "nvidia/nemotron-3-embed-1b:free"
    embedding_dimension: int = 2048

    # Reranker
    reranker_provider: str = "openrouter"
    reranker_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    # Generation
    generation_provider: str = "openrouter"
    generation_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    generation_fallback_provider: str | None = "openrouter"
    generation_fallback_model: str | None = "openrouter/free"

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
    unorouter_base_url: str = "https://api.unorouter.com/v1"

    # RAG Parameters
    top_k: int = 20
    rerank_top_k: int = 6
    max_context_chunks: int = 6
    chunk_size: int = 1000
    chunk_overlap: int = 150
    temperature: float = 0.1
    max_output_tokens: int = 1500

    @field_validator("openrouter_api_key", "codecraft_api_key", "unorouter_api_key", "qdrant_api_key", mode="before")
    @classmethod
    def _strip_keys(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("openrouter_base_url", "codecraft_base_url", "unorouter_base_url", mode="before")
    @classmethod
    def _sanitize_base_urls(cls, v: str | None) -> str | None:
        if not v or not isinstance(v, str):
            return v
        v = v.strip().rstrip("/")
        # If user accidentally provided full completions or embeddings endpoint, strip it
        suffixes_to_strip = ["/chat/completions", "/embeddings", "/models"]
        for suffix in suffixes_to_strip:
            if v.endswith(suffix):
                v = v[: -len(suffix)].rstrip("/")
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

