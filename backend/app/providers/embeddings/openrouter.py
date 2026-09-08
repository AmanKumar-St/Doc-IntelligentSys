from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import httpx
from app.providers.embeddings.base import EmbeddingProvider
from app.core.exceptions import ProviderError
from app.core.logging import logger


class OpenRouterEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model: str = "text-embedding-3-small", dimension: int = 1536):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={"HTTP-Referer": "https://github.com/doc-intelligence", "X-Title": "Document Intelligence"},
        )
        self.model = model
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            # Batch embedding call
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            # Ensure sorted order matching input index
            sorted_items = sorted(response.data, key=lambda item: item.index)
            embeddings = [item.embedding for item in sorted_items]
            return embeddings
        except Exception as e:
            logger.error(f"OpenRouter Embedding error: {e}")
            raise ProviderError(f"OpenRouter embedding failed: {str(e)}") from e
