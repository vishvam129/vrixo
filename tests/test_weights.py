"""Tests for ai.models.weights — registry, availability switch and download."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from ai.models import weights


@pytest.fixture
def models_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(weights, "MODELS_DIR", tmp_path)
    monkeypatch.delenv("VRIXO_DISABLE_MODELS", raising=False)
    return tmp_path


def test_registry_entries_are_complete() -> None:
    assert {"realesrgan_x4", "gfpgan", "yunet", "lama"} <= set(weights.WEIGHTS)
    for weight in weights.WEIGHTS.values():
        assert weight.url.startswith("https://")
        assert weight.filename and weight.license and weight.size_mb > 0


def test_unavailable_until_file_exists(models_dir: Path) -> None:
    assert not weights.is_available("lama")
    weights.weight_path("lama").write_bytes(b"x")
    assert weights.is_available("lama")
    assert not weights.is_available("lama", "gfpgan")  # all names must be present


def test_disable_switch_overrides_installed_files(
    models_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    weights.weight_path("lama").write_bytes(b"x")
    monkeypatch.setenv("VRIXO_DISABLE_MODELS", "1")
    assert not weights.is_available("lama")
    assert weights.status()["lama"] is True  # status reports what is on disk


def test_download_writes_file_and_cleans_temp(
    models_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(weights.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"weights"))
    path = weights.download("yunet")
    assert path.read_bytes() == b"weights"
    assert not list(models_dir.glob("*.part"))


def test_download_skips_when_present(models_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    weights.weight_path("yunet").write_bytes(b"existing")

    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("should not hit the network")

    monkeypatch.setattr(weights.urllib.request, "urlopen", fail)
    assert weights.download("yunet").read_bytes() == b"existing"


def test_interrupted_download_leaves_no_model_file(
    models_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Broken(io.BytesIO):
        def read(self, *args: object) -> bytes:
            raise ConnectionError("dropped")

    monkeypatch.setattr(weights.urllib.request, "urlopen", lambda *a, **k: Broken())
    with pytest.raises(ConnectionError):
        weights.download("yunet", retries=2)
    assert not weights.weight_path("yunet").exists()


class _Response(io.BytesIO):
    def __init__(self, data: bytes, status: int) -> None:
        super().__init__(data)
        self.status = status


def test_download_resumes_from_partial_file(
    models_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    part = weights.weight_path("yunet").with_suffix(".onnx.part")
    part.write_bytes(b"first-")
    requested: list[str | None] = []

    def urlopen(request: object, **kwargs: object) -> _Response:
        requested.append(request.get_header("Range"))  # type: ignore[attr-defined]
        return _Response(b"second", status=206)

    monkeypatch.setattr(weights.urllib.request, "urlopen", urlopen)

    assert weights.download("yunet").read_bytes() == b"first-second"
    assert requested == ["bytes=6-"]


def test_download_restarts_when_server_ignores_range(
    models_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    weights.weight_path("yunet").with_suffix(".onnx.part").write_bytes(b"stale")
    monkeypatch.setattr(
        weights.urllib.request, "urlopen", lambda *a, **k: _Response(b"whole-file", status=200)
    )
    assert weights.download("yunet").read_bytes() == b"whole-file"


def test_download_retries_after_timeout(models_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    class DropsOnce(_Response):
        def read(self, *args: object) -> bytes:
            raise TimeoutError("stalled")

    def urlopen(*args: object, **kwargs: object) -> _Response:
        calls["n"] += 1
        return DropsOnce(b"", 200) if calls["n"] == 1 else _Response(b"ok", 200)

    monkeypatch.setattr(weights.urllib.request, "urlopen", urlopen)
    assert weights.download("yunet").read_bytes() == b"ok"
    assert calls["n"] == 2
