"""Tests for ai.models.background_removal."""

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from ai.models.background_removal import remove_background


@patch("ai.models.background_removal.remove")
@patch("ai.models.background_removal._get_session")
def test_remove_background_writes_output(mock_session, mock_remove, tmp_path: Path) -> None:
    """Pipeline loads input, calls rembg.remove, saves result."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (50, 50), color=(0, 255, 0)).save(input_path)

    mock_session.return_value = "fake_session"
    mock_remove.return_value = Image.new("RGBA", (50, 50), color=(0, 0, 0, 0))

    result = remove_background(input_path, output_path)

    assert result == output_path
    assert output_path.exists()
    mock_remove.assert_called_once()


@patch("ai.models.background_removal.remove")
@patch("ai.models.background_removal._get_session")
def test_output_is_rgba(mock_session, mock_remove, tmp_path: Path) -> None:
    """Output must be RGBA for transparency (#10)."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (30, 30)).save(input_path)

    mock_session.return_value = "fake_session"
    # Return an RGB image to test conversion fallback
    mock_remove.return_value = Image.new("RGB", (30, 30))

    remove_background(input_path, output_path)

    loaded = Image.open(output_path)
    assert loaded.mode == "RGBA"


@patch("ai.models.background_removal.remove")
@patch("ai.models.background_removal._get_session")
def test_large_image_is_resized(mock_session, mock_remove, tmp_path: Path) -> None:
    """Images larger than MAX_INPUT_SIDE get auto-resized (#9)."""
    input_path = tmp_path / "huge.png"
    output_path = tmp_path / "out.png"
    Image.new("RGB", (5000, 5000)).save(input_path)

    mock_session.return_value = "fake_session"
    mock_remove.return_value = Image.new("RGBA", (4096, 4096))

    remove_background(input_path, output_path)

    # Verify the call got a resized image (<=4096 on longest side)
    call_args = mock_remove.call_args
    passed_image = call_args[0][0]
    assert max(passed_image.size) <= 4096


@patch("ai.models.background_removal.remove")
@patch("ai.models.background_removal._get_session")
def test_model_parameter_passed(mock_session, mock_remove, tmp_path: Path) -> None:
    """Different models can be selected via parameter (#11)."""
    input_path = tmp_path / "in.png"
    output_path = tmp_path / "out.png"
    Image.new("RGB", (30, 30)).save(input_path)

    mock_session.return_value = "fake_session"
    mock_remove.return_value = Image.new("RGBA", (30, 30))

    remove_background(input_path, output_path, model="isnet-general-use")

    mock_session.assert_called_with("isnet-general-use")


@patch("ai.models.background_removal.remove")
@patch("ai.models.background_removal._get_session")
def test_session_caching(mock_session, mock_remove, tmp_path: Path) -> None:
    """Session cache avoids re-loading the model (#8)."""
    # Note: _get_session itself caches internally; we verify it's called
    # once per unique model when called multiple times. Since we mock
    # _get_session, this just verifies our code path uses it.
    input_path = tmp_path / "in.png"
    Image.new("RGB", (20, 20)).save(input_path)

    mock_session.return_value = "fake_session"
    mock_remove.return_value = Image.new("RGBA", (20, 20))

    remove_background(input_path, tmp_path / "o1.png", model="u2net")
    remove_background(input_path, tmp_path / "o2.png", model="u2net")

    assert mock_session.call_count == 2  # called each time
    assert mock_remove.call_count == 2
