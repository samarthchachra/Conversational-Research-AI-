"""BGE document embedding provider for the offline corpus builder.

This is the DOCUMENT embedding side — used for indexing large batches of
paper chunks into Qdrant. It is intentionally separate from the production
query embedding in backend/app/services/vectorstore/embeddingService.py.

Key differences vs. the production embedding:
  - batch_size default is larger (suitable for bulk indexing)
  - show_progress_bar is enabled by default (useful for long offline runs)
  - No lazy loading — in the corpus builder we always want the model ready
    at startup since we know we're doing heavy embedding work

The model output dimension is 768 for BAAI/bge-base-en-v1.5, which must
match the Qdrant collection's dense vector dimension.
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

from corpus_builder.config import BGE_MODEL, EMBED_BATCH_SIZE


EXPECTED_DIMENSION = 768  # BAAI/bge-base-en-v1.5 output dimension


class BAAIDocumentEmbeddings(Embeddings):
    """Batch document embeddings using BAAI/bge-base-en-v1.5.

    Designed for offline bulk encoding of paper chunks. Embeddings are
    L2-normalized so cosine similarity in Qdrant works correctly.
    """

    def __init__(
        self,
        model_name: str = BGE_MODEL,
        batch_size: int = EMBED_BATCH_SIZE,
    ):
        self.model_name = model_name
        self.batch_size = batch_size

        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Verify dimension at construction time so misconfiguration fails fast.
        test_dim = len(self.embed_query("dimension check"))
        if test_dim != EXPECTED_DIMENSION:
            raise ValueError(
                f"Embedding model '{model_name}' produced {test_dim}-dim vectors; "
                f"expected {EXPECTED_DIMENSION}. "
                "Update EXPECTED_DIMENSION or choose a compatible model."
            )

        print(f"Embedding model ready. Dimension: {test_dim}\n")

    # -----------------------------------------------------------------------

    def embed_query(self, text: str) -> list[float]:
        """Embed a single text (query or short string)."""
        return (
            self.model
            .encode(text, normalize_embeddings=True, convert_to_numpy=True)
            .tolist()
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of document texts.

        Processes in batches of `batch_size` to avoid OOM on large corpora.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()
