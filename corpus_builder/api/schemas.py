"""Pydantic schemas for the corpus builder API."""

from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Ingestion request / response
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    queries: list[str] = Field(
        ...,
        description="One or more search queries to find relevant papers.",
        examples=[["transformer attention mechanisms", "retrieval augmented generation"]],
        min_length=1,
    )
    top_k: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of papers to retrieve per query from the dataset.",
    )
    dry_run: bool = Field(
        default=False,
        description="If true, search and preprocess only — skip embedding and Qdrant upsert.",
    )


class JobStatus(str, Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class QueryProgress(BaseModel):
    query: str
    papers_found: int = 0
    papers_new: int = 0
    papers_processed: int = 0
    chunks_indexed: int = 0
    status: str = "pending"
    error: Optional[str] = None


class IngestResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    queries: list[QueryProgress]
    total_papers_processed: int
    total_chunks_indexed: int
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Collection / stats
# ---------------------------------------------------------------------------

class CollectionInfo(BaseModel):
    collection_name: str
    exists: bool
    vectors_count: Optional[int] = None
    indexed_vectors_count: Optional[int] = None
    points_count: Optional[int] = None
    status: Optional[str] = None


class IngestedPaperInfo(BaseModel):
    paper_id: str
    title: str
    pdf_url: Optional[str]
    ingested_at: Optional[datetime]


class IngestedPapersResponse(BaseModel):
    total: int
    papers: list[IngestedPaperInfo]
