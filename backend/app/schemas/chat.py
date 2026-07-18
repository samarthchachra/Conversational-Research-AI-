from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):

    conversation_id: UUID

    query: str


class CitationResponse(BaseModel):

    title: str

    authors: list[str]

    published: str

    pdf_url: str


class ChatResponse(BaseModel):

    answer: str

    citations: list[CitationResponse]