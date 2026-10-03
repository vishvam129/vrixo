"""Tests for LaMa inpainting: padding, compositing, downscaling and the real model."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

from ai.models import lama, object_remove

FIXTURES = Path(__file__).parent / "fixtures"


def _fill_white(image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """A stand-in 'model' that paints everything white."""
    return torch.ones_like(image)


def _square_mask(height: int, width: int) -> np.ndarray:
    mask = np.zeros((height, width), dtype=np.uint8)
    mask[20:40, 30:60] = 255
    return mask


def test_hole_is_filled_and_rest_is_untouched() -> None:
    rgb = np.full((80, 100, 3), 50, dtype=np.uint8)
    out = lama.inpaint(rgb, _square_mask(80, 100), run=_fill_white)

    assert (out[25:35, 35:55] == 255).all()  # inside the hole: new content
    assert (out[60:, :] == 50).all()  # far from the hole: identical
    assert (out[:, :15] == 50).all()
    assert out.shape == rgb.shape


def test_inputs_are_padded_to_multiple_of_eight() -> None:
    shapes: list[tuple[int, ...]] = []

    def spy(image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        shapes.append((*image.shape, *mask.shape))
        return image

    out = lama.inpaint(np.zeros((75, 101, 3), np.uint8), _square_mask(75, 101), run=spy)

    assert shapes == [(1, 3, 80, 104, 1, 1, 80, 104)]
    assert out.shape == (75, 101, 3)  # padding is cropped off again


def test_mask_is_binarised_for_the_model() -> None:
    values: list[set[float]] = []

    def spy(image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        values.append(set(mask.unique().tolist()))
        return image

    grey_mask = np.zeros((64, 64), np.uint8)
    grey_mask[10:20, 10:20] = 7  # any non-zero value means "remove"
    lama.inpaint(np.zeros((64, 64, 3), np.uint8), grey_mask, run=spy)
    assert values == [{0.0, 1.0}]


def test_large_images_are_inpainted_at_bounded_resolution() -> None:
    sizes: list[tuple[int, int]] = []

    def spy(image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        sizes.append(tuple(image.shape[-2:]))
        return torch.ones_like(image)

    rgb = np.full((400, 800, 3), 10, dtype=np.uint8)
    mask = np.zeros((400, 800), np.uint8)
    mask[100:200, 300:500] = 255
    out = lama.inpaint(rgb, mask, run=spy, max_side=200)

    assert sizes == [(104, 200)]  # 800x400 → 200x100, padded to 104
    assert out.shape == rgb.shape
    assert (out[140:160, 380:420] == 255).all()
    assert (out[300:, :] == 10).all()


def test_object_remove_uses_opencv_when_models_disabled(tmp_path: Path) -> None:
    out = object_remove.remove_object(FIXTURES / "with_object.jpg", tmp_path / "o.png", auto=True)
    assert Image.open(out).size == Image.open(FIXTURES / "with_object.jpg").size


@pytest.mark.models
def test_real_model_removes_object(real_models: None) -> None:
    image = Image.open(FIXTURES / "with_object.jpg").convert("RGB")
    rgb = np.array(image)
    mask = object_remove.auto_detect_object(image)
    assert mask.any()

    out = lama.inpaint(rgb, mask)

    assert out.shape == rgb.shape
    hole = mask > 0
    assert np.abs(out[hole].astype(int) - rgb[hole].astype(int)).mean() > 5  # object gone
    far = np.zeros_like(hole)
    far[:10, :10] = True
    if not (hole & far).any():
        assert np.array_equal(out[:10, :10], rgb[:10, :10])
