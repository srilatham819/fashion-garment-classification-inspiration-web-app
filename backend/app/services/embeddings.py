from hashlib import sha256

from openai import OpenAI

from app.core.config import settings


class OpenAIEmbeddingClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_embedding_model
        self.client: OpenAI | None = None

    def embed_text(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key)
        response = self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


class HashEmbeddingClient:
    """Deterministic local embedding client for tests and offline development."""

    def __init__(self, dimensions: int = 64, model: str = "hash-embedding-test") -> None:
        self.dimensions = dimensions
        self.model = model

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[idx] += 1.0
        return vector
