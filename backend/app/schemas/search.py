from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str | None = None
    garment_type: str | None = None
    style: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    season: str | None = None
    occasion: str | None = None
    consumer_profile: str | None = None
    location_context: str | None = None
    continent: str | None = None
    country: str | None = None
    city: str | None = None
    year: int | None = None
    month: int | None = None
    designer: str | None = None
    annotation: str | None = None
    limit: int = 10


class SearchResult(BaseModel):
    image_id: int
    score: float | None = None
    description: str | None = None
    garment_type: str | None = None
    style: str | None = None
    material: str | None = None
    color_palette: list[str] | None = None
    pattern: str | None = None
    season: str | None = None
    occasion: str | None = None
    consumer_profile: str | None = None
    location_context: str | None = None
    created_at: str | None = None
    designers: list[str] = []
    annotation_text: str | None = None
