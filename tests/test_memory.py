"""Tests for releasing cached models between jobs."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image

from ai.models import memory


def test_release_clears_every_model_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    from ai.models import background_removal, gfpgan, lama, realesrgan

    monkeypatch.setattr(gfpgan, "weight_path", lambda name: "unused")
    cleared: list[str] = []
    for name, module, attribute in [
        ("realesrgan", realesrgan, "load_model"),
        ("gfpgan", gfpgan, "_session"),
        ("lama", lama, "load_model"),
    ]:
        original = getattr(module, attribute)

        class Spy:
            def __init__(self, label: str, wrapped: object) -> None:
                self.label, self.wrapped = label, wrapped

            def cache_clear(self) -> None:
                cleared.append(self.label)

        monkeypatch.setattr(module, attribute, Spy(name, original))
    background_removal._SESSION_CACHE["u2net"] = object()

    memory.release_models()

    assert sorted(cleared) == ["gfpgan", "lama", "realesrgan"]
    assert background_removal._SESSION_CACHE == {}


def test_release_never_imports_a_model_module(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(sys.modules):
        if name in {"ai.models.lama", "ai.models.gfpgan", "ai.models.realesrgan"}:
            monkeypatch.delitem(sys.modules, name)
    memory.release_models()
    assert "ai.models.lama" not in sys.modules


def test_models_are_released_after_a_job_even_when_it_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VRIXO_DATABASE_URL", f"sqlite:///{tmp_path / 'm.db'}")
    monkeypatch.setenv("VRIXO_STORAGE_DIR", str(tmp_path / "storage"))
    from backend import config, db, storage, tasks
    from backend.models import Job, Upload, User

    for cached in (config.get_settings, db.get_engine, db.get_sessionmaker, storage.get_storage):
        cached.cache_clear()
    db.Base.metadata.create_all(db.get_engine())

    released: list[int] = []
    monkeypatch.setattr(tasks, "release_models", lambda: released.append(1))

    def boom(*args: object) -> None:
        raise RuntimeError("crash")

    monkeypatch.setattr(tasks, "run_operation", boom)

    source = tmp_path / "storage" / "uploads" / "a.png"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (8, 8)).save(source)
    with db.get_sessionmaker()() as session:
        user = User(email="m@example.com", password_hash="h", password_salt="s")
        session.add(user)
        session.flush()
        upload = Upload(user_id=user.id, filename="a.png", image_format="PNG", size_bytes=1,
                        width=8, height=8, storage_key="uploads/a.png")  # fmt: skip
        session.add(upload)
        session.flush()
        job = Job(user_id=user.id, upload_id=upload.id, operation="upscale", params={})
        session.add(job)
        session.commit()
        job_id = job.id

    assert tasks.process_job(job_id) == "failed"
    assert released == [1]

    db.get_engine().dispose()
    for cached in (config.get_settings, db.get_engine, db.get_sessionmaker, storage.get_storage):
        cached.cache_clear()
