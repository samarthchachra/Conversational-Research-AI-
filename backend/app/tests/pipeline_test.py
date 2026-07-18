from app.services.ingestion.pdf_ingestion_pipeline import (
    PDFIngestionPipeline
)

from app.services.ingestion.vector_ingestion_pipeline import (
    VectorIngestionPipeline
)


pdf_pipeline = PDFIngestionPipeline(
    dataset_directory="research-papers"
)

documents = pdf_pipeline.ingest(
    query="vision transformer",
    top_k=5
)

vector_pipeline = VectorIngestionPipeline()

chunks = vector_pipeline.ingest(
    documents
)

print(chunks[0].metadata)

print(chunks[0].page_content[:300])
