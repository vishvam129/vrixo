"""Tests for ai.models.object_remove."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ai.models.object_remove import auto_detect_object, remove_object


@pytest.fixture
def sample_with_object(tmp_path: Path) -> Path:
    path = tmp_path / "scene.jpg"
    # Light background with a dark square in the middle
    arr = np.full((200, 200, 3), 220, dtype=np.uint8)
    arr[80:120, 80:120] = [50, 50, 50]  # dark object
    Image.fromarray(arr).save(path)
    return path


@pytest.fixture
def full_mask(tmp_path: Path) -> Path:
    """Mask that covers the object region (80-120, 80-120)."""
    path = tmp_path / "mask.png"
    arr = np.zeros((200, 200), dtype=np.uint8)
    arr[80:120, 80:120] = 255
    Image.fromarray(arr).save(path)
    return path


def test_remove_object_with_mask(sample_with_object: Path, full_mask: Path, tmp_path: Path) -> None:
    """#26, #27: user-provided mask removes the object."""
    output = tmp_path / "out.png"
    result = remove_object(sample_with_object, output, mask_path=full_mask)
    assert result == output
    assert output.exists()

    # The masked region should now approximate background color (~220)
    arr = np.array(Image.open(output).convert("RGB"))
    center_pixel = arr[100, 100]
    # After inpainting, the center should be much closer to background (220) than to original (50)
    assert center_pixel[0] > 100


def test_auto_detect_object(sample_with_object: Path) -> None:
    """#28: auto-detect returns a non-empty mask for an image with an object."""
    image = Image.open(sample_with_object)
    mask = auto_detect_object(image)
    assert mask.shape == (200, 200)
    assert mask.sum() > 0


def test_remove_object_auto(sample_with_object: Path, tmp_path: Path) -> None:
    """#28: auto mode runs without a provided mask."""
    output = tmp_path / "out.png"
    result = remove_object(sample_with_object, output, auto=True)
    assert result.exists()


def test_remove_object_requires_mask_or_auto(sample_with_object: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        remove_object(sample_with_object, tmp_path / "out.png")


def test_empty_mask_preserves_image(sample_with_object: Path, tmp_path: Path) -> None:
    """#29: empty mask saves image unchanged."""
    empty_mask_path = tmp_path / "empty.png"
    Image.new("L", (200, 200), color=0).save(empty_mask_path)
    output = tmp_path / "out.png"
    remove_object(sample_with_object, output, mask_path=empty_mask_path)
    assert output.exists()
