"""Tests for ai.models.face_enhance."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ai.models.face_enhance import detect_faces, enhance_faces


@pytest.fixture
def no_face_image(tmp_path: Path) -> Path:
    path = tmp_path / "no_face.jpg"
    Image.new("RGB", (200, 200), color=(50, 50, 50)).save(path)
    return path


def test_detect_faces_on_blank_image_returns_empty() -> None:
    img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    faces = detect_faces(img)
    assert faces == []


def test_enhance_no_face_saves_unchanged(no_face_image: Path, tmp_path: Path) -> None:
    """#19: no-face path gracefully saves unchanged image."""
    output = tmp_path / "out.png"
    result, count = enhance_faces(no_face_image, output)
    assert count == 0
    assert result.exists()


def test_enhance_no_face_strict_raises(no_face_image: Path, tmp_path: Path) -> None:
    """Strict mode raises on missing face."""
    with pytest.raises(ValueError):
        enhance_faces(no_face_image, tmp_path / "out.png", fail_on_no_face=True)


def test_non_face_region_preserved(tmp_path: Path) -> None:
    """#20: pixels outside face regions are unchanged when no face detected."""
    input_path = tmp_path / "in.jpg"
    Image.new("RGB", (100, 100), color=(200, 100, 50)).save(input_path)
    output = tmp_path / "out.png"

    enhance_faces(input_path, output)

    original = np.array(Image.open(input_path).convert("RGB"))
    result = np.array(Image.open(output).convert("RGB"))
    # Corner pixels should be identical (no face means no changes)
    assert np.array_equal(original[0, 0], result[0, 0])
