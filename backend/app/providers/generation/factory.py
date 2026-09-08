from app.core.config import Settings
from app.providers.generation.base import GenerationProvider
from app.providers.generation.openrouter import OpenRouterGenerationProvider
from app.providers.generation.codecraft import CodeCraftGenerationProvider
from app.providers.generation.unorouter import UnoRouterGenerationProvider
from app.providers.generation.mock import MockGenerationProvider
from app.core.exceptions import ProviderError
from app.core.logging import logger


class FallbackGenerationProvider(GenerationProvider):
    """Wrapper that tries primary generation provider, falling back to secondary if primary fails."""
    def __init__(self, primary: GenerationProvider, fallback: GenerationProvider | None = None):
        self.primary = primary
        self.fallback = fallback

    @property
    def provider_name(self) -> str:
        return self.primary.provider_name

    @property
    def model_name(self) -> str:
        return self.primary.model_name

    async def generate(self, messages: list[dict[str, str]], **kwargs) -> str:
        try:
            return await self.primary.generate(messages, **kwargs)
        except Exception as primary_err:
            if self.fallback:
                logger.warning(
                    f"Primary generation provider ({self.primary.provider_name}) failed: {primary_err}. "
                    f"Engaging fallback provider ({self.fallback.provider_name})..."
                )
                try:
                    return await self.fallback.generate(messages, **kwargs)
                except Exception as fallback_err:
                    logger.error(f"Fallback generation provider failed: {fallback_err}")
                    raise ProviderError(
                        f"Both primary ({primary_err}) and fallback ({fallback_err}) generation failed"
                    ) from fallback_err
            raise primary_err


def _build_single_provider(provider_name: str, model_name: str, settings: Settings) -> GenerationProvider:
    name = provider_name.lower().strip()
    if name == "openrouter":
        if not settings.openrouter_api_key:
            raise ProviderError("OPENROUTER_API_KEY is required for OpenRouter generation")
        return OpenRouterGenerationProvider(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            model=model_name,
        )
    elif name == "codecraft":
        if not settings.codecraft_api_key:
            raise ProviderError("CODECRAFT_API_KEY is required for CodeCraft generation")
        return CodeCraftGenerationProvider(
            api_key=settings.codecraft_api_key,
            base_url=settings.codecraft_base_url,
            model=model_name,
        )
    elif name == "unorouter":
        if not settings.unorouter_api_key:
            raise ProviderError("UNOROUTER_API_KEY is required for UnoRouter generation")
        return UnoRouterGenerationProvider(
            api_key=settings.unorouter_api_key,
            base_url=settings.unorouter_base_url,
            model=model_name,
        )
    elif name == "mock":
        return MockGenerationProvider()
    else:
        raise ProviderError(f"Unsupported generation provider: {name}")


def create_generation_provider(settings: Settings, model_override: str | None = None) -> GenerationProvider:
    primary_model = model_override or settings.generation_model
    primary = _build_single_provider(settings.generation_provider, primary_model, settings)
    
    fallback = None
    if settings.generation_fallback_provider and settings.generation_fallback_provider != settings.generation_provider:
        try:
            fallback = _build_single_provider(
                settings.generation_fallback_provider,
                settings.generation_fallback_model or primary_model,
                settings,
            )
        except Exception as e:
            logger.warning(f"Could not initialize fallback generator: {e}")
            fallback = None

    return FallbackGenerationProvider(primary=primary, fallback=fallback)
