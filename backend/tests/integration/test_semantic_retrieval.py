from app.models import AIMetadata, Image
from app.repositories.embeddings import EmbeddingReferenceRepository
from app.repositories.metadata import AIMetadataRepository
from app.schemas.search import SearchRequest
from app.services.embeddings import HashEmbeddingClient
from app.services.search import HybridSearchService
from app.services.semantic_index import SemanticIndexService
from app.vector.faiss_index import FaissIndex


def add_metadata(db, description: str, garment_type: str) -> int:
    image = Image(
        original_filename=f"{garment_type}.jpg",
        storage_path=f"/tmp/{garment_type}.jpg",
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
            style="festive" if garment_type == "dress" else "casual",
            material="cotton",
            color_palette=["red"],
            pattern="embroidered" if "embroidered" in description else "solid",
            season="seasonless",
            occasion="festival" if garment_type == "dress" else "everyday",
            consumer_profile="occasionwear customer" if garment_type == "dress" else "general fashion customer",
            trend_notes="embroidered detail" if garment_type == "dress" else "minimal",
            location_context="unknown",
            description=description,
            raw_response={},
            model="test-model",
        )
    )
    db.commit()
    return image.id


def test_semantic_retrieval_returns_similar_description(db_session, tmp_path) -> None:
    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "test.index")),
        embedding_client=HashEmbeddingClient(),
    )
    dress_id = add_metadata(db_session, "red festive embroidered dress", "dress")
    add_metadata(db_session, "blue casual denim jacket", "jacket")
    semantic_index.index_description(image_id=dress_id, description="red festive embroidered dress")

    results = semantic_index.search(query="red embroidered dress", limit=1)

    assert results[0][0] == dress_id


def test_hybrid_search_combines_filter_and_semantic_query(db_session, tmp_path) -> None:
    semantic_index = SemanticIndexService(
        embedding_refs=EmbeddingReferenceRepository(db_session),
        vector_index=FaissIndex(str(tmp_path / "hybrid.index")),
        embedding_client=HashEmbeddingClient(),
    )
    dress_id = add_metadata(db_session, "red festive embroidered dress", "dress")
    jacket_id = add_metadata(db_session, "red embroidered denim jacket", "jacket")
    semantic_index.index_description(image_id=dress_id, description="red festive embroidered dress")
    semantic_index.index_description(image_id=jacket_id, description="red embroidered denim jacket")

    results = HybridSearchService(
        metadata=AIMetadataRepository(db_session),
        semantic_index=semantic_index,
    ).search(
        SearchRequest(query="red festive embroidered dress", garment_type="dress")
    )

    assert len(results) == 1
    assert results[0].image_id == dress_id
