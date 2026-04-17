from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIMetadata(Base):
    __tablename__ = "ai_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), unique=True, index=True)
    garment_type: Mapped[str] = mapped_column(String(255), index=True)
    style: Mapped[str] = mapped_column(String(255), index=True)
    material: Mapped[str] = mapped_column(String(255), index=True)
    color_palette: Mapped[list[str]] = mapped_column(JSON)
    pattern: Mapped[str] = mapped_column(String(255), default="unknown", index=True)
    season: Mapped[str] = mapped_column(String(255), default="unknown", index=True)
    occasion: Mapped[str] = mapped_column(String(255), index=True)
    consumer_profile: Mapped[str] = mapped_column(String(255), default="unknown", index=True)
    trend_notes: Mapped[str] = mapped_column(Text)
    location_context: Mapped[str] = mapped_column(Text, index=True)
    description: Mapped[str] = mapped_column(Text)
    raw_response: Mapped[dict] = mapped_column(JSON)
    model: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    image = relationship("Image", back_populates="ai_metadata")
