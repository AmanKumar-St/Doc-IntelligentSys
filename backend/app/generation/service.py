from app.core.config import Settings, get_settings
from app.generation.prompts import build_chat_messages
from app.generation.validation import CitationValidator
from app.models.chunk import Chunk
from app.models.citation import Citation
from app.providers.generation.factory import create_generation_provider
from app.core.logging import logger


class GenerationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def answer_question(
        self,
        question: str,
        context_chunks: list[Chunk],
        history: list[dict[str, str]] | None = None,
        model_override: str | None = None,
    ) -> tuple[str, list[Citation], str, str, str]:
        """
        Executes end-to-end grounded generation:
        1. Prepares messages with strict citation instructions.
        2. Queries generation provider with automatic retry/fallback.
        3. Validates and maps citations against context chunks.
        
        Returns:
            (answer_text, citations, provider_name, model_name, validation_status)
        """
        if not context_chunks:
            return (
                "I couldn't find any relevant information in the uploaded documents to answer your question.",
                [],
                "none",
                "none",
                "valid",
            )

        messages = build_chat_messages(
            question=question,
            chunks=context_chunks,
            history=history,
        )

        generator = create_generation_provider(self.settings, model_override=model_override)
        
        logger.info(f"Generating answer using {generator.provider_name} ({generator.model_name})...")
        raw_response = await generator.generate(
            messages=messages,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_output_tokens,
        )

        # Validate citations
        cleaned_answer, citations, val_status = CitationValidator.validate_and_map_citations(
            answer_text=raw_response,
            context_chunks=context_chunks,
            strict=False,
        )

        return (
            cleaned_answer,
            citations,
            generator.provider_name,
            generator.model_name,
            val_status,
        )
