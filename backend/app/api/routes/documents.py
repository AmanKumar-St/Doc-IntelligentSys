import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.dependencies import get_ingestion_service, get_file_storage
from app.ingestion.service import IngestionService
from app.storage.files import FileStorage
from app.schemas.documents import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.core.logging import logger

router = APIRouter()


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Sanitize filename to prevent path traversal
    safe_filename = Path(file.filename).name.replace("..", "").replace("/", "").replace("\\", "").strip()
    if not safe_filename:
        safe_filename = "uploaded_document"

    temp_dir = Path("./data/uploads/tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / safe_filename

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_meta = await ingestion_service.ingest_file(
            file_path=temp_path,
            original_filename=file.filename,
        )

        return DocumentUploadResponse(
            document_id=doc_meta.id,
            filename=doc_meta.filename,
            status=doc_meta.status,
            message="Document uploaded and indexed successfully",
            chunk_count=doc_meta.chunk_count,
        )
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}") from e
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    files: FileStorage = Depends(get_file_storage),
):
    docs = files.list_documents()
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=d["id"],
                filename=d["filename"],
                file_type=d["file_type"],
                size_bytes=d["size_bytes"],
                chunk_count=d.get("chunk_count", 0),
                created_at=d["created_at"],
                status=d.get("status", "embedded"),
                error_message=d.get("error_message"),
            )
            for d in docs
        ],
        total=len(docs),
    )


@router.get("/{document_id}")
async def get_document_details(
    document_id: str,
    files: FileStorage = Depends(get_file_storage),
):
    doc = files.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Read markdown snippet if available
    markdown_content = ""
    md_path = doc.get("markdown_path")
    if md_path and Path(md_path).exists():
        try:
            markdown_content = Path(md_path).read_text(encoding="utf-8")
        except Exception:
            pass

    return {**doc, "markdown_preview": markdown_content[:5000]}


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    success = ingestion_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {document_id} deleted successfully"}
