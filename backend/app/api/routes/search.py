from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_retrieval_service
from app.retrieval.service import RetrievalService
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.core.logging import logger

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    try:
        chunks = await retrieval_service.retrieve(
            query=request.query,
            rerank_top_k=request.top_k,
            document_id=request.document_id,
        )

        results = [
            SearchResultItem(
                citation_id=c.citation_id or f"C{i+1}",
                chunk_id=c.id,
                document_id=c.document_id,
                source=c.source,
                text=c.text,
                section=c.section,
                page=c.page,
                heading_path=c.heading_path,
                score=c.score or 0.0,
            )
            for i, c in enumerate(chunks)
        ]

        return SearchResponse(
            query=request.query,
            total_results=len(results),
            results=results,
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") from e
