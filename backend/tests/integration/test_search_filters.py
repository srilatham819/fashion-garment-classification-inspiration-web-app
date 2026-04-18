from datetime import datetime

from app.models import AIMetadata, Image, UserAnnotation
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
    created_at: datetime | None = None,
    designer: str | None = None,
    note: str | None = None,
):
    image = Image(
        original_filename=f"{garment_type}.jpg",
        storage_path=f"/tmp/{garment_type}-{style}.jpg",
        mime_type="image/jpeg",
        status="classified",
        created_at=created_at or datetime(2026, 4, 1),
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
    if designer or note:
        db.add(
            UserAnnotation(
                image_id=image.id,
                note=note,
                tags="artisan market",
                created_by=designer,
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
        location_context="Asia > India > Mumbai artisan market",
        season="fall/winter",
        created_at=datetime(2025, 11, 8),
    )
    add_classified_image(
        db_session,
        garment_type="dress",
        style="casual",
        material="cotton",
        occasion="everyday",
        location_context="Europe > France > Paris street",
        season="spring/summer",
        created_at=datetime(2026, 4, 8),
    )

    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "location-time.index")),
    )
    results = HybridSearchService(
        metadata=AIMetadataRepository(db_session),
        semantic_index=semantic_index,
    ).search(SearchRequest(continent="Asia", country="India", city="Mumbai", year=2025, month=11))

    assert len(results) == 1
    assert results[0].location_context == "Asia > India > Mumbai artisan market"
    assert results[0].season == "fall/winter"


def test_search_includes_designer_annotations(db_session, tmp_path) -> None:
    add_classified_image(
        db_session,
        garment_type="skirt",
        style="bohemian",
        material="linen",
        occasion="market",
        location_context="Asia > India > Jaipur artisan market",
        designer="Srilatha",
        note="embroidered mirror-work hem with craft fair reference",
    )
    add_classified_image(
        db_session,
        garment_type="jacket",
        style="streetwear",
        material="denim",
        occasion="casual",
        location_context="North America > United States > New York",
        designer="Design intern",
        note="oversized utility pockets",
    )

    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "annotations.index")),
    )
    results = HybridSearchService(
        metadata=AIMetadataRepository(db_session),
        semantic_index=semantic_index,
    ).search(SearchRequest(query="mirror-work", designer="Srilatha"))

    assert len(results) == 1
    assert results[0].garment_type == "skirt"
    assert results[0].designers == ["Srilatha"]
    assert "mirror-work" in (results[0].annotation_text or "")
