"""Model weights registry — where each pretrained model lives and how to fetch it.

The neural pipelines (Real-ESRGAN, GFPGAN, LaMa) need weight files that are
too large for git. They are downloaded on demand into ``models_cache/`` and
every pipeline falls back to its classical implementation when a file is
missing, so the app always works.

    python -m ai.models.weights            # show what is installed
    python -m ai.models.weights --download # fetch everything (~620 MB)

Set ``VRIXO_DISABLE_MODELS=1`` to force the classical fallbacks (used in tests).
"""

from __future__ import annotations

import argparse
import os
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

MODELS_DIR = Path(os.environ.get("VRIXO_MODELS_DIR", "./models_cache"))


@dataclass(frozen=True)
class Weight:
    """One downloadable model file."""

    filename: str
    url: str
    size_mb: int
    license: str
    purpose: str


WEIGHTS: dict[str, Weight] = {
    "realesrgan_x4": Weight(
        filename="RealESRGAN_x4plus.pth",
        url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        size_mb=64,
        license="BSD-3-Clause",
        purpose="4x super-resolution (RRDBNet, PyTorch)",
    ),
    "gfpgan": Weight(
        filename="gfpgan_1.4.onnx",
        url="https://github.com/facefusion/facefusion-assets/releases/download/models-3.0.0/gfpgan_1.4.onnx",
        size_mb=325,
        license="Apache-2.0",
        purpose="face restoration (GFPGAN v1.4, ONNX Runtime)",
    ),
    "yunet": Weight(
        filename="face_detection_yunet_2023mar.onnx",
        url="https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        size_mb=1,
        license="MIT",
        purpose="face detection with 5 landmarks (YuNet, OpenCV)",
    ),
    "lama": Weight(
        filename="big-lama.pt",
        url="https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt",
        size_mb=196,
        license="Apache-2.0",
        purpose="object removal / inpainting (LaMa, TorchScript)",
    ),
}


def models_disabled() -> bool:
    """True when neural models are switched off via the environment."""
    return os.environ.get("VRIXO_DISABLE_MODELS", "").lower() in {"1", "true", "yes"}


def weight_path(name: str) -> Path:
    """Where the weight file for ``name`` is (or would be) stored."""
    return MODELS_DIR / WEIGHTS[name].filename


def is_available(*names: str) -> bool:
    """True if every named weight file is on disk and models are not disabled."""
    if models_disabled():
        return False
    return all(weight_path(n).is_file() for n in names)


def _fetch(url: str, tmp: Path) -> None:
    """Download ``url`` into ``tmp``, resuming if ``tmp`` already has data."""
    offset = tmp.stat().st_size if tmp.exists() else 0
    headers = {"User-Agent": "vrixo"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        # 206 = the server honoured the Range header; anything else restarts
        resumed = offset > 0 and getattr(response, "status", 200) == 206
        with open(tmp, "ab" if resumed else "wb") as fh:
            shutil.copyfileobj(response, fh, length=1024 * 1024)


def download(name: str, *, force: bool = False, retries: int = 5) -> Path:
    """Download one weight file.

    Data goes to a ``.part`` file that is renamed only when complete, so an
    interrupted download never leaves a truncated model that would fail to
    load. A dropped connection is retried and resumes from the bytes already
    on disk instead of starting over.
    """
    weight = WEIGHTS[name]
    dest = weight_path(name)
    if dest.is_file() and not force:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    if force:
        tmp.unlink(missing_ok=True)

    for attempt in range(1, retries + 1):
        try:
            _fetch(weight.url, tmp)
            break
        except (TimeoutError, ConnectionError, urllib.error.URLError):
            if attempt == retries:
                raise
    tmp.replace(dest)
    return dest


def status() -> dict[str, bool]:
    """Which weight files are present on disk (ignores the disable switch)."""
    return {name: weight_path(name).is_file() for name in WEIGHTS}


def _main() -> None:
    parser = argparse.ArgumentParser(description="Manage Vrixo model weights.")
    parser.add_argument("--download", action="store_true", help="Download missing weights")
    parser.add_argument("--only", nargs="*", choices=sorted(WEIGHTS), help="Limit to these models")
    parser.add_argument("--force", action="store_true", help="Re-download even if present")
    args = parser.parse_args()

    names = args.only or list(WEIGHTS)
    for name in names:
        weight = WEIGHTS[name]
        if args.download:
            print(f"↓ {name:14} {weight.size_mb:>4} MB  {weight.purpose}")
            download(name, force=args.force)
        present = "✓" if weight_path(name).is_file() else "·"
        print(f"{present} {name:14} {weight.filename:38} {weight.license}")


if __name__ == "__main__":
    _main()
