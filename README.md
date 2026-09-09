# AI-Powered Generative Content & Document Intelligence Platform

A production-grade, end-to-end **Generative Content & Document Intelligence Platform** built with Python (FastAPI), React + TypeScript (Vite), Microsoft MarkItDown, Qdrant Vector Storage, and OpenRouter / CodeCraft LLM & Embedding provider abstractions.

The platform provides multi-format document ingestion, dense vector retrieval with hybrid reranking, deterministic task routing across **5 Generative Task Modes** (`qa`, `summarization`, `extraction`, `classification`, `generation`), multi-turn context query rewriting, deterministic citation and output validation, production rate limiting, and an automated evaluation benchmark suite.

---

## 🌐 Live Deployments

| Component | Platform | URL |
| :--- | :--- | :--- |
| **Frontend Web App** | Vercel | [https://doc-intelligent-sys.vercel.app/](https://doc-intelligent-sys.vercel.app/) |
| **Backend REST API** | Render | [https://doc-intelligentsys.onrender.com](https://doc-intelligentsys.onrender.com) |
| **Interactive API Docs** | Swagger UI | [https://doc-intelligentsys.onrender.com/docs](https://doc-intelligentsys.onrender.com/docs) |
| **API Health Status** | Render | [https://doc-intelligentsys.onrender.com/api/health](https://doc-intelligentsys.onrender.com/api/health) |

---

## 📋 Internship Requirement Coverage Matrix

| Requirement Area | Specification / Objective | Implementation Component / File | Verification & Test Coverage | Demo Notebook Location |
| :--- | :--- | :--- | :--- | :--- |
| **1. RAG Architecture** | Modular RAG pipeline, dense embeddings, hybrid reranker, provider abstraction | [`backend/app/retrieval/service.py`](backend/app/retrieval/service.py)<br>[`backend/app/providers/adapters.py`](backend/app/providers/adapters.py) | `pytest backend/tests/integration/test_pipeline.py`<br>`pytest backend/tests/unit/test_providers.py` | Cells 4, 7 |
| **2. Multi-Format Ingestion** | Microsoft MarkItDown conversion (`.pdf`, `.docx`, `.pptx`, `.md`, `.xlsx`, etc.), hierarchical markdown chunker | [`backend/app/ingestion/service.py`](backend/app/ingestion/service.py)<br>[`backend/app/ingestion/chunker.py`](backend/app/ingestion/chunker.py) | `pytest backend/tests/unit/test_chunker.py` | Cells 3, 5 |
| **3. Vector DB Storage** | Qdrant vector database (Remote Qdrant Cloud or zero-dependency Local Embedded fallback) | [`backend/app/storage/qdrant.py`](backend/app/storage/qdrant.py) | `pytest backend/tests/integration/test_pipeline.py` | Cell 4 |
| **4. Generative AI Task Modes** | Support for 5 modes: `qa`, `summarization`, `extraction`, `classification`, `generation` | [`backend/app/generation/prompts/`](backend/app/generation/prompts)<br>[`backend/app/generation/tasks/router.py`](backend/app/generation/tasks/router.py) | `pytest backend/tests/unit/test_prompts.py`<br>`pytest backend/tests/unit/test_task_router.py` | Cells 7, 8, 9, 10, 11 |
| **5. Task Router & Query Rewriting** | Task mode dispatch, multi-turn pronoun/entity query resolution across conversation turns | [`backend/app/generation/tasks/router.py`](backend/app/generation/tasks/router.py)<br>[`backend/app/api/routes/tasks.py`](backend/app/api/routes/tasks.py) | `pytest backend/tests/unit/test_task_router.py::test_resolve_multi_turn_query` | Cell 12 |
| **6. Output & Citation Validation** | Deterministic citation validation (`[C1]`), JSON schema parsing, numerical grounding check | [`backend/app/generation/validation/`](backend/app/generation/validation) | `pytest backend/tests/unit/test_validation.py`<br>`pytest backend/tests/unit/test_citations.py` | Cells 7 - 11 |
| **7. Production Hardening** | In-memory sliding-window rate limiting, payload validation, unified error handlers, CORS | [`backend/app/core/rate_limiter.py`](backend/app/core/rate_limiter.py)<br>[`backend/app/core/error_handlers.py`](backend/app/core/error_handlers.py) | `pytest backend/tests/unit/test_production_features.py` | Full backend test suite |
| **8. Evaluation Benchmark** | Evaluation benchmark measuring Retrieval Relevance, Answer Relevance, Factuality, Citation Validity | [`scripts/evaluate_system.py`](scripts/evaluate_system.py)<br>[`data/evaluation/evaluation_cases.json`](data/evaluation/evaluation_cases.json) | `python scripts/evaluate_system.py` | Cell 13 |
| **9. React Frontend UI** | Modern UI with task mode controls, parameter sliders, structured JSON viewer, validation badges | [`frontend/src/components/TaskControls.tsx`](frontend/src/components/TaskControls.tsx)<br>[`frontend/src/components/MessageItem.tsx`](frontend/src/components/MessageItem.tsx) | Clean Vite build (`npm run build`) | [Live Demo UI](https://doc-intelligent-sys.vercel.app/) |
| **10. Demonstration Notebook** | Executable 13+ cell demonstration notebook with stored outputs showing end-to-end execution | [`notebooks/Document_Intelligence_Demo.ipynb`](notebooks/Document_Intelligence_Demo.ipynb) | Executed via `scripts/execute_notebook.py` | Full visual demonstration |

---

## 🏛️ System Architecture

```
[ Multi-Format Files (.pdf, .docx, .md, .pptx, .xlsx) ]
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
    [ Qdrant Vector Storage ] (Local Embedded ./data/qdrant_db OR Qdrant Cloud)
                       │
                       ▼
          [ Task Router & Query Rewriter ] ◄── Multi-Turn Conversation History
                       │ (Resolves pronouns / context across turns)
                       ▼
   ┌───────────────────┴─────────────────────────────────────────┐
   │ Generative Task Prompt Engine                               │
   │  ├─ QA Prompt Mode (Source-grounded & cited)               │
   │  ├─ Summarization Mode (Executive, bullet, technical)      │
   │  ├─ Structured Extraction Mode (JSON schema target fields)  │
   │  ├─ Classification Mode (Allowed categories & confidence)   │
   │  └─ Content Generation Mode (Memos, reports, emails)        │
   └───────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
   [ Deterministic Output & Citation Validation Engine ]
       ├─ Citation Validator (Verifies [C1] matches retrieved chunks)
       ├─ Structure Validator (Ensures strict JSON syntax & schema)
       ├─ Factuality Validator (Numerical grounding & claim audit)
                       │
                       ▼
 [ Production Middleware: Rate Limiter + CORS + Error Handlers ]
                       │
                       ▼
 [ React + TypeScript Web Interface & FastAPI REST API ]
```

---

## ✨ Key Capabilities

1. **Task Router & Multi-Turn Query Rewriter**:
   - Automatically detects user intent or routes explicit task requests (`qa`, `summarization`, `extraction`, `classification`, `generation`).
   - Rewrites context-dependent queries (e.g., *"How much can be carried over?"* $\rightarrow$ *"the annual leave policy for employees - How much can be carried over?"*) before running vector search.

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
   - Supports **Qdrant Cloud / Remote Docker** (`USE_EMBEDDED_QDRANT=false` and `QDRANT_URL=https://...`).

5. **Production Hardening**:
   - **Sliding Window Rate Limiter**: Independent per-IP limits for uploads, chat, and search.
   - **CORS & Regex Support**: Configured for local development (`localhost:5173`, `localhost:3000`) and production Vercel apps (`*.vercel.app`).
   - **Security**: File size validation (10MB limit), path traversal prevention, extension whitelisting, and query length constraints.

---

## 🛠️ Local Development Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- OpenRouter API key (or CodeCraft / UnoRouter API key)

---

### Step 1: Backend Setup

1. **Navigate to the backend directory and create a virtual environment**:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file inside `backend/` (or use the root `.env`):
   ```env
   # API Keys
   OPENROUTER_API_KEY=your-openrouter-api-key
   
   # Storage (Default: Zero-dependency embedded Qdrant)
   USE_EMBEDDED_QDRANT=true
   QDRANT_STORAGE_PATH=./data/qdrant_db
   
   # Models
   EMBEDDING_PROVIDER=openrouter
   EMBEDDING_MODEL=text-embedding-3-small
   GENERATION_PROVIDER=openrouter
   GENERATION_MODEL=meta-llama/llama-3.3-70b-instruct:free
   RERANKER_PROVIDER=openrouter
   RERANKER_MODEL=mistralai/mistral-7b-instruct:free
   
   # Server & CORS
   FRONTEND_URL=*
   ENVIRONMENT=development
   ```

5. **Start the FastAPI backend server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - **API Server**: `http://localhost:8000`
   - **Interactive Swagger Docs**: `http://localhost:8000/docs`
   - **Health Check**: `http://localhost:8000/api/health`

---

### Step 2: Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node dependencies**:
   ```bash
   npm install
   ```

3. **Configure local environment (optional)**:
   Create a `.env` file in `frontend/`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   - **Interactive Web App**: `http://localhost:5173`

---

## 🚢 Production Deployment Guide

### Architecture Overview
- **Frontend**: Hosted on **Vercel** (Vite SPA static build)
- **Backend**: Hosted on **Render** (FastAPI Web Service with Python runtime)
- **Vector Database**: **Qdrant Cloud** (Managed vector cluster)
- **LLM / Embeddings**: **OpenRouter** / **CodeCraft** API

---

### Backend Deployment (Render)

1. **Option A: Blueprint Deployment with `render.yaml`**:
   - Push your repository to GitHub.
   - In Render, create a new **Blueprint** and connect the repository.
   - Render automatically reads [`render.yaml`](render.yaml) and configures the service.

2. **Option B: Manual Web Service**:
   - **Service Type**: Web Service
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/health`

3. **Required Environment Variables on Render**:
   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `ENVIRONMENT` | `production` | Production environment mode |
   | `FRONTEND_URL` | `https://doc-intelligent-sys.vercel.app` (or `*`) | Allowed CORS origin |
   | `USE_EMBEDDED_QDRANT` | `false` | Disables disk-embedded Qdrant for cloud storage |
   | `QDRANT_URL` | `https://your-cluster.qdrant.io:6333` | Qdrant Cloud cluster endpoint |
   | `QDRANT_API_KEY` | `your-qdrant-api-key` | Qdrant Cloud API key |
   | `OPENROUTER_API_KEY` | `your-openrouter-api-key` | OpenRouter API key |
   | `RATE_LIMIT_ENABLED` | `true` | Enables in-memory sliding window rate limiter |
   | `MAX_UPLOAD_SIZE_MB` | `10` | Maximum file size in MB |

---

### Frontend Deployment (Vercel)

1. **Import Repository to Vercel**:
   - Create a new project in Vercel and select the repository.
   - Set **Root Directory** to `frontend`.
   - **Framework Preset**: `Vite`.
   - **Build Command**: `npm run build`.
   - **Output Directory**: `dist`.

2. **Environment Variables on Vercel**:
   | Variable | Value |
   | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://doc-intelligentsys.onrender.com/api` |

3. **Deploy**:
   - Click **Deploy**. Vercel will build the frontend and serve it at `https://<your-project>.vercel.app`.

---

## 🧪 Testing & Evaluation

### 1. Run Backend Unit & Integration Tests
```bash
pytest backend/tests/ -v
```
Tests cover:
- Production features, CORS, and rate limiting (`test_production_features.py`)
- Chunker & MarkItDown ingestion (`test_chunker.py`)
- Task router & prompt generation (`test_prompts.py`, `test_task_router.py`)
- Citation & output validation (`test_validation.py`, `test_citations.py`)
- End-to-end RAG pipeline (`test_pipeline.py`)

### 2. Run System Evaluation Benchmark
```bash
python scripts/evaluate_system.py
```
Computes system scores across 13 benchmark test cases:
- **Retrieval Relevance**: Evaluates context overlap and recall
- **Answer Relevance**: Evaluates semantic alignment with ground truth
- **Factuality**: Audits numerical values and factual claims
- **Citation Validity**: Verifies accuracy of inline citations
- Output report: [`data/evaluation/evaluation_results.json`](data/evaluation/evaluation_results.json)

---

## 📓 Demonstration Notebook

The repository contains an executable, self-contained demonstration notebook:
- **Location**: [`notebooks/Document_Intelligence_Demo.ipynb`](notebooks/Document_Intelligence_Demo.ipynb)
- **Contents**: 13 code cells demonstrating end-to-end document conversion, embedding generation, Qdrant vector indexing, all 5 task modes, multi-turn pronoun rewriting, citation validation, and benchmark metrics with rendered outputs.

---

## 📂 Repository Structure

```
DocIntelligentSystem/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST API endpoints (documents, tasks, chat, search, health)
│   │   ├── core/                # Config, rate limiter, error handlers, logging
│   │   ├── generation/          # Task router, prompts (5 modes), output validation
│   │   ├── ingestion/           # MarkItDown converter, hierarchical chunker
│   │   ├── providers/           # OpenRouter, CodeCraft, UnoRouter adapters
│   │   ├── retrieval/           # Retrieval service with hybrid reranking
│   │   └── storage/             # Qdrant client (embedded / cloud) & file storage
│   ├── tests/                   # Unit & integration test suite
│   ├── DEPLOYMENT.md            # Comprehensive backend deployment guide
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client for backend REST endpoints
│   │   ├── components/          # React components (TaskControls, ChatBox, MessageItem, etc.)
│   │   └── types/               # TypeScript interfaces & types
│   ├── package.json             # Frontend dependencies
│   └── .env.example             # Frontend environment template
├── data/
│   ├── evaluation/              # Benchmark test cases & results
│   ├── sample_docs/             # Sample documents (.docx, .pdf)
│   └── uploads/                 # Document storage directory
├── notebooks/
│   └── Document_Intelligence_Demo.ipynb  # Interactive demonstration notebook
├── scripts/
│   ├── evaluate_system.py       # Automated evaluation benchmark script
│   └── execute_notebook.py      # Headless notebook execution script
├── render.yaml                  # Render Blueprint configuration
└── README.md                    # Project documentation
```
