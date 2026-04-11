"""Face enhancement — Vrixo AI feature.

Uses OpenCV Haar cascade for face detection + OpenCV-based sharpening
as the MVP fallback. A future revision will swap the enhancement step
for GFPGAN when model weights are downloaded.

Features:
    #18 Face enhancement CLI
    #19 Face detection gate (no-face → unchanged + warning)
    #20 Non-face region preservation
    #21 Unit-tested
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from ai.utils.image_utils import load_image, save_image


def detect_faces(image: Image.Image) -> list[tuple[int, int, int, int]]:
    """Return list of (x, y, w, h) face bounding boxes. (#19)"""
    arr = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(cascade_path)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return [tuple(map(int, face)) for face in faces]


def _sharpen_region(arr: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Sharpen the (x, y, w, h) region of `arr` in place."""
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    region = arr[y : y + h, x : x + w]
    if region.size == 0:
        return arr
    sharpened = cv2.filter2D(region, -1, kernel)
    arr[y : y + h, x : x + w] = sharpened
    return arr


def enhance_faces(
    input_path: str | Path,
    output_path: str | Path,
    fail_on_no_face: bool = False,
) -> tuple[Path, int]:
    """Enhance all faces in the image.

    Returns:
        (output_path, num_faces_detected)
    """
    image = load_image(input_path)
    faces = detect_faces(image)

    if not faces:
        if fail_on_no_face:
            raise ValueError("No face detected in image")
        # Gracefully save unchanged image (#19)
        save_image(image, Path(output_path))
        return Path(output_path), 0

    # Enhance only face regions, preserving the rest (#20)
    arr = np.array(image.convert("RGB"))
    for x, y, w, h in faces:
        arr = _sharpen_region(arr, x, y, w, h)

    result = Image.fromarray(arr).convert("RGBA")
    save_image(result, Path(output_path))
    return Path(output_path), len(faces)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhance faces in a photo.")
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--strict", action="store_true", help="Fail if no face detected")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result, count = enhance_faces(args.input, args.output, fail_on_no_face=args.strict)
    print(f"Enhanced {count} face(s) -> {result}")


if __name__ == "__main__":
    main()
