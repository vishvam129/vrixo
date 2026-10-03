"""Image upscaling — Vrixo AI feature.

Uses Real-ESRGAN x4 (``ai.models.realesrgan``) when its weights are installed,
and falls back to high-quality LANCZOS resampling otherwise, so the feature
works before any model is downloaded.

2x and 8x are produced from the 4x result (the model is trained for 4x):
2x is downsampled from it, 8x is the 4x output resampled once more.

Features:
    #13 2x / 4x / 8x upscaling CLI
    #14 Face-optimized upscale (GFPGAN face restoration when installed)
    #15 CPU / GPU auto-detection
    #16 Multiple scale factors
    #17 Unit-tested
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

from PIL import Image

try:  # pragma: no cover — torch is heavy, only import when available
    import torch

    _TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TORCH_AVAILABLE = False

from ai.models.weights import is_available
from ai.utils.image_utils import load_image, save_image

ScaleFactor = Literal[2, 4, 8]
Engine = Literal["auto", "realesrgan", "lanczos"]
UPSCALE_METHOD = Image.LANCZOS  # high-quality fallback

# Real-ESRGAN on CPU costs roughly a second per 192px tile; beyond this input
# size "auto" stays on LANCZOS rather than making the user wait minutes.
MAX_MODEL_INPUT_SIDE = 1024


def get_device() -> str:
    """Return 'cuda' if a GPU is available, else 'cpu'. (#15)"""
    if _TORCH_AVAILABLE and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def resolve_engine(engine: Engine, width: int, height: int) -> Literal["realesrgan", "lanczos"]:
    """Pick the engine that will actually run for an image of this size."""
    if engine == "lanczos":
        return "lanczos"
    if not is_available("realesrgan_x4"):
        if engine == "realesrgan":
            raise RuntimeError(
                "Real-ESRGAN weights are not installed — run: python -m ai.models.weights --download"
            )
        return "lanczos"
    if engine == "auto" and max(width, height) > MAX_MODEL_INPUT_SIDE:
        return "lanczos"
    return "realesrgan"


def _upscale_realesrgan(image: Image.Image, scale: int) -> Image.Image:
    """Run Real-ESRGAN on the colour channels; alpha (if any) is resampled."""
    import numpy as np

    from ai.models.realesrgan import upscale_x4

    rgba = image.convert("RGBA")
    rgb_x4 = Image.fromarray(upscale_x4(np.array(rgba.convert("RGB"))))
    target = (image.width * scale, image.height * scale)
    rgb = rgb_x4 if scale == 4 else rgb_x4.resize(target, UPSCALE_METHOD)

    result = rgb.convert("RGBA")
    result.putalpha(rgba.getchannel("A").resize(target, UPSCALE_METHOD))
    return result


def upscale_image(
    input_path: str | Path,
    output_path: str | Path,
    scale: ScaleFactor = 4,
    face_optimized: bool = False,
    engine: Engine = "auto",
) -> Path:
    """Upscale an image by the given factor.

    Args:
        input_path: Path to input image.
        output_path: Where to save the upscaled result.
        scale: Upscale factor (2, 4, or 8).
        face_optimized: If True, restore faces in the result (GFPGAN when
            installed, otherwise a light sharpening pass).
        engine: "auto" uses Real-ESRGAN when installed and the image is small
            enough; "realesrgan" / "lanczos" force one.

    Returns:
        Path where the upscaled image was saved.
    """
    if scale not in (2, 4, 8):
        raise ValueError(f"scale must be 2, 4, or 8; got {scale}")

    image = load_image(input_path)
    width, height = image.size

    if resolve_engine(engine, width, height) == "realesrgan":
        upscaled = _upscale_realesrgan(image, scale)
    else:
        upscaled = image.resize((width * scale, height * scale), UPSCALE_METHOD)

    if face_optimized:
        from ai.models.face_enhance import restore_faces_in_image

        upscaled, _ = restore_faces_in_image(upscaled)

    output_path = Path(output_path)
    save_image(upscaled, output_path)
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upscale images with AI.")
    parser.add_argument("--input", "-i", required=True, help="Path to input image")
    parser.add_argument("--output", "-o", required=True, help="Path to output image")
    parser.add_argument("--scale", "-s", type=int, default=4, choices=[2, 4, 8])
    parser.add_argument("--face", "-f", action="store_true", help="Face-optimized mode")
    parser.add_argument(
        "--engine",
        "-e",
        default="auto",
        choices=["auto", "realesrgan", "lanczos"],
        help="Upscaling engine",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    device = get_device()
    print(f"Using device: {device}")
    result = upscale_image(
        args.input, args.output, scale=args.scale, face_optimized=args.face, engine=args.engine
    )
    print(f"Upscaled {args.scale}x -> {result}")


if __name__ == "__main__":
    main()
