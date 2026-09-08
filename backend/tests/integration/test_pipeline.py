import pytest
from pathlib import Path
from app.core.config import Settings
from app.ingestion.service import IngestionService
from app.retrieval.service import RetrievalService
from app.generation.service import GenerationService
from app.storage.files import FileStorage
from app.storage.qdrant import QdrantStorage


@pytest.fixture
def test_settings(tmp_path):
    return Settings(
        embedding_provider="mock",
        generation_provider="mock",
        reranker_provider="mock",
        embedding_dimension=128,
        upload_dir=str(tmp_path / "uploads"),
        markdown_dir=str(tmp_path / "markdown"),
        qdrant_storage_path=str(tmp_path / "qdrant_test_db"),
        use_embedded_qdrant=True,
    )


@pytest.mark.asyncio
async def test_end_to_end_pipeline(test_settings, tmp_path):
    # 1. Create a sample document
    sample_file = tmp_path / "employee_handbook.md"
    sample_file.write_text(
        """# Acme Corp Employee Handbook

## Annual Leave Policy
Employees in full-time employment receive 25 days of paid annual leave per calendar year.
Leave requests should be submitted at least two weeks in advance.

## Health and Dental Benefits
Acme Corp provides comprehensive medical, dental, and vision insurance coverage starting day one.
""",
        encoding="utf-8",
    )

    qdrant = QdrantStorage(test_settings)
    files = FileStorage(test_settings)
    ingestion = IngestionService(settings=test_settings, qdrant=qdrant, files=files)
    retrieval = RetrievalService(settings=test_settings, qdrant=qdrant)
    generation = GenerationService(settings=test_settings)

    # 2. Ingest document
    doc_meta = await ingestion.ingest_file(sample_file, "employee_handbook.md")
    assert doc_meta.status == "embedded"
    assert doc_meta.chunk_count >= 2

    # 3. Retrieve chunks for a query
    chunks = await retrieval.retrieve("How many days of paid annual leave do employees get?")
    assert len(chunks) > 0
    assert chunks[0].citation_id == "C1"

    # 4. Generate answer and validate citations
    answer, citations, provider, model, status = await generation.answer_question(
        question="How many days of paid annual leave do employees get?",
        context_chunks=chunks,
    )

    assert len(answer) > 0
    assert len(citations) > 0
    assert citations[0].id == "C1"
    assert citations[0].source == "employee_handbook.md"
