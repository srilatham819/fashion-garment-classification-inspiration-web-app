from typing import Protocol

from app.repositories.embeddings import EmbeddingReferenceRepository
from app.core.config import settings
from app.services.embeddings import HashEmbeddingClient, OpenAIEmbeddingClient
from app.vector.faiss_index import FaissIndex


class EmbeddingClient(Protocol):
    model: str

    def embed_text(self, text: str) -> list[float]:
        ...


class SemanticIndexService:
    def __init__(
        self,
        *,
        embedding_refs: EmbeddingReferenceRepository,
        vector_index: FaissIndex | None = None,
        embedding_client: EmbeddingClient | None = None,
    ) -> None:
        self.embedding_refs = embedding_refs
        self.vector_index = vector_index or FaissIndex()
        self.embedding_client = embedding_client or self._default_embedding_client()

    def index_description(self, *, image_id: int, description: str) -> int:
        vector = self.embedding_client.embed_text(description)
        vector_id = self.embedding_refs.next_vector_id()
        self.vector_index.add(vector_id=vector_id, vector=vector)
        self.embedding_refs.upsert(
            image_id=image_id,
            vector_id=vector_id,
            model=self.embedding_client.model,
            source_field="description",
        )
        return vector_id

    def search(self, *, query: str, limit: int) -> list[tuple[int, float]]:
        if not query.strip():
            return []
        vector = self.embedding_client.embed_text(query)
        vector_matches = self.vector_index.search(vector=vector, limit=limit)
        image_ids_by_vector_id = self.embedding_refs.image_ids_for_vector_ids(
            [vector_id for vector_id, _score in vector_matches]
        )
        return [
            (image_ids_by_vector_id[vector_id], score)
            for vector_id, score in vector_matches
            if vector_id in image_ids_by_vector_id
        ]

    @staticmethod
    def _default_embedding_client() -> EmbeddingClient:
        if settings.openai_api_key:
            return OpenAIEmbeddingClient()
        return HashEmbeddingClient()
