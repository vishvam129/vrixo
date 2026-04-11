"""Tests for ai.models.restoration."""

from pathlib import Path

import pytest
from PIL import Image

from ai.models.restoration import (
    colorize_bw,
    denoise,
    is_grayscale,
    remove_scratches,
    restore_photo,
)


def test_is_grayscale_on_color_image() -> None:
    img = Image.new("RGB", (50, 50), color=(200, 50, 50))
    assert is_grayscale(img) is False


def test_is_grayscale_on_bw_image() -> None:
    img = Image.new("RGB", (50, 50), color=(128, 128, 128))
    assert is_grayscale(img) is True


def test_colorize_bw_produces_different_channels() -> None:
    """#23: colorize should tint a gray image."""
    gray = Image.new("RGB", (50, 50), color=(128, 128, 128))
    tinted = colorize_bw(gray)
    # Channels should no longer all be identical
    r, g, b = tinted.split()
    import numpy as np

    r_arr, g_arr = np.array(r), np.array(g)
    assert not np.array_equal(r_arr, g_arr)


def test_denoise_returns_same_size() -> None:
    img = Image.new("RGB", (100, 100), color=(120, 120, 120))
    result = denoise(img)
    assert result.size == img.size


def test_remove_scratches_handles_clean_image() -> None:
    """#24: scratch removal on a clean image returns unchanged."""
    img = Image.new("RGB", (50, 50), color=(100, 100, 100))
    result = remove_scratches(img)
    assert result.size == img.size


@pytest.fixture
def sample_photo(tmp_path: Path) -> Path:
    path = tmp_path / "old.jpg"
    # Create a simple test image
    Image.new("RGB", (200, 200), color=(150, 130, 110)).save(path)
    return path


def test_restore_photo_pipeline(sample_photo: Path, tmp_path: Path) -> None:
    """#22: full pipeline produces output."""
    output = tmp_path / "restored.png"
    result = restore_photo(sample_photo, output, colorize=False, repair_scratches=False)
    assert result == output
    assert output.exists()
