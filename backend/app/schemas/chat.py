from pydantic import BaseModel, Field


class ChatCitation(BaseModel):
    id: str  # "C1", "C2"
    chunk_id: str
    document_id: str
    source: str
    section: str | None = None
    page: int | None = None
    heading_path: list[str] = []
    snippet: str
    score: float | None = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to answer using documents")
    history: list[ChatMessage] = Field(default_factory=list, description="Optional previous chat turns")
    document_id: str | None = Field(default=None, description="Optional document filter")
    model_override: str | None = Field(default=None, description="Optional model override")


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
    provider: str
    model: str
    chunks_used: int
    validation_status: str  # "valid" | "fallback_applied" | "unverified"
