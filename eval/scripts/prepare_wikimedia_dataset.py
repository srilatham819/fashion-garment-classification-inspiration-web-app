"""Prepare a 50-image open-license fashion evaluation starter set.

This script uses Wikimedia Commons search results and writes a label file that
should be manually reviewed before final reporting. The initial expected labels
come from the curated query buckets below so the eval can be run immediately,
but the case-study-quality workflow is to inspect each downloaded image and
correct `eval/dataset/labels/labels.json` before publishing the report.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT / "eval/dataset/images"
LABEL_PATH = ROOT / "eval/dataset/labels/labels.json"

QUERY_BUCKETS = [
    ("black dress fashion", {"garment_type": "dress", "color_palette": ["black"], "style": "casual", "material": "unknown", "pattern": "solid", "season": "fall/winter", "occasion": "everyday", "consumer_profile": "general fashion customer", "location_context": "unknown"}),
    ("red dress fashion", {"garment_type": "dress", "color_palette": ["red"], "style": "festive", "material": "unknown", "pattern": "solid", "season": "seasonless", "occasion": "celebration", "consumer_profile": "occasionwear customer", "location_context": "unknown"}),
    ("denim jacket street fashion", {"garment_type": "jacket", "color_palette": ["blue"], "style": "streetwear", "material": "denim", "pattern": "solid", "season": "fall/winter", "occasion": "everyday", "consumer_profile": "trend-led casual customer", "location_context": "street"}),
    ("white shirt fashion", {"garment_type": "top", "color_palette": ["white"], "style": "casual", "material": "cotton", "pattern": "solid", "season": "spring/summer", "occasion": "everyday", "consumer_profile": "general fashion customer", "location_context": "unknown"}),
    ("floral skirt fashion", {"garment_type": "skirt", "color_palette": ["unknown"], "style": "casual", "material": "unknown", "pattern": "printed", "season": "spring/summer", "occasion": "everyday", "consumer_profile": "general fashion customer", "location_context": "unknown"}),
]


def commons_search(query: str, limit: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"file:{query}",
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": "600",
            "format": "json",
            "origin": "*",
        }
    )
    request = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{params}",
        headers={"User-Agent": "fashion-inspiration-ai-eval/0.1 (local take-home project)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return list((payload.get("query", {}).get("pages") or {}).values())


def download(url: str, path: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "fashion-inspiration-ai-eval/0.1 (local take-home project)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    labels: list[dict[str, Any]] = []

    per_bucket = 10
    for bucket_index, (query, expected) in enumerate(QUERY_BUCKETS, start=1):
        pages = commons_search(query, per_bucket * 2)
        downloaded = 0
        for page in pages:
            image_info = (page.get("imageinfo") or [{}])[0]
            url = image_info.get("thumburl") or image_info.get("url")
            mime = image_info.get("mime") or "image/jpeg"
            if not url or not mime.startswith("image/"):
                continue
            suffix = ".png" if "png" in mime else ".jpg"
            filename = f"wikimedia-{bucket_index:02d}-{downloaded + 1:02d}{suffix}"
            path = IMAGE_DIR / filename
            try:
                download(url, path)
            except Exception:
                continue
            labels.append(
                {
                    "image_path": f"eval/dataset/images/{filename}",
                    "source": "Wikimedia Commons",
                    "source_query": query,
                    "mime_type": mime,
                    "expected": expected,
                    "needs_manual_review": True,
                }
            )
            downloaded += 1
            if downloaded >= per_bucket:
                break
            time.sleep(0.2)

    LABEL_PATH.write_text(json.dumps(labels, indent=2))
    print(f"Wrote {len(labels)} labeled starter examples to {LABEL_PATH}")


if __name__ == "__main__":
    main()
