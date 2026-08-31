from fastapi import APIRouter

from app.api.routes.conversation import router as conversation_router
from app.api.routes.paper_request import router as paper_request_router

api_router = APIRouter()

api_router.include_router(
    conversation_router
)
api_router.include_router(
    paper_request_router
)