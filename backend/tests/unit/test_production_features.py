import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os
import sys

# Import these before clearing modules
from app.core.config import Settings
from app.core.rate_limiter import InMemoryRateLimiter, RateLimitExceeded


def get_test_client(extra_env=None, tmp_path=None, mock_ingestion=None):
    env = {
        "EMBEDDING_PROVIDER": "mock",
        "GENERATION_PROVIDER": "mock",
        "RERANKER_PROVIDER": "mock",
        "EMBEDDING_DIMENSION": "128",
    }
    if tmp_path:
        env["QDRANT_STORAGE_PATH"] = str(tmp_path / "qdrant_test_db")
    if extra_env:
        env.update(extra_env)
    
    with patch.dict(os.environ, env):
        # Clear module cache to force reimport with new env
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith("app.")]
        for mod in modules_to_clear:
            del sys.modules[mod]
        
        from app.main import app as fresh_app
        from app.dependencies import (
            get_ingestion_service, get_qdrant_storage, get_file_storage,
            get_retrieval_service, get_generation_service
        )
        
        # Clear lru_cache
        get_ingestion_service.cache_clear()
        get_qdrant_storage.cache_clear()
        get_file_storage.cache_clear()
        get_retrieval_service.cache_clear()
        get_generation_service.cache_clear()
        
        if mock_ingestion:
            fresh_app.dependency_overrides[get_ingestion_service] = lambda: mock_ingestion
        
        return TestClient(fresh_app)


# Create a base client with mock providers
client = get_test_client()


class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app_name" in data
        assert "environment" in data

    def test_root_endpoint_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "api_prefix" in data


