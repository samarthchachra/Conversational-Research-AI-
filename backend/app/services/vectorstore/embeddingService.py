from __future__ import annotations

import os
import math
import requests
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

load_dotenv()

MODEL_NAME = "@cf/baai/bge-base-en-v1.5"


def _l2_normalize(vector: list[float]) -> list[float]:
    """L2-normalize a vector so cosine similarity in Qdrant works accurately."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


class BAAIEmbeddings(Embeddings):
    """Query embedding provider for BAAI/bge-base-en-v1.5 via Cloudflare Workers AI.

    Zero local model weights in memory — fits Render Free Tier (512MB limit).
    Produces 768-dimensional dense vectors identical to BAAI/bge-base-en-v1.5.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        batch_size: int = 32,
        timeout: int = 30,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.timeout = timeout
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID") or os.getenv("CLOUDFARE_ACCOUNT_ID")
        self.api_token = (
            os.getenv("CLOUDFLARE_API_TOKEN")
            or os.getenv("CLOUDFLARE_API_KEY")
            or os.getenv("CLOUDFARE_API_KEY")
            or os.getenv("CLOUDFARE_API_TOKEN")
        )

    def _get_api_url(self) -> str:
        if not self.account_id:
            raise ValueError(
                "CLOUDFLARE_ACCOUNT_ID is not set. Please set it in your environment or .env file."
            )
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model_name}"

    def _embed_one(self, text: str) -> list[float]:
        if not self.api_token:
            raise ValueError(
                "CLOUDFLARE_API_TOKEN is not set. Please set it in your environment or .env file."
            )

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {"text": [text]}

        response = requests.post(
            self._get_api_url(),
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            errors = data.get("errors", [])
            raise RuntimeError(f"Cloudflare Workers AI embedding error: {errors}")

        vector = data["result"]["data"][0]
        return _l2_normalize(vector)

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]
