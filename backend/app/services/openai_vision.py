import base64
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI
from PIL import Image as PILImage

from app.core.config import settings
from app.schemas.classification import CLASSIFICATION_JSON_SCHEMA, ClassificationResult


class OpenAIVisionClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_vision_model
        self.client: OpenAI | None = None

    def classify_image(self, image_path: str, mime_type: str, context_name: str | None = None) -> ClassificationResult:
        if not self.api_key:
            if settings.demo_ai_fallback:
                return demo_classification(image_path=image_path, context_name=context_name)
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key)

        image_b64 = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You classify fashion inspiration images. Return only strict JSON "
                                "matching the supplied schema. Use 'unknown' when a field cannot be "
                                "visually inferred. Do not invent specific locations."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract garment metadata and write a concise natural language "
                                "description for this image."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{mime_type};base64,{image_b64}",
                        },
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "fashion_image_classification",
                    "strict": True,
                    "schema": CLASSIFICATION_JSON_SCHEMA,
                }
            },
        )
        return parse_classification_response(extract_response_text(response))


def extract_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    output = getattr(response, "output", None) or []
    chunks: list[str] = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)
    return "".join(chunks)


def parse_classification_response(raw_text: str) -> ClassificationResult:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("Model response was not valid JSON.") from exc
    return ClassificationResult.model_validate(payload)


@dataclass
class VisualSignals:
    colors: list[str]
    brightness: float
    color_variety: int
    horizontal_changes: float
    vertical_changes: float


def demo_classification(image_path: str, context_name: str | None = None) -> ClassificationResult:
    name = Path(context_name or image_path).stem.lower().replace("-", " ").replace("_", " ")
    signals = analyze_image(image_path)
    garment_type = "dress"
    if "jacket" in name or "coat" in name:
        garment_type = "jacket"
    elif "shirt" in name or "top" in name:
        garment_type = "top"
    elif "pant" in name or "trouser" in name:
        garment_type = "pants"
    elif "skirt" in name:
        garment_type = "skirt"

    filename_colors = [
        color
        for color in ["red", "blue", "green", "black", "white", "gold", "pink", "purple", "yellow", "orange", "gray"]
        if color in name
    ]
    colors = filename_colors or signals.colors or ["unknown"]

    style = "festive" if any(token in name for token in ["festive", "embroidered", "wedding", "party"]) else "casual"
    pattern = infer_pattern(name, signals)
    material = infer_material(name, colors, pattern, signals)
    season = infer_season(name, colors, material)
    occasion = infer_occasion(name, style, garment_type)
    consumer_profile = infer_consumer_profile(style, occasion, garment_type)
    trend_notes = (
        f"Local visual fallback detected {', '.join(colors)} color cues and a {pattern} surface. "
        "Add OPENAI_API_KEY for true multimodal garment reasoning."
    )
    description = (
        f"A {', '.join(colors)} {style} {material} {garment_type} with a {pattern} look, "
        f"suited for {occasion} styling."
    )
    return ClassificationResult(
        garment_type=garment_type,
        style=style,
        material=material,
        color_palette=colors,
        pattern=pattern,
        season=season,
        occasion=occasion,
        consumer_profile=consumer_profile,
        trend_notes=trend_notes,
        location_context="unknown",
        description=description,
    )


def analyze_image(image_path: str, max_colors: int = 3) -> VisualSignals:
    try:
        image = PILImage.open(image_path).convert("RGB")
    except Exception:
        return VisualSignals([], 0, 0, 0, 0)

    image.thumbnail((96, 96))
    counts: Counter[str] = Counter()
    pixels = list(image.getdata())
    for red, green, blue in image.getdata():
        if red > 240 and green > 240 and blue > 240:
            continue
        counts[classify_rgb_color(red, green, blue)] += 1

    colors = [color for color, _count in counts.most_common(max_colors) if color != "unknown"]
    brightness = sum((red + green + blue) / 3 for red, green, blue in pixels) / max(len(pixels), 1)
    horizontal_changes = image_change_score(image, axis="x")
    vertical_changes = image_change_score(image, axis="y")
    return VisualSignals(colors, brightness, len([color for color in counts if color != "unknown"]), horizontal_changes, vertical_changes)