class TestCORSConfiguration:
    def test_cors_headers_present_for_allowed_origin(self):
        with patch("app.main.settings") as mock_settings:
            mock_settings.frontend_url = "http://localhost:5173"
            mock_settings.environment = "development"
            response = client.options(
                "/api/health",
                headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
            )
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers

    def test_cors_allows_development_origins(self):
        response = client.options(
            "/api/health",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"}
        )
        assert response.status_code == 200

    def test_cors_allows_vercel_origin(self):
        response = client.options(
            "/api/health",
            headers={"Origin": "https://doc-intelligent-sys.vercel.app", "Access-Control-Request-Method": "GET"}
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestFileUploadValidation:
    def test_oversized_upload_rejected(self):
        with patch("app.api.routes.documents.get_settings") as mock_settings:
            mock_settings.return_value = Settings(max_upload_size_mb=1)
            large_content = b"x" * (2 * 1024 * 1024)
            response = client.post(
                "/api/documents",
                files={"file": ("test.pdf", large_content, "application/pdf")},
            )
            assert response.status_code == 413

    def test_unsupported_file_type_rejected(self):
        with patch("app.api.routes.documents.get_settings") as mock_settings:
            mock_settings.return_value = Settings(allowed_file_extensions=".pdf,.txt")
            response = client.post(
                "/api/documents",
                files={"file": ("test.exe", b"executable content", "application/octet-stream")},
            )
            assert response.status_code == 400
            data = response.json()
            assert "Unsupported file type" in data["detail"]

    def test_filename_path_traversal_prevented(self, tmp_path):
        with patch("app.api.routes.documents.get_settings") as mock_settings:
            mock_settings.return_value = Settings()
            
            mock_service = AsyncMock()
            mock_service.ingest_file = AsyncMock(return_value=MagicMock(
                id="doc_123", filename="passwd.txt", status="embedded", chunk_count=5
            ))
            
            test_client = get_test_client(tmp_path=tmp_path, mock_ingestion=mock_service)
            response = test_client.post(
                "/api/documents",
                files={"file": ("../../etc/passwd.txt", b"content", "text/plain")},
            )
            assert response.status_code == 200
            data = response.json()
            # Verify path traversal sequences are removed - filename should not contain .. or /
            filename = data.get("filename", "")
            assert ".." not in filename
            assert "/" not in filename
            assert "\\" not in filename
            # The base filename should be preserved
            assert filename == "passwd.txt"

    def test_valid_upload_accepted(self, tmp_path):
        # Create a client with matching embedding dimension
        mock_service = AsyncMock()
        mock_service.ingest_file = AsyncMock(return_value=MagicMock(
            id="doc_123", filename="test.pdf", status="embedded", chunk_count=5
        ))
        test_client = get_test_client({"EMBEDDING_DIMENSION": "128"}, tmp_path=tmp_path, mock_ingestion=mock_service)
        
        with patch("app.api.routes.documents.get_settings") as mock_settings:
            mock_settings.return_value = Settings(embedding_dimension=128)

            response = test_client.post(
                "/api/documents",
                files={"file": ("test.pdf", b"PDF content", "application/pdf")},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["document_id"] == "doc_123"
            assert data["filename"] == "test.pdf"


class TestRequestValidation:
    def test_overly_long_chat_question_rejected(self):
        long_question = "x" * 5000
        response = client.post(
            "/api/chat",
            json={"question": long_question, "history": []},
        )
        assert response.status_code == 422

    def test_overly_long_search_query_rejected(self):
        long_query = "x" * 3000
        response = client.post(
            "/api/search",
            json={"query": long_query, "top_k": 5},
        )
        assert response.status_code == 422

    def test_empty_chat_question_rejected(self):
        response = client.post(
            "/api/chat",
            json={"question": "", "history": []},
        )
        assert response.status_code == 422

    def test_empty_search_query_rejected(self):
        response = client.post(
            "/api/search",
            json={"query": "", "top_k": 5},
        )
        assert response.status_code == 422


class TestRateLimiting:
    def test_rate_limiter_allows_requests_under_limit(self):
        limiter = InMemoryRateLimiter()
        for i in range(5):
            allowed, info = limiter.check_rate_limit("test_client", 10, 60)
            assert allowed is True
            assert info["remaining"] == 9 - i

    def test_rate_limiter_blocks_requests_over_limit(self):
        limiter = InMemoryRateLimiter()
        for i in range(10):
            allowed, info = limiter.check_rate_limit("test_client_2", 10, 60)
            assert allowed is True
        
        allowed, info = limiter.check_rate_limit("test_client_2", 10, 60)
        assert allowed is False
        assert info["remaining"] == 0
        assert info["retry_after"] > 0

    def test_rate_limiter_different_clients_independent(self):
        limiter = InMemoryRateLimiter()
        for i in range(10):
            limiter.check_rate_limit("client_a", 10, 60)
        
        allowed, _ = limiter.check_rate_limit("client_b", 10, 60)
        assert allowed is True

    def test_rate_limiter_cleanup_old_requests(self):
        limiter = InMemoryRateLimiter()
        import time
        now = time.time()
        
        for i in range(5):
            limiter._get_bucket("cleanup_test").add_request(now - 120)
        
        allowed, info = limiter.check_rate_limit("cleanup_test", 10, 60)
        assert allowed is True
        assert info["remaining"] == 9

    def test_upload_rate_limit_function(self):
        limiter = InMemoryRateLimiter()
        # Clear any existing bucket
        limiter._get_bucket("upload:test_ip").requests.clear()
        
        # Use the limiter directly
        for i in range(2):
            allowed, _ = limiter.check_rate_limit("upload:test_ip", 2, 60)
            assert allowed is True
        
        allowed, info = limiter.check_rate_limit("upload:test_ip", 2, 60)
        assert allowed is False
        assert info["remaining"] == 0


class TestSettingsEnvironmentVariables:
    def test_settings_read_frontend_url(self):
        with patch.dict(os.environ, {"FRONTEND_URL": "https://myapp.vercel.app"}):
            from app.core.config import Settings
            settings = Settings()
            assert settings.frontend_url == "https://myapp.vercel.app"

    def test_settings_read_upload_limits(self):
        with patch.dict(os.environ, {"MAX_UPLOAD_SIZE_MB": "25", "ALLOWED_FILE_EXTENSIONS": ".pdf,.docx"}):
            from app.core.config import Settings
            settings = Settings()
            assert settings.max_upload_size_mb == 25
            assert settings.allowed_file_extensions == ".pdf,.docx"

    def test_settings_read_rate_limits(self):
        with patch.dict(os.environ, {
            "RATE_LIMIT_ENABLED": "false",
            "UPLOAD_RATE_LIMIT": "10",
            "CHAT_RATE_LIMIT": "50",
            "SEARCH_RATE_LIMIT": "100",
        }):
            from app.core.config import Settings
            settings = Settings()
            assert settings.rate_limit_enabled is False
            assert settings.upload_rate_limit == 10
            assert settings.chat_rate_limit == 50
            assert settings.search_rate_limit == 100

    def test_settings_read_qdrant_config(self):
        with patch.dict(os.environ, {
            "QDRANT_URL": "https://my-qdrant.cloud",
            "QDRANT_API_KEY": "secret-key",
            "USE_EMBEDDED_QDRANT": "false",
        }):
            from app.core.config import Settings
            settings = Settings()
            assert settings.qdrant_url == "https://my-qdrant.cloud"
            assert settings.qdrant_api_key == "secret-key"
            assert settings.use_embedded_qdrant is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])