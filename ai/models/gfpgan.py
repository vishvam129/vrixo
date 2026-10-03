"""GFPGAN v1.4 face restoration through ONNX Runtime.

Pipeline for each face:

1. **Detect** the face and its 5 landmarks (eyes, nose, mouth corners) with
   OpenCV's YuNet detector.
2. **Align** — estimate the similarity transform that maps those landmarks
   onto the canonical FFHQ positions and warp the face to a 512x512 crop,
   which is the layout GFPGAN was trained on.
3. **Restore** the crop with the GFPGAN generator (ONNX).
4. **Paste back** with the inverse transform, blended through a feathered
   mask so only the face changes and no edge is visible.
"""

from __future__ import annotations

from functools import lru_cache

import cv2
import numpy as np

from ai.models.weights import weight_path

FACE_SIZE = 512

# Canonical 5-point landmark positions in a 512x512 FFHQ-aligned crop:
# left eye, right eye, nose tip, left mouth corner, right mouth corner.
FFHQ_TEMPLATE = np.array(
    [
        [192.98138, 239.94708],
        [318.90277, 240.19360],
        [256.63416, 314.01935],
        [201.26117, 371.41043],
        [313.08905, 371.15118],
    ],
    dtype=np.float32,
)


@lru_cache(maxsize=1)
def _session():  # -> onnxruntime.InferenceSession
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.intra_op_num_threads = 4  # leave cores free for the rest of the machine
    return ort.InferenceSession(
        str(weight_path("gfpgan")), sess_options=options, providers=["CPUExecutionProvider"]
    )


def detect_faces(rgb: np.ndarray, score_threshold: float = 0.6) -> list[np.ndarray]:
    """Return one 5x2 landmark array per detected face (image coordinates)."""
    height, width = rgb.shape[:2]
    detector = cv2.FaceDetectorYN.create(
        str(weight_path("yunet")), "", (width, height), score_threshold
    )
    _, faces = detector.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if faces is None:
        return []
    # each row: x, y, w, h, then 5 landmark (x, y) pairs, then score
    return [face[4:14].reshape(5, 2).astype(np.float32) for face in faces]


def alignment_matrix(landmarks: np.ndarray) -> np.ndarray:
    """2x3 similarity transform mapping a face's landmarks onto the template."""
    matrix, _ = cv2.estimateAffinePartial2D(landmarks, FFHQ_TEMPLATE, method=cv2.LMEDS)
    if matrix is None:
        raise ValueError("could not align face landmarks")
    return matrix


def restore_crop(crop: np.ndarray) -> np.ndarray:
    """Run GFPGAN on one aligned 512x512 uint8 RGB face crop."""
    # the model expects NCHW float in [-1, 1]
    blob = (crop.astype(np.float32) / 127.5 - 1.0).transpose(2, 0, 1)[None]
    session = _session()
    output = session.run(None, {session.get_inputs()[0].name: blob})[0][0]
    restored = (output.transpose(1, 2, 0).clip(-1, 1) + 1.0) * 127.5
    return restored.round().astype(np.uint8)


def _feather_mask(size: int = FACE_SIZE, border: int = 48) -> np.ndarray:
    """Soft-edged mask for the aligned crop: 1 in the middle, fading to 0."""
    mask = np.zeros((size, size), dtype=np.float32)
    mask[border:-border, border:-border] = 1.0
    blur = border // 2 * 2 + 1
    return cv2.GaussianBlur(mask, (blur, blur), 0)


def paste_back(rgb: np.ndarray, restored: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Warp a restored crop back into the image and blend it in."""
    height, width = rgb.shape[:2]
    inverse = cv2.invertAffineTransform(matrix)
    warped = cv2.warpAffine(restored, inverse, (width, height), flags=cv2.INTER_LINEAR)
    mask = cv2.warpAffine(_feather_mask(), inverse, (width, height), flags=cv2.INTER_LINEAR)
    mask = mask[..., None]
    blended = warped.astype(np.float32) * mask + rgb.astype(np.float32) * (1.0 - mask)
    return blended.round().astype(np.uint8)


def restore_faces(rgb: np.ndarray) -> tuple[np.ndarray, int]:
    """Restore every face in an HxWx3 uint8 RGB image.

    Returns the new image and the number of faces restored. Pixels outside the
    feathered face regions are returned unchanged.
    """
    result = rgb.copy()
    faces = detect_faces(rgb)
    for landmarks in faces:
        matrix = alignment_matrix(landmarks)
        crop = cv2.warpAffine(
            rgb,
            matrix,
            (FACE_SIZE, FACE_SIZE),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT,
        )
        result = paste_back(result, restore_crop(crop), matrix)
    return result, len(faces)
