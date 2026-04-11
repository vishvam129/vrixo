"""Shared image processing utilities for Vrixo AI pipelines."""

from pathlib import Path
from PIL import Image


def load_image(path: str | Path) -> Image.Image:
    """Load an image from disk and convert to RGBA."""
    image = Image.open(path)
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return image


def save_image(image: Image.Image, path: str | Path) -> None:
    """Save an image to disk, creating parent dirs if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def resize_if_too_large(image: Image.Image, max_side: int = 2048) -> Image.Image:
    """Downscale an image if its longest side exceeds `max_side`."""
    width, height = image.size
    if max(width, height) <= max_side:
        return image
    scale = max_side / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size, Image.LANCZOS)
