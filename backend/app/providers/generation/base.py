from abc import ABC, abstractmethod
from typing import Any


class GenerationProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        **kwargs: Any,
    ) -> str:
        """Generates a text completion response given chat messages."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
