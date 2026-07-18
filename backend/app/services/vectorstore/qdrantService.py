from langchain_qdrant import (
    QdrantVectorStore,
    FastEmbedSparse,
    RetrievalMode
)

from langchain_huggingface import HuggingFaceEmbeddings

from qdrant_client import QdrantClient


COLLECTION_NAME = "research_papers"

URL = "http://localhost:6333"


dense_embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en"
)

sparse_embedding = FastEmbedSparse(
    model_name="Qdrant/bm25"
)


client = QdrantClient(
    url=URL
)


def get_vector_store(mode:RetrievalMode):

    return QdrantVectorStore.from_existing_collection(

        collection_name=COLLECTION_NAME,

        url=URL,

        embedding=dense_embedding,

        sparse_embedding=sparse_embedding,

        retrieval_mode=mode,
    )


def add_documents_to_vector_store(chunks):

    if not client.collection_exists(COLLECTION_NAME):

        print("Creating hybrid collection...")

        vector_store = QdrantVectorStore.from_documents(

            documents=chunks,

            embedding=dense_embedding,

            sparse_embedding=sparse_embedding,

            url=URL,

            collection_name=COLLECTION_NAME,

            retrieval_mode=RetrievalMode.HYBRID,
        )

        print(f"Added {len(chunks)} chunks.")

        return vector_store

    vector_store = get_vector_store(RetrievalMode.HYBRID)

    vector_store.add_documents(chunks)

    print(f"Added {len(chunks)} chunks.")

    return vector_store