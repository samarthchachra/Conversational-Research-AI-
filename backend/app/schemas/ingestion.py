from pydantic import BaseModel


class IngestionRequest(BaseModel):

    query: str

    top_k: int = 20


class IngestionResponse(BaseModel):

    ingested_documents: int

    ingested_chunks: int

    message: str