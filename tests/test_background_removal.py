"""Tests for ai.models.background_removal."""

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from ai.models.background_removal import remove_background


@patch("ai.models.background_removal.remove")
def test_remove_background_writes_output(mock_remove, tmp_path: Path) -> None:
    """Verify the pipeline loads, calls rembg, and saves the result."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (50, 50), color=(0, 255, 0)).save(input_path)

    # Mock rembg.remove to return a fake transparent image
    mock_remove.return_value = Image.new("RGBA", (50, 50), color=(0, 0, 0, 0))

    result = remove_background(input_path, output_path)

    assert result == output_path
    assert output_path.exists()
    mock_remove.assert_called_once()


@patch("ai.models.background_removal.remove")
def test_remove_background_creates_parent_dir(mock_remove, tmp_path: Path) -> None:
    """Output directories should be created if they don't exist."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "nested" / "dir" / "output.png"
    Image.new("RGB", (10, 10)).save(input_path)
    mock_remove.return_value = Image.new("RGBA", (10, 10))

    remove_background(input_path, output_path)

    assert output_path.exists()
