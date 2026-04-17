"""Run model evaluation against a labeled image dataset.

Expected label format:
[
  {
    "image_path": "eval/dataset/images/example.jpg",
    "expected": {
      "garment_type": "dress",
      "style": "festive",
      "material": "cotton",
      "color_palette": ["red"],
      "occasion": "celebration",
      "location_context": "unknown"
    }
  }
]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.schemas.classification import ClassificationResult
from app.services.openai_vision import OpenAIVisionClient


EVAL_FIELDS = [
    "garment_type",
    "style",
    "material",
    "color_palette",
    "pattern",
    "season",
    "occasion",
    "consumer_profile",
    "trend_notes",
    "location_context",
]


def load_labels(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def normalize(value: Any) -> str:
    if isinstance(value, list):
        return "|".join(sorted(str(item).strip().lower() for item in value))
    return str(value or "").strip().lower()


def score_predictions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: 0 for field in EVAL_FIELDS}
    correct = {field: 0 for field in EVAL_FIELDS}
    confusion: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for row in rows:
        expected = row["expected"]
        predicted = row.get("predicted") or {}
        for field in EVAL_FIELDS:
            if field not in expected:
                continue
            totals[field] += 1
            expected_value = normalize(expected.get(field))
            predicted_value = normalize(predicted.get(field))
            if expected_value == predicted_value:
                correct[field] += 1
            else:
                confusion[field][expected_value][predicted_value] += 1

    accuracy = {
        field: (correct[field] / totals[field] if totals[field] else None)
        for field in EVAL_FIELDS
    }
    return {
        "total_examples": len(rows),
        "accuracy": accuracy,
        "correct": correct,
        "totals": totals,
        "confusion": confusion,
    }


def write_summary(report: dict[str, Any], output_path: Path) -> None:
    lines = ["# Evaluation Summary", "", f"Total examples: {report['total_examples']}", "", "| Field | Accuracy |", "| --- | ---: |"]
    for field, accuracy in report["accuracy"].items():
        display = "n/a" if accuracy is None else f"{accuracy:.2%}"
        lines.append(f"| {field} | {display} |")
    lines.extend(["", "## Confusion Analysis", ""])
    for field, expected_map in report["confusion"].items():
        lines.append(f"### {field}")
        if not expected_map:
            lines.append("No mismatches.")
            lines.append("")
            continue
        for expected, predicted_map in expected_map.items():
            for predicted, count in predicted_map.items():
                lines.append(f"- expected `{expected}`, predicted `{predicted}`: {count}")
        lines.append("")
    output_path.write_text("\n".join(lines))


def run_eval(labels_path: Path, output_dir: Path) -> dict[str, Any]:
    labels = load_labels(labels_path)
    client = OpenAIVisionClient()
    rows = []
    for item in labels:
        image_path = str((ROOT / item["image_path"]).resolve())
        mime_type = item.get("mime_type", "image/jpeg")
        prediction: ClassificationResult = client.classify_image(image_path, mime_type)
        rows.append(
            {
                "image_path": item["image_path"],
                "expected": item["expected"],
                "predicted": prediction.model_dump(),
            }
        )

    report = score_predictions(rows)
    report["rows"] = rows
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "eval_report.json").write_text(json.dumps(report, indent=2, default=dict))
    write_summary(report, output_dir / "eval_summary.md")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, default=ROOT / "eval/dataset/labels/labels.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "eval/reports")
    args = parser.parse_args()
    run_eval(args.labels, args.output_dir)


if __name__ == "__main__":
    main()
