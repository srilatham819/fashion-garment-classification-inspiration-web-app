"""Build a static demo library for GitHub Pages.

The full application uses the FastAPI backend for upload, classification, and
persistence. GitHub Pages can only host static files, so this script packages a
small, pre-classified Pexels sample from the evaluation dataset into
`frontend/public/demo` before a static build.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABELS_PATH = ROOT / "eval/dataset/labels/labels.json"
OUTPUT_DIR = ROOT / "frontend/public/demo"
IMAGE_DIR = OUTPUT_DIR / "images"


def build_demo(limit: int) -> None:
    labels = json.loads(LABELS_PATH.read_text())
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    library = []
    for index, item in enumerate(labels[:limit], start=1):
        source = ROOT / item["image_path"]
        if not source.exists():
            continue
        target = IMAGE_DIR / source.name
        shutil.copy2(source, target)
        expected = item["expected"]
        library.append(
            {
                "id": index,
                "original_filename": source.name,
                "status": "classified",
                "image_url": f"demo/images/{source.name}",
                "error_message": None,
                "created_at": datetime(2026, (index % 12) + 1, min(index, 28)).isoformat(),
                "ai_metadata": {
                    "garment_type": expected.get("garment_type", "unknown"),
                    "style": expected.get("style", "unknown"),
                    "material": expected.get("material", "unknown"),
                    "color_palette": expected.get("color_palette", ["unknown"]),
                    "pattern": expected.get("pattern", "unknown"),
                    "season": expected.get("season", "unknown"),
                    "occasion": expected.get("occasion", "unknown"),
                    "consumer_profile": expected.get("consumer_profile", "unknown"),
                    "trend_notes": expected.get("trend_notes", item.get("source_query", "")),
                    "location_context": expected.get("location_context", "unknown"),
                    "description": (
                        f"{expected.get('style', 'fashion')} {expected.get('garment_type', 'garment')} "
                        f"from the {item.get('source_query', 'Pexels fashion')} evaluation bucket."
                    ),
                },
                "annotations": [
                    {
                        "id": index,
                        "note": "Static demo sample from the Pexels evaluation set.",
                        "tags": item.get("source_query", "fashion inspiration"),
                        "created_by": "Srilatha",
                    }
                ],
            }
        )

    (OUTPUT_DIR / "library.json").write_text(json.dumps(library, indent=2))
    print(f"Wrote {len(library)} static demo images to {OUTPUT_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=24)
    args = parser.parse_args()
    build_demo(args.limit)


if __name__ == "__main__":
    main()
