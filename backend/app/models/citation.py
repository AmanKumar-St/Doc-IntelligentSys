from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    id: str  # e.g., "C1", "C2"
    chunk_id: str
    document_id: str
    source: str
    section: str | None = None
    page: int | None = None
    heading_path: list[str] = field(default_factory=list)
    snippet: str = ""
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source": self.source,
            "section": self.section,
            "page": self.page,
            "heading_path": self.heading_path,
            "snippet": self.snippet,
            "score": self.score,
        }
