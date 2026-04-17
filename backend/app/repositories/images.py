from sqlalchemy.orm import Session

from app.models import Image


class ImageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, image_id: int) -> Image | None:
        return self.db.get(Image, image_id)

    def create_upload(self, *, filename: str, storage_path: str, mime_type: str) -> Image:
        image = Image(
            original_filename=filename,
            storage_path=storage_path,
            mime_type=mime_type,
            status="pending",
        )
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def mark_processing(self, image: Image) -> None:
        image.status = "processing"
        image.error_message = None
        self.db.commit()

    def mark_classified(self, image: Image) -> None:
        image.status = "classified"
        self.db.commit()
        self.db.refresh(image)

    def mark_failed(self, image: Image, error: str) -> None:
        image.status = "failed"
        image.error_message = error[:1024]
        self.db.commit()

