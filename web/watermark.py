"""Watermarking for Vrixo free tier exports.

Features:
    #59 Apply Vrixo watermark to free tier downloads
    #60 Remove watermark for paid users (handled by caller)
    #61 Watermark bottom-right, 10% of image width
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

WATERMARK_TEXT = os.environ.get("WATERMARK_TEXT", "Edited with Vrixo")
WATERMARK_OPACITY = float(os.environ.get("WATERMARK_OPACITY", "0.5"))
WATERMARK_POSITION = os.environ.get("WATERMARK_POSITION", "bottom-right")


def _get_font(size: int) -> ImageFont.ImageFont:
    """Load a TTF font if available, otherwise fall back to the default."""
    try:
        # Common Linux font path
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def apply_watermark(
    image: Image.Image,
    text: str = WATERMARK_TEXT,
    opacity: float = WATERMARK_OPACITY,
    position: str = WATERMARK_POSITION,
) -> Image.Image:
    """Overlay a watermark on the image.

    #61: Default size is 10% of image width, positioned bottom-right.
    """
    base = image.convert("RGBA")
    width, height = base.size

    # Font size = ~5% of image width (text needs to fit in 10% area)
    font_size = max(16, int(width * 0.04))
    font = _get_font(font_size)

    # Measure text
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = int(width * 0.02)

    # Position mapping
    positions = {
        "bottom-right": (width - text_width - padding, height - text_height - padding * 2),
        "bottom-left": (padding, height - text_height - padding * 2),
        "top-right": (width - text_width - padding, padding),
        "top-left": (padding, padding),
        "center": ((width - text_width) // 2, (height - text_height) // 2),
    }
    x, y = positions.get(position, positions["bottom-right"])

    alpha = int(255 * opacity)
    # Draw a subtle shadow for readability
    draw.text((x + 2, y + 2), text, fill=(0, 0, 0, alpha), font=font)
    draw.text((x, y), text, fill=(255, 255, 255, alpha), font=font)

    return Image.alpha_composite(base, overlay)
