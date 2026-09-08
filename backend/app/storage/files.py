import json
import warnings
from pathlib import Path
from typing import Any
from app.core.config import Settings, get_settings
from app.models.document import DocumentMetadata
from app.core.logging import logger


class FileStorage:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.markdown_dir = Path(self.settings.markdown_dir)
        self.catalog_file = self.upload_dir / "catalog.json"

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        if self.settings.environment == "production":
            warnings.warn(
                "FileStorage is using local filesystem which is EPHEMERAL on Render Free tier. "
                "Uploaded files and markdown will be lost on service restart or sleep. "
                "Configure persistent storage (e.g., S3, GCS) for production use.",
                UserWarning,
                stacklevel=2,
            )

        self._init_catalog()

    def _init_catalog(self) -> None:
        if not self.catalog_file.exists():
            self._save_catalog({})

    def _load_catalog(self) -> dict[str, dict[str, Any]]:
        try:
            if self.catalog_file.exists():
                return json.loads(self.catalog_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error loading document catalog: {e}")
        return {}

    def _save_catalog(self, catalog: dict[str, dict[str, Any]]) -> None:
        self.catalog_file.write_text(json.dumps(catalog, indent=2, default=str), encoding="utf-8")

    def save_document_record(self, doc: DocumentMetadata) -> None:
        catalog = self._load_catalog()
        catalog[doc.id] = {
            "id": doc.id,
            "filename": doc.filename,
            "original_path": doc.original_path,
            "markdown_path": doc.markdown_path,
            "file_type": doc.file_type,
            "size_bytes": doc.size_bytes,
            "chunk_count": doc.chunk_count,
            "created_at": doc.created_at.isoformat(),
            "status": doc.status,
            "error_message": doc.error_message,
        }
        self._save_catalog(catalog)

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        catalog = self._load_catalog()
        return catalog.get(document_id)

    def list_documents(self) -> list[dict[str, Any]]:
        catalog = self._load_catalog()
        return sorted(list(catalog.values()), key=lambda d: d.get("created_at", ""), reverse=True)

    def delete_document(self, document_id: str) -> bool:
        catalog = self._load_catalog()
        if document_id in catalog:
            doc = catalog.pop(document_id)
            self._save_catalog(catalog)
            # Remove files if exist
            for p_key in ["original_path", "markdown_path"]:
                path_str = doc.get(p_key)
                if path_str:
                    p = Path(path_str)
                    if p.exists():
                        try:
                            p.unlink()
                        except Exception as e:
                            logger.warning(f"Failed to delete file {p}: {e}")
            return True
        return False
