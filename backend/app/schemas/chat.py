from pydantic import BaseModel, Field, field_validator
from app.core.config import get_settings


DEFAULT_MAX_CHAT_LENGTH = 4000
DEFAULT_MAX_QUERY_LENGTH = 2000


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
    content: str = Field(..., max_length=DEFAULT_MAX_CHAT_LENGTH)

    @field_validator("content")
    @classmethod
    def validate_content_length(cls, v: str) -> str:
        settings = get_settings()
        max_len = settings.max_chat_message_length
        if len(v) > max_len:
            raise ValueError(f"Message content exceeds maximum length of {max_len} characters")
        return v


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=DEFAULT_MAX_CHAT_LENGTH, description="Question to answer using documents")
    history: list[ChatMessage] = Field(default_factory=list, description="Optional previous chat turns")
    document_id: str | None = Field(default=None, description="Optional document filter")
    model_override: str | None = Field(default=None, description="Optional model override")

    @field_validator("question")
    @classmethod
    def validate_question_length(cls, v: str) -> str:
        settings = get_settings()
        max_len = settings.max_chat_message_length
        if len(v) > max_len:
            raise ValueError(f"Question exceeds maximum length of {max_len} characters")
        return v


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
    provider: str
    model: str
    chunks_used: int
    validation_status: str  # "valid" | "fallback_applied" | "unverified"
