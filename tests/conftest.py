"""Shared pytest configuration.

The unit tests exercise the classical (no-download) code paths, so neural
models are switched off by default. Tests that run the real networks carry
the ``models`` marker, opt back in with the ``real_models`` fixture, and are
skipped automatically when the weight files are not installed.
"""

from __future__ import annotations

import pytest

from ai.models import weights


@pytest.fixture(autouse=True)
def _classical_pipelines_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VRIXO_DISABLE_MODELS", "1")


@pytest.fixture
def real_models(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enable the neural models for a test (skips if weights are missing)."""
    monkeypatch.delenv("VRIXO_DISABLE_MODELS", raising=False)
    missing = [name for name, present in weights.status().items() if not present]
    if missing:
        pytest.skip(f"model weights not installed: {', '.join(missing)}")
