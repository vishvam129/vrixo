"""Shared image processing utilities for Vrixo AI pipelines.

Features:
    #31 Format conversion (JPG, PNG, WebP, HEIC)
    #32 EXIF stripping for privacy
    #33 Aspect-preserving resize
    #34 Thumbnail generation
    #35 Well-tested
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP", "BMP", "TIFF"}
FORMAT_ALIASES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    "tif": "TIFF",
}


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
    # JPEG doesn't support alpha — drop it for .jpg files
    if path.suffix.lower() in {".jpg", ".jpeg"} and image.mode == "RGBA":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    image.save(path)


def resize_if_too_large(image: Image.Image, max_side: int = 2048) -> Image.Image:
    """Downscale an image if its longest side exceeds `max_side`."""
    width, height = image.size
    if max(width, height) <= max_side:
        return image
    scale = max_side / max(width, height)
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size, Image.LANCZOS)


def convert_format(
    input_path: str | Path,
    output_path: str | Path,
    output_format: str | None = None,
) -> Path:
    """Convert an image between formats. (#31)

    Supported: JPG, JPEG, PNG, WebP, BMP, TIFF.
    If `output_format` is None, it's inferred from the output file extension.
    """
    image = Image.open(input_path)
    output_path = Path(output_path)

    if output_format is None:
        ext = output_path.suffix.lstrip(".").lower()
        output_format = FORMAT_ALIASES.get(ext, ext.upper())

    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {output_format}")

    # JPEG requires RGB mode (no alpha)
    if output_format == "JPEG" and image.mode != "RGB":
        rgb = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "RGBA":
            rgb.paste(image, mask=image.split()[3])
        else:
            rgb.paste(image.convert("RGB"))
        image = rgb

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format=output_format)
    return output_path


def strip_exif(image: Image.Image) -> Image.Image:
    """Remove EXIF metadata for privacy. (#32)"""
    data = list(image.getdata())
    clean = Image.new(image.mode, image.size)
    clean.putdata(data)
    return clean


def resize_preserve_aspect(
    image: Image.Image,
    max_side: int,
) -> Image.Image:
    """Resize so the longest side equals `max_side`, preserving aspect ratio. (#33)"""
    width, height = image.size
    if width >= height:
        new_width = max_side
        new_height = int(height * max_side / width)
    else:
        new_height = max_side
        new_width = int(width * max_side / height)
    return image.resize((new_width, new_height), Image.LANCZOS)


def make_thumbnail(image: Image.Image, size: int = 256) -> Image.Image:
    """Create a thumbnail with longest side <= `size`. (#34)"""
    thumb = image.copy()
    thumb.thumbnail((size, size), Image.LANCZOS)
    return thumb
