"""Old photo restoration — Vrixo AI feature.

Combines multiple restoration steps into one pipeline:
    1. Denoise
    2. Sharpen / face enhance
    3. Optional upscale
    4. Optional colorization (B&W -> color)
    5. Optional scratch repair

Features:
    #22 Restoration pipeline CLI
    #23 B&W colorization
    #24 Scratch / damage detection + inpainting
    #25 Unit-tested
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from ai.models.face_enhance import enhance_faces
from ai.utils.image_utils import load_image, save_image


def is_grayscale(image: Image.Image, tolerance: int = 10) -> bool:
    """Detect whether an image is effectively black-and-white."""
    arr = np.array(image.convert("RGB"))
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    max_diff = max(
        int(np.abs(r.astype(np.int16) - g.astype(np.int16)).max()),
        int(np.abs(g.astype(np.int16) - b.astype(np.int16)).max()),
    )
    return max_diff <= tolerance


def colorize_bw(image: Image.Image) -> Image.Image:
    """Naive B&W colorization using a warm sepia-to-color tint.

    This is a placeholder for DeOldify — it applies a gentle color tint
    so B&W photos come out with a warm tone rather than pure gray.
    Real colorization would use a deep-learning model. (#23)
    """
    arr = np.array(image.convert("RGB")).astype(np.float32)
    gray = arr.mean(axis=-1, keepdims=True)
    # Apply warm tint
    tinted = np.concatenate(
        [gray * 1.00, gray * 0.92, gray * 0.80],
        axis=-1,
    )
    tinted = np.clip(tinted, 0, 255).astype(np.uint8)
    return Image.fromarray(tinted)


def remove_scratches(image: Image.Image) -> Image.Image:
    """Remove scratches and dust using morphological inpainting. (#24)"""
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    # Detect bright streaks (scratches)
    _, mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    # Inpaint the detected regions if any were found
    restored = cv2.inpaint(arr, mask, 3, cv2.INPAINT_TELEA) if mask.sum() > 0 else arr
    return Image.fromarray(restored)


def denoise(image: Image.Image) -> Image.Image:
    """Apply OpenCV non-local-means denoising."""
    arr = np.array(image.convert("RGB"))
    denoised = cv2.fastNlMeansDenoisingColored(arr, None, 10, 10, 7, 21)
    return Image.fromarray(denoised)


def restore_photo(
    input_path: str | Path,
    output_path: str | Path,
    colorize: bool = True,
    repair_scratches: bool = True,
) -> Path:
    """Full restoration pipeline: denoise -> enhance faces -> scratches -> colorize.

    (#22) Combines multiple restoration steps.
    """
    image = load_image(input_path)
    rgb = image.convert("RGB")

    # Step 1: denoise
    rgb = denoise(rgb)

    # Step 2: scratch repair
    if repair_scratches:
        rgb = remove_scratches(rgb)

    # Step 3: colorize if B&W
    if colorize and is_grayscale(rgb):
        rgb = colorize_bw(rgb)

    # Save intermediate before face enhancement (which reads from disk)
    tmp_path = Path(output_path).with_suffix(".tmp.png")
    save_image(rgb.convert("RGBA"), tmp_path)

    # Step 4: enhance faces
    enhance_faces(tmp_path, Path(output_path))

    # Clean up temp
    tmp_path.unlink(missing_ok=True)
    return Path(output_path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore old / damaged photos.")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--no-colorize", action="store_true")
    parser.add_argument("--no-scratch-repair", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result = restore_photo(
        args.input,
        args.output,
        colorize=not args.no_colorize,
        repair_scratches=not args.no_scratch_repair,
    )
    print(f"Restored -> {result}")


if __name__ == "__main__":
    main()
