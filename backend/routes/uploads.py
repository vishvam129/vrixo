"""Image upload."""

from __future__ import annotations

import io
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from backend.config import get_settings
from backend.deps import CurrentUser, DbSession
from backend.models import Upload
from backend.schemas import UploadOut
from backend.storage import get_storage

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_FORMATS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


def inspect_image(data: bytes, max_pixels: int) -> tuple[str, int, int]:
    """Return (format, width, height), judging by the bytes — not the filename
    or the Content-Type header, both of which the client controls."""
    try:
        with Image.open(io.BytesIO(data)) as image:
            image_format, (width, height) = image.format, image.size
            image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File is not a valid image"
        ) from None
    if image_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported format {image_format}; use JPEG, PNG or WebP",
        )
    if width * height > max_pixels:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Image has too many pixels")
    return image_format, width, height


@router.post("", response_model=UploadOut, status_code=status.HTTP_201_CREATED)
async def create_upload(file: UploadFile, user: CurrentUser, db: DbSession) -> Upload:
    settings = get_settings()
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)  # never buffer more than the limit
    if len(data) > limit:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE, f"File exceeds {settings.max_upload_mb} MB"
        )
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")

    image_format, width, height = inspect_image(data, settings.max_image_pixels)

    upload_id = str(uuid.uuid4())
    key = f"uploads/{user.id}/{upload_id}.{ALLOWED_FORMATS[image_format]}"
    get_storage().save(key, data)

    upload = Upload(
        id=upload_id,
        user_id=user.id,
        filename=(file.filename or "upload")[:255],
        image_format=image_format,
        size_bytes=len(data),
        width=width,
        height=height,
        storage_key=key,
    )
    db.add(upload)
    db.commit()
    return upload
