from sqlalchemy import String, cast, select
from sqlalchemy.orm import Session

from app.models import AIMetadata
from app.schemas.classification import ClassificationResult
from app.schemas.search import SearchRequest


class AIMetadataRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_prediction(
        self,
        *,
        image_id: int,
        prediction: ClassificationResult,
        model: str,
    ) -> AIMetadata:
        metadata = self.db.scalar(select(AIMetadata).where(AIMetadata.image_id == image_id))
        if metadata is None:
            metadata = AIMetadata(image_id=image_id)

        metadata.garment_type = prediction.garment_type
        metadata.style = prediction.style
        metadata.material = prediction.material
        metadata.color_palette = prediction.color_palette
        metadata.pattern = prediction.pattern
        metadata.season = prediction.season
        metadata.occasion = prediction.occasion
        metadata.consumer_profile = prediction.consumer_profile
        metadata.trend_notes = prediction.trend_notes
        metadata.location_context = prediction.location_context
        metadata.description = prediction.description
        metadata.raw_response = prediction.model_dump()
        metadata.model = model
        self.db.add(metadata)
        self.db.commit()
        self.db.refresh(metadata)
        return metadata

    def filter(self, request: SearchRequest, *, limit: int) -> list[AIMetadata]:
        stmt = select(AIMetadata)
        if request.garment_type:
            stmt = stmt.where(AIMetadata.garment_type.ilike(f"%{request.garment_type}%"))
        if request.style:
            stmt = stmt.where(AIMetadata.style.ilike(f"%{request.style}%"))
        if request.material:
            stmt = stmt.where(AIMetadata.material.ilike(f"%{request.material}%"))
        if request.color:
            stmt = stmt.where(cast(AIMetadata.color_palette, String).ilike(f"%{request.color}%"))
        if request.pattern:
            stmt = stmt.where(AIMetadata.pattern.ilike(f"%{request.pattern}%"))
        if request.season:
            stmt = stmt.where(AIMetadata.season.ilike(f"%{request.season}%"))
        if request.occasion:
            stmt = stmt.where(AIMetadata.occasion.ilike(f"%{request.occasion}%"))
        if request.consumer_profile:
            stmt = stmt.where(AIMetadata.consumer_profile.ilike(f"%{request.consumer_profile}%"))
        if request.location_context:
            stmt = stmt.where(AIMetadata.location_context.ilike(f"%{request.location_context}%"))
        return list(self.db.scalars(stmt.limit(limit)))

    def get_by_image_ids(self, image_ids: list[int]) -> dict[int, AIMetadata]:
        if not image_ids:
            return {}
        rows = self.db.scalars(select(AIMetadata).where(AIMetadata.image_id.in_(image_ids))).all()
        return {row.image_id: row for row in rows}
