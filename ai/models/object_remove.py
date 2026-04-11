"""Object removal — Vrixo AI feature.

Uses OpenCV inpainting (TELEA / NS algorithms) as the MVP backend.
A future revision will swap to LaMa for higher-quality results when
model weights are downloaded.

Features:
    #26 Object removal with mask input
    #27 Mask-as-input (white pixels = remove)
    #28 Auto-detect prominent object for one-click removal
    #29 Edge cases (object touching border, very large objects)
    #30 Unit-tested
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from ai.utils.image_utils import load_image, save_image


def _load_mask(mask_path: str | Path, target_size: tuple[int, int]) -> np.ndarray:
    """Load a mask image and convert to binary uint8 (255 = remove)."""
    mask_img = Image.open(mask_path).convert("L")
    if mask_img.size != target_size:
        mask_img = mask_img.resize(target_size, Image.NEAREST)
    arr = np.array(mask_img)
    return (arr > 127).astype(np.uint8) * 255


def auto_detect_object(image: Image.Image) -> np.ndarray:
    """Return a mask covering the most salient object in the image. (#28)

    Uses a simple saliency method: find the largest colored blob that
    differs from the background. Not as good as a proper SAM model,
    but works for one-click removal in the MVP.
    """
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    # Edge detection + dilation to find connected objects
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)

    # Find contours and keep the largest
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        cv2.drawContours(mask, [largest], -1, 255, thickness=cv2.FILLED)
    return mask


def remove_object(
    input_path: str | Path,
    output_path: str | Path,
    mask_path: str | Path | None = None,
    auto: bool = False,
    radius: int = 5,
) -> Path:
    """Remove an object from the image.

    Args:
        input_path: Source image.
        output_path: Destination for the result.
        mask_path: Optional mask (white = remove). If None and auto=True, auto-detect.
        auto: Auto-detect the most prominent object.
        radius: Inpainting radius.

    Returns:
        Path to the output image.
    """
    image = load_image(input_path)
    rgb = np.array(image.convert("RGB"))

    if mask_path is not None:
        mask = _load_mask(mask_path, image.size)
    elif auto:
        mask = auto_detect_object(image)
    else:
        raise ValueError("Either mask_path or auto=True must be provided")

    if mask.sum() == 0:
        # Nothing to remove — save unchanged
        save_image(image, Path(output_path))
        return Path(output_path)

    # Ensure mask covers full image boundaries correctly (#29)
    mask_padded = cv2.copyMakeBorder(mask, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    rgb_padded = cv2.copyMakeBorder(rgb, 1, 1, 1, 1, cv2.BORDER_REPLICATE)

    inpainted = cv2.inpaint(rgb_padded, mask_padded, radius, cv2.INPAINT_TELEA)
    # Crop back to original size
    inpainted = inpainted[1:-1, 1:-1]

    result = Image.fromarray(inpainted).convert("RGBA")
    save_image(result, Path(output_path))
    return Path(output_path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove objects from photos with AI.")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--mask", "-m", default=None, help="Path to mask image (white = remove)")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto-detect object to remove")
    parser.add_argument("--radius", "-r", type=int, default=5, help="Inpaint radius")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.mask and not args.auto:
        raise SystemExit("Must provide --mask or --auto")
    result = remove_object(
        args.input, args.output, mask_path=args.mask, auto=args.auto, radius=args.radius
    )
    print(f"Object removed -> {result}")


if __name__ == "__main__":
    main()
