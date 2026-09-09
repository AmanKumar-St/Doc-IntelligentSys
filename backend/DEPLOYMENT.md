# Document Intelligence & RAG System - Deployment Guide

## Prerequisites

- Python 3.11+
- Qdrant Cloud account (for production) or local Qdrant for development
- OpenRouter API key (or CodeCraft/UnoRouter alternatives)
- Render account (for free web service deployment)
- Vercel account (for frontend deployment)

## Local Setup

### 1. Clone and Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required for local development:
- `OPENROUTER_API_KEY` (or alternative provider key)
- `QDRANT_URL=http://localhost:6333` (if running local Qdrant)
- `USE_EMBEDDED_QDRANT=true` (uses embedded Qdrant, no separate server needed)

### 3. Start Local Qdrant (Optional - Embedded Mode Works Without)

```bash
# Using Docker
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Or use embedded mode (default) which requires no separate Qdrant instance.

### 4. Start the Backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **OpenAPI Docs**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Upload a document
curl -X POST http://localhost:8000/api/documents \
  -F "file=@sample.pdf"

# Search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "annual leave policy", "top_k": 5}'

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the annual leave policy?", "history": []}'
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment name (development/production) | development | No |
| `FRONTEND_URL` | Vercel frontend URL for CORS | http://localhost:5173 | **Yes (production)** |
| `MAX_UPLOAD_SIZE_MB` | Maximum file upload size in MB | 10 | No |
| `ALLOWED_FILE_EXTENSIONS` | Comma-separated allowed extensions | .pdf,.docx,... | No |
| `MAX_QUERY_LENGTH` | Maximum search query length | 2000 | No |
| `MAX_CHAT_MESSAGE_LENGTH` | Maximum chat message length | 4000 | No |
| `RATE_LIMIT_ENABLED` | Enable in-process rate limiting | true | No |
| `UPLOAD_RATE_LIMIT` | Max upload requests per window | 5 | No |
| `UPLOAD_RATE_WINDOW_SECONDS` | Upload rate limit window (seconds) | 3600 | No |
| `CHAT_RATE_LIMIT` | Max chat requests per window | 30 | No |
| `CHAT_RATE_WINDOW_SECONDS` | Chat rate limit window (seconds) | 3600 | No |
| `SEARCH_RATE_LIMIT` | Max search requests per window | 60 | No |
| `SEARCH_RATE_WINDOW_SECONDS` | Search rate limit window (seconds) | 3600 | No |
| `QDRANT_URL` | Qdrant server URL | http://localhost:6333 | **Yes (production)** |
| `QDRANT_API_KEY` | Qdrant Cloud API key | (empty) | **Yes (Qdrant Cloud)** |
| `QDRANT_STORAGE_PATH` | Local Qdrant storage path | ./data/qdrant_db | No |
| `QDRANT_COLLECTION` | Qdrant collection name | documents | No |
| `USE_EMBEDDED_QDRANT` | Use embedded Qdrant (true/false) | true | No |
| `UPLOAD_DIR` | Local upload directory | ./data/uploads | No |
| `MARKDOWN_DIR` | Local markdown directory | ./data/markdown | No |
| `EMBEDDING_PROVIDER` | Embedding provider | openrouter | No |
| `EMBEDDING_MODEL` | Embedding model name | text-embedding-3-small | No |
| `EMBEDDING_DIMENSION` | Embedding dimension | 1536 | No |
| `RERANKER_PROVIDER` | Reranker provider | openrouter | No |
| `RERANKER_MODEL` | Reranker model | mistralai/mistral-7b-instruct:free | No |
| `GENERATION_PROVIDER` | Generation provider | openrouter | No |
| `GENERATION_MODEL` | Generation model | meta-llama/llama-3.3-70b-instruct:free | No |
| `GENERATION_FALLBACK_PROVIDER` | Fallback generation provider | codecraft | No |
| `GENERATION_FALLBACK_MODEL` | Fallback generation model | gpt-4o-mini | No |
| `OPENROUTER_API_KEY` | OpenRouter API key | (empty) | **Yes (if using OpenRouter)** |
| `CODECRAFT_API_KEY` | CodeCraft API key | (empty) | **Yes (if using CodeCraft)** |
| `UNOROUTER_API_KEY` | UnoRouter API key | (empty) | **Yes (if using UnoRouter)** |

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests use mock providers by default and don't require external API keys or Qdrant.

## Render Deployment

### 1. Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `doc-intelligence-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/health`

### 2. Set Environment Variables in Render Dashboard

Go to **Environment** tab and add:

**Required for Production:**
```
ENVIRONMENT=production
FRONTEND_URL=https://doc-intelligent-sys.vercel.app
QDRANT_URL=https://e9edec85-6617-49bf-b299-032dfb818357.australia-southeast1-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=<your-qdrant-api-key>
USE_EMBEDDED_QDRANT=false
OPENROUTER_API_KEY=<your-openrouter-key>
```

**Optional (defaults shown):**
```
MAX_UPLOAD_SIZE_MB=10
MAX_QUERY_LENGTH=2000
MAX_CHAT_MESSAGE_LENGTH=4000
RATE_LIMIT_ENABLED=true
UPLOAD_RATE_LIMIT=5
UPLOAD_RATE_WINDOW_SECONDS=3600
CHAT_RATE_LIMIT=30
CHAT_RATE_WINDOW_SECONDS=3600
SEARCH_RATE_LIMIT=60
SEARCH_RATE_WINDOW_SECONDS=3600
LOG_LEVEL=INFO
EMBEDDING_PROVIDER=openrouter
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
RERANKER_PROVIDER=openrouter
RERANKER_MODEL=mistralai/mistral-7b-instruct:free
GENERATION_PROVIDER=openrouter
GENERATION_MODEL=meta-llama/llama-3.3-70b-instruct:free
GENERATION_FALLBACK_PROVIDER=codecraft
GENERATION_FALLBACK_MODEL=gpt-4o-mini
QDRANT_COLLECTION=documents
QDRANT_STORAGE_PATH=./data/qdrant_db
UPLOAD_DIR=./data/uploads
MARKDOWN_DIR=./data/markdown
```

### 3. Deploy

Click **Create Web Service**. Render will build and deploy automatically.

### 4. Verify Deployment

- Health check: `https://your-service.onrender.com/api/health`
- API docs: `https://your-service.onrender.com/docs`

