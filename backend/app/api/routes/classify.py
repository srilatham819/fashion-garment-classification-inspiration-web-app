from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_classification_service
from app.core.errors import ClassificationError, NotFoundError
from app.schemas.classification import ClassificationResult
from app.services.classification import ClassificationService

router = APIRouter()


@router.post("/{image_id}", response_model=ClassificationResult)
def classify_image(
    image_id: int,
    service: ClassificationService = Depends(get_classification_service),
) -> ClassificationResult:
    try:
        return service.classify_image(image_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ClassificationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
