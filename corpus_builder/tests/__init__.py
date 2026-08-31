"""Tests for the offline corpus builder.

Uses synthetic data so no real JSONL files or network access is needed.
"""

from __future__ import annotations

import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_jsonl_dir():
    """Create a temp directory with a small synthetic JSONL dataset."""
    records = [
        {
            "id": f"paper_{i}",
            "title": f"Test Paper {i} on Transformers",
            "abstract": f"This paper discusses transformer architecture variant {i}.",
            "authors": ["Alice", "Bob"],
            "published": "2024-01-01",
            "categories": ["cs.AI"],
            "primary_category": "cs.AI",
            "pdf_url": f"https://arxiv.org/pdf/{i}.pdf",
        }
        for i in range(50)
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        jsonl_path = os.path.join(tmpdir, "test_papers.jsonl")
        with open(jsonl_path, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        yield tmpdir


# ---------------------------------------------------------------------------
# Test 1 — DatasetSearcher
# ---------------------------------------------------------------------------

class TestDatasetSearcher:

    def test_loads_records_and_returns_results(self, synthetic_jsonl_dir):
        from corpus_builder.dataset import DatasetSearcher
        searcher = DatasetSearcher(synthetic_jsonl_dir)
        results = searcher.search("transformer architecture", top_k=5)
        assert len(results) <= 5
        assert all("id" in r for r in results)
        assert all("score" in r for r in results)

    def test_deduplicates_records(self, synthetic_jsonl_dir):
        """If the same paper appears in multiple JSONL files, it should only appear once."""
        from corpus_builder.dataset import DatasetSearcher
        # Write a second JSONL file with overlapping IDs
        import shutil
        src = os.path.join(synthetic_jsonl_dir, "test_papers.jsonl")
        dst = os.path.join(synthetic_jsonl_dir, "test_papers_dup.jsonl")
        shutil.copy(src, dst)

        searcher = DatasetSearcher(synthetic_jsonl_dir)
        # Total unique records should still be 50, not 100
        assert len(searcher.records) == 50

    def test_raises_on_missing_directory(self, tmp_path):
        from corpus_builder.dataset import DatasetSearcher
        with pytest.raises(FileNotFoundError):
            DatasetSearcher(str(tmp_path / "nonexistent"))


# ---------------------------------------------------------------------------
# Test 2 — Preprocessing
# ---------------------------------------------------------------------------

class TestPreprocessing:

    def test_removes_references_section(self):
        from corpus_builder.processing import Preprocessing
        text = "Introduction text. References\n[1] Smith 2020."
        result = Preprocessing.preprocess(text)
        assert "References" not in result
        assert "Introduction text" in result

    def test_fixes_hyphenation(self):
        from corpus_builder.processing import Preprocessing
        text = "trans-\nformer model"
        result = Preprocessing.preprocess(text)
        assert "transformer" in result

    def test_removes_extra_whitespace(self):
        from corpus_builder.processing import Preprocessing
        text = "word1   word2\n\n\nword3"
        result = Preprocessing.preprocess(text)
        assert "  " not in result


# ---------------------------------------------------------------------------
# Test 3 — Chunking
# ---------------------------------------------------------------------------

class TestChunking:

    def test_splits_long_document(self):
        from langchain_core.documents import Document
        from corpus_builder.processing.chunking import chunk_documents
        long_text = "This is a sentence about research. " * 200
        doc = Document(
            page_content=long_text,
            metadata={"title": "Long Paper", "authors": [], "pdf_url": ""},
        )
        chunks = chunk_documents([doc])
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk.page_content) <= 2000 + 100  # chunk_size with small tolerance

    def test_metadata_propagates_to_chunks(self):
        from langchain_core.documents import Document
        from corpus_builder.processing.chunking import chunk_documents
        text = "word " * 500
        doc = Document(
            page_content=text,
            metadata={"title": "Meta Paper", "authors": ["X"], "pdf_url": "u"},
        )
        chunks = chunk_documents([doc])
        for chunk in chunks:
            assert chunk.metadata["title"] == "Meta Paper"


# ---------------------------------------------------------------------------
# Test 4 — PDFPipeline deduplication (mocked DB + download)
# ---------------------------------------------------------------------------

class TestPDFPipelineDeduplication:

    def test_skips_already_indexed_papers(self, synthetic_jsonl_dir):
        """Papers whose IDs are already in the DB should not be downloaded."""
        from corpus_builder.ingestion import PDFPipeline
        from corpus_builder.db import PaperRepository

        pipeline = PDFPipeline(dataset_directory=synthetic_jsonl_dir)

        mock_db = MagicMock()
        mock_repo = MagicMock(spec=PaperRepository)
        pipeline.repository = mock_repo

        # Pretend all 50 papers are already indexed
        mock_repo.get_existing_ids.return_value = {f"paper_{i}" for i in range(50)}

        with patch.object(pipeline, "download_pdf") as mock_download:
            docs = pipeline.run(db=mock_db, query="transformer", top_k=10)

        mock_download.assert_not_called()
        assert docs == []


# ---------------------------------------------------------------------------
# Test 5 — Dimension consistency
# ---------------------------------------------------------------------------

class TestDimensionConsistency:
    """Query and document embeddings must have the same dimension (768)."""

    def test_corpus_builder_embedding_dimension(self):
        """BAAIDocumentEmbeddings must produce 768-dim vectors."""
        from corpus_builder.embeddings import BAAIDocumentEmbeddings
        emb = BAAIDocumentEmbeddings()
        q_vec = emb.embed_query("test")
        assert len(q_vec) == 768, f"Expected 768, got {len(q_vec)}"
        d_vecs = emb.embed_documents(["doc a", "doc b"])
        for v in d_vecs:
            assert len(v) == 768
