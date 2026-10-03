"""Tests for GFPGAN face restoration: alignment, paste-back and the real model."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from ai.models import face_enhance, gfpgan

FIXTURES = Path(__file__).parent / "fixtures"


def test_template_aligns_to_identity() -> None:
    matrix = gfpgan.alignment_matrix(gfpgan.FFHQ_TEMPLATE.copy())
    assert np.allclose(matrix, [[1, 0, 0], [0, 1, 0]], atol=1e-3)


def test_alignment_recovers_scale_and_shift() -> None:
    # a face half the template size, moved to (40, 25)
    landmarks = gfpgan.FFHQ_TEMPLATE * 0.5 + np.array([40.0, 25.0], dtype=np.float32)
    matrix = gfpgan.alignment_matrix(landmarks)
    mapped = cv2.transform(landmarks[None], matrix)[0]
    assert np.allclose(mapped, gfpgan.FFHQ_TEMPLATE, atol=0.5)


def test_paste_back_only_changes_face_region() -> None:
    image = np.full((600, 600, 3), 100, dtype=np.uint8)
    restored = np.full((512, 512, 3), 200, dtype=np.uint8)
    identity = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    out = gfpgan.paste_back(image, restored, identity)

    assert (out[256, 256] == 200).all()  # centre of the face takes the new pixels
    assert (out[550:, 550:] == 100).all()  # outside the crop: untouched
    assert (out[:512, 590:] == 100).all()
    assert 100 < out[30, 256, 0] < 200  # the border is blended, not a hard edge


def test_restore_crop_normalises_and_denormalises(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, np.ndarray] = {}

    class EchoSession:
        def get_inputs(self) -> list[object]:
            return [type("Input", (), {"name": "input"})()]

        def run(self, _outputs: object, feed: dict[str, np.ndarray]) -> list[np.ndarray]:
            seen["blob"] = feed["input"]
            return [feed["input"]]

    monkeypatch.setattr(gfpgan, "_session", lambda: EchoSession())
    crop = np.random.default_rng(1).integers(0, 256, (512, 512, 3), dtype=np.uint8)

    out = gfpgan.restore_crop(crop)

    assert seen["blob"].shape == (1, 3, 512, 512)
    assert seen["blob"].min() >= -1.0 and seen["blob"].max() <= 1.0
    assert np.abs(out.astype(int) - crop.astype(int)).max() <= 1  # round trip


def test_fallback_used_when_models_disabled() -> None:
    assert not face_enhance.gfpgan_available()


@pytest.mark.models
def test_real_model_restores_face(real_models: None, tmp_path: Path) -> None:
    source = np.array(Image.open(FIXTURES / "real_face.jpg").convert("RGB"))
    landmarks = gfpgan.detect_faces(source)
    assert len(landmarks) == 1

    restored, count = gfpgan.restore_faces(source)
    assert count == 1 and restored.shape == source.shape
    assert np.abs(restored.astype(int) - source.astype(int)).mean() > 0.5  # face changed
    assert np.array_equal(restored[-8:, :8], source[-8:, :8])  # a corner far from the face did not

    _, faces = face_enhance.enhance_faces(FIXTURES / "real_face.jpg", tmp_path / "out.png")
    assert faces == 1


@pytest.mark.models
def test_real_detector_finds_no_face_in_landscape(real_models: None) -> None:
    landscape = np.array(Image.open(FIXTURES / "landscape.jpg").convert("RGB"))
    assert gfpgan.detect_faces(landscape) == []
