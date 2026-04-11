"""Tests for ai.utils.image_utils."""

from pathlib import Path

import pytest
from PIL import Image

from ai.utils.image_utils import (
    convert_format,
    load_image,
    make_thumbnail,
    resize_if_too_large,
    resize_preserve_aspect,
    save_image,
    strip_exif,
)


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    Image.new("RGB", (100, 50), color=(255, 0, 0)).save(path)
    return path


def test_load_image_returns_rgba(sample_image: Path) -> None:
    image = load_image(sample_image)
    assert image.mode == "RGBA"
    assert image.size == (100, 50)


def test_save_image_creates_parent_dirs(tmp_path: Path) -> None:
    image = Image.new("RGBA", (10, 10))
    target = tmp_path / "nested" / "dir" / "out.png"
    save_image(image, target)
    assert target.exists()


def test_save_image_converts_rgba_to_jpeg(tmp_path: Path) -> None:
    """JPEG doesn't support alpha — should auto-convert."""
    image = Image.new("RGBA", (10, 10), color=(255, 0, 0, 128))
    target = tmp_path / "out.jpg"
    save_image(image, target)
    loaded = Image.open(target)
    assert loaded.mode == "RGB"


def test_resize_if_too_large_downscales() -> None:
    image = Image.new("RGBA", (4000, 2000))
    resized = resize_if_too_large(image, max_side=2048)
    assert max(resized.size) == 2048
    assert resized.size == (2048, 1024)


def test_resize_if_too_large_keeps_small_images() -> None:
    image = Image.new("RGBA", (500, 300))
    resized = resize_if_too_large(image, max_side=2048)
    assert resized.size == (500, 300)


def test_convert_format_jpg_to_png(sample_image: Path, tmp_path: Path) -> None:
    """#31: convert JPG to PNG."""
    output = tmp_path / "converted.png"
    result = convert_format(sample_image, output)
    assert result == output
    assert Image.open(output).format == "PNG"


def test_convert_format_png_to_webp(sample_image: Path, tmp_path: Path) -> None:
    """#31: convert PNG to WebP."""
    output = tmp_path / "out.webp"
    convert_format(sample_image, output)
    assert Image.open(output).format == "WEBP"


def test_convert_format_unsupported_raises(sample_image: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        convert_format(sample_image, tmp_path / "out.xyz", output_format="XYZ")


def test_strip_exif_returns_clean_image() -> None:
    """#32: strip_exif returns an image with same content but no metadata."""
    image = Image.new("RGB", (20, 20), color=(100, 150, 200))
    stripped = strip_exif(image)
    assert stripped.size == image.size
    assert stripped.mode == image.mode
    assert list(stripped.getdata()) == list(image.getdata())


def test_resize_preserve_aspect_landscape() -> None:
    """#33: landscape image resize preserves aspect ratio."""
    image = Image.new("RGB", (2000, 1000))
    resized = resize_preserve_aspect(image, max_side=1024)
    assert resized.size == (1024, 512)


def test_resize_preserve_aspect_portrait() -> None:
    image = Image.new("RGB", (500, 1000))
    resized = resize_preserve_aspect(image, max_side=800)
    assert resized.size == (400, 800)


def test_make_thumbnail_under_size() -> None:
    """#34: thumbnail fits within specified size."""
    image = Image.new("RGB", (1000, 500))
    thumb = make_thumbnail(image, size=256)
    assert max(thumb.size) <= 256


def test_make_thumbnail_preserves_aspect_ratio() -> None:
    image = Image.new("RGB", (2000, 1000))
    thumb = make_thumbnail(image, size=200)
    # Aspect ratio should be preserved
    original_ratio = 2000 / 1000
    thumb_ratio = thumb.size[0] / thumb.size[1]
    assert abs(original_ratio - thumb_ratio) < 0.01
