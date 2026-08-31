"""Qdrant write client for the offline corpus builder.

Handles collection creation and bulk document upsert. This module is the
WRITE path — it is only used by the corpus builder, never by the production
FastAPI service (which is read-only).

The collection schema matches what the production retriever expects:
  - Dense vector: "" (unnamed), COSINE distance, dim=768 (BGE-base)
  - Sparse vector: "langchain-sparse" (BM25)
"""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http.models import models as rest
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
)
from langchain_qdrant import (
    QdrantVectorStore,
    FastEmbedSparse,
    RetrievalMode,
)
from langchain_core.documents import Document

from corpus_builder.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    COLLECTION_NAME,
)
from corpus_builder.embeddings import BAAIDocumentEmbeddings

# Number of chunks sent per Qdrant upsert request.
# Keeping this small avoids WriteTimeout on slow or metered cloud connections.
UPLOAD_BATCH_SIZE = 50


class QdrantWriter:
    """Manages Qdrant collection creation and document upsert for the corpus builder.

    Usage:
        writer = QdrantWriter(embedding_provider)
        writer.ensure_collection()
        writer.add_chunks(chunks)
    """

    def __init__(self, embedding_provider: BAAIDocumentEmbeddings):
        self.embedding = embedding_provider

        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            check_compatibility=False,
            timeout=120,          # seconds — prevents WriteTimeout on large batches
        )

        self.sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")

    # -----------------------------------------------------------------------

    def ensure_collection(self) -> None:
        """Create the Qdrant collection if it does not already exist.

        Does NOT recreate or modify an existing collection, so this is safe
        to call on a partially-indexed corpus.
        """
        if self.client.collection_exists(COLLECTION_NAME):
            print(f"Collection '{COLLECTION_NAME}' already exists — skipping creation.")
            return

        print(f"Creating collection '{COLLECTION_NAME}'...")

        dimension = len(self.embedding.embed_query("dimension probe"))

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "": VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "langchain-sparse": SparseVectorParams()
            },
        )

        print(f"Collection '{COLLECTION_NAME}' created (dim={dimension}).")

    # -----------------------------------------------------------------------

    def add_chunks(self, chunks: list[Document]) -> None:
        """Upsert chunks into Qdrant in batches to avoid WriteTimeout.

        Sends UPLOAD_BATCH_SIZE chunks per request. Dense embeddings come from
        BAAIDocumentEmbeddings; sparse (BM25) from FastEmbedSparse.

        Args:
            chunks: List of LangChain Document objects with page_content and metadata.
        """
        if not chunks:
            print("No chunks to add — skipping.")
            return

        vector_store = QdrantVectorStore.from_existing_collection(
            collection_name=COLLECTION_NAME,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            embedding=self.embedding,
            sparse_embedding=self.sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID,
        )

        total = len(chunks)
        uploaded = 0

        for i in range(0, total, UPLOAD_BATCH_SIZE):
            batch = chunks[i : i + UPLOAD_BATCH_SIZE]
            vector_store.add_documents(batch)
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{total} chunks...")

        print(f"Upserted {total} chunks into '{COLLECTION_NAME}'.")
