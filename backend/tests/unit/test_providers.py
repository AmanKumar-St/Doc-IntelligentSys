import pytest
from app.providers.embeddings.mock import MockEmbeddingProvider
from app.providers.generation.mock import MockGenerationProvider
from app.providers.reranking.mock import MockRerankerProvider
from app.models.chunk import Chunk


@pytest.mark.asyncio
async def test_mock_embedding_provider():
    provider = MockEmbeddingProvider(dimension=128)
    texts = ["Hello world", "Document intelligence RAG"]
    vectors = await provider.embed(texts)
    
    assert len(vectors) == 2
    assert len(vectors[0]) == 128
    assert len(vectors[1]) == 128


@pytest.mark.asyncio
async def test_mock_generation_provider():
    provider = MockGenerationProvider()
    messages = [
        {"role": "system", "content": "RAG system"},
        {"role": "user", "content": "Context: [C1] Annual leave is 20 days. Question: What is leave?"}
    ]
    response = await provider.generate(messages)
    assert "[C1]" in response
    assert len(response) > 10


@pytest.mark.asyncio
async def test_mock_reranker():
    reranker = MockRerankerProvider()
    chunks = [
        Chunk(id="1", document_id="d1", text="Unrelated text about weather", source="a.txt", score=0.9),
        Chunk(id="2", document_id="d1", text="Specific policy about employee leave", source="b.txt", score=0.5),
    ]
    reranked = await reranker.rerank(query="employee leave", chunks=chunks, top_k=2)
    assert reranked[0].id == "2"
