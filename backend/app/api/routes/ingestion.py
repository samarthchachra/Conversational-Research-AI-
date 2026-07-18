from fastapi import APIRouter

from app.schemas.ingestion import (
    IngestionRequest,
    IngestionResponse
)

from app.services.ingestion.manual_ingestion import (
    ManualIngestionService
)

router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"]
)

service = ManualIngestionService()

@router.post(
    "",
    response_model=IngestionResponse
)
def ingest_documents(
    request: IngestionRequest
):

    return service.ingest(
        query=request.query,
        top_k=request.top_k
    )