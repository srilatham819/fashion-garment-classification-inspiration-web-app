from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.embeddings import EmbeddingReferenceRepository
from app.repositories.images import ImageRepository
from app.repositories.metadata import AIMetadataRepository
from app.services.classification import ClassificationService
from app.services.image_upload import ImageUploadService
from app.services.search import HybridSearchService
from app.services.semantic_index import SemanticIndexService
from app.storage.local import LocalImageStorage


def build_semantic_index_service(db: Session) -> SemanticIndexService:
    return SemanticIndexService(embedding_refs=EmbeddingReferenceRepository(db))


def get_upload_service(db: Session = Depends(get_db)) -> ImageUploadService:
    return ImageUploadService(images=ImageRepository(db), storage=LocalImageStorage())


def get_classification_service(db: Session = Depends(get_db)) -> ClassificationService:
    return ClassificationService(
        images=ImageRepository(db),
        metadata=AIMetadataRepository(db),
        semantic_index=build_semantic_index_service(db),
    )


def get_search_service(db: Session = Depends(get_db)) -> HybridSearchService:
    return HybridSearchService(
        metadata=AIMetadataRepository(db),
        semantic_index=build_semantic_index_service(db),
    )
