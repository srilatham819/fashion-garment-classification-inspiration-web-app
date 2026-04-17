from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class LocalImageStorage:
    allowed_content_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}

    def __init__(self, root_path: str | None = None) -> None:
        self.root_path = Path(root_path or settings.upload_storage_path)
        self.root_path.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> tuple[str, bytes]:
        if file.content_type not in self.allowed_content_types:
            raise ValueError("Unsupported file type. Upload a JPEG, PNG, WEBP, or GIF image.")

        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")
        if len(content) > settings.max_upload_bytes:
            raise ValueError("Uploaded file exceeds the configured size limit.")

        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            suffix = self._suffix_for_content_type(file.content_type)

        storage_path = self.root_path / f"{uuid4().hex}{suffix}"
        storage_path.write_bytes(content)
        return str(storage_path), content

    @staticmethod
    def _suffix_for_content_type(content_type: str | None) -> str:
        return {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }.get(content_type or "", ".img")

