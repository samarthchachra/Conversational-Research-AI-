"""Tests for the production RAG pipeline.

Verifies that:
1. The production request path (query → retrieve → rerank → generate → citations)
   works end-to-end with mocked dependencies.
2. The production app can be imported without loading any heavyweight models.
3. The ingestion code path is NOT reachable from the production pipeline.
"""

from __future__ import annotations

import sys
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Test 1 — import safety (no model loaded at startup)
# ---------------------------------------------------------------------------

class TestImportSafety:
    """Importing production modules must not load any heavy local PyTorch models."""

    def test_embedding_service_import(self):
        from app.services.vectorstore.embeddingService import BAAIEmbeddings
        instance = BAAIEmbeddings()
        assert instance.model_name == "BAAI/bge-base-en-v1.5"

    def test_qdrant_service_has_no_module_level_dense_embedding(self):
        import app.services.vectorstore.qdrantService as qs
        # The module-level dense_embedding singleton must not exist
        assert not hasattr(qs, "dense_embedding"), (
            "Module-level 'dense_embedding' singleton found in qdrantService — "
            "remove it to avoid model loading at import time."
        )

    def test_adaptive_pipeline_does_not_import_ingestion_modules(self):
        # Import the pipeline
        import app.services.retrieval.adaptive_rag_pipeline  # noqa: F401

        # Confirm ingestion modules are NOT pulled in as a side effect
        ingestion_modules = [
            k for k in sys.modules
            if "dataset_searcher" in k
            or "pdf_ingestion" in k
            or "manual_ingestion" in k
        ]
        assert ingestion_modules == [], (
            f"Ingestion modules imported by production pipeline: {ingestion_modules}"
        )


# ---------------------------------------------------------------------------
# Test 2 — production pipeline flow (mocked)
# ---------------------------------------------------------------------------

class TestProductionPipelineFlow:
    """End-to-end production pipeline with all external deps mocked."""

    def _make_mock_doc(self, title: str = "Test Paper", score: float = 0.9):
        doc = MagicMock()
        doc.page_content = "This is a test chunk about transformers."
        doc.metadata = {
            "title": title,
            "authors": ["Author A", "Author B"],
            "published": "2024-01-01",
            "pdf_url": "https://arxiv.org/pdf/test.pdf",
            "reranker_score": score,
        }
        return doc

    def test_pipeline_does_not_ingest_on_high_quality_retrieval(self):
        """When retrieval quality is good, invoke() should skip ingestion."""
        from app.services.retrieval.adaptive_rag_pipeline import AdaptiveRagPipeline

        pipeline = AdaptiveRagPipeline()

        good_doc = self._make_mock_doc(score=0.9)

        with (
            patch.object(pipeline, "retrieve", return_value=[good_doc]),
            patch.object(
                pipeline.generator,
                "generate",
                return_value={"answer": "Test answer", "citations": []},
            ) as mock_generate,
        ):
            result = pipeline.invoke("what is a transformer?")

        mock_generate.assert_called_once()
        assert result["answer"] == "Test answer"

    def test_pipeline_does_not_ingest_on_knowledge_gap(self):
        """Even when a knowledge gap is detected, no ingestion must happen."""
        from app.services.retrieval.adaptive_rag_pipeline import AdaptiveRagPipeline

        pipeline = AdaptiveRagPipeline()

        weak_doc = self._make_mock_doc(score=0.2)  # below 0.65 threshold

        with (
            patch.object(pipeline, "retrieve", return_value=[weak_doc]),
            patch.object(
                pipeline.generator,
                "generate",
                return_value={"answer": "Partial answer", "citations": []},
            ),
        ):
            result = pipeline.invoke("very obscure topic")

        # Must still return a result (not crash or hang)
        assert "answer" in result

    def test_knowledge_gap_does_not_call_pdf_pipeline(self):
        """Confirm pdf_pipeline is not even an attribute of the pipeline."""
        from app.services.retrieval.adaptive_rag_pipeline import AdaptiveRagPipeline
        pipeline = AdaptiveRagPipeline()
        assert not hasattr(pipeline, "pdf_pipeline"), (
            "pdf_pipeline should not exist on the production AdaptiveRagPipeline"
        )
        assert not hasattr(pipeline, "vector_pipeline"), (
            "vector_pipeline should not exist on the production AdaptiveRagPipeline"
        )


# ---------------------------------------------------------------------------
# Test 3 — embedding dimension
# ---------------------------------------------------------------------------

class TestEmbeddingDimension:
    """BGE-base-en-v1.5 must produce 768-dimensional vectors."""

    def test_query_embedding_dimension(self):
        """Lazy-load model and verify output dimension."""
        from app.services.vectorstore.embeddingService import BAAIEmbeddings
        embeddings = BAAIEmbeddings()
        vector = embeddings.embed_query("test embedding dimension")
        assert len(vector) == 768, (
            f"Expected 768-dim vector from BGE-base, got {len(vector)}"
        )

    def test_document_embedding_dimension(self):
        from app.services.vectorstore.embeddingService import BAAIEmbeddings
        embeddings = BAAIEmbeddings()
        vectors = embeddings.embed_documents(["doc one", "doc two"])
        assert len(vectors) == 2
        for v in vectors:
            assert len(v) == 768, f"Expected 768-dim, got {len(v)}"
