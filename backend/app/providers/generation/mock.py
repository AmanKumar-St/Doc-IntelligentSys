import re
from typing import Any
from app.providers.generation.base import GenerationProvider


class MockGenerationProvider(GenerationProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-generator"

    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        **kwargs: Any,
    ) -> str:
        # Scan messages for citation IDs [C1], [C2], etc.
        combined = "\n".join(m.get("content", "") for m in messages)
        citations_found = re.findall(r"\[(C\d+)\]", combined)
        valid_citations = sorted(list(set(citations_found)))

        if valid_citations:
            cited_str = " ".join(f"[{c}]" for c in valid_citations[:2])
            return (
                f"Based on the provided documentation, the requested information is verified and supported. "
                f"Specifically, the policies and details are outlined directly in the reference sections {cited_str}."
            )
        return "I couldn't find enough information in the provided documents."
