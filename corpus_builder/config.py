"""Corpus builder configuration.

All settings are read from environment variables so the corpus builder
can be run against any Qdrant instance and any local dataset directory
without modifying code.

Required env vars:
    QDRANT_URL          — Qdrant cloud or local URL
    QDRANT_API_KEY      — Qdrant API key (empty string for local)
    POSTGRES_URL        — PostgreSQL connection string

Optional env vars:
    DATASET_DIR         — Directory containing *.jsonl dataset files
                          (default: ./research-papers)
    COLLECTION_NAME     — Qdrant collection name (default: research_papers)
    BGE_MODEL           — HuggingFace model id for document embeddings
                          (default: BAAI/bge-base-en-v1.5)
    EMBED_BATCH_SIZE    — Batch size for document embedding (default: 32)
    HF_TOKEN            — HuggingFace token for private models (optional)
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Qdrant
# ---------------------------------------------------------------------------

QDRANT_URL: str = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "research_papers")

# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

# Path to the directory containing the *.jsonl research-paper dataset files.
# Points to backend/research-papers relative to the repo root.
DATASET_DIR: str = os.getenv("DATASET_DIR", "backend/research-papers")

# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

BGE_MODEL: str = os.getenv("BGE_MODEL", "BAAI/bge-base-en-v1.5")
EMBED_BATCH_SIZE: int = int(os.getenv("EMBED_BATCH_SIZE", "32"))
