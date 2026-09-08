# AI-Powered Generative Content & Document Intelligence Platform

A production-grade, end-to-end **Generative Content & Document Intelligence Platform** built with Python (FastAPI), React + TypeScript (Vite), Microsoft MarkItDown, Qdrant Vector Storage, and OpenRouter / CodeCraft LLM/Embedding provider abstractions.

The platform provides multi-format document ingestion, dense vector retrieval with reranking, deterministic task routing across **5 Generative Task Modes** (`qa`, `summarization`, `extraction`, `classification`, `generation`), a multi-turn context query rewriter, deterministic citation & output validation, and an automated evaluation benchmark suite.

---

## 📋 Internship Requirement Coverage Matrix

| Requirement Area | Specification / Objective | Implementation Component / File | Verification & Test Coverage | Demo Notebook Location |
| :--- | :--- | :--- | :--- | :--- |
| **1. RAG Architecture** | Modular RAG pipeline, dense embeddings, hybrid reranker, provider abstraction | [`backend/app/retrieval/service.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/retrieval/service.py)<br>[`backend/app/providers/adapters.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/providers/adapters.py) | `pytest backend/tests/integration/test_pipeline.py`<br>`pytest backend/tests/unit/test_providers.py` | Cells 4, 7 |
| **2. Multi-Format Ingestion** | Microsoft MarkItDown conversion (`.pdf`, `.docx`, `.pptx`, `.md`), hierarchical markdown chunker | [`backend/app/ingestion/service.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/ingestion/service.py)<br>[`backend/app/ingestion/chunker.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/ingestion/chunker.py) | `pytest backend/tests/unit/test_chunker.py` | Cells 3, 5 |
| **3. Vector DB Storage** | Qdrant vector database (Docker or zero-dependency Local Embedded fallback) | [`backend/app/storage/qdrant.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/storage/qdrant.py) | `pytest backend/tests/integration/test_pipeline.py` | Cell 4 |
| **4. Generative AI Task Modes** | Support for 5 modes: `qa`, `summarization`, `extraction`, `classification`, `generation` | [`backend/app/generation/prompts/`](file:///e:/Projects/DocIntelligentSystem/backend/app/generation/prompts)<br>[`backend/app/generation/tasks/router.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/generation/tasks/router.py) | `pytest backend/tests/unit/test_prompts.py`<br>`pytest backend/tests/unit/test_task_router.py` | Cells 7, 8, 9, 10, 11 |
| **5. Task Router & Query Rewriting** | Task mode dispatch, multi-turn pronoun/entity query resolution across conversation turns | [`backend/app/generation/tasks/router.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/generation/tasks/router.py)<br>[`backend/app/api/routes/tasks.py`](file:///e:/Projects/DocIntelligentSystem/backend/app/api/routes/tasks.py) | `pytest backend/tests/unit/test_task_router.py::test_resolve_multi_turn_query` | Cell 12 |
| **6. Output & Citation Validation** | Deterministic citation validation (`[C1]`), JSON schema parsing, numerical grounding check | [`backend/app/generation/validation/`](file:///e:/Projects/DocIntelligentSystem/backend/app/generation/validation) | `pytest backend/tests/unit/test_validation.py`<br>`pytest backend/tests/unit/test_citations.py` | Cells 7 - 11 |
| **7. Evaluation Benchmark** | Evaluation benchmark measuring Retrieval Relevance, Answer Relevance, Factuality, Citation Validity | [`scripts/evaluate_system.py`](file:///e:/Projects/DocIntelligentSystem/scripts/evaluate_system.py)<br>[`data/evaluation/evaluation_cases.json`](file:///e:/Projects/DocIntelligentSystem/data/evaluation/evaluation_cases.json) | `python scripts/evaluate_system.py` | Cell 13 |
| **8. React Frontend UI** | Modern UI with task mode controls, parameter sliders, structured JSON viewer, validation badges | [`frontend/src/components/TaskControls.tsx`](file:///e:/Projects/DocIntelligentSystem/frontend/src/components/TaskControls.tsx)<br>[`frontend/src/components/MessageItem.tsx`](file:///e:/Projects/DocIntelligentSystem/frontend/src/components/MessageItem.tsx) | `npm run build` (clean Vite build) | Interactive web UI (`http://localhost:5173`) |
| **9. Demonstration Notebook** | Executable 13+ cell demonstration notebook with stored outputs showing end-to-end execution | [`notebooks/Document_Intelligence_Demo.ipynb`](file:///e:/Projects/DocIntelligentSystem/notebooks/Document_Intelligence_Demo.ipynb) | Executed via `scripts/execute_notebook.py` | Full visual demonstration |

---

## 🏛️ System Architecture

```
[ Multi-Format Files (.pdf, .docx, .md, .pptx) ]
                       │
                       ▼
            [ Microsoft MarkItDown ]
                       │
                       ▼
       [ Markdown-Aware Hierarchical Chunker ]
                       │ (Headers, tables, citation tags [C1], [C2])
                       ▼
      [ Embedding Provider Abstraction ] (OpenRouter / CodeCraft)
                       │
                       ▼
    [ Qdrant Vector Storage ] (Local Embedded ./data/qdrant_db or Remote Docker)
                       │
                       ▼
          [ Task Router & Query Rewriter ] ◄── Multi-Turn Conversation History
                       │ (Resolves pronouns / context across turns)
                       ▼
   ┌───────────────────┴─────────────────────────────────────────┐
   │ Generative Task Prompt Engine                               │
   │  ├─ QA Prompt Mode (Source-grounded & cited)               │
   │  ├─ Summarization Mode (Executive, bullet, technical)     │
   │  ├─ Structured Extraction Mode (JSON schema target fields) │
   │  ├─ Classification Mode (Allowed categories & confidence)   │
   │  └─ Content Generation Mode (Memos, reports, emails)       │
   └───────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
   [ Deterministic Output & Citation Validation Engine ]
       ├─ Citation Validator (Verifies [C1] matches retrieved chunks)
       ├─ Structure Validator (Ensures strict JSON syntax & schema)
       ├─ Factuality Validator (Numerical grounding & claim audit)
                       │
                       ▼
 [ React + TypeScript Web Interface & FastAPI REST API ]
```

---

## ✨ Key Capabilities

1. **Task Router & Multi-Turn Query Rewriter**:
   - Automatically detects user intent or routes explicit task requests (`qa`, `summarization`, `extraction`, `classification`, `generation`).
   - Rewrites context-dependent queries (e.g., *"How much can be carried over?"* -> *"the annual leave policy for employees - How much can be carried over?"*) before running vector search.

2. **5 Specialized Generative Task Modes**:
   - **QA Mode**: Returns concise answers with strict `[C1]` inline citations.
   - **Summarization Mode**: Produces executive, bulleted, or technical summaries with section tags.
   - **Extraction Mode**: Extracts typed key-value pairs in strict JSON matching requested `target_fields`.
   - **Classification Mode**: Categorizes document content into `allowed_categories` with a normalized confidence score (0.0 - 1.0) and reasoning.
   - **Generation Mode**: Drafts formal executive memos, policy updates, release notes, or emails grounded in document context.

3. **Deterministic Output & Citation Validation Engine**:
   - Validates inline `[C1]` tags against retrieved context chunk IDs, stripping hallucinated tags.
   - Ensures structured JSON responses conform to target fields.
   - Audits numerical quantities, currency figures, and percentages against source text for factual grounding.

4. **Dual Vector Storage Modes**:
   - Runs out-of-the-box with **Local Embedded Qdrant** (`USE_EMBEDDED_QDRANT=true`) stored in `./data/qdrant_db` with zero external database installation required.
   - Supports remote Qdrant Docker instances (`http://localhost:6333`).

5. **Automated Evaluation Benchmark Framework**:
   - Evaluates system performance across 13 standardized test cases in `data/evaluation/evaluation_cases.json`.
   - Computes aggregate metrics for Retrieval Relevance, Answer Relevance, Factuality, Citation Validity, Consistency, and Latency.

---

## 🚀 Quickstart Guide

### 1. Environment Configuration

```bash
# 1. Activate Python virtual environment
.\.venv\Scripts\activate

# 2. Configure .env file
# (OpenRouter API key or CodeCraft key is pre-configured in .env)
```

### 2. Start Backend API Server

```bash
# Start FastAPI backend at http://localhost:8000
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
or if virtual environment exist
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Interactive API documentation available at `http://localhost:8000/docs`.

### 3. Start React Frontend UI

```bash
cd frontend
npm install
npm run dev
```
Interactive Web UI available at `http://localhost:5173`.

---

## 🧪 Testing & Evaluation

### Run Pytest Suite (26 Unit & Integration Tests)
```bash
.\.venv\Scripts\pytest.exe -v
```

### Run Full System Evaluation Benchmark
```bash
.\.venv\Scripts\python.exe scripts/evaluate_system.py
```
Benchmark report is written to `data/evaluation/evaluation_results.json`.

---

## 📓 Demonstration Notebook

The repository contains a complete, self-contained demonstration notebook:
- **Location**: [`notebooks/Document_Intelligence_Demo.ipynb`](file:///e:/Projects/DocIntelligentSystem/notebooks/Document_Intelligence_Demo.ipynb)
- **Contents**: 13 code cells demonstrating setup, document ingestion, vector retrieval, all 5 task modes, multi-turn query rewriting, citation validation, and benchmark execution with outputs pre-rendered directly in the notebook file.
