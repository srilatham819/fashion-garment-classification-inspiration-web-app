from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Image, UserAnnotation
from app.schemas.annotation import AnnotationCreate, AnnotationRead


router = APIRouter()


@router.post("/{image_id}", response_model=AnnotationRead, status_code=status.HTTP_201_CREATED)
def create_annotation(
    image_id: int,
    payload: AnnotationCreate,
    db: Session = Depends(get_db),
) -> AnnotationRead:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

    annotation = UserAnnotation(
        image_id=image_id,
        note=payload.note,
        tags=payload.tags,
        created_by=payload.created_by,
    )
    db.add(annotation)
    db.commit()
    db.refresh(annotation)
    return AnnotationRead(
        id=annotation.id,
        image_id=annotation.image_id,
        note=annotation.note,
        tags=annotation.tags,
        created_by=annotation.created_by,
    )
