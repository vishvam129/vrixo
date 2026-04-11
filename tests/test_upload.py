"""Tests for web.upload."""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from web.upload import (
    UploadError,
    _touch_file_with_mtime,
    cleanup_old_uploads,
    download_as_format,
    generate_unique_filename,
    save_upload,
    validate_file_size,
    validate_real_image,
)


def _make_image_bytes(fmt: str = "PNG", size: tuple[int, int] = (100, 100)) -> bytes:
    """Build a real image in memory as bytes."""
    buf = BytesIO()
    Image.new("RGB", size, color=(128, 64, 32)).save(buf, format=fmt)
    return buf.getvalue()


def test_validate_file_size_small_ok() -> None:
    validate_file_size(_make_image_bytes())  # should not raise


def test_validate_file_size_too_large_raises() -> None:
    """#45: oversized files are rejected."""
    fake_big_bytes = b"\x00" * (11 * 1024 * 1024)
    with pytest.raises(UploadError):
        validate_file_size(fake_big_bytes)


def test_validate_real_image_accepts_png() -> None:
    """#44: real PNG passes validation."""
    fmt = validate_real_image(_make_image_bytes("PNG"))
    assert fmt == "PNG"


def test_validate_real_image_accepts_jpeg() -> None:
    fmt = validate_real_image(_make_image_bytes("JPEG"))
    assert fmt == "JPEG"


def test_validate_real_image_rejects_garbage() -> None:
    """#44: spoofed file (not a real image) is rejected."""
    with pytest.raises(UploadError):
        validate_real_image(b"not an image at all")


def test_generate_unique_filename_is_unique() -> None:
    """#47: each call produces a different name."""
    names = {generate_unique_filename("photo.jpg") for _ in range(10)}
    assert len(names) == 10
    for name in names:
        assert name.endswith(".jpg")


def test_save_upload_strips_exif(tmp_path: Path, monkeypatch) -> None:
    """#48: EXIF is stripped from saved uploads."""
    from web import upload

    monkeypatch.setattr(upload, "UPLOAD_DIR", tmp_path / "uploads")

    path = save_upload(_make_image_bytes("JPEG"), "photo.jpg", strip_metadata=True)
    assert path.exists()
    # Uploaded file should be loadable as a real image
    loaded = Image.open(path)
    assert loaded.size == (100, 100)


def test_cleanup_old_uploads(tmp_path: Path, monkeypatch) -> None:
    """#46: files older than retention are deleted."""
    from web import upload

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(upload, "UPLOAD_DIR", upload_dir)

    # Create an old file and a fresh file
    old_file = upload_dir / "old.png"
    old_file.write_bytes(b"old")
    fresh_file = upload_dir / "fresh.png"
    fresh_file.write_bytes(b"fresh")

    _touch_file_with_mtime(old_file, hours_ago=48)
    # Fresh file keeps default mtime

    deleted = cleanup_old_uploads(max_age_hours=24)
    assert deleted == 1
    assert not old_file.exists()
    assert fresh_file.exists()


def test_download_as_format_png_to_webp(tmp_path: Path) -> None:
    """#49: download can convert to a different format."""
    source = tmp_path / "photo.png"
    Image.new("RGB", (50, 50)).save(source)
    target = tmp_path / "converted.webp"
    result = download_as_format(source, "WEBP", output_path=target)
    assert result == target
    assert Image.open(target).format == "WEBP"
