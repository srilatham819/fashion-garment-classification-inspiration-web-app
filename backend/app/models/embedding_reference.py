from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmbeddingReference(Base):
    __tablename__ = "embedding_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), unique=True, index=True)
    vector_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    embedding_model: Mapped[str] = mapped_column(String(255))
    source_field: Mapped[str] = mapped_column(String(255), default="description")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    image = relationship("Image", back_populates="embedding")

