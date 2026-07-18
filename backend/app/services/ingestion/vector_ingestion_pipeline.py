from langchain_core.documents import Document

from app.services.processing.chunkingService import (
    chunk_document
)

from app.services.vectorstore.qdrantService import (
    add_documents_to_vector_store
)
# from app.services.ingestion.bm25_service import ( BM25Indexer )

class VectorIngestionPipeline:

    def __init__(self):
        pass



    def chunk_documents(
        self,
        documents: list[Document]
    ):

        return chunk_document(
            documents
        )



    def store_chunks(
        self,
        chunks: list[Document]
    ):

        add_documents_to_vector_store(
            chunks
        )



    def ingest(
        self,
        documents: list[Document]
    ):

        chunks = self.chunk_documents(
            documents
        )

        print(
            f"Generated {len(chunks)} chunks."
        )

        # bm25_indexer = BM25Indexer()
        # bm25_indexer.build_and_save(chunks)

        self.store_chunks(
            chunks
        )

        print(
            "Successfully stored in Qdrant."
        )

        return chunks