from fastapi import UploadFile

from app.core.errors import UploadValidationError
from app.models import Image
from app.repositories.images import ImageRepository
from app.storage.local import LocalImageStorage


class ImageUploadService:
    def __init__(self, *, images: ImageRepository, storage: LocalImageStorage) -> None:
        self.images = images
        self.storage = storage

    async def create_upload(self, file: UploadFile) -> Image:
        try:
            storage_path, _content = await self.storage.save_upload(file)
        except ValueError as exc:
            raise UploadValidationError(str(exc)) from exc
        return self.images.create_upload(
            filename=file.filename or "upload",
            storage_path=storage_path,
            mime_type=file.content_type or "application/octet-stream",
        )

