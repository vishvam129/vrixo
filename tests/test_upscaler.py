"""Tests for ai.models.upscaler."""

from pathlib import Path

import pytest
from PIL import Image

from ai.models.upscaler import get_device, upscale_image


@pytest.fixture
def small_image(tmp_path: Path) -> Path:
    path = tmp_path / "small.jpg"
    Image.new("RGB", (100, 100), color=(128, 128, 128)).save(path)
    return path


def test_upscale_2x(small_image: Path, tmp_path: Path) -> None:
    output = tmp_path / "out_2x.png"
    result = upscale_image(small_image, output, scale=2)
    assert result == output
    loaded = Image.open(output)
    assert loaded.size == (200, 200)


def test_upscale_4x(small_image: Path, tmp_path: Path) -> None:
    output = tmp_path / "out_4x.png"
    upscale_image(small_image, output, scale=4)
    loaded = Image.open(output)
    assert loaded.size == (400, 400)


def test_upscale_8x(small_image: Path, tmp_path: Path) -> None:
    output = tmp_path / "out_8x.png"
    upscale_image(small_image, output, scale=8)
    loaded = Image.open(output)
    assert loaded.size == (800, 800)


def test_invalid_scale_raises(small_image: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        upscale_image(small_image, tmp_path / "bad.png", scale=3)  # type: ignore[arg-type]


def test_face_optimized_mode(small_image: Path, tmp_path: Path) -> None:
    output = tmp_path / "face.png"
    result = upscale_image(small_image, output, scale=2, face_optimized=True)
    assert result.exists()


def test_get_device_returns_valid_value() -> None:
    device = get_device()
    assert device in ("cuda", "cpu")
