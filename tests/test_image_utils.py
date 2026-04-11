"""Tests for ai.utils.image_utils."""

from pathlib import Path

import pytest
from PIL import Image

from ai.utils.image_utils import load_image, resize_if_too_large, save_image


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


def test_resize_if_too_large_downscales() -> None:
    image = Image.new("RGBA", (4000, 2000))
    resized = resize_if_too_large(image, max_side=2048)
    assert max(resized.size) == 2048
    assert resized.size == (2048, 1024)


def test_resize_if_too_large_keeps_small_images() -> None:
    image = Image.new("RGBA", (500, 300))
    resized = resize_if_too_large(image, max_side=2048)
    assert resized.size == (500, 300)
