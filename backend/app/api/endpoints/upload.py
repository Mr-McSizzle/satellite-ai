import logging
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import settings
from app.schemas.analysis import ALLOWED_IMAGE_EXTENSIONS
from app.schemas.upload import UploadResponse

# Make the repo root importable so we can reach sentinel_index (offline engine).
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))

logger = logging.getLogger("app")
router = APIRouter()

ALLOWED_MODALITIES = {"optical", "SAR"}


def _upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.is_absolute():
        upload_dir = Path.cwd() / upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _safe_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported image extension. Upload .tif, .tiff, .png, .jpg or .jpeg.",
        )
    return suffix


def _auto_ingest(path: Path) -> None:
    """Add every cloud upload to the offline archive (runs after the response is sent)."""
    try:
        from sentinel_index.ingest import ingest_user_upload

        ingest_user_upload(path)
    except Exception as e:  # never let archiving break the chat flow
        logger.error(f"Failed to auto-ingest user upload {path.name}: {e}")


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload imagery for GAIA analysis",
    description="Stores a browser-uploaded image and returns a backend reference for /api/v1/analyze.",
)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    modality: str = Form("optical"),
) -> UploadResponse:
    """Stores an uploaded image using an opaque backend-generated filename."""
    if modality not in ALLOWED_MODALITIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported modality. Must be 'optical' or 'SAR'.",
        )

    original_name = file.filename or "image"
    extension = _safe_extension(original_name)
    upload_dir = _upload_dir()

    file_id = uuid4().hex
    destination = upload_dir / f"{file_id}{extension}"
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty.",
            )
        destination.write_bytes(contents)
    finally:
        await file.close()

    # Validate the image is decodable and build a browser-safe PNG preview.
    preview_url = None
    try:
        from sentinel_index.imaging import make_preview

        make_preview(destination, upload_dir / f"{file_id}.preview.png")
        preview_url = f"{settings.API_V1_STR}/upload/preview/{file_id}"
    except Exception as e:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not decode image '{original_name}': {e}",
        )

    background_tasks.add_task(_auto_ingest, destination)

    return UploadResponse(
        reference=str(destination),
        filename=original_name,
        modality=modality,
        preview_url=preview_url,
    )


@router.get("/upload/preview/{file_id}", summary="PNG preview of an uploaded image")
def get_preview(file_id: str):
    if not file_id.isalnum():
        raise HTTPException(status_code=400, detail="Invalid preview id.")
    path = _upload_dir() / f"{file_id}.preview.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Preview not found.")
    return FileResponse(path, media_type="image/png")
