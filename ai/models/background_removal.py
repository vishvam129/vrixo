"""Background removal — Vrixo's first AI feature.

Uses `rembg` (backed by the U^2-Net / BiRefNet family of models) to strip
backgrounds from arbitrary photos. Runs entirely on CPU — no API keys,
no cloud, no payment.

Usage:
    python ai/models/background_removal.py --input photo.jpg --output result.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rembg import remove

from ai.utils.image_utils import load_image, save_image


def remove_background(input_path: str | Path, output_path: str | Path) -> Path:
    """Remove the background from `input_path` and save to `output_path`."""
    image = load_image(input_path)
    result = remove(image)
    output_path = Path(output_path)
    save_image(result, output_path)
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove photo backgrounds with AI.")
    parser.add_argument("--input", "-i", required=True, help="Path to input image")
    parser.add_argument("--output", "-o", required=True, help="Path to output PNG")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result_path = remove_background(args.input, args.output)
    print(f"Background removed -> {result_path}")


if __name__ == "__main__":
    main()
