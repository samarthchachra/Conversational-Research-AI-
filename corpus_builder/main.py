#!/usr/bin/env python3
"""Offline corpus builder — CLI entry point.

This script indexes research papers from local JSONL dataset files into
Qdrant. It is entirely separate from the production FastAPI service and
should NEVER be run inside the Render deployment.

Usage examples:

    # Index papers relevant to a query topic
    python -m corpus_builder.main --query "transformer attention mechanisms" --top-k 20

    # Use a custom dataset directory
    DATASET_DIR=/data/papers python -m corpus_builder.main --query "reinforcement learning"

    # Dry-run: search and show papers that would be indexed, without downloading
    python -m corpus_builder.main --query "vision transformers" --dry-run

    # Index multiple topics in one run
    python -m corpus_builder.main \\
        --query "large language models" \\
        --query "retrieval augmented generation" \\
        --top-k 30

Environment variables (set in .env or shell):
    QDRANT_URL          Qdrant cloud or local URL (required)
    QDRANT_API_KEY      Qdrant API key (required for cloud)
    POSTGRES_URL        PostgreSQL connection string (required)
    DATASET_DIR         Path to directory with *.jsonl files
                        (default: ./research-papers)
    BGE_MODEL           Embedding model (default: BAAI/bge-base-en-v1.5)
    EMBED_BATCH_SIZE    Batch size for embedding (default: 32)
"""

from __future__ import annotations

import argparse
import sys

from corpus_builder.config import DATASET_DIR, QDRANT_URL, POSTGRES_URL
from corpus_builder.embeddings import BAAIDocumentEmbeddings
from corpus_builder.vectorstore import QdrantWriter
from corpus_builder.ingestion import PDFPipeline
from corpus_builder.ingestion.vector_pipeline import VectorPipeline
from corpus_builder.db import get_db_session


def _validate_env() -> None:
    """Fail fast if required environment variables are missing."""
    missing = []
    if not QDRANT_URL:
        missing.append("QDRANT_URL")
    if not POSTGRES_URL:
        missing.append("POSTGRES_URL")
    if missing:
        print(
            f"[ERROR] Missing required environment variable(s): {', '.join(missing)}\n"
            "Create a .env file in the corpus_builder/ directory (see .env.example)."
        )
        sys.exit(1)


def build_corpus(
    queries: list[str],
    top_k: int,
    dry_run: bool,
) -> None:
    """Run the full offline corpus-building pipeline.

    Flow for each query:
        JSONL search → deduplication → PDF download → preprocessing
        → chunking → BGE embeddings → BM25 sparse → Qdrant upsert
        → PostgreSQL record
    """
    _validate_env()

    print("=" * 70)
    print("OFFLINE CORPUS BUILDER")
    print("=" * 70)
    print(f"Dataset directory : {DATASET_DIR}")
    print(f"Qdrant URL        : {QDRANT_URL}")
    print(f"Queries           : {queries}")
    print(f"Top-K per query   : {top_k}")
    print(f"Dry run           : {dry_run}")
    print("=" * 70 + "\n")

    # -- Embeddings & Qdrant writer ----------------------------------------
    embedding = BAAIDocumentEmbeddings()
    writer = QdrantWriter(embedding)

    if not dry_run:
        writer.ensure_collection()

    # -- Pipelines ----------------------------------------------------------
    pdf_pipeline    = PDFPipeline(dataset_directory=DATASET_DIR)
    vector_pipeline = VectorPipeline(qdrant_writer=writer)

    total_papers = 0
    total_chunks = 0

    db = get_db_session()

    try:
        for query in queries:

            print(f"\n{'='*70}")
            print(f"QUERY: {query!r}")
            print(f"{'='*70}")

            # Step 1: search + dedup + download + preprocess
            documents = pdf_pipeline.run(
                db=db,
                query=query,
                top_k=top_k,
            )

            if not documents:
                print("No new documents to index for this query.")
                continue

            if dry_run:
                print(f"\n[DRY RUN] Would index {len(documents)} document(s). "
                      "Skipping embedding and Qdrant upsert.\n")
                total_papers += len(documents)
                continue

            # Step 2: chunk + embed + upsert
            chunks = vector_pipeline.run(documents)

            total_papers += len(documents)
            total_chunks += len(chunks)

    finally:
        db.close()

    # -- Summary ------------------------------------------------------------
    print("\n" + "=" * 70)
    print("CORPUS BUILD COMPLETE")
    print("=" * 70)
    print(f"Papers processed : {total_papers}")
    if not dry_run:
        print(f"Chunks indexed   : {total_chunks}")
    print("=" * 70 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline research-paper corpus builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        metavar="QUERY",
        required=True,
        help="Search query to find relevant papers (can be repeated for multiple topics).",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of papers to retrieve per query (default: 20).",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search and preprocess only — do not embed or write to Qdrant.",
    )

    args = parser.parse_args()

    build_corpus(
        queries=args.queries,
        top_k=args.top_k,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
