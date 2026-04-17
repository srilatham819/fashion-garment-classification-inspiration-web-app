"""Prepare a reproducible 100-image Fashion-MNIST evaluation set.

Fashion-MNIST is an open-source Zalando Research dataset of garment images.
It is grayscale and low-resolution, so it is useful for repeatable garment-type
evaluation but weak for material, occasion, and location-context evaluation.
Those limitations are called out in the generated labels and should be discussed
in the final report.
"""

from __future__ import annotations

import gzip
import json
import struct
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT / "eval/dataset/images"
LABEL_PATH = ROOT / "eval/dataset/labels/labels.json"

BASE_URL = "https://github.com/zalandoresearch/fashion-mnist/raw/master/data/fashion"
FILES = {
    "images": "t10k-images-idx3-ubyte.gz",
    "labels": "t10k-labels-idx1-ubyte.gz",
}

CLASS_MAP = {
    0: ("top", "T-shirt/top"),
    1: ("pants", "trouser"),
    2: ("top", "pullover"),
    3: ("dress", "dress"),
    4: ("jacket", "coat"),
    5: ("shoe", "sandal"),
    6: ("top", "shirt"),
    7: ("shoe", "sneaker"),
    8: ("bag", "bag"),
    9: ("shoe", "ankle boot"),
}


def download_file(name: str) -> Path:
    target = ROOT / f"eval/dataset/{name}"
    if target.exists():
        return target
    request = urllib.request.Request(
        f"{BASE_URL}/{name}",
        headers={"User-Agent": "fashion-inspiration-ai-eval/0.1"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        target.write_bytes(response.read())
    return target


def load_images(path: Path) -> list[bytes]:
    with gzip.open(path, "rb") as handle:
        _magic, count, rows, cols = struct.unpack(">IIII", handle.read(16))
        return [handle.read(rows * cols) for _ in range(count)]


def load_labels(path: Path) -> list[int]:
    with gzip.open(path, "rb") as handle:
        _magic, count = struct.unpack(">II", handle.read(8))
        return list(handle.read(count))


def expected_for(label: int) -> dict:
    garment_type, class_name = CLASS_MAP[label]
    material = "unknown"
    if garment_type in {"top", "dress"}:
        material = "cotton"
    elif garment_type == "jacket":
        material = "wool or cotton"

    return {
        "garment_type": garment_type,
        "style": "casual",
        "material": material,
        "color_palette": ["unknown"],
        "pattern": "solid",
        "season": "seasonless",
        "occasion": "everyday",
        "consumer_profile": "general fashion customer",
        "trend_notes": f"Fashion-MNIST class: {class_name}",
        "location_context": "unknown",
    }


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    images = load_images(download_file(FILES["images"]))
    labels = load_labels(download_file(FILES["labels"]))

    examples = []
    selected = 0
    for index, (image_bytes, label) in enumerate(zip(images, labels, strict=False)):
        garment_type, class_name = CLASS_MAP[label]
        if garment_type in {"bag", "shoe"}:
            continue
        filename = f"fashion-mnist-{selected + 1:03d}-{class_name.replace('/', '-')}.png"
        path = IMAGE_DIR / filename
        image = Image.frombytes("L", (28, 28), image_bytes).resize((224, 224))
        image.save(path)
        examples.append(
            {
                "image_path": f"eval/dataset/images/{filename}",
                "source": "Fashion-MNIST, Zalando Research",
                "source_index": index,
                "mime_type": "image/png",
                "expected": expected_for(label),
                "needs_manual_review": False,
            }
        )
        selected += 1
        if selected >= 100:
            break

    LABEL_PATH.write_text(json.dumps(examples, indent=2))
    print(f"Wrote {len(examples)} Fashion-MNIST examples to {LABEL_PATH}")


if __name__ == "__main__":
    main()

