from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query text to search for")
    top_k: int = Field(default=6, ge=1, le=50, description="Number of results to return")
    document_id: str | None = Field(default=None, description="Optional document filter")


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
