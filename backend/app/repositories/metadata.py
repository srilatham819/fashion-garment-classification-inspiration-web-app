from sqlalchemy import String, cast, extract, or_, select
from sqlalchemy.orm import Session

from app.models import AIMetadata, Image, UserAnnotation
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
        stmt = select(AIMetadata).join(Image, Image.id == AIMetadata.image_id).outerjoin(
            UserAnnotation,
            UserAnnotation.image_id == AIMetadata.image_id,
        )
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
        if request.continent:
            stmt = stmt.where(AIMetadata.location_context.ilike(f"%{request.continent}%"))
        if request.country:
            stmt = stmt.where(AIMetadata.location_context.ilike(f"%{request.country}%"))
        if request.city:
            stmt = stmt.where(AIMetadata.location_context.ilike(f"%{request.city}%"))
        if request.year:
            stmt = stmt.where(extract("year", Image.created_at) == request.year)
        if request.month:
            stmt = stmt.where(extract("month", Image.created_at) == request.month)
        if request.designer:
            stmt = stmt.where(UserAnnotation.created_by.ilike(f"%{request.designer}%"))
        if request.annotation:
            stmt = stmt.where(
                or_(
                    UserAnnotation.note.ilike(f"%{request.annotation}%"),
                    UserAnnotation.tags.ilike(f"%{request.annotation}%"),
                )
            )
        if request.query:
            query_terms = [request.query, *request.query.replace("-", " ").split()]
            stmt = stmt.where(
                or_(
                    *[
                        field.ilike(f"%{term}%")
                        for term in query_terms
                        for field in [
                            AIMetadata.garment_type,
                            AIMetadata.style,
                            AIMetadata.material,
                            cast(AIMetadata.color_palette, String),
                            AIMetadata.pattern,
                            AIMetadata.occasion,
                            AIMetadata.description,
                            AIMetadata.trend_notes,
                            AIMetadata.location_context,
                            AIMetadata.consumer_profile,
                            UserAnnotation.note,
                            UserAnnotation.tags,
                        ]
                    ]
                )
            )
        return list(self.db.scalars(stmt.distinct().limit(limit)))

    def get_by_image_ids(self, image_ids: list[int]) -> dict[int, AIMetadata]:
        if not image_ids:
            return {}
        rows = self.db.scalars(select(AIMetadata).where(AIMetadata.image_id.in_(image_ids))).all()
        return {row.image_id: row for row in rows}
