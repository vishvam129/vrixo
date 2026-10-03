"""Tests for the Real-ESRGAN network, tiling and engine selection."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image
from torch.nn import functional as F

from ai.models import realesrgan, upscaler
from ai.models.realesrgan import RRDBNet, tiled_upscale

FIXTURES = Path(__file__).parent / "fixtures"


def _nearest_x4(tensor: torch.Tensor) -> torch.Tensor:
    """A stand-in 'model': plain nearest-neighbour 4x upsampling."""
    return F.interpolate(tensor, scale_factor=4, mode="nearest")


def test_network_upscales_four_times() -> None:
    model = RRDBNet(num_block=1).eval()
    with torch.inference_mode():
        out = model(torch.rand(1, 3, 24, 32))
    assert out.shape == (1, 3, 96, 128)


def test_layer_names_match_official_checkpoint() -> None:
    keys = set(RRDBNet(num_block=23).state_dict())
    assert {"conv_first.weight", "conv_body.bias", "conv_up2.weight", "conv_last.bias"} <= keys
    assert "body.22.rdb3.conv5.weight" in keys
    assert "body.23.rdb1.conv1.weight" not in keys


@pytest.mark.parametrize("size", [(64, 64), (50, 70), (193, 31)])
def test_tiling_matches_single_pass(size: tuple[int, int]) -> None:
    rng = np.random.default_rng(0)
    image = rng.integers(0, 256, (*size, 3), dtype=np.uint8)
    whole = tiled_upscale(image, _nearest_x4, tile=4096)
    tiled = tiled_upscale(image, _nearest_x4, tile=32, pad=8)
    assert whole.shape == (size[0] * 4, size[1] * 4, 3)
    assert np.array_equal(whole, tiled)


def test_tiles_get_surrounding_context() -> None:
    seen: list[tuple[int, int]] = []

    def spy(tensor: torch.Tensor) -> torch.Tensor:
        seen.append(tuple(tensor.shape[-2:]))
        return _nearest_x4(tensor)

    tiled_upscale(np.zeros((64, 64, 3), np.uint8), spy, tile=32, pad=8)
    assert len(seen) == 4
    assert all(shape == (40, 40) for shape in seen)  # 32 + 8px of context on the inner sides


def test_engine_falls_back_without_weights() -> None:
    # models are disabled by default in tests (see conftest)
    assert upscaler.resolve_engine("auto", 100, 100) == "lanczos"
    assert upscaler.resolve_engine("lanczos", 100, 100) == "lanczos"
    with pytest.raises(RuntimeError, match="weights"):
        upscaler.resolve_engine("realesrgan", 100, 100)


def test_auto_engine_skips_model_for_large_images(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(upscaler, "is_available", lambda *names: True)
    assert upscaler.resolve_engine("auto", 200, 200) == "realesrgan"
    assert upscaler.resolve_engine("auto", 4000, 3000) == "lanczos"
    assert upscaler.resolve_engine("realesrgan", 4000, 3000) == "realesrgan"  # forced


@pytest.mark.models
def test_real_weights_upscale_fixture(real_models: None, tmp_path: Path) -> None:
    source = Image.open(FIXTURES / "low_res.jpg").convert("RGB")
    out = realesrgan.upscale_x4(np.array(source))
    assert out.shape == (source.height * 4, source.width * 4, 3)

    lanczos = np.array(source.resize((source.width * 4, source.height * 4), Image.LANCZOS))
    assert np.abs(out.astype(int) - lanczos.astype(int)).mean() > 0.5  # not just a resize

    saved = upscaler.upscale_image(FIXTURES / "low_res.jpg", tmp_path / "x2.png", scale=2)
    assert Image.open(saved).size == (source.width * 2, source.height * 2)
