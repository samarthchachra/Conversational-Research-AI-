import os
import tempfile

import fitz
import requests
from sqlalchemy.orm import Session
from langchain_core.documents import Document

from app.services.dataset.dataset_searcher import DatasetSearcher
from app.services.processing.preprocessing_service import Processing
from app.repositories.research_paper_repo import IngestedPaperRepository
from app.database.database import SessionLocal




class PDFIngestionPipeline:

    def __init__(self, dataset_directory: str):

        self.dataset_directory = dataset_directory
        self.searcher = None
        self.processing = Processing()
        self.repository = IngestedPaperRepository()
    def get_searcher(self):
    
        if self.searcher is None:
        
            self.searcher = DatasetSearcher(
                self.dataset_directory
            )
    
        return self.searcher


    def search_papers(
        self,
        query: str,
        top_k: int = 20
    ):
        searcher = self.get_searcher()
        return searcher.search(
            query=query,
            top_k=top_k
        )
    

    def download_pdf(
        self,
        pdf_url: str
    ):

        response = requests.get(
            pdf_url,
            timeout=60
        )

        response.raise_for_status()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_file:

            tmp_file.write(response.content)

            return tmp_file.name
        

    def extract_pdf_text(
        self,
        pdf_path: str
    ):

        document = fitz.open(
            pdf_path
        )

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text
    

    def create_document(
        self,
        paper: dict,
        text: str
    ):

        return Document(

            page_content=text,

            metadata={

                "paper_id":
                    paper["id"],

                "title":
                    paper["title"],

                "authors":
                    paper["authors"],

                "published":
                    paper["published"],

                "categories":
                    paper["categories"],

                "primary_category":
                    paper["primary_category"],

                "pdf_url":
                    paper["pdf_url"],

                "abstract":
                    paper["abstract"]
            }
        )


    def process_paper(
            self,
            paper: dict
        ):

            pdf_path = None

            try:

                pdf_path = self.download_pdf(
                    paper["pdf_url"]
                )

                raw_text = self.extract_pdf_text(
                    pdf_path
                )

                cleaned_text = self.processing.preprocess_text(
                    raw_text
                )

                document = self.create_document(

                    paper,

                    cleaned_text
                )

                return document

            finally:

                if pdf_path and os.path.exists(pdf_path):

                    os.remove(pdf_path)

    def ingest(
        self,
        db:Session,
        query: str,
        top_k: int = 20
    ):

        papers = self.search_papers(
            query=query,
            top_k=top_k
        )

        paper_ids = [
            paper["id"]
            for paper in papers
        ]

        existing_ids = self.repository.get_existing_ids(
            db=db,
            paper_ids=paper_ids
        )

        papers = [
            paper
            for paper in papers
            if paper["id"] not in existing_ids
        ]

        print(
            f"\nFound {len(existing_ids)} already ingested papers."
        )

        print(
            f"Ingesting {len(papers)} new papers.\n"
        )

        documents = []

        ingested_papers = []

        for index, paper in enumerate(
            papers,
            start=1
        ):

            try:

                print(
                    f"[{index}/{len(papers)}] "
                    f"{paper['title']}"
                )

                document = self.process_paper(
                    paper
                )

                documents.append(
                    document
                )

                ingested_papers.append(
                    paper
                )

            except Exception as e:

                print(
                    f"Failed : {paper['title']}"
                )

                print(e)

        if ingested_papers:

            self.repository.bulk_insert(
                db=db,
                papers=ingested_papers
            )

        return documents