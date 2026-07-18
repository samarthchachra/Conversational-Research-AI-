from fastapi import APIRouter

from app.api.routes.conversation import router as conversation_router
from app.api.routes.ingestion import router as ingestion_router
api_router = APIRouter()

api_router.include_router(
    conversation_router
)

api_router.include_router(
    ingestion_router
)