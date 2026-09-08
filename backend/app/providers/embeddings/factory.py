from app.core.config import Settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.codecraft import CodeCraftEmbeddingProvider
from app.providers.embeddings.openrouter import OpenRouterEmbeddingProvider
from app.providers.embeddings.unorouter import UnoRouterEmbeddingProvider
from app.providers.embeddings.mock import MockEmbeddingProvider
from app.core.exceptions import ProviderError


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider_name = settings.embedding_provider.lower().strip()

    if provider_name == "openrouter":
        if not settings.openrouter_api_key:
            raise ProviderError("OPENROUTER_API_KEY is required for OpenRouter embeddings")
        return OpenRouterEmbeddingProvider(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    elif provider_name == "codecraft":
        if not settings.codecraft_api_key:
            raise ProviderError("CODECRAFT_API_KEY is required for CodeCraft embeddings")
        return CodeCraftEmbeddingProvider(
            api_key=settings.codecraft_api_key,
            base_url=settings.codecraft_base_url,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    elif provider_name == "unorouter":
        if not settings.unorouter_api_key:
            raise ProviderError("UNOROUTER_API_KEY is required for UnoRouter embeddings")
        return UnoRouterEmbeddingProvider(
            api_key=settings.unorouter_api_key,
            base_url=settings.unorouter_base_url,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    elif provider_name == "mock":
        return MockEmbeddingProvider(dimension=settings.embedding_dimension)
    else:
        raise ProviderError(f"Unsupported embedding provider: {provider_name}")