## Qdrant Cloud Configuration

### 1. Create Qdrant Cloud Cluster

1. Go to [Qdrant Cloud](https://cloud.qdrant.io)
2. Create a new cluster (free tier available)
3. Note the cluster URL and API key

### 2. Configure in Render

Set these environment variables in Render:
```
QDRANT_URL=https://e9edec85-6617-49bf-b299-032dfb818357.australia-southeast1-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=<your-qdrant-api-key>
USE_EMBEDDED_QDRANT=false
```

### 3. Vector Dimension

Ensure `EMBEDDING_DIMENSION` matches your embedding model:
- `text-embedding-3-small`: 1536
- `text-embedding-3-large`: 3072
- Other models: check provider documentation

## Secret Configuration

**NEVER** commit secrets to version control:
- `.env` files with real keys
- API keys in code or config files
- Qdrant credentials in frontend code

All secrets must be set in:
- Local: `.env` file (gitignored)
- Render: Environment Variables in Dashboard
- Vercel: Environment Variables in Project Settings

## CORS Configuration

The backend accepts requests from `FRONTEND_URL` only (plus localhost in development).

**Production:**
```
FRONTEND_URL=https://your-app.vercel.app
```

**Development (automatic):**
- http://localhost:5173 (Vite default)
- http://localhost:3000 (Next.js default)

## Vercel Frontend URL Configuration

1. Deploy frontend to Vercel
2. Copy the Vercel URL (e.g., `https://my-app.vercel.app`)
3. Set `FRONTEND_URL` in Render environment variables
4. Redeploy Render service

## Rate Limiting Behavior

The in-process rate limiter provides basic protection for public demos:

| Endpoint | Limit | Window | Identifier |
|----------|-------|--------|------------|
| POST /api/documents | 5 | 1 hour | Client IP |
| POST /api/chat | 30 | 1 hour | Client IP |
| POST /api/search | 60 | 1 hour | Client IP |

**Limitations:**
- Resets on service restart (Render free tier spins down after inactivity)
- Not distributed (single instance only)
- Uses `X-Forwarded-For` header for client IP behind Render proxy

**Response when exceeded:**
```json
{
  "detail": "Rate limit exceeded...",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 3599,
  "limit": 5,
  "window_seconds": 3600
}
```
Headers: `Retry-After: 3599`

## Upload Size Limits

- **Default**: 10 MB
- **Configurable**: `MAX_UPLOAD_SIZE_MB`
- **Response for oversized**: HTTP 413 with clear message
- **Validation**: Streaming (checks size while reading, not after full upload)

## Render Free Tier Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Spins down after 15 min inactivity | Cold starts (~30s) | Acceptable for demos |
| 512 MB RAM | Limited memory for large embeddings | Use smaller models |
| No persistent disk | Local files lost on restart | Use Qdrant Cloud only |
| Shared CPU | Variable performance | Acceptable for demos |
| No custom domains on free | Uses `.onrender.com` | Acceptable for demos |

## Ephemeral Filesystem Limitation

**⚠️ CRITICAL**: Render free web services have ephemeral local storage.

- Uploaded files in `UPLOAD_DIR` are **LOST** on restart/sleep
- Markdown files in `MARKDOWN_DIR` are **LOST** on restart/sleep
- Embedded Qdrant data in `QDRANT_STORAGE_PATH` is **LOST** on restart/sleep

**For Production Use:**
- Use Qdrant Cloud (external vector database)
- Implement persistent file storage (S3, GCS, Azure Blob) - *not included in this version*
- The application will warn on startup in production mode about ephemeral storage

## Health Check

**Endpoint**: `GET /api/health`

**Response:**
```json
{
  "status": "ok",
  "app_name": "document-intelligence",
  "environment": "production",
  "embedding_provider": "openrouter",
  "generation_provider": "openrouter",
  "reranker_provider": "openrouter",
  "storage_mode": "remote"
}
```

- Responds in < 100ms
- Does not invoke LLMs
- Does not access Qdrant (only checks configuration)
- Suitable for Render health checks and load balancers

## Troubleshooting

### "OPENROUTER_API_KEY is required" Error
- Ensure `OPENROUTER_API_KEY` is set in Render environment variables
- Verify the key is valid at https://openrouter.ai/keys

### "Could not connect to Qdrant" Error
- Check `QDRANT_URL` and `QDRANT_API_KEY` in Render
- Ensure Qdrant Cloud cluster is running
- Verify network access (Qdrant Cloud allows all IPs by default)

### "Storage folder already accessed" Error
- Multiple service instances trying to use embedded Qdrant
- Set `USE_EMBEDDED_QDRANT=false` and use Qdrant Cloud

### CORS Errors from Frontend
- Verify `FRONTEND_URL` matches exactly (including protocol)
- Check browser console for exact origin being sent
- Ensure no trailing slashes mismatch

### Rate Limit 429 Errors
- Expected behavior under load
- Adjust limits in environment variables if needed
- Remember: resets on service restart

### "File size exceeds maximum" (413)
- Check `MAX_UPLOAD_SIZE_MB` setting
- Compress or split large documents

### "Unsupported file type" (400)
- Check `ALLOWED_FILE_EXTENSIONS` includes your file type
- Ensure file has correct extension

### Permission Denied / Qdrant Lock Errors (Local)
- Only one process can use embedded Qdrant at a time
- Stop other running instances
- Or use separate `QDRANT_STORAGE_PATH` per instance

## Local Development with Frontend

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend (in separate repo)
cd frontend
npm run dev  # Runs on http://localhost:5173
```

CORS is pre-configured for localhost:5173 and localhost:3000 in development mode.

## Regression Checklist

After deployment, verify:

- [ ] `GET /api/health` returns 200
- [ ] `GET /docs` loads OpenAPI documentation
- [ ] `POST /api/documents` accepts valid PDF/DOCX/TXT
- [ ] `POST /api/documents` rejects files > 10 MB (413)
- [ ] `POST /api/documents` rejects .exe files (400)
- [ ] `POST /api/search` returns results for indexed documents
- [ ] `POST /api/chat` returns answers with citations
- [ ] CORS works from Vercel frontend
- [ ] Rate limiting returns 429 after limit exceeded
- [ ] Long queries/messages rejected with 422
- [ ] Path traversal filenames sanitized
- [ ] No secrets in logs or responses