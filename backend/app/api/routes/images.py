from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_upload_service
from app.core.errors import UploadValidationError
from app.db.session import get_db
from app.models import Image
from app.schemas.classification import ClassificationResult
from app.schemas.image import AnnotationRead, ImageRead, ImageUploadResponse
from app.services.image_upload import ImageUploadService
from app.workers.classification_tasks import classify_image_task

router = APIRouter()


@router.post("", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: ImageUploadService = Depends(get_upload_service),
) -> ImageUploadResponse:
    try:
        image = await service.create_upload(file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image.") from exc

    background_tasks.add_task(classify_image_task, image.id)
    return ImageUploadResponse(image_id=image.id, status=image.status)


@router.get("", response_model=list[ImageRead])
def list_images(db: Session = Depends(get_db)) -> list[ImageRead]:
    images = db.scalars(select(Image).order_by(Image.created_at.desc())).all()
    return [_to_image_read(image) for image in images]


@router.get("/{image_id}", response_model=ImageRead)
def get_image(image_id: int, db: Session = Depends(get_db)) -> ImageRead:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    return _to_image_read(image)


@router.get("/{image_id}/file")
def get_image_file(image_id: int, db: Session = Depends(get_db)) -> FileResponse:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    path = Path(image.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found.")
    return FileResponse(path, media_type=image.mime_type, filename=image.original_filename)


def _to_image_read(image: Image) -> ImageRead:
    metadata = None
    if image.ai_metadata:
        metadata = ClassificationResult(
            garment_type=image.ai_metadata.garment_type,
            style=image.ai_metadata.style,
            material=image.ai_metadata.material,
            color_palette=image.ai_metadata.color_palette,
            pattern=image.ai_metadata.pattern,
            season=image.ai_metadata.season,
            occasion=image.ai_metadata.occasion,
            consumer_profile=image.ai_metadata.consumer_profile,
            trend_notes=image.ai_metadata.trend_notes,
            location_context=image.ai_metadata.location_context,
            description=image.ai_metadata.description,
        )
    return ImageRead(
        id=image.id,
        original_filename=image.original_filename,
        status=image.status,
        image_url=f"/api/images/{image.id}/file",
        error_message=image.error_message,
        created_at=image.created_at.isoformat() if image.created_at else None,
        ai_metadata=metadata,
        annotations=[
            AnnotationRead(
                id=annotation.id,
                note=annotation.note,
                tags=annotation.tags,
                created_by=annotation.created_by,
            )
            for annotation in image.annotations
        ],
    )
