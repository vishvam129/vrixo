"""Real-ESRGAN x4 super-resolution, implemented directly in PyTorch.

The official ``RealESRGAN_x4plus`` generator is an RRDBNet: 23 Residual-in-
Residual Dense Blocks followed by two nearest-neighbour 2x upsampling stages.
The network is defined here (layer names match the released checkpoint, so the
official weights load unchanged) instead of depending on the unmaintained
``basicsr`` / ``realesrgan`` packages.

Large images are processed in overlapping tiles so memory stays flat on CPU.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ai.models.weights import weight_path

SCALE = 4


class ResidualDenseBlock(nn.Module):
    """Five 3x3 convs where each sees the concatenation of all earlier outputs."""

    def __init__(self, num_feat: int = 64, num_grow_ch: int = 32) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
        self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
        self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.lrelu(self.conv1(x))
        x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x  # residual scaling keeps a deep stack trainable


class RRDB(nn.Module):
    """Residual-in-Residual Dense Block: three dense blocks plus a skip."""

    def __init__(self, num_feat: int, num_grow_ch: int = 32) -> None:
        super().__init__()
        self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
        self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.rdb3(self.rdb2(self.rdb1(x)))
        return out * 0.2 + x


class RRDBNet(nn.Module):
    """The Real-ESRGAN x4 generator."""

    def __init__(self, num_feat: int = 64, num_block: int = 23, num_grow_ch: int = 32) -> None:
        super().__init__()
        self.conv_first = nn.Conv2d(3, num_feat, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(num_feat, num_grow_ch) for _ in range(num_block)])
        self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
        self.conv_last = nn.Conv2d(num_feat, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.conv_first(x)
        feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def load_model() -> RRDBNet:
    """Build the network and load the official checkpoint (cached after first call)."""
    checkpoint = torch.load(weight_path("realesrgan_x4"), map_location="cpu", weights_only=True)
    state = checkpoint.get("params_ema", checkpoint.get("params", checkpoint))
    model = RRDBNet()
    model.load_state_dict(state, strict=True)
    return model.eval().to(get_device())


def tiled_upscale(
    image: np.ndarray,
    run: Callable[[torch.Tensor], torch.Tensor],
    *,
    scale: int = SCALE,
    tile: int = 192,
    pad: int = 16,
) -> np.ndarray:
    """Upscale an HxWx3 uint8 RGB array tile by tile.

    Each tile is run with ``pad`` pixels of surrounding context and only its
    centre is kept, so there are no visible seams where tiles meet.
    ``run`` maps a 1x3xhxw float tensor in [0, 1] to its upscaled version.
    """
    height, width = image.shape[:2]
    source = torch.from_numpy(image).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    output = torch.zeros((3, height * scale, width * scale), dtype=torch.float32)

    for top in range(0, height, tile):
        for left in range(0, width, tile):
            bottom, right = min(top + tile, height), min(left + tile, width)
            # the padded window, clamped to the image
            p_top, p_left = max(top - pad, 0), max(left - pad, 0)
            p_bottom, p_right = min(bottom + pad, height), min(right + pad, width)

            result = run(source[:, :, p_top:p_bottom, p_left:p_right])[0]

            # cut the context back off (coordinates are in upscaled pixels)
            y0, x0 = (top - p_top) * scale, (left - p_left) * scale
            y1, x1 = y0 + (bottom - top) * scale, x0 + (right - left) * scale
            output[:, top * scale : bottom * scale, left * scale : right * scale] = result[
                :, y0:y1, x0:x1
            ]

    return output.clamp(0, 1).mul(255.0).round().byte().permute(1, 2, 0).numpy()


def upscale_x4(image: np.ndarray, *, tile: int = 192, pad: int = 16) -> np.ndarray:
    """Upscale an HxWx3 uint8 RGB array 4x with Real-ESRGAN."""
    model = load_model()
    device = get_device()

    def run(tensor: torch.Tensor) -> torch.Tensor:
        with torch.inference_mode():
            return model(tensor.to(device)).cpu()

    return tiled_upscale(image, run, tile=tile, pad=pad)
