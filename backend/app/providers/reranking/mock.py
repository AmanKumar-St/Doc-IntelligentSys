from app.models.chunk import Chunk
from app.providers.reranking.base import RerankerProvider


class MockRerankerProvider(RerankerProvider):
    async def rerank(self, query: str, chunks: list[Chunk], top_k: int = 6) -> list[Chunk]:
        # Return chunks sorted by score or simple keyword presence
        query_words = set(query.lower().split())

        def score_chunk(c: Chunk) -> float:
            base = c.score or 0.0
            chunk_words = set(c.text.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            return (overlap * 10.0) + base

        return sorted(chunks, key=score_chunk, reverse=True)[:top_k]
