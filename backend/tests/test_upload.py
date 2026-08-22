from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings


def test_upload_image_returns_backend_reference(client: TestClient, tmp_path: Path) -> None:
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path)

    try:
        response = client.post(
            "/api/v1/upload",
            data={"modality": "optical"},
            files={"file": ("scene.png", b"fake image bytes", "image/png")},
        )
    finally:
        settings.UPLOAD_DIR = original_upload_dir

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["filename"] == "scene.png"
    assert data["modality"] == "optical"
    assert data["reference"].endswith(".png")
    assert Path(data["reference"]).exists()


def test_upload_rejects_unsupported_extension(client: TestClient, tmp_path: Path) -> None:
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path)

    try:
        response = client.post(
            "/api/v1/upload",
            data={"modality": "optical"},
            files={"file": ("scene.bmp", b"fake image bytes", "image/bmp")},
        )
    finally:
        settings.UPLOAD_DIR = original_upload_dir

    assert response.status_code == 422


def test_upload_rejects_unsupported_modality(client: TestClient, tmp_path: Path) -> None:
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path)

    try:
        response = client.post(
            "/api/v1/upload",
            data={"modality": "thermal"},
            files={"file": ("scene.tif", b"fake image bytes", "image/tiff")},
        )
    finally:
        settings.UPLOAD_DIR = original_upload_dir

    assert response.status_code == 422
