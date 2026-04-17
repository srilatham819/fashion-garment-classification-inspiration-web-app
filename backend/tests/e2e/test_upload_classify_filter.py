from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image as PILImage

from app.core.config import settings
from app.main import app


def test_upload_classify_and_filter_end_to_end(tmp_path) -> None:
    settings.upload_storage_path = str(tmp_path / "uploads")
    settings.demo_ai_fallback = True
    settings.faiss_index_path = str(tmp_path / "faiss.index")
    settings.openai_api_key = None

    image_path = tmp_path / "black-dress.png"
    PILImage.new("RGB", (128, 128), (8, 8, 8)).save(image_path)

    client = TestClient(app)
    with image_path.open("rb") as image_file:
        upload_response = client.post(
            "/api/images",
            files={"file": ("black-dress.png", image_file, "image/png")},
        )

    assert upload_response.status_code == 201
    image_id = upload_response.json()["image_id"]

    detail_response = client.get(f"/api/images/{image_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["status"] == "classified"
    assert detail["ai_metadata"]["garment_type"] == "dress"
    assert "black" in detail["ai_metadata"]["color_palette"]

    search_response = client.post(
        "/api/search",
        json={"query": "black dress", "limit": 10},
    )
    assert search_response.status_code == 200
    results = search_response.json()
    assert [result["image_id"] for result in results] == [image_id]

