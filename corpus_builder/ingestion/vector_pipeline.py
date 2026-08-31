"""Vector ingestion pipeline for the offline corpus builder.

Takes processed LangChain Documents, chunks them, generates dense + sparse
embeddings, and upserts into Qdrant. This is the final stage of the offline
corpus-building workflow.
"""

from __future__ import annotations

from langchain_core.documents import Document

from corpus_builder.processing.chunking import chunk_documents
from corpus_builder.vectorstore import QdrantWriter


class VectorPipeline:
    """Chunk → embed → upsert pipeline for the offline corpus builder.

    Usage:
        writer = QdrantWriter(embedding_provider)
        pipeline = VectorPipeline(writer)
        pipeline.run(documents)
    """

    def __init__(self, qdrant_writer: QdrantWriter):
        self.writer = qdrant_writer

    def run(self, documents: list[Document]) -> list[Document]:
        """Chunk documents and upsert all chunks into Qdrant.

        Args:
            documents: Processed paper Documents from PDFPipeline.run().

        Returns:
            The list of chunk Documents that were upserted.
        """
        if not documents:
            print("No documents to index.")
            return []

        print(f"\nChunking {len(documents)} document(s)...")
        chunks = chunk_documents(documents)
        print(f"Generated {len(chunks)} chunk(s).")

        self.writer.add_chunks(chunks)

        return chunks
