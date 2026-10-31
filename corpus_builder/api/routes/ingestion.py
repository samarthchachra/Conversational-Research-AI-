"""Ingestion routes for the corpus builder API.

Endpoints:
    POST /ingest            — start a background ingestion job
    GET  /ingest/jobs       — list all jobs and their status
    GET  /ingest/jobs/{id}  — get detailed status of a specific job
    POST /ingest/sync       — synchronous ingestion (small batches / debugging)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from corpus_builder.api.schemas import (
    IngestRequest,
    IngestResponse,
    JobStatus,
    JobStatusResponse,
    QueryProgress,
)
from corpus_builder.api.job_store import create_job, get_job, list_jobs, JobState
from corpus_builder.config import DATASET_DIR
from corpus_builder.db import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _run_ingestion(job: JobState, request: IngestRequest) -> None:
    """Background task that runs the full ingestion pipeline for all queries."""
    from corpus_builder.embeddings import BAAIDocumentEmbeddings
    from corpus_builder.vectorstore import QdrantWriter
    from corpus_builder.ingestion import PDFPipeline
    from corpus_builder.ingestion.vector_pipeline import VectorPipeline

    job.status = JobStatus.RUNNING
    job.started_at = datetime.now(timezone.utc)

    try:
        # Initialise shared components once per job
        embedding = BAAIDocumentEmbeddings()
        writer = QdrantWriter(embedding)

        if not request.dry_run:
            writer.ensure_collection()

        pdf_pipeline = PDFPipeline(dataset_directory=DATASET_DIR)
        vector_pipeline = VectorPipeline(qdrant_writer=writer)

        db = get_db_session()

        try:
            for query in request.queries:
                qp: QueryProgress = job.query_progress[query]
                qp.status = "running"

                try:
                    # Step 1 — search + dedup + download + preprocess
                    papers_before = qp.papers_found
                    documents = pdf_pipeline.run(
                        db=db,
                        query=query,
                        top_k=request.top_k,
                    )

                    qp.papers_found  = request.top_k
                    qp.papers_new    = len(documents)
                    qp.papers_processed = len(documents)

                    if not request.dry_run and documents:
                        # Step 2 — chunk + embed + upsert
                        chunks = vector_pipeline.run(documents)
                        qp.chunks_indexed = len(chunks)

                        # Step 3 — record in PostgreSQL ONLY after successful Qdrant indexing
                        ingested_papers = [
                            {
                                "id": doc.metadata["paper_id"],
                                "title": doc.metadata["title"],
                                "pdf_url": doc.metadata.get("pdf_url", ""),
                            }
                            for doc in documents
                        ]
                        pdf_pipeline.repository.bulk_insert(db=db, papers=ingested_papers)

                    qp.status = "completed"

                except Exception as exc:
                    logger.exception("Query failed: %r", query)
                    qp.status = "failed"
                    qp.error  = str(exc)

        finally:
            db.close()

        job.status       = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)

    except Exception as exc:
        logger.exception("Job %s failed", job.job_id)
        job.status       = JobStatus.FAILED
        job.error        = str(exc)
        job.completed_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helper — convert JobState → JobStatusResponse
# ---------------------------------------------------------------------------

def _job_to_response(job: JobState) -> JobStatusResponse:
    return JobStatusResponse(
        job_id               = job.job_id,
        status               = job.status,
        started_at           = job.started_at,
        completed_at         = job.completed_at,
        queries              = list(job.query_progress.values()),
        total_papers_processed = job.total_papers_processed,
        total_chunks_indexed   = job.total_chunks_indexed,
        error                = job.error,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=IngestResponse,
    summary="Start a background ingestion job",
    description=(
        "Triggers the full corpus-building pipeline asynchronously. "
        "Returns a job_id you can poll with GET /ingest/jobs/{job_id}.\n\n"
        "Pipeline: JSONL search → dedup → PDF download → preprocess → "
        "chunk → BGE embed → BM25 sparse → Qdrant upsert → PostgreSQL record."
    ),
)
def start_ingestion(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
) -> IngestResponse:
    job = create_job(request.queries)
    background_tasks.add_task(_run_ingestion, job, request)

    return IngestResponse(
        job_id  = job.job_id,
        status  = JobStatus.PENDING,
        message = (
            f"Ingestion job started for {len(request.queries)} query/queries. "
            f"Poll GET /ingest/jobs/{job.job_id} for status."
        ),
    )


@router.get(
    "/jobs",
    response_model=list[JobStatusResponse],
    summary="List all ingestion jobs",
)
def list_all_jobs() -> list[JobStatusResponse]:
    return [_job_to_response(j) for j in list_jobs()]


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get status of a specific ingestion job",
)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return _job_to_response(job)


@router.post(
    "/sync",
    response_model=JobStatusResponse,
    summary="Synchronous ingestion (blocks until complete)",
    description=(
        "Runs the ingestion pipeline synchronously and returns when done. "
        "Use for small batches or debugging. For large corpora, use POST /ingest instead."
    ),
)
def ingest_sync(request: IngestRequest) -> JobStatusResponse:
    job = create_job(request.queries)
    _run_ingestion(job, request)      # blocking — intentional
    return _job_to_response(job)
