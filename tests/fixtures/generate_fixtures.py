"""Generate 5 synthetic test fixture images.

Run once to produce deterministic test images in tests/fixtures/.
These are NOT real photos — just procedurally generated PNGs with
distinct characteristics that match each AI feature's use case.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FIXTURES_DIR = Path(__file__).parent


def make_portrait() -> Image.Image:
    """A 400x600 synthetic portrait: gradient background + face-like oval."""
    img = Image.new("RGB", (400, 600), (220, 200, 180))
    draw = ImageDraw.Draw(img)
    # Face oval
    draw.ellipse([100, 100, 300, 400], fill=(230, 200, 170), outline=(180, 150, 120), width=3)
    # Eyes
    draw.ellipse([150, 200, 180, 230], fill=(40, 40, 40))
    draw.ellipse([220, 200, 250, 230], fill=(40, 40, 40))
    # Mouth
    draw.arc([160, 280, 240, 340], start=0, end=180, fill=(120, 60, 60), width=4)
    return img


def make_landscape() -> Image.Image:
    """An 800x400 synthetic landscape: sky + ground."""
    img = Image.new("RGB", (800, 400), (135, 206, 235))  # sky blue
    arr = np.array(img)
    # Gradient sky
    for y in range(200):
        arr[y, :, 0] = 135 + int(y * 0.3)
        arr[y, :, 1] = 206 - int(y * 0.2)
        arr[y, :, 2] = 235 - int(y * 0.3)
    # Green ground
    arr[200:, :, 0] = 90
    arr[200:, :, 1] = 140
    arr[200:, :, 2] = 60
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    # Sun
    draw.ellipse([650, 40, 730, 120], fill=(255, 220, 100))
    # Mountains
    draw.polygon([(0, 200), (200, 80), (400, 200)], fill=(90, 80, 70))
    draw.polygon([(300, 200), (500, 100), (700, 200)], fill=(100, 90, 80))
    return img


def make_low_res() -> Image.Image:
    """A 64x64 heavily pixelated image (simulating blurry / low-res input)."""
    base = make_portrait().resize((64, 64), Image.NEAREST)
    return base


def make_old() -> Image.Image:
    """A 500x500 sepia-toned noisy image (simulating an old damaged photo)."""
    img = make_portrait().resize((500, 500))
    # Convert to sepia
    arr = np.array(img).astype(np.float32)
    sepia = np.zeros_like(arr)
    sepia[..., 0] = arr[..., 0] * 0.393 + arr[..., 1] * 0.769 + arr[..., 2] * 0.189
    sepia[..., 1] = arr[..., 0] * 0.349 + arr[..., 1] * 0.686 + arr[..., 2] * 0.168
    sepia[..., 2] = arr[..., 0] * 0.272 + arr[..., 1] * 0.534 + arr[..., 2] * 0.131
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    # Add noise
    rng = np.random.default_rng(seed=42)
    noise = rng.integers(-30, 30, size=sepia.shape, dtype=np.int32)
    sepia = np.clip(sepia.astype(np.int32) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(sepia).filter(ImageFilter.GaussianBlur(radius=1.5))
    return img


def make_with_object() -> Image.Image:
    """A 600x400 scene with a prominent red rectangle (target for removal)."""
    img = make_landscape().resize((600, 400))
    draw = ImageDraw.Draw(img)
    # Red object in middle of scene
    draw.rectangle([250, 250, 350, 350], fill=(200, 40, 40), outline=(100, 20, 20), width=3)
    return img


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    fixtures = {
        "portrait.jpg": make_portrait(),
        "landscape.jpg": make_landscape(),
        "low_res.jpg": make_low_res(),
        "old.jpg": make_old(),
        "with_object.jpg": make_with_object(),
    }
    for name, image in fixtures.items():
        path = FIXTURES_DIR / name
        image.save(path, quality=90)
        print(f"Created: {path} ({image.size[0]}x{image.size[1]})")


if __name__ == "__main__":
    main()
