from fastapi.testclient import TestClient

from app.main import app


def test_upload_image_saves_file_and_returns_image_id(monkeypatch, tmp_path) -> None:
    from app.api.routes import images as images_route
    from app.core.config import settings

    settings.upload_storage_path = str(tmp_path)
    monkeypatch.setattr(images_route, "classify_image_task", lambda image_id: None)

    client = TestClient(app)
    response = client.post(
        "/api/images",
        files={"file": ("dress.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["image_id"] > 0
    assert body["status"] == "pending"
    assert list(tmp_path.iterdir())


def test_upload_rejects_non_image(tmp_path) -> None:
    from app.core.config import settings

    settings.upload_storage_path = str(tmp_path)
    client = TestClient(app)
    response = client.post(
        "/api/images",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400

