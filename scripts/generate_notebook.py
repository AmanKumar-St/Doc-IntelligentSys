import json
from pathlib import Path


def build_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "language_info": {"name": "python", "version": "3.12.12"},
            "kernelspec": {"display_name": "Python 3.12", "language": "python", "name": "python3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    def add_md(source):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": source.strip().splitlines(keepends=True),
        })

    def add_code(source):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source.strip().splitlines(keepends=True),
        })

    # CELL 1
    add_md("""
# AI-Powered Generative Content & Document Intelligence Platform
### Internship Submission & Architectural Demonstration Notebook

**Platform Overview & Architecture:**
This platform is a modular **Document Intelligence and Generative Content** system built with Python 3.12, FastAPI, Qdrant vector storage, Microsoft MarkItDown, and flexible LLM provider abstractions (OpenRouter, CodeCraft, UnoRouter).

**Key Modules Demonstrated:**
1. **Multi-Format Document Ingestion**: Parsing PDF, DOCX, Markdown via Microsoft MarkItDown.
2. **Hierarchy-Preserving Chunking**: Structural Markdown chunker tracking header paths (`# Doc > ## Section`), table boundaries, and character offsets.
3. **Provider-Abstracted Dense Vector Retrieval & Reranking**: Qdrant vector store with cross-encoder reranking.
4. **5 Generative AI Task Modes**:
   - `qa`: Grounded Question Answering with bracket citations `[C1]`, `[C2]`.
   - `summarization`: Concise, detailed, and key-points structured summaries.
   - `extraction`: Strict JSON field extraction with explicit `null` for missing facts.
   - `classification`: Category classification strictly constrained to user-provided allowed lists.
   - `generation`: Deliverable content generation (emails, reports, memos) separating user requirements from source context facts.
5. **Context-Aware Multi-Step Workflow**: Resolving referential pronouns across multi-turn user conversations.
6. **Deterministic Output & Factuality Validation Engine**: Structural JSON verification, citation validation, and numerical/lexical factuality checking.
7. **Automated Evaluation Framework**: Metric calculation across retrieval relevance, answer relevance, factuality, consistency, and citation validity.
""")

    # CELL 2
    add_code("""
import sys
import os
import json
import asyncio
from pathlib import Path
import pandas as pd

# Add backend to Python path
sys.path.insert(0, str(Path.cwd().parent / "backend") if Path.cwd().name == "notebooks" else str(Path.cwd() / "backend"))

from app.core.config import get_settings
from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import MarkdownChunker
from app.ingestion.service import IngestionService
from app.storage.qdrant import QdrantStorage
from app.storage.files import FileStorage
from app.retrieval.service import RetrievalService
from app.generation.tasks.router import TaskRouter
from app.generation.tasks.models import TaskRequest, TaskType
from app.generation.validation import ValidationService, CitationValidator, FactualityValidator, StructureValidator

settings = get_settings()
print(f"App Name           : {settings.app_name}")
print(f"Environment        : {settings.environment}")
print(f"Embedding Provider : {settings.embedding_provider} ({settings.embedding_model})")
print(f"Generation Provider: {settings.generation_provider} ({settings.generation_model})")
print(f"Vector Store Mode  : {'Embedded Local Storage' if settings.use_embedded_qdrant else 'Remote Qdrant'}")
""")

    # CELL 3
    add_md("""
## 1. Document Ingestion & MarkItDown Parsing
Demonstrating multi-format document conversion (`.docx`, `.pdf`, `.md`) into clean, structured Markdown using Microsoft **MarkItDown**.
""")

    # CELL 4
    add_code("""
parser = DocumentParser()

data_dir = Path("../data/uploads") if Path.cwd().name == "notebooks" else Path("data/uploads")
sample_docx = data_dir / "employee_handbook.docx"
sample_pdf = data_dir / "cloud_api_guide.pdf"

if sample_docx.exists():
    md_docx = parser.parse(sample_docx)
    print("=== MARKDOWN PARSED FROM EMPLOYEE_HANDBOOK.DOCX ===")
    print(md_docx[:600] + "\n...\n")

if sample_pdf.exists():
    md_pdf = parser.parse(sample_pdf)
    print("=== MARKDOWN PARSED FROM CLOUD_API_GUIDE.PDF ===")
    print(md_pdf[:600] + "\n...\n")
""")

    # CELL 5
    add_md("""
## 2. Hierarchy-Preserving Markdown Chunking
Splitting parsed document Markdown into semantic chunks while capturing section heading paths (`["Apex Global", "1. Paid Time Off"]`), source metadata, and character bounds.
""")

    # CELL 6
    add_code("""
chunker = MarkdownChunker(chunk_size=500, chunk_overlap=80)
sample_md_file = data_dir / "q3_financial_report.md"

if sample_md_file.exists():
    raw_md = sample_md_file.read_text(encoding="utf-8")
    chunks = chunker.chunk_document(raw_md, document_id="doc_demo_fin", source="q3_financial_report.md")

    print(f"Total Chunks Generated: {len(chunks)}\n")
    for idx, c in enumerate(chunks, start=1):
        print(f"Chunk [{idx}] | ID: {c.id}")
        print(f"  Heading Path: {c.heading_path}")
        print(f"  Section     : {c.section}")
        print(f"  Text Snippet: {c.text[:150]}...")
        print("-" * 60)
""")

    # CELL 7
    add_md("""
## 3. Vector Embedding & Qdrant Vector Storage
Upserting dense vector embeddings into Qdrant collection with deterministic MD5 point identifiers.
""")

    # CELL 8
    add_code("""
qdrant = QdrantStorage(settings)
files = FileStorage(settings)
ingestion = IngestionService(settings=settings, qdrant=qdrant, files=files)

# Ingest all evaluation documents
docs_to_ingest = ["employee_handbook.docx", "cloud_api_guide.pdf", "q3_financial_report.md"]
ingested_metadata = []

for d in docs_to_ingest:
    p = data_dir / d
    if p.exists():
        meta = await ingestion.ingest_file(p, original_filename=d)
        ingested_metadata.append(meta)
        print(f"Ingested '{meta.filename}' -> {meta.chunk_count} chunks embedded (Status: {meta.status})")

print(f"\nQdrant Collection Status: Active ({settings.qdrant_collection})")
""")

    # CELL 9
    add_md("""
## 4. Dense Retrieval & Cross-Encoder Reranking
Demonstrating dense vector search followed by cross-encoder reranking to produce precision context chunks labeled with deterministic citation IDs (`[C1]`, `[C2]`).
""")

    # CELL 10
    add_code("""
retrieval = RetrievalService(settings=settings, qdrant=qdrant)
query = "What is the monthly internet subsidy allowance for remote employees?"

chunks_retrieved = await retrieval.retrieve(query, top_k=10, rerank_top_k=4)

print(f"Query: '{query}'")
print(f"Precision Chunks Reranked: {len(chunks_retrieved)}\n")

for c in chunks_retrieved:
    print(f"[{c.citation_id}] Source: {c.source} | Score: {(c.score or 0)*100:.1f}%")
    print(f"  Heading: {' > '.join(c.heading_path)}")
    print(f"  Passage: {c.text[:180]}...\n")
""")

    # CELL 11
    add_md("""
## 5. Task Mode 1: Grounded Question Answering (QA)
Executing grounded RAG question answering with inline bracket citations `[C1]`, `[C2]`.
""")

    # CELL 12
    add_code("""
router = TaskRouter(settings=settings, retrieval_service=retrieval)

req_qa = TaskRequest(
    task_type=TaskType.QA,
    instruction="What is the annual leave allocation and what is the carryover policy?"
)

resp_qa = await router.execute_task(req_qa)

print(f"Task Mode   : {resp_qa.task_type.value.upper()}")
print(f"Provider    : {resp_qa.provider} ({resp_qa.model})")
print(f"Answer      :\n{resp_qa.answer}\n")
print(f"Citations   : {[f'[{c.id}] {c.source}' for c in resp_qa.citations]}")
print(f"Validation  : {resp_qa.validation.status.upper()} (Factuality: {resp_qa.validation.factuality_status})")
""")

    # CELL 13
    add_md("""
## 6. Task Mode 2: Structured Summarization
Executing document summarization with configurable summary styles (Concise, Detailed, Key Points) and verified citations.
""")

    # CELL 14
    add_code("""
req_sum = TaskRequest(
    task_type=TaskType.SUMMARIZATION,
    instruction="Summarize the core leave, fitness, and equipment benefits from the handbook.",
    summary_type="key_points"
)

resp_sum = await router.execute_task(req_sum)

print(f"Task Mode   : {resp_sum.task_type.value.upper()} (Style: key_points)")
print(f"Summary Output:\n{resp_sum.answer}\n")
print(f"Citations   : {[f'[{c.id}] {c.source}' for c in resp_sum.citations]}")
print(f"Validation  : {resp_sum.validation.status.upper()}")
""")

    # CELL 15
    add_md("""
## 7. Task Mode 3: Structured Information Extraction
Extracting specific entity attributes into strict JSON with explicit `null` for missing values and citation references.
""")

    # CELL 16
    add_code("""
req_ext = TaskRequest(
    task_type=TaskType.EXTRACTION,
    instruction="Extract annual leave days, carryover limit, sick leave days, and equity bonus percentage.",
    target_fields=["annual_leave_days", "carryover_limit", "sick_leave_days", "equity_bonus_pct"]
)

resp_ext = await router.execute_task(req_ext)

print(f"Task Mode   : {resp_ext.task_type.value.upper()}")
print(f"Parsed JSON Output:\n{json.dumps(resp_ext.structured_data, indent=2)}\n")
print(f"Validation  : Structure Valid: {resp_ext.validation.structure_valid} | Warnings: {resp_ext.validation.warnings}")
""")

    # CELL 17
    add_md("""
## 8. Task Mode 4: Constrained Document Classification
Classifying document context strictly into a user-provided allowed category list.
""")

    # CELL 18
    add_code("""
req_cls = TaskRequest(
    task_type=TaskType.CLASSIFICATION,
    instruction="Classify the topic of this API reference document.",
    allowed_categories=["HR Policy", "Technical Documentation", "Financial Report", "Legal Agreement"]
)

resp_cls = await router.execute_task(req_cls)

print(f"Task Mode        : {resp_cls.task_type.value.upper()}")
print(f"Classification   :\n{json.dumps(resp_cls.structured_data, indent=2)}\n")
print(f"Validation Status: {resp_cls.validation.status.upper()} (Category Constrained: {resp_cls.validation.structure_valid})")
""")

    # CELL 19
    add_md("""
## 9. Task Mode 5: Structured Content Generation
Generating deliverable content (Executive Email, Technical Memo, Report) enforcing strict boundary separation between User Requirements and Source Document Facts.
""")

    # CELL 20
    add_code("""
req_gen = TaskRequest(
    task_type=TaskType.GENERATION,
    instruction="Generate an executive performance briefing email summarizing Q3 revenue, ARR, and gross profit margins.",
    output_format="email"
)

resp_gen = await router.execute_task(req_gen)

print(f"Task Mode      : {resp_gen.task_type.value.upper()} (Format: EMAIL)")
print(f"Generated Content:\n{resp_gen.answer}\n")
print(f"Citations      : {[f'[{c.id}] {c.source}' for c in resp_gen.citations]}")
print(f"Factuality Score: {resp_gen.validation.factuality_score * 100:.1f}% ({resp_gen.validation.factuality_status})")
""")

    # CELL 21
    add_md("""
## 10. Context-Aware Multi-Step Conversation Workflow
Demonstrating multi-turn pronoun resolution ("it", "how much can be carried over") by prepending conversation context.
""")

    # CELL 22
    add_code("""
history = [
    {"role": "user", "content": "What is the annual leave policy for full-time employees?"},
    {"role": "assistant", "content": "Full-time employees receive 22 days of paid annual leave per calendar year [C1]."}
]

req_turn2 = TaskRequest(
    task_type=TaskType.QA,
    instruction="How much can be carried over into the next calendar year?",
    history=history
)

resp_turn2 = await router.execute_task(req_turn2)

print(f"User Query      : '{req_turn2.instruction}'")
print(f"Resolved Query  : '{resp_turn2.resolved_query}'")
print(f"Contextual Answer:\n{resp_turn2.answer}\n")
print(f"Citations       : {[f'[{c.id}] {c.source}' for c in resp_turn2.citations]}")
""")

    # CELL 23
    add_md("""
## 11. Deterministic Output, Citation & Factuality Validation
Demonstrating the validation engine catching invalid/hallucinated citation tags and checking numerical grounding.
""")

    # CELL 24
    add_code("""
sample_context_chunk = chunks_retrieved[0] if chunks_retrieved else None

if sample_context_chunk:
    # 1. Test citation validation & hallucination filter
    test_text_with_hallucination = "Employees receive $80 monthly subsidy [C1] and $5,000 bonus stipend [C99]."
    cleaned, citations, status = CitationValidator.validate_and_map_citations(test_text_with_hallucination, [sample_context_chunk])
    
    print("=== CITATION HALLUCINATION FILTER TEST ===")
    print(f"Raw Input Text : '{test_text_with_hallucination}'")
    print(f"Cleaned Output : '{cleaned}'")
    print(f"Filter Status  : {status.upper()} (Invalid tag [C99] stripped)\n")

    # 2. Test factuality validator
    status_f, score_f, warns_f = FactualityValidator.check_factuality("Employees receive $80 per month.", [sample_context_chunk])
    print("=== FACTUALITY GROUNDING TEST ===")
    print(f"Factuality Status: {status_f.upper()} | Score: {score_f * 100:.1f}%")
""")

    # CELL 25
    add_md("""
## 12. Automated Evaluation Framework & Benchmark Matrix
Loading benchmark results evaluated across 13 test cases covering QA, Summarization, Extraction, Classification, Content Generation, Multi-turn Context, and Factuality.
""")

    # CELL 26
    add_code("""
eval_res_path = Path("../data/evaluation/evaluation_results.json") if Path.cwd().name == "notebooks" else Path("data/evaluation/evaluation_results.json")

if eval_res_path.exists():
    eval_data = json.loads(eval_res_path.read_text(encoding="utf-8"))
    
    print("=======================================================================")
    print("SYSTEM EVALUATION METRICS SUMMARY")
    print("=======================================================================")
    print(f"Total Test Cases Evaluated : {eval_data['total_tests']}")
    print(f"Retrieval Relevance        : {eval_data['retrieval_relevance_pct']}%")
    print(f"Answer Relevance           : {eval_data['answer_relevance_pct']}%")
    print(f"Factuality Score           : {eval_data['factuality_pct']}%")
    print(f"Consistency Score          : {eval_data['consistency_pct']}%")
    print(f"Citation Validity          : {eval_data['citation_validity_pct']}%")
    print(f"Overall Benchmark Pass     : {eval_data['overall_pass_pct']}%")
    print(f"Average Latency            : {eval_data['avg_latency_sec']}s")
    print("=======================================================================\n")

    # Render Pandas DataFrame Table
    df = pd.DataFrame(eval_data["results"])
    display(df[["test_id", "task", "question", "expected_source", "relevance", "factuality", "consistency", "citation_valid", "overall_pass", "latency_sec"]])
else:
    print("Run `python scripts/evaluate_system.py` to generate the evaluation dataset.")
""")

    # CELL 27
    add_md("""
## 13. Internship Requirements Coverage & Conclusion

| Requirement Area | Platform Capability & Module | Verification Evidence | Status |
| :--- | :--- | :--- | :--- |
| **Generative AI** | 5 Task Modes (`qa`, `summarization`, `extraction`, `classification`, `generation`) | `TaskRouter` & `app/generation/prompts/` | **COMPLETE** |
| **Prompt Engineering** | Task-specific prompt builders with citation constraints | `backend/app/generation/prompts/` | **COMPLETE** |
| **Document Intelligence** | Microsoft MarkItDown ingestion & MarkdownChunker | `backend/app/ingestion/` | **COMPLETE** |
| **Retrieval & Reranking** | Qdrant vector store + cross-encoder reranking | `backend/app/storage/qdrant.py` & `retrieval/` | **COMPLETE** |
| **Context-Aware Workflow** | Multi-turn pronoun resolution query rewriting | `TaskRouter.resolve_multi_turn_query` | **COMPLETE** |
| **Output & Quality Checks** | JSON structure, category constraints, citation validation, factuality checking | `backend/app/generation/validation/` | **COMPLETE** |
| **Evaluation Framework** | Automated metric calculation across 13 test cases | `scripts/evaluate_system.py` & `data/evaluation/` | **COMPLETE** |
| **Full-Stack Interface** | React + TypeScript + Vite UI with Citation Inspector & Task Controls | `frontend/src/` | **COMPLETE** |
| **Python Submission** | Executable Python demonstration notebook | `notebooks/Document_Intelligence_Demo.ipynb` | **COMPLETE** |
""")

    out_dir = Path("notebooks")
    out_dir.mkdir(parents=True, exist_ok=True)
    nb_path = out_dir / "Document_Intelligence_Demo.ipynb"
    nb_path.write_text(json.dumps(nb, indent=2), encoding="utf-8")
    print(f"Created notebook at {nb_path}")


if __name__ == "__main__":
    build_notebook()
