from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class CreateConversationRequest(BaseModel):

    title: str | None = None


class ConversationResponse(BaseModel):

    id: UUID

    title: str | None

    created_at: datetime

    class Config:

        from_attributes = True