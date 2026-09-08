import hashlib
import math
from app.providers.embeddings.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic offline embedding provider for tests and local experiments."""
    def __init__(self, dimension: int = 1536):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            # Generate deterministic float vector from md5/sha256 hash
            vector: list[float] = []
            seed = hashlib.sha256(text.encode("utf-8")).digest()
            for i in range(self._dimension):
                b = seed[i % len(seed)]
                val = (b / 255.0) * 2.0 - 1.0
                vector.append(val)
            
            # Normalize vector
            norm = math.sqrt(sum(x * x for x in vector)) or 1.0
            results.append([x / norm for x in vector])
        return results
