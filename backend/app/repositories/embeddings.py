from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import EmbeddingReference


class EmbeddingReferenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_vector_id(self) -> int:
        current = self.db.scalar(select(func.max(EmbeddingReference.vector_id)))
        return int(current or 0) + 1

    def upsert(self, *, image_id: int, vector_id: int, model: str, source_field: str = "description") -> None:
        existing = self.db.scalar(select(EmbeddingReference).where(EmbeddingReference.image_id == image_id))
        if existing:
            existing.vector_id = vector_id
            existing.embedding_model = model
            existing.source_field = source_field
        else:
            self.db.add(
                EmbeddingReference(
                    image_id=image_id,
                    vector_id=vector_id,
                    embedding_model=model,
                    source_field=source_field,
                )
            )
        self.db.commit()

    def image_ids_for_vector_ids(self, vector_ids: list[int]) -> dict[int, int]:
        if not vector_ids:
            return {}
        rows = self.db.scalars(select(EmbeddingReference).where(EmbeddingReference.vector_id.in_(vector_ids))).all()
        return {row.vector_id: row.image_id for row in rows}

