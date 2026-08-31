from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.ingestion.pdf_ingestion_pipeline import (
    PDFIngestionPipeline
)

from app.services.ingestion.vector_ingestion_pipeline import (
    VectorIngestionPipeline
)


class ManualIngestionService:
    """Offline ingestion facade — not used in the production request path.

    This service is intentionally NOT registered on the production FastAPI
    router. It exists so the ingestion endpoint can be re-enabled locally
    or moved to the corpus builder CLI.
    """

    def __init__(self, dataset_directory: str = "research-papers"):

        self.pdf_pipeline = PDFIngestionPipeline(
            dataset_directory=dataset_directory
        )

        self.vector_pipeline = VectorIngestionPipeline()

    ###########################################################

    def ingest(
        self,
        db: Session,
        query: str,
        top_k: int = 20
    ):

        documents = self.pdf_pipeline.ingest(
            db=db,
            query=query,
            top_k=top_k
        )

        chunks = self.vector_pipeline.ingest(
            documents
        )

        return {

            "ingested_documents": len(documents),

            "ingested_chunks": len(chunks),

            "message": "Documents ingested successfully."
        }