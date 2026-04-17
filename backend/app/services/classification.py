from app.core.errors import ClassificationError, NotFoundError
from app.repositories.images import ImageRepository
from app.repositories.metadata import AIMetadataRepository
from app.schemas.classification import ClassificationResult
from app.services.semantic_index import SemanticIndexService
from app.services.openai_vision import OpenAIVisionClient


class ClassificationService:
    def __init__(
        self,
        *,
        images: ImageRepository,
        metadata: AIMetadataRepository,
        semantic_index: SemanticIndexService,
        vision_client: OpenAIVisionClient | None = None,
    ) -> None:
        self.images = images
        self.metadata = metadata
        self.semantic_index = semantic_index
        self.vision_client = vision_client or OpenAIVisionClient()

    def classify_image(self, image_id: int) -> ClassificationResult:
        image = self.images.get(image_id)
        if image is None:
            raise NotFoundError(f"Image {image_id} was not found.")

        self.images.mark_processing(image)

        try:
            result = self.vision_client.classify_image(
                image.storage_path,
                image.mime_type,
                context_name=image.original_filename,
            )
            self.metadata.upsert_prediction(
                image_id=image.id,
                prediction=result,
                model=self.vision_client.model,
            )
            self.images.mark_classified(image)
            self.semantic_index.index_description(image_id=image.id, description=result.description)
            return result
        except Exception as exc:
            self.images.mark_failed(image, str(exc))
            raise ClassificationError(str(exc)) from exc
