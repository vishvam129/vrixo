"""Tests for web.watermark."""

import numpy as np
from PIL import Image

from web.watermark import apply_watermark


def test_watermark_returns_same_size() -> None:
    img = Image.new("RGB", (500, 300), color=(128, 128, 128))
    result = apply_watermark(img)
    assert result.size == (500, 300)


def test_watermark_changes_pixels() -> None:
    """#59: watermark should visibly alter the image."""
    img = Image.new("RGB", (600, 400), color=(100, 100, 100))
    result = apply_watermark(img, text="TEST")

    original = np.array(img.convert("RGBA"))
    modified = np.array(result.convert("RGBA"))
    assert not np.array_equal(original, modified)


def test_watermark_output_is_rgba() -> None:
    img = Image.new("RGB", (300, 300))
    result = apply_watermark(img)
    assert result.mode == "RGBA"


def test_watermark_position_bottom_right_changes_corner() -> None:
    """#61: bottom-right placement should alter bottom-right pixels."""
    img = Image.new("RGB", (800, 600), color=(0, 0, 0))
    result = apply_watermark(img, text="VRIXO", position="bottom-right")
    arr = np.array(result.convert("RGB"))
    # Somewhere in the bottom-right quadrant should have non-black pixels
    bottom_right = arr[400:, 400:]
    assert bottom_right.sum() > 0
