from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CreatePaperRequest(BaseModel):
    query: str

class PaperRequestResponse(BaseModel):
    id: UUID
    query: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
