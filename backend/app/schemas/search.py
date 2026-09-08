from pydantic import BaseModel, Field, field_validator
from app.core.config import get_settings


DEFAULT_MAX_QUERY_LENGTH = 2000


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=DEFAULT_MAX_QUERY_LENGTH, description="Query text to search for")
    top_k: int = Field(default=6, ge=1, le=50, description="Number of results to return")
    document_id: str | None = Field(default=None, description="Optional document filter")

    @field_validator("query")
    @classmethod
    def validate_query_length(cls, v: str) -> str:
        settings = get_settings()
        max_len = settings.max_query_length
        if len(v) > max_len:
            raise ValueError(f"Query exceeds maximum length of {max_len} characters")
        return v


class SearchResultItem(BaseModel):
    citation_id: str
    chunk_id: str
    document_id: str
    source: str
    text: str
    section: str | None = None
    page: int | None = None
    heading_path: list[str] = []
    score: float


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResultItem]
