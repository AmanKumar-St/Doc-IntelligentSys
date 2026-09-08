import pytest
from app.core.config import Settings
from app.generation.tasks.models import TaskRequest, TaskType
from app.generation.tasks.router import TaskRouter
from app.retrieval.service import RetrievalService
from app.storage.qdrant import QdrantStorage


@pytest.fixture
def mock_router(tmp_path):
    settings = Settings(
        embedding_provider="mock",
        generation_provider="mock",
        reranker_provider="mock",
        embedding_dimension=128,
        upload_dir=str(tmp_path / "uploads"),
        markdown_dir=str(tmp_path / "markdown"),
        qdrant_storage_path=str(tmp_path / "qdrant_router_test"),
        use_embedded_qdrant=True,
    )
    qdrant = QdrantStorage(settings)
    retrieval = RetrievalService(settings, qdrant=qdrant)
    return TaskRouter(settings, retrieval_service=retrieval)


def test_resolve_multi_turn_query(mock_router):
    history = [
        {"role": "user", "content": "What is the annual leave allocation for employees?"},
        {"role": "assistant", "content": "Employees get 22 days of annual leave [C1]."},
    ]
    resolved = mock_router.resolve_multi_turn_query("How much can be carried over?", history)
    assert "annual leave" in resolved.lower()
    assert "carried over" in resolved.lower()


@pytest.mark.asyncio
async def test_execute_task_qa(mock_router):
    req = TaskRequest(
        task_type=TaskType.QA,
        instruction="What is the company policy?",
    )
    resp = await mock_router.execute_task(req)
    assert resp.task_type == TaskType.QA
    assert resp.validation.status in ["valid", "partial"]
    assert len(resp.answer) > 0


@pytest.mark.asyncio
async def test_execute_task_classification(mock_router):
    req = TaskRequest(
        task_type=TaskType.CLASSIFICATION,
        instruction="Classify this document",
        allowed_categories=["HR Policy", "Financial Report", "Other"],
    )
    resp = await mock_router.execute_task(req)
    assert resp.task_type == TaskType.CLASSIFICATION
    assert resp.validation.structure_valid is True
