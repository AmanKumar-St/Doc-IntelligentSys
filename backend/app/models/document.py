from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


@dataclass
class DocumentMetadata:
    id: str
    filename: str
    original_path: str
    markdown_path: str
    file_type: str
    size_bytes: int
    chunk_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: Literal["uploaded", "parsing", "chunking", "embedded", "error"] = "uploaded"
    error_message: str | None = None
