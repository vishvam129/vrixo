"""LaMa inpainting (Large Mask inpainting, TorchScript).

LaMa fills a masked region using fast Fourier convolutions, which gives it an
image-wide receptive field — it can continue textures and structures across a
large hole instead of smearing neighbouring pixels the way classical
inpainting does.

The image is inpainted at a bounded working resolution and the result is
composited back through the mask (feathered by a few pixels at its edge), so
the rest of the photo is returned exactly as it was.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import lru_cache

import cv2
import numpy as np
import torch

from ai.models.weights import weight_path

MAX_SIDE = 1024  # working resolution cap — keeps CPU time and memory bounded
MULTIPLE = 8  # the network downsamples 8x, so both sides must divide by 8

Inpainter = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]


@lru_cache(maxsize=1)
def load_model() -> torch.jit.ScriptModule:
    """Load the TorchScript big-lama checkpoint (cached after first call)."""
    with warnings.catch_warnings():
        # the published big-lama checkpoint is TorchScript; newer torch only
        # warns that the format is superseded by torch.export
        warnings.simplefilter("ignore", FutureWarning)
        model = torch.jit.load(str(weight_path("lama")), map_location="cpu")
    return model.eval()


def _pad_to_multiple(array: np.ndarray, multiple: int = MULTIPLE) -> np.ndarray:
    """Reflect-pad the bottom/right so height and width divide by ``multiple``."""
    height, width = array.shape[:2]
    pad_h, pad_w = -height % multiple, -width % multiple
    if pad_h == 0 and pad_w == 0:
        return array
    return cv2.copyMakeBorder(array, 0, pad_h, 0, pad_w, cv2.BORDER_REFLECT)


def inpaint(
    rgb: np.ndarray,
    mask: np.ndarray,
    *,
    run: Inpainter | None = None,
    max_side: int = MAX_SIDE,
) -> np.ndarray:
    """Fill the masked region of an HxWx3 uint8 RGB image.

    ``mask`` is HxW uint8 where non-zero means "remove this". ``run`` defaults
    to the LaMa network; it takes (image, mask) float tensors and returns the
    inpainted image tensor, all 1xCxHxW in [0, 1].
    """
    height, width = rgb.shape[:2]
    hole = (mask > 0).astype(np.uint8)

    # work at a bounded resolution
    scale = min(1.0, max_side / max(height, width))
    if scale < 1.0:
        size = (max(1, round(width * scale)), max(1, round(height * scale)))
        work_rgb = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)
        work_hole = cv2.resize(hole, size, interpolation=cv2.INTER_NEAREST)
    else:
        work_rgb, work_hole = rgb, hole

    work_h, work_w = work_rgb.shape[:2]
    image_t = torch.from_numpy(_pad_to_multiple(work_rgb)).permute(2, 0, 1).float().div(255.0)[None]
    mask_t = torch.from_numpy(_pad_to_multiple(work_hole)).float()[None, None]

    if run is None:
        model = load_model()

        def run(image: torch.Tensor, hole_mask: torch.Tensor) -> torch.Tensor:
            with torch.inference_mode():
                return model(image, hole_mask)

    output = run(image_t, mask_t)[0].permute(1, 2, 0).clamp(0, 1).mul(255.0).round().byte().numpy()
    filled = output[:work_h, :work_w]
    if scale < 1.0:
        filled = cv2.resize(filled, (width, height), interpolation=cv2.INTER_CUBIC)

    # only the hole (plus a few feathered pixels around it) takes the new content
    alpha = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), sigmaX=1.5)
    alpha = np.maximum(alpha, hole.astype(np.float32))[..., None]
    alpha[cv2.dilate(hole, np.ones((9, 9), np.uint8)) == 0] = 0.0
    blended = filled.astype(np.float32) * alpha + rgb.astype(np.float32) * (1.0 - alpha)
    return blended.round().astype(np.uint8)
