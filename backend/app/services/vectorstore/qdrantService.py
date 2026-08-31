from __future__ import annotations

from dotenv import load_dotenv
import os

from qdrant_client import QdrantClient
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

load_dotenv()


COLLECTION_NAME = "research_papers"

URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("QDRANT_API_KEY")


# Lightweight network client — safe to create at module level.
client = QdrantClient(
    url=URL,
    api_key=API_KEY,
    check_compatibility=False,
)

# Sparse embedding is a tiny BM25 tokenizer, not a neural model — fine at module level.
sparse_embedding = FastEmbedSparse(
    model_name="Qdrant/bm25"
)

# Dense embedding is lazily initialized so the BGE model is NOT loaded at import time.
_dense_embedding = None


def _get_dense_embedding():
    """Return the BAAIEmbeddings instance, creating it on the first call.

    The SentenceTransformer model is only loaded when a retrieval or
    collection-creation operation is actually needed, not at server startup.
    """
    global _dense_embedding
    if _dense_embedding is None:
        from app.services.vectorstore.embeddingService import BAAIEmbeddings
        _dense_embedding = BAAIEmbeddings()
    return _dense_embedding


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------

def create_collection():

    if client.collection_exists(COLLECTION_NAME):

        print(f"{COLLECTION_NAME} already exists")

        return

    print(f"Creating {COLLECTION_NAME}")

    dense = _get_dense_embedding()

    dimension = len(
        dense.embed_query("test")
    )

    client.create_collection(

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

    print("Collection created successfully")


# ---------------------------------------------------------------------------
# Vector store access (read / retrieval path)
# ---------------------------------------------------------------------------

def get_vector_store(
    mode: RetrievalMode,
):
    if not client.collection_exists(COLLECTION_NAME):

        create_collection()

    return QdrantVectorStore.from_existing_collection(

        collection_name=COLLECTION_NAME,

        url=URL,

        api_key=API_KEY,

        embedding=_get_dense_embedding(),

        sparse_embedding=sparse_embedding,

        retrieval_mode=mode,
    )


# ---------------------------------------------------------------------------
# Write path (used by the offline corpus builder, not the production API)
# ---------------------------------------------------------------------------

def add_documents_to_vector_store(
    chunks,
):

    if not client.collection_exists(COLLECTION_NAME):

        create_collection()

    vector_store = get_vector_store(
        RetrievalMode.HYBRID
    )

    vector_store.add_documents(
        chunks
    )

    print(
        f"Added {len(chunks)} chunks."
    )

    return vector_store