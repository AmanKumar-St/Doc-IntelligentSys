from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_retrieval_service
from app.retrieval.service import RetrievalService
from app.generation.tasks.models import TaskRequest, TaskResponse
from app.generation.tasks.router import TaskRouter
from app.core.logging import logger

router = APIRouter()


@router.post("", response_model=TaskResponse)
async def process_task(
    request: TaskRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    try:
        task_router = TaskRouter(retrieval_service=retrieval_service)
        response = await task_router.execute_task(request)
        return response
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}") from e