def classify_rgb_color(red: int, green: int, blue: int) -> str:
    brightness = (red + green + blue) / 3
    if brightness < 55:
        return "black"
    if brightness > 220 and max(red, green, blue) - min(red, green, blue) < 28:
        return "white"
    if abs(red - green) < 24 and abs(green - blue) < 24:
        return "gray"
    if red > 180 and green > 145 and blue < 90:
        return "gold"
    if red > green * 1.25 and red > blue * 1.25:
        return "red"
    if blue > red * 1.2 and blue > green * 1.1:
        return "blue"
    if green > red * 1.15 and green > blue * 1.1:
        return "green"
    if red > 150 and blue > 140 and green < 130:
        return "purple"
    if red > 190 and green > 160 and blue < 80:
        return "yellow"
    if red > 180 and 75 < green < 170 and blue < 90:
        return "orange"
    return "unknown"


def image_change_score(image: PILImage.Image, axis: str) -> float:
    width, height = image.size
    if width < 2 or height < 2:
        return 0
    total = 0.0
    comparisons = 0
    x_range = range(width - 1) if axis == "x" else range(width)
    y_range = range(height) if axis == "x" else range(height - 1)
    for y in y_range:
        for x in x_range:
            a = image.getpixel((x, y))
            b = image.getpixel((x + 1, y)) if axis == "x" else image.getpixel((x, y + 1))
            total += sum(abs(a[channel] - b[channel]) for channel in range(3)) / 3
            comparisons += 1
    return total / max(comparisons, 1)


def infer_pattern(name: str, signals: VisualSignals) -> str:
    if any(token in name for token in ["stripe", "striped"]):
        return "striped"
    if any(token in name for token in ["check", "plaid", "gingham"]):
        return "checked"
    if any(token in name for token in ["floral", "print", "printed", "embroidered"]):
        return "embroidered" if "embroidered" in name else "printed"
    if signals.color_variety >= 4 or max(signals.horizontal_changes, signals.vertical_changes) > 45:
        return "printed"
    if abs(signals.horizontal_changes - signals.vertical_changes) > 16 and max(signals.horizontal_changes, signals.vertical_changes) > 25:
        return "striped"
    return "solid"


def infer_material(name: str, colors: list[str], pattern: str, signals: VisualSignals) -> str:
    for material in ["denim", "silk", "linen", "leather", "wool", "knit", "cotton", "satin"]:
        if material in name:
            return material
    if "blue" in colors and pattern == "solid" and signals.brightness < 140:
        return "denim"
    if "black" in colors and signals.brightness < 70:
        return "leather or heavy cotton"
    if pattern in {"embroidered", "printed"}:
        return "cotton blend"
    return "cotton"


def infer_season(name: str, colors: list[str], material: str) -> str:
    for season in ["spring", "summer", "fall", "autumn", "winter"]:
        if season in name:
            return "fall" if season == "autumn" else season
    if material in {"wool", "knit", "leather or heavy cotton"} or "black" in colors:
        return "fall/winter"
    if any(color in colors for color in ["white", "pink", "yellow", "green"]):
        return "spring/summer"
    return "seasonless"


def infer_occasion(name: str, style: str, garment_type: str) -> str:
    if any(token in name for token in ["wedding", "party", "festive", "formal", "evening"]):
        return "celebration"
    if garment_type in {"jacket", "pants", "top"} and style == "casual":
        return "everyday"
    if style == "festive":
        return "celebration"
    return "everyday"


def infer_consumer_profile(style: str, occasion: str, garment_type: str) -> str:
    if occasion == "celebration":
        return "occasionwear customer"
    if style == "streetwear":
        return "trend-led casual customer"
    if garment_type in {"jacket", "pants"}:
        return "everyday wardrobe customer"
    return "general fashion customer"
