import re
from typing import Any
from app.core.config import Settings, get_settings
from app.core.logging import logger
from app.generation.tasks.models import TaskType, TaskRequest, TaskResponse, ValidationReportSchema
from app.generation.prompts import (
    build_qa_messages,
    build_summarization_messages,
    build_extraction_messages,
    build_classification_messages,
    build_content_generation_messages,
)
from app.generation.validation import ValidationService
from app.providers.generation.factory import create_generation_provider
from app.retrieval.service import RetrievalService
from app.schemas.chat import ChatCitation


class TaskRouter:
    """Orchestrates generative task execution with multi-turn context resolution and validation."""

    def __init__(
        self,
        settings: Settings | None = None,
        retrieval_service: RetrievalService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.retrieval = retrieval_service or RetrievalService(self.settings)

    def resolve_multi_turn_query(self, instruction: str, history: list[dict[str, str]]) -> str:
        """
        Performs context-aware query resolution for multi-turn conversations.
        Detects referential pronouns and binds context from previous turns.
        """
        if not history:
            return instruction

        pronoun_triggers = [
            r"\b(it|this|that|they|them|these|those)\b",
            r"\b(how much|how many|what about|and what|what else)\b",
            r"\b(carry over|carried over|reimbursement|allowance)\b",
        ]

        needs_context = any(re.search(pat, instruction, re.IGNORECASE) for pat in pronoun_triggers)

        if needs_context:
            # Find the most recent user turn
            for turn in reversed(history):
                if turn.get("role") == "user":
                    prev_user_text = turn.get("content", "").strip()
                    if prev_user_text:
                        # Extract core topic from previous user query
                        clean_prev = re.sub(r"^(what is|how to|tell me about|explain)\s+", "", prev_user_text, flags=re.IGNORECASE)
                        clean_prev = clean_prev.rstrip("?.,")
                        resolved = f"{clean_prev} - {instruction}"
                        logger.info(f"Resolved multi-turn context: '{instruction}' -> '{resolved}'")
                        return resolved

        return instruction

    async def execute_task(self, request: TaskRequest) -> TaskResponse:
        logger.info(f"Executing task: {request.task_type.value} | Instruction: '{request.instruction[:60]}...'")

        # 1. Multi-turn context resolution
        history_dicts = [h.model_dump() for h in request.history]
        resolved_query = self.resolve_multi_turn_query(request.instruction, history_dicts)

        # 2. Retrieve & rerank relevant document chunks
        context_chunks = await self.retrieval.retrieve(
            query=resolved_query,
            document_id=request.document_id,
        )

        # 3. Build task-specific prompt messages
        if request.task_type == TaskType.QA:
            messages = build_qa_messages(
                question=request.instruction,
                chunks=context_chunks,
                history=history_dicts,
            )
        elif request.task_type == TaskType.SUMMARIZATION:
            messages = build_summarization_messages(
                instruction=request.instruction,
                chunks=context_chunks,
                summary_type=request.summary_type,
                history=history_dicts,
            )
        elif request.task_type == TaskType.EXTRACTION:
            messages = build_extraction_messages(
                instruction=request.instruction,
                chunks=context_chunks,
                fields=request.target_fields,
                history=history_dicts,
            )
        elif request.task_type == TaskType.CLASSIFICATION:
            allowed_cats = request.allowed_categories or [
                "HR Policy",
                "Technical Documentation",
                "Financial Report",
                "Other",
            ]
            messages = build_classification_messages(
                instruction=request.instruction,
                chunks=context_chunks,
                categories=allowed_cats,
                history=history_dicts,
            )
        elif request.task_type == TaskType.GENERATION:
            messages = build_content_generation_messages(
                user_requirement=request.instruction,
                chunks=context_chunks,
                output_format=request.output_format,
                history=history_dicts,
            )
        else:
            messages = build_qa_messages(
                question=request.instruction,
                chunks=context_chunks,
                history=history_dicts,
            )

        # 4. Execute generation provider with fallback
        generator = create_generation_provider(self.settings, model_override=request.model_override)
        raw_output = await generator.generate(
            messages=messages,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_output_tokens,
        )

        # 5. Execute structural, citation, and factuality validation
        cleaned_text, citations, val_report = ValidationService.validate_task_output(
            task_type=request.task_type.value,
            raw_output=raw_output,
            context_chunks=context_chunks,
            target_fields=request.target_fields,
            allowed_categories=request.allowed_categories,
        )

        chat_citations = [
            ChatCitation(
                id=c.id,
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                source=c.source,
                section=c.section,
                page=c.page,
                heading_path=c.heading_path,
                snippet=c.snippet,
                score=c.score,
            )
            for c in citations
        ]

        return TaskResponse(
            task_type=request.task_type,
            answer=cleaned_text,
            structured_data=val_report.extracted_data,
            citations=chat_citations,
            validation=ValidationReportSchema(
                status=val_report.status,
                structure_valid=val_report.structure_valid,
                citation_valid=val_report.citation_valid,
                factuality_status=val_report.factuality_status,
                factuality_score=val_report.factuality_score,
                warnings=val_report.warnings,
                extracted_data=val_report.extracted_data,
            ),
            provider=generator.provider_name,
            model=generator.model_name,
            chunks_used=len(context_chunks),
            resolved_query=resolved_query if resolved_query != request.instruction else None,
        )
