from app.db.session import SessionLocal
from app.repositories.embeddings import EmbeddingReferenceRepository
from app.repositories.images import ImageRepository
from app.repositories.metadata import AIMetadataRepository
from app.services.classification import ClassificationService
from app.services.semantic_index import SemanticIndexService


def classify_image_task(image_id: int) -> None:
    db = SessionLocal()
    try:
        service = ClassificationService(
            images=ImageRepository(db),
            metadata=AIMetadataRepository(db),
            semantic_index=SemanticIndexService(embedding_refs=EmbeddingReferenceRepository(db)),
        )
        service.classify_image(image_id)
    except Exception:
        # ClassificationService persists failed status. Background failures
        # should not invalidate the already-successful upload response.
        return
    finally:
        db.close()

