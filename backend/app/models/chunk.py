from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    source: str
    citation_id: str | None = None
    section: str | None = None
    page: int | None = None
    heading_path: list[str] = field(default_factory=list)
    start_char: int | None = None
    end_char: int | None = None
    score: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "text": self.text,
            "source": self.source,
            "citation_id": self.citation_id,
            "section": self.section,
            "page": self.page,
            "heading_path": self.heading_path,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "score": self.score,
        }
