from app.models import AIMetadata, Image
from app.repositories.embeddings import EmbeddingReferenceRepository
from app.repositories.metadata import AIMetadataRepository
from app.schemas.search import SearchRequest
from app.services.search import HybridSearchService
from app.services.semantic_index import SemanticIndexService
from app.vector.faiss_index import FaissIndex


def add_classified_image(
    db,
    *,
    garment_type: str,
    style: str,
    material: str,
    occasion: str,
    location_context: str,
    season: str = "seasonless",
):
    image = Image(
        original_filename=f"{garment_type}.jpg",
        storage_path=f"/tmp/{garment_type}-{style}.jpg",
        mime_type="image/jpeg",
        status="classified",
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    db.add(
        AIMetadata(
            image_id=image.id,
            garment_type=garment_type,
            style=style,
            material=material,
            color_palette=["red"],
            pattern="solid",
            season=season,
            occasion=occasion,
            consumer_profile="general fashion customer",
            trend_notes="sample",
            location_context=location_context,
            description=f"{style} {material} {garment_type}",
            raw_response={},
            model="test-model",
        )
    )
    db.commit()
    return image


def test_structured_search_filters_by_material_and_occasion(db_session, tmp_path) -> None:
    add_classified_image(
        db_session,
        garment_type="dress",
        style="festive",
        material="silk",
        occasion="wedding",
        location_context="India market",
        season="fall/winter",
    )
    add_classified_image(
        db_session,
        garment_type="jacket",
        style="streetwear",
        material="denim",
        occasion="casual",
        location_context="New York street",
        season="spring/summer",
    )

    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "filters.index")),
    )
    results = HybridSearchService(
        metadata=AIMetadataRepository(db_session),
        semantic_index=semantic_index,
    ).search(SearchRequest(material="silk", occasion="wedding"))

    assert len(results) == 1
    assert results[0].garment_type == "dress"


def test_filter_behavior_supports_location_and_time_filters(db_session, tmp_path) -> None:
    add_classified_image(
        db_session,
        garment_type="dress",
        style="festive",
        material="silk",
        occasion="wedding",
        location_context="Mumbai artisan market",
        season="fall/winter",
    )
    add_classified_image(
        db_session,
        garment_type="dress",
        style="casual",
        material="cotton",
        occasion="everyday",
        location_context="Paris street",
        season="spring/summer",
    )

    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "location-time.index")),
    )
    results = HybridSearchService(
        metadata=AIMetadataRepository(db_session),
        semantic_index=semantic_index,
    ).search(SearchRequest(location_context="Mumbai", season="fall/winter"))

    assert len(results) == 1
    assert results[0].location_context == "Mumbai artisan market"
    assert results[0].season == "fall/winter"
