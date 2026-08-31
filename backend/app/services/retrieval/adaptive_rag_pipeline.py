from __future__ import annotations

import logging

from langchain_qdrant import RetrievalMode

from app.services.retrieval.retriever import Retriever
from app.services.retrieval.reranker import Reranker
from app.services.retrieval.ingestion_condition import ingestionCondition
from app.services.generation.generation_service import GenerationService

logger = logging.getLogger(__name__)

# Maximum chunks kept per unique paper before reranking.
# Ensures the final top-5 spans multiple papers rather than
# being dominated by many chunks from one highly-similar paper.
MAX_CHUNKS_PER_PAPER = 2


class AdaptiveRagPipeline:
    """Production RAG pipeline.

    Request flow:
        query
          → hybrid retrieval (k=30, wide net)
          → paper-level diversification (max 2 chunks/paper)
          → Cohere reranking (top 5)
          → generation → citations

    Knowledge gap detection is preserved: if retrieval quality is poor, the
    gap is logged and generation continues with the best available context.
    Gaps are NOT resolved by ingesting new papers at request time — that
    responsibility belongs to the offline corpus builder.
    """

    def __init__(self):
        self.retriever = Retriever()
        self.reranker  = Reranker()
        self.generator = GenerationService()
        self.detector  = ingestionCondition()

    # ------------------------------------------------------------------

    def _diversify(self, docs: list) -> list:
        """Cap chunks per paper to MAX_CHUNKS_PER_PAPER before reranking.

        Guarantees that multiple papers are represented in the reranker's
        input pool, so the final top-5 can draw from diverse sources.

        Paper identity is determined by the 'title' metadata field.
        Chunks are kept in the order Qdrant returned them (highest
        similarity first), so we always retain the best chunks per paper.
        """
        seen: dict[str, int] = {}   # title → count
        diverse = []

        for doc in docs:
            title = doc.metadata.get("title", "unknown")
            count = seen.get(title, 0)
            if count < MAX_CHUNKS_PER_PAPER:
                diverse.append(doc)
                seen[title] = count + 1

        logger.debug(
            "Diversification: %d chunks → %d chunks (%d unique papers)",
            len(docs), len(diverse), len(seen)
        )
        return diverse

    # ------------------------------------------------------------------

    def retrieve(self, query: str) -> list:
        # Cast a wide net — retrieve more so diversification has room to work
        docs = self.retriever.retrieve(
            query=query,
            mode=RetrievalMode.HYBRID,
            k=30,
        )

        # Ensure diverse paper coverage before reranking
        docs = self._diversify(docs)

        # Rerank the diverse pool — Cohere picks the best 5
        docs = self.reranker.rerank(
            query=query,
            documents=docs,
            top_k=5,
        )

        unique_papers = {d.metadata.get("title") for d in docs}
        print(f"\nRetrieved top-5 from {len(unique_papers)} unique paper(s):")
        for i, doc in enumerate(docs):
            score = doc.metadata.get("reranker_score", 0)
            print(f"  [{i}] {score:.4f} | {doc.metadata.get('title', 'N/A')}")

        return docs

    # ------------------------------------------------------------------

    def invoke(self, query: str) -> dict:
        print("\nRetrieving...\n")

        documents = self.retrieve(query)

        # Knowledge gap detection — log only, do NOT ingest at request time.
        if self.detector.should_ingest(documents):
            logger.warning(
                "Knowledge gap detected for query: %r — "
                "proceeding with best available context. "
                "Run the corpus builder to index additional papers.",
                query
            )
            print(
                "\nKnowledge gap detected — continuing with available context.\n"
                "Tip: run the corpus builder to index more papers for this topic.\n"
            )

        return self.generator.generate(
            question=query,
            documents=documents,
        )