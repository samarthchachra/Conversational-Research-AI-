from app.services.ingestion.pdf_ingestion_pipeline import (
    PDFIngestionPipeline
)

from app.services.ingestion.vector_ingestion_pipeline import (
    VectorIngestionPipeline
)
from app.database.database import get_db

db =next(get_db())

class ManualIngestionService:

    def __init__(self):

        self.pdf_pipeline = PDFIngestionPipeline(
            dataset_directory="research-papers"
        )

        self.vector_pipeline = VectorIngestionPipeline()

    ###########################################################

    def ingest(
        self,
        query: str,
        top_k: int
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