import asyncio
import sys
import time
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.config import get_settings
from app.ingestion.service import IngestionService
from app.retrieval.service import RetrievalService
from app.generation.service import GenerationService
from app.storage.files import FileStorage
from app.storage.qdrant import QdrantStorage


BENCHMARK_QUESTIONS = [
    {
        "question": "How many days of annual leave are employees allocated and what is the carryover policy?",
        "expected_source": "employee_handbook.docx",
    },
    {
        "question": "What is the monthly internet subsidy allowance?",
        "expected_source": "employee_handbook.docx",
    },
    {
        "question": "What header format is required for authentication in the Cloud API?",
        "expected_source": "cloud_api_guide.pdf",
    },
    {
        "question": "What rate limit is enforced on the standard tier and what status code is returned when exceeded?",
        "expected_source": "cloud_api_guide.pdf",
    },
    {
        "question": "What was the Q3 ARR and the Enterprise SaaS YoY growth rate?",
        "expected_source": "q3_financial_report.md",
    },
]


async def run_benchmark():
    settings = get_settings()
    print("=" * 70)
    print("DOCUMENT INTELLIGENCE - RAG BENCHMARK & EVALUATION SUITE")
    print(f"Embedding Provider : {settings.embedding_provider} ({settings.embedding_model})")
    print(f"Generation Provider: {settings.generation_provider} ({settings.generation_model})")
    print(f"Reranker Provider  : {settings.reranker_provider} ({settings.reranker_model})")
    print("=" * 70)

    qdrant = QdrantStorage(settings)
    files = FileStorage(settings)
    ingestion = IngestionService(settings=settings, qdrant=qdrant, files=files)
    retrieval = RetrievalService(settings=settings, qdrant=qdrant)
    generation = GenerationService(settings=settings)

    # 1. Ingestion Phase
    sample_dir = Path("data/uploads")
    docs_to_ingest = [
        sample_dir / "employee_handbook.docx",
        sample_dir / "cloud_api_guide.pdf",
        sample_dir / "q3_financial_report.md",
    ]

    print("\n--- PHASE 1: INGESTION ---")
    for doc_path in docs_to_ingest:
        if doc_path.exists():
            start_t = time.perf_counter()
            meta = await ingestion.ingest_file(doc_path, original_filename=doc_path.name)
            elapsed = time.perf_counter() - start_t
            print(f"[OK] Ingested '{meta.filename}' -> {meta.chunk_count} chunks in {elapsed:.2f}s (Status: {meta.status})")

    # 2. Retrieval & Generation Evaluation
    print("\n--- PHASE 2: RETRIEVAL & GROUNDED CITATION EVALUATION ---")
    total_latency = 0.0
    passed_citations = 0
    total_questions = len(BENCHMARK_QUESTIONS)

    for i, item in enumerate(BENCHMARK_QUESTIONS, start=1):
        q = item["question"]
        expected_src = item["expected_source"]
        
        print(f"\n[Q{i}] Question: {q}")
        start_q = time.perf_counter()
        
        chunks = await retrieval.retrieve(q)
        ans, citations, provider, model, status = await generation.answer_question(q, chunks)
        latency = time.perf_counter() - start_q
        total_latency += latency

        retrieved_sources = [c.source for c in chunks]
        source_hit = any(expected_src.lower() in s.lower() for s in retrieved_sources)

        print(f"     Answer: {ans[:160]}...")
        print(f"     Citations ({len(citations)}): {[f'[{c.id}] {c.source}' for c in citations]}")
        print(f"     Validation Status: {status} | Latency: {latency:.2f}s | Source Hit: {'YES' if source_hit else 'NO'}")

        if status == "valid" and citations:
            passed_citations += 1

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print(f"Total Questions Evaluated : {total_questions}")
    print(f"Average Turn Latency      : {total_latency / total_questions:.2f}s")
    print(f"Citation Faithful Score   : {(passed_citations / total_questions) * 100:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
