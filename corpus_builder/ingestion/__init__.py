"""PDF ingestion pipeline for the offline corpus builder.

Orchestrates: dataset search → deduplication → PDF download →
              text extraction → preprocessing → LangChain Documents

No dependency on the backend/ production app.
"""

from __future__ import annotations

import os
import tempfile

import fitz  # PyMuPDF
import requests
from sqlalchemy.orm import Session
from langchain_core.documents import Document

from corpus_builder.dataset import DatasetSearcher
from corpus_builder.processing import Preprocessing
from corpus_builder.db import PaperRepository


class PDFPipeline:
    """Download and process research PDFs from dataset search results.

    Steps for each paper:
        1. Download PDF to a temporary file
        2. Extract raw text with PyMuPDF
        3. Clean text with Preprocessing
        4. Wrap in a LangChain Document with full metadata
    """

    def __init__(self, dataset_directory: str):
        self.dataset_directory = dataset_directory
        self._searcher: DatasetSearcher | None = None
        self.processing = Preprocessing()
        self.repository = PaperRepository()

    # -----------------------------------------------------------------------
    # Lazy dataset searcher (avoids loading 700 MB of JSONL at import time)
    # -----------------------------------------------------------------------

    def _get_searcher(self) -> DatasetSearcher:
        if self._searcher is None:
            self._searcher = DatasetSearcher(self.dataset_directory)
        return self._searcher

    # -----------------------------------------------------------------------

    def search_papers(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[dict]:
        return self._get_searcher().search(query=query, top_k=top_k)

    def download_pdf(self, pdf_url: str) -> str:
        """Download PDF to a temp file and return the file path."""
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            return tmp.name

    def extract_text(self, pdf_path: str) -> str:
        """Extract plain text from a PDF file using PyMuPDF."""
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text

    def _make_document(self, paper: dict, text: str) -> Document:
        return Document(
            page_content=text,
            metadata={
                "paper_id":        paper["id"],
                "title":           paper["title"],
                "authors":         paper["authors"],
                "published":       paper["published"],
                "categories":      paper.get("categories", []),
                "primary_category": paper.get("primary_category", ""),
                "pdf_url":         paper["pdf_url"],
                "abstract":        paper.get("abstract", ""),
            },
        )

    def process_paper(self, paper: dict) -> Document | None:
        """Download, extract, and preprocess a single paper. Returns None on failure."""
        pdf_path = None
        try:
            pdf_path = self.download_pdf(paper["pdf_url"])
            raw_text = self.extract_text(pdf_path)
            cleaned  = Preprocessing.preprocess(raw_text)
            return self._make_document(paper, cleaned)
        except Exception as exc:
            print(f"  [SKIP] {paper['title']}: {exc}")
            return None
        finally:
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)

    # -----------------------------------------------------------------------

    def run(
        self,
        db: Session,
        query: str,
        top_k: int = 20,
    ) -> list[Document]:
        """Full pipeline: search → deduplicate → download → process.

        Args:
            db:     SQLAlchemy session for deduplication check and recording.
            query:  Search query used to find relevant papers.
            top_k:  Number of papers to retrieve from the dataset.

        Returns:
            List of processed LangChain Documents (new papers only).
        """
        papers = self.search_papers(query=query, top_k=top_k)

        paper_ids = [p["id"] for p in papers]
        existing  = self.repository.get_existing_ids(db=db, paper_ids=paper_ids)
        new_papers = [p for p in papers if p["id"] not in existing]

        print(f"\nAlready indexed: {len(existing)} | New papers to process: {len(new_papers)}\n")

        documents: list[Document] = []
        ingested: list[dict] = []

        for i, paper in enumerate(new_papers, start=1):
            print(f"[{i}/{len(new_papers)}] {paper['title']}")
            doc = self.process_paper(paper)
            if doc is not None:
                documents.append(doc)
                ingested.append(paper)

        if ingested:
            self.repository.bulk_insert(db=db, papers=ingested)
            print(f"\nRecorded {len(ingested)} new papers in the database.")

        return documents
