"""Cohere-powered reranker for the production RAG pipeline.

Replaces the local BAAI/bge-reranker-base CrossEncoder with the
Cohere Rerank API. No model is downloaded or loaded into memory —
reranking is a single HTTPS call to Cohere's API.

Benefits over local CrossEncoder:
  - Zero RAM overhead on Render (no ~1.1GB model in memory)
  - No startup latency for model loading
  - Cohere rerank-v3.5 quality is significantly better than bge-reranker-base
  - Free tier: 1,000 API calls/month
  - Paid: $2 / 1,000 calls (~$0.002 per chat message)

Required env var:
  COHERE_API_KEY   — get from https://dashboard.cohere.com/api-keys
"""

from __future__ import annotations

import os


class Reranker:
    """Cohere Rerank API wrapper.

    Provides the same interface as the old local CrossEncoder reranker
    so the rest of the pipeline (AdaptiveRagPipeline, ingestion_condition)
    requires zero changes.

    Reranker scores from Cohere are relevance probabilities in [0, 1].
    The ingestion_condition threshold of 0.35 works well with this scale.
    """

    def __init__(
        self,
        model: str = "rerank-v3.5",
    ):
        import cohere  # lazy import

        self.model = model
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError(
                "COHERE_API_KEY is not set. "
                "Add it to your .env file — get a free key at "
                "https://dashboard.cohere.com/api-keys"
            )
        self._client = cohere.Client(api_key)

    # ------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5,
    ) -> list:
        """Rerank documents using the Cohere Rerank API.

        Args:
            query:     The user's search query.
            documents: Retrieved LangChain Document objects (page_content + metadata).
            top_k:     Number of top documents to return after reranking.

        Returns:
            Top-k documents sorted by Cohere relevance score (descending),
            with `reranker_score` added to each document's metadata.
        """
        if not documents:
            return []

        passages = [doc.page_content for doc in documents]

        response = self._client.rerank(
            model=self.model,
            query=query,
            documents=passages,
            top_n=top_k,
            return_documents=False,   # we already have documents locally
        )

        reranked = []

        for result in response.results:
            doc = documents[result.index]
            doc.metadata["reranker_score"] = result.relevance_score
            reranked.append(doc)

        return reranked