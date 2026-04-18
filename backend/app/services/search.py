from app.models import AIMetadata
from app.repositories.metadata import AIMetadataRepository
from app.schemas.search import SearchRequest, SearchResult
from app.services.semantic_index import SemanticIndexService

COLOR_TERMS = {"black", "white", "red", "blue", "green", "gold", "pink", "purple", "yellow", "orange", "gray", "grey"}
GARMENT_TERMS = {
    "dress": "dress",
    "dresses": "dress",
    "jacket": "jacket",
    "coat": "jacket",
    "shirt": "top",
    "top": "top",
    "pants": "pants",
    "trousers": "pants",
    "skirt": "skirt",
}
STYLE_TERMS = {"festive", "casual", "streetwear", "formal", "bohemian", "minimal"}
MATERIAL_TERMS = {"cotton", "silk", "denim", "linen", "wool", "leather", "knit"}
PATTERN_TERMS = {"solid", "striped", "stripe", "checked", "plaid", "printed", "print", "floral", "embroidered"}
SEASON_TERMS = {"spring", "summer", "fall", "autumn", "winter", "seasonless"}
OCCASION_TERMS = {"everyday", "casual", "celebration", "party", "wedding", "formal", "workwear"}


class HybridSearchService:
    def __init__(self, *, metadata: AIMetadataRepository, semantic_index: SemanticIndexService) -> None:
        self.metadata = metadata
        self.semantic_index = semantic_index

    def search(self, request: SearchRequest) -> list[SearchResult]:
        normalized_request = self._augment_request_from_query(request)
        structured_matches = self.metadata.filter(normalized_request, limit=max(normalized_request.limit, 100))
        structured_ids = {item.image_id for item in structured_matches}

        if normalized_request.query:
            semantic_matches = self.semantic_index.search(query=normalized_request.query, limit=max(normalized_request.limit, 100))
            score_by_image_id = dict(semantic_matches)
            candidate_ids = set(score_by_image_id) or structured_ids
            if self._has_structured_filters(normalized_request):
                candidate_ids &= structured_ids
            ordered_ids = sorted(candidate_ids, key=lambda image_id: score_by_image_id.get(image_id, 0.0), reverse=True)
        else:
            score_by_image_id = {}
            ordered_ids = sorted(structured_ids)

        if not ordered_ids:
            return []

        row_by_image_id = self.metadata.get_by_image_ids(ordered_ids)
        results = [
            self._to_result(row_by_image_id[image_id], score_by_image_id.get(image_id))
            for image_id in ordered_ids[: request.limit]
            if image_id in row_by_image_id
        ]
        return [result for result in results if self._matches_request(result, normalized_request)]

    @staticmethod
    def _has_structured_filters(request: SearchRequest) -> bool:
        return any(
            [
                request.garment_type,
                request.style,
                request.material,
                request.color,
                request.pattern,
                request.season,
                request.occasion,
                request.consumer_profile,
                request.location_context,
                request.continent,
                request.country,
                request.city,
                request.year,
                request.month,
                request.designer,
                request.annotation,
            ]
        )

    @staticmethod
    def _to_result(metadata: AIMetadata, score: float | None) -> SearchResult:
        annotations = metadata.image.annotations if metadata.image else []
        designers = sorted({annotation.created_by for annotation in annotations if annotation.created_by})
        annotation_text = " ".join(
            part
            for annotation in annotations
            for part in [annotation.tags, annotation.note]
            if part
        ) or None
        return SearchResult(
            image_id=metadata.image_id,
            score=score,
            description=metadata.description,
            garment_type=metadata.garment_type,
            style=metadata.style,
            material=metadata.material,
            color_palette=metadata.color_palette,
            pattern=metadata.pattern,
            season=metadata.season,
            occasion=metadata.occasion,
            consumer_profile=metadata.consumer_profile,
            location_context=metadata.location_context,
            created_at=metadata.image.created_at.isoformat() if metadata.image and metadata.image.created_at else None,
            designers=designers,
            annotation_text=annotation_text,
        )

    @staticmethod
    def _augment_request_from_query(request: SearchRequest) -> SearchRequest:
        tokens = set((request.query or "").lower().replace("-", " ").split())
        color = request.color
        garment_type = request.garment_type
        style = request.style
        material = request.material
        pattern = request.pattern
        season = request.season
        occasion = request.occasion

        for token in tokens:
            normalized = "gray" if token == "grey" else token
            if not color and normalized in COLOR_TERMS:
                color = normalized
            if not garment_type and token in GARMENT_TERMS:
                garment_type = GARMENT_TERMS[token]
            if not style and token in STYLE_TERMS:
                style = token
            if not material and token in MATERIAL_TERMS:
                material = token
            if not pattern and token in PATTERN_TERMS:
                pattern = {"stripe": "striped", "print": "printed", "plaid": "checked"}.get(token, token)
            if not season and token in SEASON_TERMS:
                season = "fall" if token == "autumn" else token
            if not occasion and token in OCCASION_TERMS:
                occasion = "celebration" if token in {"party", "wedding", "formal"} else token

        return request.model_copy(
            update={
                "color": color,
                "garment_type": garment_type,
                "style": style,
                "material": material,
                "pattern": pattern,
                "season": season,
                "occasion": occasion,
            }
        )

    @staticmethod
    def _matches_request(result: SearchResult, request: SearchRequest) -> bool:
        checks = [
            (request.garment_type, result.garment_type),
            (request.style, result.style),
            (request.material, result.material),
            (request.pattern, result.pattern),
            (request.season, result.season),
            (request.occasion, result.occasion),
            (request.consumer_profile, result.consumer_profile),
            (request.location_context, result.location_context),
            (request.continent, result.location_context),
            (request.country, result.location_context),
            (request.city, result.location_context),
            (request.annotation, result.annotation_text),
        ]
        for expected, actual in checks:
            if expected and expected.lower() not in (actual or "").lower():
                return False
        if request.designer:
            designers = [designer.lower() for designer in result.designers]
            if not any(request.designer.lower() in designer for designer in designers):
                return False
        if request.year or request.month:
            if not result.created_at:
                return False
            date_part = result.created_at.split("T", maxsplit=1)[0]
            year, month, *_ = date_part.split("-")
            if request.year and int(year) != request.year:
                return False
            if request.month and int(month) != request.month:
                return False
        if request.color:
            colors = [color.lower() for color in (result.color_palette or [])]
            if request.color.lower() not in colors:
                return False
        return True
