"""End-to-end integration test simulating a full user flow.

Feature #71: verifies the complete pipeline from upload through AI
processing to download — without needing the Streamlit server.
"""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from ai.models.background_removal import remove_background
from ai.models.face_enhance import enhance_faces
from ai.models.object_remove import remove_object
from ai.models.restoration import restore_photo
from ai.models.upscaler import upscale_image
from web.watermark import apply_watermark


@pytest.fixture
def fake_upload_bytes() -> bytes:
    """Simulate a user uploading a small PNG."""
    buf = BytesIO()
    Image.new("RGB", (200, 150), color=(120, 80, 40)).save(buf, format="PNG")
    return buf.getvalue()


def test_full_upload_to_download_flow(fake_upload_bytes: bytes, tmp_path: Path) -> None:
    """Simulate: validate upload -> run AI -> apply watermark -> download.

    Uses a lightweight AI step (face enhance) that doesn't require model downloads.
    """
    # 1. Validate the "uploaded" bytes
    from web.upload import validate_file_size, validate_real_image

    validate_file_size(fake_upload_bytes)
    fmt = validate_real_image(fake_upload_bytes)
    assert fmt == "PNG"

    # 2. Save to disk (mimics what the web layer does)
    input_path = tmp_path / "upload.png"
    input_path.write_bytes(fake_upload_bytes)

    # 3. Run an AI feature on it
    output_path = tmp_path / "output.png"
    _, face_count = enhance_faces(input_path, output_path)
    assert output_path.exists()
    assert face_count == 0  # No face in our synthetic image

    # 4. Apply watermark for "free tier" download
    result_image = Image.open(output_path)
    watermarked = apply_watermark(result_image)
    download_buf = BytesIO()
    watermarked.save(download_buf, format="PNG")
    download_bytes = download_buf.getvalue()

    # 5. Verify the download is a valid PNG
    assert download_bytes.startswith(b"\x89PNG")
    roundtrip = Image.open(BytesIO(download_bytes))
    assert roundtrip.size == result_image.size


@pytest.mark.slow
def test_background_removal_on_real_fixture(tmp_path: Path) -> None:
    """Integration test using a real fixture image and real rembg model.

    Marked as slow because first run downloads ~170MB of model weights.
    Skip with: pytest -m 'not slow'
    """
    fixture = Path(__file__).parent / "fixtures" / "portrait.jpg"
    if not fixture.exists():
        pytest.skip("Fixture not generated yet")

    output = tmp_path / "no_bg.png"
    remove_background(fixture, output)
    assert output.exists()

    loaded = Image.open(output)
    assert loaded.mode == "RGBA"
    # Background removal should produce some transparent pixels
    alpha = loaded.split()[3]
    transparent_count = sum(1 for p in alpha.getdata() if p < 128)
    assert transparent_count > 0


def test_upscale_pipeline(tmp_path: Path) -> None:
    """Integration: upscale a small fixture to 4x."""
    fixture = Path(__file__).parent / "fixtures" / "low_res.jpg"
    if not fixture.exists():
        pytest.skip("Fixture not generated yet")

    output = tmp_path / "upscaled.png"
    upscale_image(fixture, output, scale=4)

    input_img = Image.open(fixture)
    output_img = Image.open(output)
    assert output_img.size == (input_img.size[0] * 4, input_img.size[1] * 4)


def test_restore_pipeline(tmp_path: Path) -> None:
    """Integration: restore the 'old' fixture."""
    fixture = Path(__file__).parent / "fixtures" / "old.jpg"
    if not fixture.exists():
        pytest.skip("Fixture not generated yet")

    output = tmp_path / "restored.png"
    restore_photo(fixture, output, colorize=False, repair_scratches=True)
    assert output.exists()


def test_object_removal_pipeline(tmp_path: Path) -> None:
    """Integration: auto-detect and remove object from the fixture."""
    fixture = Path(__file__).parent / "fixtures" / "with_object.jpg"
    if not fixture.exists():
        pytest.skip("Fixture not generated yet")

    output = tmp_path / "clean.png"
    remove_object(fixture, output, auto=True)
    assert output.exists()
