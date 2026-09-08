from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_retrieval_service, get_generation_service
from app.retrieval.service import RetrievalService
from app.generation.service import GenerationService
from app.schemas.chat import ChatRequest, ChatResponse, ChatCitation
from app.core.logging import logger

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    generation_service: GenerationService = Depends(get_generation_service),
):
    try:
        # 1. Retrieve & Rerank precision chunks
        context_chunks = await retrieval_service.retrieve(
            query=request.question,
            document_id=request.document_id,
        )

        # 2. Convert history to dictionary format
        history_dicts = [h.model_dump() for h in request.history]

        # 3. Grounded generation & citation validation
        answer, citations, provider, model, val_status = await generation_service.answer_question(
            question=request.question,
            context_chunks=context_chunks,
            history=history_dicts,
            model_override=request.model_override,
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

        return ChatResponse(
            answer=answer,
            citations=chat_citations,
            provider=provider,
            model=model,
            chunks_used=len(context_chunks),
            validation_status=val_status,
        )
    except Exception as e:
        logger.error(f"Chat execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}") from e
