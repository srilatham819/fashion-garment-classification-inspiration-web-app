"""Import evaluation dataset images into the local app library.

This is a development helper so downloaded evaluation images can be browsed in
the React app. It creates `images` rows, runs the classifier, and indexes
descriptions for hybrid search.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Image
from app.repositories.embeddings import EmbeddingReferenceRepository
from app.repositories.images import ImageRepository
from app.repositories.metadata import AIMetadataRepository
from app.services.classification import ClassificationService
from app.services.semantic_index import SemanticIndexService


def import_dataset(labels_path: Path, *, limit: int | None = None, copy_files: bool = True) -> int:
    Base.metadata.create_all(bind=engine)
    labels = json.loads(labels_path.read_text())
    storage_dir = ROOT / settings.upload_storage_path
    storage_dir.mkdir(parents=True, exist_ok=True)

    imported = 0
    db = SessionLocal()
    try:
        images = ImageRepository(db)
        classifier = ClassificationService(
            images=images,
            metadata=AIMetadataRepository(db),
            semantic_index=SemanticIndexService(embedding_refs=EmbeddingReferenceRepository(db)),
        )

        for item in labels[:limit]:
            source_path = ROOT / item["image_path"]
            if not source_path.exists():
                continue

            existing = db.query(Image).filter(Image.original_filename == source_path.name).first()
            if existing:
                continue

            target_path = source_path
            if copy_files:
                target_path = storage_dir / source_path.name
                if not target_path.exists():
                    shutil.copy2(source_path, target_path)

            image = images.create_upload(
                filename=source_path.name,
                storage_path=str(target_path),
                mime_type=item.get("mime_type") or mimetypes.guess_type(source_path.name)[0] or "image/jpeg",
            )
            classifier.classify_image(image.id)
            imported += 1
    finally:
        db.close()
    return imported


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=ROOT / "eval/dataset/labels/labels.json")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-copy", action="store_true")
    args = parser.parse_args()

    count = import_dataset(args.labels, limit=args.limit, copy_files=not args.no_copy)
    print(f"Imported {count} image(s) into the app library")


if __name__ == "__main__":
    main()

