from pydantic import BaseModel

from app.schemas.classification import ClassificationResult


class AnnotationRead(BaseModel):
    id: int
    note: str | None = None
    tags: str | None = None
    created_by: str | None = None


class ImageRead(BaseModel):
    id: int
    original_filename: str
    status: str
    image_url: str
    error_message: str | None = None
    created_at: str | None = None
    ai_metadata: ClassificationResult | None = None
    annotations: list[AnnotationRead] = []


class ImageUploadResponse(BaseModel):
    image_id: int
    status: str
