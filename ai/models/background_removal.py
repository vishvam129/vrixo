"""Background removal — Vrixo AI feature.

Uses rembg (U^2-Net / BiRefNet / ISNet family) to strip backgrounds from photos.
Runs entirely on CPU — no API keys, no cloud, no payment.

Features:
    #7  CLI interface
    #8  Model download caching
    #9  Large-image auto-resize
    #10 RGBA transparent output
    #11 Multi-model support (u2net, birefnet, isnet)
    #12 Unit-tested
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Literal

from rembg import new_session, remove

from ai.utils.image_utils import load_image, resize_if_too_large, save_image

ModelName = Literal["u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "birefnet-general"]

MODELS_DIR = Path(os.environ.get("REMBG_HOME", "./models_cache/rembg"))
MAX_INPUT_SIDE = 4096  # pixels — larger images get auto-downsized first

# Session cache to avoid re-loading the ONNX model for every call
_SESSION_CACHE: dict[str, object] = {}


def _get_session(model_name: str) -> object:
    """Return a cached rembg session for the given model name."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["U2NET_HOME"] = str(MODELS_DIR)  # rembg reads this env var
    if model_name not in _SESSION_CACHE:
        _SESSION_CACHE[model_name] = new_session(model_name)
    return _SESSION_CACHE[model_name]


def remove_background(
    input_path: str | Path,
    output_path: str | Path,
    model: ModelName = "u2net",
) -> Path:
    """Remove the background from `input_path` and save to `output_path`.

    Args:
        input_path: Path to input image (any PIL-readable format).
        output_path: Where to save the result (should be .png for transparency).
        model: rembg model to use.

    Returns:
        The Path where the result was saved.
    """
    image = load_image(input_path)
    # Auto-downsize very large images to avoid OOM on CPU
    image = resize_if_too_large(image, max_side=MAX_INPUT_SIDE)

    session = _get_session(model)
    result = remove(image, session=session)

    # Ensure RGBA output with transparency
    if result.mode != "RGBA":
        result = result.convert("RGBA")

    output_path = Path(output_path)
    save_image(result, output_path)
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove photo backgrounds with AI.")
    parser.add_argument("--input", "-i", required=True, help="Path to input image")
    parser.add_argument("--output", "-o", required=True, help="Path to output PNG")
    parser.add_argument(
        "--model",
        "-m",
        default="u2net",
        choices=["u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "birefnet-general"],
        help="Model to use (default: u2net)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result_path = remove_background(args.input, args.output, model=args.model)
    print(f"Background removed ({args.model}) -> {result_path}")


if __name__ == "__main__":
    main()
