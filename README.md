# Document Intelligence & RAG System

A modular, production-grade **Document Intelligence and RAG (Retrieval-Augmented Generation)** platform engineered with strict provider abstractions, hierarchical document chunking (via Microsoft MarkItDown), dense vector retrieval with reranking, and deterministic citation validation.

---

## 🏛️ System Architecture

```
[ Upload Document (PDF/DOCX/PPTX) ]
                 │
                 ▼
     [ Microsoft MarkItDown ] ──► [ Structured Markdown ]
                 │
                 ▼
    [ Markdown-Aware Chunker ] ──► Chunks with hierarchy ([API] > [Auth]),
                 │                 source metadata, and stable citation tags [C1], [C2]
                 ▼
    [ Embedding Provider Adapter ] (CodeCraft / OpenRouter / UnoRouter)
                 │
                 ▼
    [ Qdrant Vector Database ] (Docker or Local Embedded fallback)
                 │
                 ▼
     [ User Query / Search ]
                 │
                 ▼
      [ Dense Vector Search ] ──► Top 20 Candidates
                 │
                 ▼
        [ Reranker Adapter ]  ──► Top 6 Precision Chunks
                 │
                 ▼
     [ Context Builder + LLM ] ──► Strict Prompt with Citation Constraints
                 │
                 ▼
   [ Citation Validation Engine ] ── Reject invalid citation tags / Hallucinations
                 │
                 ▼
  [ React + Vite + TS Frontend ] ──► Interactive Chat & Citation Inspector
```

---

## ✨ Key Features

1. **Provider Abstraction Layer**:
   - Zero hardcoded vendor locks. Swap embedding and generation models between **OpenRouter**, **CodeCraft**, and **UnoRouter** via configuration alone.
   - Built-in `tenacity` retry wrapper for 429 rate limits, 5xx server errors, and automated provider fallback.

2. **Hierarchical Markdown Ingestion**:
   - Integrates Microsoft **MarkItDown** for multi-format conversion (`.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`).
   - Custom **Markdown-Aware Chunker** preserves document header trees (`# Document > ## Section > ### Subsection`), table boundaries, code blocks, and byte offsets.

3. **Strict Citation Validation**:
   - Every retrieved context chunk is labeled deterministically (`[C1]`, `[C2]`, ...).
   - Hallucination-resistant prompts strictly constrain the LLM to only cite provided chunks.
   - A deterministic citation engine validates all output references and filters hallucinated tags.

4. **Dual Vector Database Modes**:
   - Supports standalone **Qdrant** Docker service (`http://localhost:6333`) or zero-dependency **Local Embedded Storage** (`./data/qdrant_db`).

5. **Modern React UI**:
   - Built with React, TypeScript, and Vite.
   - Includes drag & drop document uploading, indexed document catalog with chunk counts, chat interface with sample questions, and an interactive **Citation Inspector Drawer**.

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
# 1. Activate Python virtual environment
.venv\Scripts\activate

# 2. Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# 3. Configure environment variables in .env
cp .env.example .env

# 4. Start FastAPI server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
UI will be live at: `http://localhost:5173`

---

## 🧪 Testing & Evaluation

### Run Automated Pytest Suite
```bash
pytest backend/tests -v
```

### Run Retrieval Benchmark
```bash
python scripts/benchmark_retrieval.py
```
