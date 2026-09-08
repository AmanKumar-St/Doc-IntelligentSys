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
        combined = "\n".join(m.get("content", "") for m in messages)
        
        # Check if classification is requested
        if "ALLOWED CATEGORIES LIST" in combined or "CLASSIFICATION INSTRUCTION" in combined:
            # Extract first allowed category
            cats_match = re.search(r"ALLOWED CATEGORIES LIST:\s*\[(.*?)\]", combined)
            first_cat = "HR Policy"
            if cats_match:
                cat_tokens = re.findall(r'"(.*?)"', cats_match.group(1))
                if cat_tokens:
                    first_cat = cat_tokens[0]
            return f'{{"category": "{first_cat}", "confidence": 0.95, "explanation": "Context matches domain criteria.", "citations": ["C1"]}}'

        # Check if JSON extraction is requested
        if "EXTRACTION TASK" in combined or "Target Fields to Extract" in combined:
            return '{"annual_leave_days": "22", "carryover_limit": "5", "sick_leave_days": "12", "_citations": ["C1"], "_confidence": 1.0}'

        # Standard QA/Summarization/Generation with citations
        citations_found = re.findall(r"\[(C\d+)\]", combined)
        valid_citations = sorted(list(set(citations_found)))

        if valid_citations:
            cited_str = " ".join(f"[{c}]" for c in valid_citations[:2])
            return (
                f"Based on the provided documentation, the requested information is verified and supported. "
                f"Specifically, the policies and details are outlined directly in the reference sections {cited_str}."
            )
        return "I couldn't find enough information in the provided documents."
