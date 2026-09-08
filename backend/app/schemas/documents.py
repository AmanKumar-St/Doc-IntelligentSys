from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    size_bytes: int
    chunk_count: int = 0
    created_at: datetime
    status: Literal["uploaded", "parsing", "chunking", "embedded", "error"]
    error_message: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    chunk_count: int = 0
