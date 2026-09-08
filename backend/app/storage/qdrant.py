from pathlib import Path
from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from app.core.config import Settings, get_settings
from app.core.exceptions import VectorStorageError
from app.core.logging import logger
from app.models.chunk import Chunk


class QdrantStorage:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.collection_name = self.settings.qdrant_collection
        self.dimension = self.settings.embedding_dimension
        self.client = self._init_client()
        self.ensure_collection_exists()

    def _init_client(self) -> QdrantClient:
        # Check if embedded mode is requested
        if self.settings.use_embedded_qdrant:
            storage_path = Path(self.settings.qdrant_storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing embedded Qdrant client at {storage_path.resolve()}")
            return QdrantClient(path=str(storage_path))
        
        # Production mode with external Qdrant (Qdrant Cloud)
        try:
            logger.info(f"Connecting to Qdrant at {self.settings.qdrant_url}")
            client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                timeout=30.0,
            )
            client.get_collections()
            return client
        except Exception as e:
            logger.error(f"Could not connect to Qdrant at {self.settings.qdrant_url}: {e}")
            if self.settings.environment == "production":
                raise VectorStorageError(f"Failed to connect to Qdrant: {str(e)}") from e
            
            logger.warning(
                f"Falling back to embedded local storage at {self.settings.qdrant_storage_path}"
            )
            storage_path = Path(self.settings.qdrant_storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            return QdrantClient(path=str(storage_path))

    def ensure_collection_exists(self) -> None:
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.info(
                    f"Creating Qdrant collection '{self.collection_name}' with vector size {self.dimension}"
                )
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest_models.VectorParams(
                        size=self.dimension,
                        distance=rest_models.Distance.COSINE,
                    ),
                )
                if not self.settings.use_embedded_qdrant:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="document_id",
                        field_schema=rest_models.PayloadSchemaType.KEYWORD,
                    )
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="source",
                        field_schema=rest_models.PayloadSchemaType.KEYWORD,
                    )
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")
            raise VectorStorageError(f"Qdrant collection setup error: {str(e)}") from e

    def upsert_chunks(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if not chunks or not vectors:
            return
        if len(chunks) != len(vectors):
            raise VectorStorageError(
                f"Mismatch: {len(chunks)} chunks vs {len(vectors)} vectors"
            )

        import hashlib

        points: list[rest_models.PointStruct] = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            # Deterministic 64-bit unsigned integer ID from MD5 hash
            point_id = int(hashlib.md5(chunk.id.encode("utf-8")).hexdigest()[:15], 16)
            points.append(
                rest_models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.id,
                        "document_id": chunk.document_id,
                        "text": chunk.text,
                        "source": chunk.source,
                        "section": chunk.section,
                        "page": chunk.page,
                        "heading_path": chunk.heading_path,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                    },
                )
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            logger.info(f"Upserted {len(points)} vector points to Qdrant '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Qdrant upsert error: {e}")
            raise VectorStorageError(f"Failed to upsert chunks: {str(e)}") from e

    def search(
        self,
        query_vector: list[float],
        top_k: int = 20,
        document_id: str | None = None,
    ) -> list[Chunk]:
        query_filter = None
        if document_id:
            query_filter = rest_models.Filter(
                must=[
                    rest_models.FieldCondition(
                        key="document_id",
                        match=rest_models.MatchValue(value=document_id),
                    )
                ]
            )

        try:
            # Modern qdrant-client uses query_points, older versions use search
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True,
                )
                search_results = response.points
            else:
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True,
                )

            results: list[Chunk] = []
            for hit in search_results:
                payload = hit.payload or {}
                chunk = Chunk(
                    id=payload.get("chunk_id", str(hit.id)),
                    document_id=payload.get("document_id", ""),
                    text=payload.get("text", ""),
                    source=payload.get("source", ""),
                    section=payload.get("section"),
                    page=payload.get("page"),
                    heading_path=payload.get("heading_path", []),
                    start_char=payload.get("start_char"),
                    end_char=payload.get("end_char"),
                    score=hit.score,
                )
                results.append(chunk)

            return results
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            raise VectorStorageError(f"Vector search failed: {str(e)}") from e

    def delete_document_chunks(self, document_id: str) -> None:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest_models.Filter(
                    must=[
                        rest_models.FieldCondition(
                            key="document_id",
                            match=rest_models.MatchValue(value=document_id),
                        )
                    ]
                ),
            )
            logger.info(f"Deleted vector chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete document chunks in Qdrant: {e}")
            raise VectorStorageError(f"Delete chunks failed: {str(e)}") from e
