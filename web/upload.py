"""File upload validation and management for Vrixo.

Features:
    #44 Validate uploaded file is a real image (not spoofed extension)
    #45 Enforce 10MB maximum upload size
    #46 Auto-delete uploaded files after 24 hours
    #47 Generate unique filename to prevent collisions
    #48 Strip EXIF from uploaded images by default
    #49 Support download in multiple formats
"""

from __future__ import annotations

import os
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from PIL import Image

from ai.utils.image_utils import convert_format, strip_exif

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "./uploads"))
MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "10"))
RETENTION_HOURS = int(os.environ.get("UPLOAD_RETENTION_HOURS", "24"))

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP"}


class UploadError(ValueError):
    """Raised when an uploaded file fails validation."""


def validate_file_size(file_bytes: bytes) -> None:
    """#45: Enforce maximum upload size."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise UploadError(f"File too large: {size_mb:.1f} MB (max {MAX_UPLOAD_SIZE_MB} MB)")


def validate_real_image(file_bytes: bytes) -> str:
    """#44: Verify the file is a real image by loading it.

    Returns:
        The detected image format (e.g. "JPEG").
    Raises:
        UploadError if the file is not a valid image.
    """
    from io import BytesIO

    try:
        with Image.open(BytesIO(file_bytes)) as img:
            img.verify()
        # verify() closes the file, so reopen to read format
        with Image.open(BytesIO(file_bytes)) as img:
            fmt = img.format or ""
    except Exception as exc:
        raise UploadError(f"Not a valid image: {exc}") from exc

    if fmt not in ALLOWED_FORMATS:
        raise UploadError(f"Unsupported image format: {fmt}")
    return fmt


def generate_unique_filename(original_name: str) -> str:
    """#47: Generate a collision-proof filename."""
    suffix = Path(original_name).suffix.lower() or ".png"
    unique = uuid.uuid4().hex
    return f"{unique}{suffix}"


def save_upload(
    file_bytes: bytes,
    original_name: str,
    strip_metadata: bool = True,
) -> Path:
    """Full upload pipeline: validate, save with unique name, strip EXIF.

    Returns:
        Path to the saved file.
    """
    validate_file_size(file_bytes)
    validate_real_image(file_bytes)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = generate_unique_filename(original_name)
    target = UPLOAD_DIR / filename

    from io import BytesIO

    image = Image.open(BytesIO(file_bytes))
    if strip_metadata:  # #48
        image = strip_exif(image)
    image.save(target)
    return target


def cleanup_old_uploads(max_age_hours: int | None = None) -> int:
    """#46: Delete uploads older than max_age_hours. Returns count deleted."""
    max_age = max_age_hours if max_age_hours is not None else RETENTION_HOURS
    if not UPLOAD_DIR.exists():
        return 0

    cutoff = datetime.now(UTC) - timedelta(hours=max_age)
    deleted = 0
    for file in UPLOAD_DIR.iterdir():
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=UTC)
        if mtime < cutoff:
            file.unlink()
            deleted += 1
    return deleted


def download_as_format(
    source_path: str | Path,
    target_format: str,
    output_path: str | Path | None = None,
) -> Path:
    """#49: Convert a stored file to a user's requested download format."""
    source = Path(source_path)
    if output_path is None:
        output_path = source.with_suffix(f".{target_format.lower()}")
    return convert_format(source, output_path, output_format=target_format.upper())


def _touch_file_with_mtime(path: Path, hours_ago: float) -> None:
    """Test helper: set a file's mtime to `hours_ago` hours in the past."""
    new_time = time.time() - hours_ago * 3600
    os.utime(path, (new_time, new_time))
