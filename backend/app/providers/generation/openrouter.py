from typing import Any
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import httpx
from app.providers.generation.base import GenerationProvider
from app.core.exceptions import ProviderError
from app.core.logging import logger


class OpenRouterGenerationProvider(GenerationProvider):
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", model: str = "meta-llama/llama-3.3-70b-instruct:free"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={"HTTP-Referer": "https://github.com/doc-intelligence", "X-Title": "Document Intelligence"},
        )
        self.model = model

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def model_name(self) -> str:
        return self.model

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        reraise=True,
    )
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        **kwargs: Any,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenRouter Generation error: {e}")
            raise ProviderError(f"OpenRouter generation failed: {str(e)}") from e
