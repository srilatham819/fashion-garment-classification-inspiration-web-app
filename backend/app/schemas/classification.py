from pydantic import BaseModel


class ClassificationResult(BaseModel):
    garment_type: str
    style: str
    material: str
    color_palette: list[str]
    pattern: str
    season: str
    occasion: str
    consumer_profile: str
    trend_notes: str
    location_context: str
    description: str


CLASSIFICATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "garment_type": {"type": "string"},
        "style": {"type": "string"},
        "material": {"type": "string"},
        "color_palette": {"type": "array", "items": {"type": "string"}},
        "pattern": {"type": "string"},
        "season": {"type": "string"},
        "occasion": {"type": "string"},
        "consumer_profile": {"type": "string"},
        "trend_notes": {"type": "string"},
        "location_context": {"type": "string"},
        "description": {"type": "string"},
    },
    "required": [
        "garment_type",
        "style",
        "material",
        "color_palette",
        "pattern",
        "season",
        "occasion",
        "consumer_profile",
        "trend_notes",
        "location_context",
        "description",
    ],
    "additionalProperties": False,
}
