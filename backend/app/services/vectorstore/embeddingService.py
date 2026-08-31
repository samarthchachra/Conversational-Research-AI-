from __future__ import annotations

import os
import math
from langchain_core.embeddings import Embeddings

MODEL_NAME = "BAAI/bge-base-en-v1.5"


def _l2_normalize(vector: list[float]) -> list[float]:
    """L2-normalize a vector so cosine similarity in Qdrant works accurately."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


class BAAIEmbeddings(Embeddings):
    """Query embedding provider for BAAI/bge-base-en-v1.5 via HuggingFace InferenceClient.

    Uses the official huggingface_hub InferenceClient SDK to call HF Serverless API.
    Zero PyTorch or local model weights in memory — fits Render Free Tier (512MB limit).

    Set USE_LOCAL_EMBEDDINGS=true to load the model locally (for dev/testing only).
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        batch_size: int = 32,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.token = os.getenv("HF_TOKEN")
        self._client = None   # lazy — populated on first embedding call
        self._local_model = None

    # ------------------------------------------------------------------
    # HuggingFace InferenceClient (production)
    # ------------------------------------------------------------------

    def _get_client(self):
        if self._client is None:
            from huggingface_hub import InferenceClient
            self._client = InferenceClient(
                provider="hf-inference",
                api_key=self.token,
            )
        return self._client

    def _embed_one(self, text: str) -> list[float]:
        result = self._get_client().feature_extraction(
            text,
            model=self.model_name,
        )
        # result is a numpy array of shape (768,) or (N, 768)
        if hasattr(result, "shape") and len(result.shape) == 2:
            # Mean pool if token-level (N_tokens, dim)
            vector = result.mean(axis=0).tolist()
        else:
            vector = result.tolist()
        return _l2_normalize(vector)

    # ------------------------------------------------------------------
    # LangChain Embeddings interface
    # ------------------------------------------------------------------

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]