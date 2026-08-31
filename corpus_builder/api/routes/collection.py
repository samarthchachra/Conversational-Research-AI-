"""Collection inspection routes for the corpus builder API.

Endpoints:
    GET /collection/info      — Qdrant collection metadata and vector counts
    GET /collection/papers    — List papers recorded in PostgreSQL
    DELETE /collection/reset  — Drop and recreate the Qdrant collection (DESTRUCTIVE)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from corpus_builder.api.schemas import (
    CollectionInfo,
    IngestedPapersResponse,
    IngestedPaperInfo,
)
from corpus_builder.config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
from corpus_builder.db import get_db_session, IngestedPaper

router = APIRouter(prefix="/collection", tags=["Collection"])


def _get_qdrant_client():
    from qdrant_client import QdrantClient
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        check_compatibility=False,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/info",
    response_model=CollectionInfo,
    summary="Qdrant collection metadata and vector counts",
)
def collection_info() -> CollectionInfo:
    client = _get_qdrant_client()

    if not client.collection_exists(COLLECTION_NAME):
        return CollectionInfo(
            collection_name=COLLECTION_NAME,
            exists=False,
        )

    info = client.get_collection(COLLECTION_NAME)

    return CollectionInfo(
        collection_name      = COLLECTION_NAME,
        exists               = True,
        vectors_count        = getattr(info, 'vectors_count', getattr(info, 'points_count', 0)),
        indexed_vectors_count= getattr(info, 'indexed_vectors_count', getattr(info, 'points_count', 0)),
        points_count         = getattr(info, 'points_count', 0),
        status               = str(getattr(info, 'status', 'green')),
    )


@router.get(
    "/papers",
    response_model=IngestedPapersResponse,
    summary="List papers recorded in PostgreSQL",
    description="Returns papers that have been successfully ingested and recorded in the database.",
)
def list_ingested_papers(
    limit: int  = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> IngestedPapersResponse:
    db = get_db_session()
    try:
        rows = (
            db.query(IngestedPaper)
            .order_by(IngestedPaper.ingested_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = db.query(IngestedPaper).count()
    finally:
        db.close()

    return IngestedPapersResponse(
        total=total,
        papers=[
            IngestedPaperInfo(
                paper_id   = r.paper_id,
                title      = r.title,
                pdf_url    = r.pdf_url,
                ingested_at= r.ingested_at,
            )
            for r in rows
        ],
    )


@router.delete(
    "/reset",
    summary="⚠️ Drop and recreate the Qdrant collection",
    description=(
        "**DESTRUCTIVE** — deletes all vectors in the Qdrant collection and "
        "removes all paper records from PostgreSQL. "
        "Use this only to start a fresh corpus build from scratch."
    ),
)
def reset_collection() -> dict:
    client = _get_qdrant_client()

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    # Clear PostgreSQL records
    db = get_db_session()
    try:
        db.query(IngestedPaper).delete()
        db.commit()
    finally:
        db.close()

    return {
        "message": f"Collection '{COLLECTION_NAME}' and all paper records deleted.",
        "collection": COLLECTION_NAME,
    }
