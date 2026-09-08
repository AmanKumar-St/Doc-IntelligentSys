from fastapi import APIRouter
from app.api.routes import documents, search, chat, health, tasks

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
