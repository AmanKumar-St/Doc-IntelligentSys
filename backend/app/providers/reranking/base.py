from abc import ABC, abstractmethod
from app.models.chunk import Chunk


class RerankerProvider(ABC):
    @abstractmethod
    async def rerank(self, query: str, chunks: list[Chunk], top_k: int = 6) -> list[Chunk]:
        """Reranks candidate chunks based on relevance to query and returns top_k chunks."""
        pass
