import re
from app.core.config import Settings, get_settings
from app.core.logging import logger
from app.models.chunk import Chunk
from app.providers.embeddings.factory import create_embedding_provider
from app.providers.reranking.factory import create_reranker_provider
from app.storage.qdrant import QdrantStorage


class RetrievalService:
    def __init__(
        self,
        settings: Settings | None = None,
        qdrant: QdrantStorage | None = None,
    ):
        self.settings = settings or get_settings()
        self.qdrant = qdrant or QdrantStorage(self.settings)
        self.embedding_provider = create_embedding_provider(self.settings)
        self.reranker = create_reranker_provider(self.settings)

    def normalize_query(self, query: str) -> str:
        """Cleans and normalizes query text."""
        q = re.sub(r"\s+", " ", query).strip()
        return q

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        rerank_top_k: int | None = None,
        document_id: str | None = None,
    ) -> list[Chunk]:
        normalized = self.normalize_query(query)
        if not normalized:
            return []

        search_k = top_k or self.settings.top_k
        target_k = rerank_top_k or self.settings.rerank_top_k

        # 1. Embed query
        query_vectors = await self.embedding_provider.embed([normalized])
        if not query_vectors:
            return []
        query_vector = query_vectors[0]

        # 2. Dense search from Qdrant
        candidate_chunks = self.qdrant.search(
            query_vector=query_vector,
            top_k=search_k,
            document_id=document_id,
        )
        if not candidate_chunks:
            logger.info(f"No vector matches found for query: '{query}'")
            return []

        # 3. Rerank candidates
        reranked_chunks = await self.reranker.rerank(
            query=normalized,
            chunks=candidate_chunks,
            top_k=target_k,
        )

        # 4. Assign deterministic citation IDs: [C1], [C2], ...
        for idx, chunk in enumerate(reranked_chunks, start=1):
            chunk.citation_id = f"C{idx}"

        logger.info(
            f"Retrieved {len(candidate_chunks)} candidates, reranked to {len(reranked_chunks)} precision chunks."
        )
        return reranked_chunks
