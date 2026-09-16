import base64
import struct
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import httpx
from app.providers.embeddings.base import EmbeddingProvider
from app.core.exceptions import ProviderError
from app.core.logging import logger


class CodeCraftEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, base_url: str = "https://codecraftapi.com/v1", model: str = "text-embedding-3-small", dimension: int = 1536):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
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
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    encoding_format="float",
                )
            except Exception as req_err:
                err_msg = str(req_err).lower()
                if "encoding_format" in err_msg or "base64" in err_msg or "invalid" in err_msg:
                    response = await self.client.embeddings.create(
                        model=self.model,
                        input=texts,
                    )
                else:
                    raise req_err

            sorted_items = sorted(response.data, key=lambda item: item.index)
            embeddings: list[list[float]] = []
            for item in sorted_items:
                emb = item.embedding
                if isinstance(emb, str):
                    raw_bytes = base64.b64decode(emb)
                    float_count = len(raw_bytes) // 4
                    floats = list(struct.unpack(f"<{float_count}f", raw_bytes))
                    embeddings.append(floats)
                elif isinstance(emb, list):
                    embeddings.append(emb)
                else:
                    embeddings.append(list(emb))
            return embeddings
        except Exception as e:
            logger.error(f"CodeCraft Embedding error: {e}")
            raise ProviderError(f"CodeCraft embedding failed: {str(e)}") from e

