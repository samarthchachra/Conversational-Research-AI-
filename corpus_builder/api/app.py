"""Corpus builder FastAPI application.

This is a LOCAL-ONLY service. Run it on your machine to index papers
into Qdrant. Never deploy this to Render.

Start with:
    uvicorn corpus_builder.api.app:app --reload --port 8001
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from corpus_builder.api.routes.ingestion import router as ingestion_router
from corpus_builder.api.routes.collection import router as collection_router
from corpus_builder.config import QDRANT_URL, DATASET_DIR, COLLECTION_NAME


app = FastAPI(
    title="Corpus Builder API",
    description=(
        "**Local-only** service for indexing research papers into Qdrant.\n\n"
        "**Do not deploy this to Render or any public server.**\n\n"
        "## Pipeline\n"
        "```\n"
        "JSONL dataset search\n"
        "  → Paper deduplication (PostgreSQL)\n"
        "  → PDF download (arXiv)\n"
        "  → Text extraction (PyMuPDF)\n"
        "  → Preprocessing\n"
        "  → Chunking\n"
        "  → BGE dense embeddings (BAAI/bge-base-en-v1.5)\n"
        "  → BM25 sparse embeddings (Qdrant/bm25)\n"
        "  → Qdrant upsert\n"
        "  → PostgreSQL record\n"
        "```\n"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(collection_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service":        "Corpus Builder API",
        "status":         "running",
        "docs":           "/docs",
        "qdrant_url":     QDRANT_URL,
        "collection":     COLLECTION_NAME,
        "dataset_dir":    DATASET_DIR,
        "warning":        "Local use only — do not deploy to production.",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
