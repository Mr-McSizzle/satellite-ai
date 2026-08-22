from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.analysis import ALLOWED_IMAGE_EXTENSIONS
from app.schemas.upload import UploadResponse

router = APIRouter()

ALLOWED_MODALITIES = {"optical", "SAR"}


def _safe_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported image extension. Upload .tif, .tiff, .png, .jpg or .jpeg.",
        )
    return suffix


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload imagery for GAIA analysis",
    description="Stores a browser-uploaded image and returns a backend reference for /api/v1/analyze.",
)
async def upload_image(
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
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.is_absolute():
        upload_dir = Path.cwd() / upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    destination = upload_dir / f"{uuid4().hex}{extension}"
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

    return UploadResponse(
        reference=str(destination),
        filename=original_name,
        modality=modality,
    )
