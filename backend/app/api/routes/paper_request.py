from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.paper_request import CreatePaperRequest, PaperRequestResponse
from app.models.paper_request import PaperRequest

router = APIRouter(
    prefix="/paper-requests",
    tags=["Paper Requests"]
)

@router.post("", response_model=PaperRequestResponse)
def create_paper_request(
    request: CreatePaperRequest,
    db: Session = Depends(get_db)
):
    new_request = PaperRequest(
        query=request.query
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("", response_model=list[PaperRequestResponse])
def list_paper_requests(
    db: Session = Depends(get_db)
):
    return db.query(PaperRequest).order_by(PaperRequest.created_at.desc()).all()
