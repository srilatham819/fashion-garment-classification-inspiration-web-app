import pytest
from pydantic import ValidationError

from app.services.openai_vision import parse_classification_response


def test_parse_classification_response_accepts_strict_json() -> None:
    result = parse_classification_response(
        """
        {
          "garment_type": "dress",
          "style": "festive",
          "material": "silk",
          "color_palette": ["red", "gold"],
          "pattern": "embroidered",
          "season": "fall/winter",
          "occasion": "celebration",
          "consumer_profile": "occasionwear customer",
          "trend_notes": "embroidered neckline and ornate trim",
          "location_context": "artisan market",
          "description": "A red festive embroidered dress with gold accents."
        }
        """
    )

    assert result.garment_type == "dress"
    assert result.style == "festive"
    assert result.material == "silk"
    assert result.color_palette == ["red", "gold"]
    assert result.pattern == "embroidered"
    assert result.season == "fall/winter"
    assert result.occasion == "celebration"
    assert result.consumer_profile == "occasionwear customer"
    assert result.trend_notes == "embroidered neckline and ornate trim"
    assert result.location_context == "artisan market"
    assert result.description == "A red festive embroidered dress with gold accents."


def test_parse_classification_response_rejects_invalid_json() -> None:
    with pytest.raises(ValueError):
        parse_classification_response("not-json")


def test_parse_classification_response_rejects_missing_required_fields() -> None:
    with pytest.raises(ValidationError):
        parse_classification_response('{"garment_type": "dress"}')
