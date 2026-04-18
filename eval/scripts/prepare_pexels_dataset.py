"""Download a 50-100 image fashion evaluation set from Pexels.

Usage:
    PEXELS_API_KEY=... python eval/scripts/prepare_pexels_dataset.py --count 80

The script uses the official Pexels API instead of scraping the website. Pexels
requires an API key for programmatic access. It writes:

- eval/dataset/images/pexels-*.jpg
- eval/dataset/labels/labels.json
- eval/dataset/pexels_attribution.json

The initial labels are query-derived starter labels and are marked
`needs_manual_review=true`. For a final case-study submission, inspect every
image and correct the expected fields before reporting accuracy.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT / "eval/dataset/images"
LABEL_PATH = ROOT / "eval/dataset/labels/labels.json"
ATTRIBUTION_PATH = ROOT / "eval/dataset/pexels_attribution.json"

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

QUERY_BUCKETS = [
    {
        "query": "black dress fashion",
        "expected": {
            "garment_type": "dress",
            "style": "casual",
            "material": "unknown",
            "color_palette": ["black"],
            "pattern": "unknown",
            "season": "fall/winter",
            "occasion": "everyday",
            "consumer_profile": "general fashion customer",
            "trend_notes": "Pexels fashion image",
            "location_context": "unknown",
        },
    },
    {
        "query": "red dress fashion",
        "expected": {
            "garment_type": "dress",
            "style": "festive",
            "material": "unknown",
            "color_palette": ["red"],
            "pattern": "unknown",
            "season": "seasonless",
            "occasion": "celebration",
            "consumer_profile": "occasionwear customer",
            "trend_notes": "Pexels fashion image",
            "location_context": "unknown",
        },
    },
    {
        "query": "streetwear jacket fashion",
        "expected": {
            "garment_type": "jacket",
            "style": "streetwear",
            "material": "unknown",
            "color_palette": ["unknown"],
            "pattern": "unknown",
            "season": "fall/winter",
            "occasion": "everyday",
            "consumer_profile": "trend-led casual customer",
            "trend_notes": "Pexels streetwear image",
            "location_context": "street",
        },
    },
    {
        "query": "white shirt fashion",
        "expected": {
            "garment_type": "top",
            "style": "casual",
            "material": "cotton",
            "color_palette": ["white"],
            "pattern": "solid",
            "season": "spring/summer",
            "occasion": "everyday",
            "consumer_profile": "general fashion customer",
            "trend_notes": "Pexels fashion image",
            "location_context": "unknown",
        },
    },
    {
        "query": "floral skirt fashion",
        "expected": {
            "garment_type": "skirt",
            "style": "casual",
            "material": "unknown",
            "color_palette": ["unknown"],
            "pattern": "printed",
            "season": "spring/summer",
            "occasion": "everyday",
            "consumer_profile": "general fashion customer",
            "trend_notes": "Pexels fashion image",
            "location_context": "unknown",
        },
    },
]


def api_get(url: str, api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": api_key,
            "User-Agent": "atelier-lens-ai-eval/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, path: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "atelier-lens-ai-eval/0.1"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        path.write_bytes(response.read())


def search_photos(api_key: str, query: str, count: int) -> list[dict[str, Any]]:
    photos: list[dict[str, Any]] = []
    page = 1
    while len(photos) < count:
        params = urllib.parse.urlencode(
            {
                "query": query,
                "orientation": "portrait",
                "per_page": min(80, count - len(photos)),
                "page": page,
            }
        )
        payload = api_get(f"{PEXELS_SEARCH_URL}?{params}", api_key)
        batch = payload.get("photos") or []
        if not batch:
            break
        photos.extend(batch)
        page += 1
        time.sleep(0.25)
    return photos[:count]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=80, help="Total images to download. Use 50-100 for the case study.")
    parser.add_argument("--clear-existing", action="store_true", help="Delete existing pexels-* images before downloading.")
    args = parser.parse_args()

    if args.count < 50 or args.count > 100:
        raise SystemExit("--count must be between 50 and 100 for this case-study dataset.")

    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise SystemExit(
            "PEXELS_API_KEY is not set. Create a free Pexels API key and run:\n"
            "PEXELS_API_KEY=your_key .venv312/bin/python eval/scripts/prepare_pexels_dataset.py --count 80"
        )

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if args.clear_existing:
        for path in IMAGE_DIR.glob("pexels-*.jpg"):
            path.unlink()

    per_bucket = max(1, args.count // len(QUERY_BUCKETS))
    remainder = args.count % len(QUERY_BUCKETS)
    labels: list[dict[str, Any]] = []
    attribution: list[dict[str, Any]] = []
    seen_ids: set[int] = set()

    for bucket_index, bucket in enumerate(QUERY_BUCKETS):
        target = per_bucket + (1 if bucket_index < remainder else 0)
        photos = search_photos(api_key, bucket["query"], target * 2)
        downloaded = 0
        for photo in photos:
            photo_id = int(photo["id"])
            if photo_id in seen_ids:
                continue
            seen_ids.add(photo_id)
            image_url = photo["src"].get("large2x") or photo["src"].get("large") or photo["src"].get("original")
            if not image_url:
                continue

            filename = f"pexels-{len(labels) + 1:03d}-{photo_id}.jpg"
            image_path = IMAGE_DIR / filename
            try:
                download_file(image_url, image_path)
            except Exception:
                continue

            labels.append(
                {
                    "image_path": f"eval/dataset/images/{filename}",
                    "source": "Pexels",
                    "source_query": bucket["query"],
                    "pexels_id": photo_id,
                    "mime_type": "image/jpeg",
                    "expected": bucket["expected"],
                    "needs_manual_review": True,
                }
            )
            attribution.append(
                {
                    "pexels_id": photo_id,
                    "photographer": photo.get("photographer"),
                    "photographer_url": photo.get("photographer_url"),
                    "photo_url": photo.get("url"),
                    "local_file": f"eval/dataset/images/{filename}",
                    "source_query": bucket["query"],
                }
            )
            downloaded += 1
            if downloaded >= target or len(labels) >= args.count:
                break
        if len(labels) >= args.count:
            break

    LABEL_PATH.write_text(json.dumps(labels, indent=2))
    ATTRIBUTION_PATH.write_text(json.dumps(attribution, indent=2))
    print(f"Downloaded {len(labels)} Pexels images")
    print(f"Wrote labels to {LABEL_PATH}")
    print(f"Wrote attribution to {ATTRIBUTION_PATH}")
    if len(labels) < args.count:
        print("Warning: fewer images were downloaded than requested. Re-run with another query/API key quota if needed.")


if __name__ == "__main__":
    main()
