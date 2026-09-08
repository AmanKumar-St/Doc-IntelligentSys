import shutil
import uuid
from pathlib import Path
from app.core.config import Settings, get_settings
from app.core.exceptions import DocumentParsingError
from app.core.logging import logger
from app.ingestion.chunker import MarkdownChunker
from app.ingestion.parser import DocumentParser
from app.models.document import DocumentMetadata
from app.providers.embeddings.factory import create_embedding_provider
from app.storage.files import FileStorage
from app.storage.qdrant import QdrantStorage


class IngestionService:
    def __init__(
        self,
        settings: Settings | None = None,
        parser: DocumentParser | None = None,
        chunker: MarkdownChunker | None = None,
        qdrant: QdrantStorage | None = None,
        files: FileStorage | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.parser = parser or DocumentParser()
        self.chunker = chunker or MarkdownChunker(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        self.embedding_provider = create_embedding_provider(self.settings)
        self.qdrant = qdrant or QdrantStorage(self.settings)
        self.files = files or FileStorage(self.settings)

    async def ingest_file(self, file_path: Path | str, original_filename: str | None = None) -> DocumentMetadata:
        source_path = Path(file_path)
        filename = original_filename or source_path.name
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        target_upload_path = Path(self.settings.upload_dir) / f"{doc_id}_{filename}"
        if source_path != target_upload_path:
            shutil.copy2(source_path, target_upload_path)

        doc_meta = DocumentMetadata(
            id=doc_id,
            filename=filename,
            original_path=str(target_upload_path),
            markdown_path="",
            file_type=target_upload_path.suffix.lower(),
            size_bytes=target_upload_path.stat().st_size,
            status="parsing",
        )
        self.files.save_document_record(doc_meta)

        try:
            # 1. Parse document to Markdown via MarkItDown
            logger.info(f"Parsing document {filename} ({doc_id})...")
            markdown_content = self.parser.parse(target_upload_path)
            
            # Save normalized markdown
            md_file_path = Path(self.settings.markdown_dir) / f"{doc_id}.md"
            md_file_path.write_text(markdown_content, encoding="utf-8")
            doc_meta.markdown_path = str(md_file_path)
            doc_meta.status = "chunking"
            self.files.save_document_record(doc_meta)

            # 2. Markdown-aware chunking
            logger.info(f"Chunking document {filename}...")
            chunks = self.chunker.chunk_document(
                markdown_text=markdown_content,
                document_id=doc_id,
                source=filename,
            )
            if not chunks:
                raise ValueError("No chunks generated from document")

            # 3. Generate embeddings
            doc_meta.status = "parsing"
            self.files.save_document_record(doc_meta)
            logger.info(f"Generating embeddings for {len(chunks)} chunks via {self.settings.embedding_provider}...")
            texts_to_embed = [c.text for c in chunks]
            vectors = await self.embedding_provider.embed(texts_to_embed)

            # 4. Upsert to Qdrant vector storage
            logger.info(f"Storing vectors in Qdrant collection '{self.settings.qdrant_collection}'...")
            self.qdrant.upsert_chunks(chunks=chunks, vectors=vectors)

            doc_meta.chunk_count = len(chunks)
            doc_meta.status = "embedded"
            self.files.save_document_record(doc_meta)
            logger.info(f"Successfully ingested {filename}: {len(chunks)} chunks embedded.")
            return doc_meta

        except Exception as e:
            logger.error(f"Ingestion failed for {filename}: {e}")
            doc_meta.status = "error"
            doc_meta.error_message = str(e)
            self.files.save_document_record(doc_meta)
            raise

    def delete_document(self, document_id: str) -> bool:
        self.qdrant.delete_document_chunks(document_id)
        return self.files.delete_document(document_id)
