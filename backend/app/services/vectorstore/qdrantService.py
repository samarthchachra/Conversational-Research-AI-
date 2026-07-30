from langchain_qdrant import (
    QdrantVectorStore,
    FastEmbedSparse,
    RetrievalMode
)
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams
)

from langchain_huggingface import HuggingFaceEmbeddings

from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()


COLLECTION_NAME = "research_papers"

URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("QDRANT_API_KEY")


dense_embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en"
)

sparse_embedding = FastEmbedSparse(
    model_name="Qdrant/bm25"
)


client = QdrantClient(
    url=URL,
    api_key=API_KEY,
    check_compatibility=False
)


def get_vector_store(mode:RetrievalMode):

    return QdrantVectorStore.from_existing_collection(

        collection_name=COLLECTION_NAME,

        url=URL,

        api_key=API_KEY,

        embedding=dense_embedding,

        sparse_embedding=sparse_embedding,

        retrieval_mode=mode,
    )

def create_collection():

    collections = client.get_collections()

    existing = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME in existing:
        print(f"{COLLECTION_NAME} already exists")
        return

    print(f"Creating {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,

        vectors_config={
            "": VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        },

        sparse_vectors_config={
            "langchain-sparse": SparseVectorParams()
        }
    )

    print("Collection created successfully")

def add_documents_to_vector_store(chunks):

    if not client.collection_exists(COLLECTION_NAME):

        print("Creating hybrid collection...")

        vector_store = QdrantVectorStore.from_documents(

            documents=chunks,

            embedding=dense_embedding,

            sparse_embedding=sparse_embedding,

            url=URL,

            api_key = API_KEY,

            collection_name=COLLECTION_NAME,

            retrieval_mode=RetrievalMode.HYBRID,

        )

        print(f"Added {len(chunks)} chunks.")

        return vector_store

    vector_store = get_vector_store(RetrievalMode.HYBRID)

    vector_store.add_documents(chunks)

    print(f"Added {len(chunks)} chunks.")

    return vector_store