from langchain_qdrant import RetrievalMode

from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.ingestion_condition import ingestionCondition

from app.services.ingestion.pdf_ingestion_pipeline import PDFIngestionPipeline
from app.services.ingestion.vector_ingestion_pipeline import VectorIngestionPipeline

from app.services.generation.generation_service import GenerationService

from app.database.database import SessionLocal

db = SessionLocal()

class AdaptiveRagPipeline:

    def __init__(self):

        self.retriever = Retriever()

        self.reranker = Reranker()

        self.generator = GenerationService()

        self.detector = ingestionCondition()

        self.pdf_pipeline = PDFIngestionPipeline(
            dataset_directory="research-papers"
        )

        self.vector_pipeline = VectorIngestionPipeline()

        

    def retrieve(
        self,
        query
    ):

        docs = self.retriever.retrieve(

            query=query,

            mode=RetrievalMode.HYBRID,

            k=20
        )

        docs = self.reranker.rerank(

            query=query,

            documents=docs,

            top_k=5
        )
        for i, doc in enumerate(docs):

            print(i)
        
            print(doc.metadata["title"])
        
            print("-" * 80)

        return docs
    

    def invoke(
        self,
        query
    ):

        print("\nRetrieving...\n")

        documents = self.retrieve(
            query
        )

        if self.detector.should_ingest(
            documents
        ):

            print(
                "\nKnowledge gap detected.\n"
            )

            new_documents = self.pdf_pipeline.ingest(
                db=db,
                query=query,
                top_k=20
            )

            self.vector_pipeline.ingest(
                new_documents
            )
            
            print(
                "\nRetrying Retrieval...\n"
            )

            documents = self.retrieve(
                query
            )

        return self.generator.generate(

            question=query,

            documents=documents
        )