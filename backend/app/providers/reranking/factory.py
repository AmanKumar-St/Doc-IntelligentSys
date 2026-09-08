from app.core.config import Settings
from app.providers.reranking.base import RerankerProvider
from app.providers.reranking.openrouter import OpenRouterRerankerProvider
from app.providers.reranking.mock import MockRerankerProvider


def create_reranker_provider(settings: Settings) -> RerankerProvider:
    provider_name = settings.reranker_provider.lower().strip()

    if provider_name == "openrouter" and settings.openrouter_api_key:
        return OpenRouterRerankerProvider(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=settings.reranker_model,
        )
    return MockRerankerProvider()
