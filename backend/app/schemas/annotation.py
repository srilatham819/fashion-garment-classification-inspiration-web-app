from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    note: str | None = None
    tags: str | None = None
    created_by: str | None = "designer"


class AnnotationRead(BaseModel):
    id: int
    image_id: int
    note: str | None = None
    tags: str | None = None
    created_by: str | None = None

