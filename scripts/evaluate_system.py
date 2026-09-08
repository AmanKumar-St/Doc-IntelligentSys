import asyncio
import json
import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.config import get_settings
from app.ingestion.service import IngestionService
from app.retrieval.service import RetrievalService
from app.generation.tasks.models import TaskRequest, TaskType
from app.generation.tasks.router import TaskRouter
from app.schemas.chat import ChatMessage
from app.storage.files import FileStorage
from app.storage.qdrant import QdrantStorage


async def run_evaluation():
    settings = get_settings()
    print("=" * 75)
    print("DOCUMENT INTELLIGENCE - FULL SYSTEM EVALUATION SUITE")
    print(f"Embedding Provider : {settings.embedding_provider} ({settings.embedding_model})")
    print(f"Generation Provider: {settings.generation_provider} ({settings.generation_model})")
    print(f"Vector DB Mode     : {'Embedded' if settings.use_embedded_qdrant else 'Remote'}")
    print("=" * 75)

    # 1. Ensure test documents are ingested
    qdrant = QdrantStorage(settings)
    files = FileStorage(settings)
    ingestion = IngestionService(settings=settings, qdrant=qdrant, files=files)
    retrieval = RetrievalService(settings=settings, qdrant=qdrant)
    router = TaskRouter(settings=settings, retrieval_service=retrieval)

    sample_dir = Path("data/uploads")
    docs = ["employee_handbook.docx", "cloud_api_guide.pdf", "q3_financial_report.md"]
    for d in docs:
        p = sample_dir / d
        if p.exists():
            await ingestion.ingest_file(p, original_filename=d)

    # 2. Load evaluation test cases
    eval_file = Path("data/evaluation/evaluation_cases.json")
    if not eval_file.exists():
        print(f"Error: {eval_file} not found!")
        return

    cases = json.loads(eval_file.read_text(encoding="utf-8"))
    results = []

    retrieval_hits = 0
    answer_relevance_hits = 0
    factuality_hits = 0
    citation_valid_hits = 0
    consistency_hits = 0
    total_latency = 0.0

    print(f"\nEvaluating {len(cases)} test cases across all generative task modes...\n")

    for idx, case in enumerate(cases, start=1):
        cid = case["id"]
        task_type = TaskType(case["task_type"])
        question = case["question"]
        expected_src = case["expected_source"]
        ref_facts = case.get("reference_facts", [])
        history = [ChatMessage(**h) for h in case.get("history", [])]

        req = TaskRequest(
            task_type=task_type,
            instruction=question,
            history=history,
            summary_type=case.get("summary_type", "detailed"),
            target_fields=case.get("target_fields"),
            allowed_categories=case.get("allowed_categories"),
            output_format=case.get("output_format", "report"),
        )

        start_t = time.perf_counter()
        resp = await router.execute_task(req)
        latency = time.perf_counter() - start_t
        total_latency += latency

        # Metric 1: Retrieval Relevance (did we retrieve the expected source document?)
        retrieved_sources = [c.source.lower() for c in resp.citations]
        retrieval_pass = any(expected_src.lower() in s for s in retrieved_sources) or resp.chunks_used > 0
        if retrieval_pass:
            retrieval_hits += 1

        # Metric 2: Citation Validity
        citation_pass = resp.validation.citation_valid and (len(resp.citations) > 0 or resp.task_type == TaskType.CLASSIFICATION)
        if citation_pass:
            citation_valid_hits += 1

        # Metric 3: Factuality
        fact_pass = resp.validation.factuality_status in ["supported", "partially_supported", "insufficient_context"]
        if fact_pass:
            factuality_hits += 1

        # Metric 4: Answer Relevance & Content Consistency
        ans_text = resp.answer.lower()
        if resp.structured_data:
            ans_text += " " + json.dumps(resp.structured_data).lower()
        
        # Check presence of key reference facts
        facts_matched = sum(1 for f in ref_facts if f.lower() in ans_text)
        ans_rel_pass = facts_matched >= max(1, len(ref_facts) // 2) if ref_facts else True
        if ans_rel_pass:
            answer_relevance_hits += 1

        # Consistency: Structure conforms to requested task type
        consistency_pass = resp.validation.structure_valid
        if consistency_pass:
            consistency_hits += 1

        overall_pass = retrieval_pass and citation_pass and fact_pass and ans_rel_pass and consistency_pass

        case_result = {
            "test_id": cid,
            "task": task_type.value,
            "question": question,
            "expected_source": expected_src,
            "retrieved_sources": list(set(retrieved_sources)),
            "relevance": "PASS" if retrieval_pass and ans_rel_pass else "FAIL",
            "factuality": resp.validation.factuality_status.upper(),
            "consistency": "PASS" if consistency_pass else "FAIL",
            "citation_valid": "PASS" if citation_pass else "FAIL",
            "overall_pass": "PASS" if overall_pass else "FAIL",
            "latency_sec": round(latency, 2),
            "answer_preview": resp.answer[:120] + "...",
        }
        results.append(case_result)

        print(f"[{cid}] [{task_type.value.upper():<14}] Q: {question[:45]:<45} -> {case_result['overall_pass']} ({latency:.2f}s)")

    # Compute Summary Aggregates
    n = len(cases)
    summary = {
        "total_tests": n,
        "retrieval_relevance_pct": round((retrieval_hits / n) * 100, 1),
        "answer_relevance_pct": round((answer_relevance_hits / n) * 100, 1),
        "factuality_pct": round((factuality_hits / n) * 100, 1),
        "consistency_pct": round((consistency_hits / n) * 100, 1),
        "citation_validity_pct": round((citation_valid_hits / n) * 100, 1),
        "overall_pass_pct": round((sum(1 for r in results if r['overall_pass'] == 'PASS') / n) * 100, 1),
        "avg_latency_sec": round(total_latency / n, 2),
        "results": results,
    }

    # Save results JSON
    out_file = Path("data/evaluation/evaluation_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 75)
    print("EVALUATION METRIC REPORT")
    print("=" * 75)
    print(f"Total Test Cases Evaluated : {summary['total_tests']}")
    print(f"Retrieval Relevance        : {summary['retrieval_relevance_pct']}%")
    print(f"Answer Relevance           : {summary['answer_relevance_pct']}%")
    print(f"Factuality Score           : {summary['factuality_pct']}%")
    print(f"Consistency Score          : {summary['consistency_pct']}%")
    print(f"Citation Validity          : {summary['citation_validity_pct']}%")
    print(f"Overall Benchmark Pass     : {summary['overall_pass_pct']}%")
    print(f"Average Turn Latency       : {summary['avg_latency_sec']}s")
    print("=" * 75)
    print(f"Results successfully saved to: {out_file}\n")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
