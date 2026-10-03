"""API tests: auth, uploads, the job lifecycle and admission control.

The app runs against a temporary SQLite database and storage directory, and
Celery runs tasks inline (eager), so no PostgreSQL / Redis is needed here.
"""

from __future__ import annotations

import io
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("VRIXO_DATABASE_URL", f"sqlite:///{tmp_path / 'api.db'}")
    monkeypatch.setenv("VRIXO_STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("VRIXO_MAX_UPLOAD_MB", "1")

    from backend import config, db, storage
    from backend.queue import celery_app

    for cached in (config.get_settings, db.get_engine, db.get_sessionmaker, storage.get_storage):
        cached.cache_clear()
    monkeypatch.setattr(celery_app.conf, "task_always_eager", True)

    from backend.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client

    db.get_engine().dispose()
    for cached in (config.get_settings, db.get_engine, db.get_sessionmaker, storage.get_storage):
        cached.cache_clear()


def _png(size: tuple[int, int] = (48, 32), color: str = "teal") -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "PNG")
    return buffer.getvalue()


def _signup(client: TestClient, email: str = "a@example.com") -> dict[str, str]:
    response = client.post("/auth/signup", json={"email": email, "password": "correct-horse"})
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _upload(client: TestClient, headers: dict[str, str], data: bytes | None = None) -> str:
    response = client.post(
        "/uploads", headers=headers, files={"file": ("photo.png", data or _png(), "image/png")}
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


# ----------------------------------------------------------------- health + auth


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_signup_login_me(client: TestClient) -> None:
    headers = _signup(client, "User@Example.com")
    assert client.get("/auth/me", headers=headers).json()["email"] == "user@example.com"

    login = client.post(
        "/auth/login", json={"email": "user@example.com", "password": "correct-horse"}
    )
    assert login.status_code == 200
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}).status_code == 200  # fmt: skip


def test_duplicate_email_conflicts(client: TestClient) -> None:
    _signup(client)
    again = client.post(
        "/auth/signup", json={"email": "A@example.com", "password": "correct-horse"}
    )
    assert again.status_code == 409


def test_wrong_password_and_unknown_email_look_the_same(client: TestClient) -> None:
    _signup(client)
    wrong = client.post(
        "/auth/login", json={"email": "a@example.com", "password": "wrong-password"}
    )
    unknown = client.post(
        "/auth/login", json={"email": "b@example.com", "password": "wrong-password"}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_weak_password_rejected(client: TestClient) -> None:
    assert client.post("/auth/signup", json={"email": "a@example.com", "password": "short"}).status_code == 422  # fmt: skip


@pytest.mark.parametrize("header", [{}, {"Authorization": "Bearer not-a-token"}])
def test_protected_routes_need_a_valid_token(client: TestClient, header: dict[str, str]) -> None:
    assert client.get("/auth/me", headers=header).status_code == 401
    assert client.get("/jobs", headers=header).status_code == 401
    assert client.post("/uploads", headers=header, files={"file": ("a.png", _png())}).status_code == 401  # fmt: skip


def test_passwords_are_not_stored_in_plain_text(client: TestClient) -> None:
    _signup(client)
    from backend.db import get_sessionmaker
    from backend.models import User

    with get_sessionmaker()() as session:
        user = session.query(User).one()
    assert "correct-horse" not in user.password_hash
    assert len(user.password_hash) == 64 and len(user.password_salt) == 32


# ----------------------------------------------------------------------- uploads


def test_upload_records_real_image_metadata(client: TestClient) -> None:
    headers = _signup(client)
    response = client.post(
        "/uploads", headers=headers, files={"file": ("x.png", _png((60, 40)), "image/png")}
    )
    body = response.json()
    assert (body["width"], body["height"], body["image_format"]) == (60, 40, "PNG")


def test_upload_rejects_non_images_whatever_the_content_type(client: TestClient) -> None:
    headers = _signup(client)
    response = client.post(
        "/uploads",
        headers=headers,
        files={"file": ("evil.png", b"#!/bin/sh\nrm -rf /", "image/png")},
    )
    assert response.status_code == 415


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    headers = _signup(client)
    too_big = _png() + b"\0" * (1024 * 1024 + 1)  # limit is 1 MB in this fixture
    response = client.post("/uploads", headers=headers, files={"file": ("big.png", too_big)})
    assert response.status_code == 413


def test_upload_rejects_unsupported_format(client: TestClient) -> None:
    headers = _signup(client)
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buffer, "BMP")
    response = client.post(
        "/uploads", headers=headers, files={"file": ("a.bmp", buffer.getvalue())}
    )
    assert response.status_code == 415


def test_original_file_can_be_fetched_by_its_owner_only(client: TestClient) -> None:
    alice, bob = _signup(client, "alice@example.com"), _signup(client, "bob@example.com")
    data = _png((20, 10))
    upload_id = _upload(client, alice, data)

    mine = client.get(f"/uploads/{upload_id}/file", headers=alice)
    assert mine.status_code == 200 and mine.content == data
    assert mine.headers["content-type"] == "image/png"
    assert client.get(f"/uploads/{upload_id}/file", headers=bob).status_code == 404


def test_cors_allows_the_configured_frontend_only(client: TestClient) -> None:
    allowed = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    other = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in other.headers


# -------------------------------------------------------------------------- jobs


def test_job_runs_and_result_is_downloadable(client: TestClient) -> None:
    headers = _signup(client)
    upload_id = _upload(client, headers, _png((48, 32)))

    created = client.post(
        "/jobs",
        headers=headers,
        json={"upload_id": upload_id, "operation": "upscale", "params": {"scale": 2}},
    )
    assert created.status_code == 202, created.text
    job = created.json()
    assert job["status"] == "succeeded"  # eager mode: already processed
    assert job["params"] == {"scale": 2, "face_optimized": False, "engine": "auto"}
    assert job["duration_ms"] is not None and job["started_at"] and job["finished_at"]
    assert job["upload"]["filename"] == "photo.png" and job["upload"]["width"] == 48

    result = client.get(f"/jobs/{job['id']}/result", headers=headers)
    assert result.status_code == 200 and result.headers["content-type"] == "image/png"
    assert Image.open(io.BytesIO(result.content)).size == (96, 64)

    assert [j["id"] for j in client.get("/jobs", headers=headers).json()] == [job["id"]]


@pytest.mark.parametrize("operation", ["enhance_faces", "restore", "remove_object"])
def test_other_operations_succeed(client: TestClient, operation: str) -> None:
    headers = _signup(client)
    upload_id = _upload(client, headers, (FIXTURES / "with_object.jpg").read_bytes())
    job = client.post("/jobs", headers=headers, json={"upload_id": upload_id, "operation": operation}).json()  # fmt: skip
    assert job["status"] == "succeeded", job
    assert client.get(f"/jobs/{job['id']}/result", headers=headers).status_code == 200


def test_unknown_operation_and_bad_params_are_rejected_before_queueing(client: TestClient) -> None:
    headers = _signup(client)
    upload_id = _upload(client, headers)
    base = {"upload_id": upload_id}

    assert client.post("/jobs", headers=headers, json={**base, "operation": "explode"}).status_code == 422  # fmt: skip
    bad = client.post("/jobs", headers=headers, json={**base, "operation": "upscale", "params": {"scale": 3}})  # fmt: skip
    assert bad.status_code == 422
    assert client.get("/jobs", headers=headers).json() == []  # nothing was queued


def test_users_cannot_see_each_others_uploads_or_jobs(client: TestClient) -> None:
    alice, bob = _signup(client, "alice@example.com"), _signup(client, "bob@example.com")
    upload_id = _upload(client, alice)
    job_id = client.post("/jobs", headers=alice, json={"upload_id": upload_id, "operation": "upscale"}).json()["id"]  # fmt: skip

    assert client.post("/jobs", headers=bob, json={"upload_id": upload_id, "operation": "upscale"}).status_code == 404  # fmt: skip
    assert client.get(f"/jobs/{job_id}", headers=bob).status_code == 404
    assert client.get(f"/jobs/{job_id}/result", headers=bob).status_code == 404
    assert client.get("/jobs", headers=bob).json() == []


def test_failed_job_records_the_error_and_has_no_result(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from backend import tasks

    def boom(*args: object) -> None:
        raise RuntimeError("model crashed")

    monkeypatch.setattr(tasks, "run_operation", boom)
    headers = _signup(client)
    job = client.post("/jobs", headers=headers, json={"upload_id": _upload(client, headers), "operation": "upscale"}).json()  # fmt: skip

    assert job["status"] == "failed"
    assert job["error"] == "RuntimeError: model crashed"
    assert client.get(f"/jobs/{job['id']}/result", headers=headers).status_code == 409


def test_job_is_processed_only_once(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """A redelivered message must not run a finished job again."""
    from backend import tasks

    headers = _signup(client)
    job = client.post("/jobs", headers=headers, json={"upload_id": _upload(client, headers), "operation": "upscale"}).json()  # fmt: skip

    def must_not_run(*args: object) -> None:
        raise AssertionError("job ran twice")

    monkeypatch.setattr(tasks, "run_operation", must_not_run)
    assert tasks.process_job(job["id"]) == "succeeded"
    assert tasks.process_job("no-such-job") == "missing"


# ------------------------------------------------------------- admission control


@pytest.fixture
def held_queue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Accept jobs but never run them, so they stay 'queued'."""
    from backend import queue

    monkeypatch.setattr(queue, "enqueue", lambda job_id: None)


def _submit(client: TestClient, headers: dict[str, str], upload_id: str) -> int:
    return client.post("/jobs", headers=headers, json={"upload_id": upload_id, "operation": "upscale"}).status_code  # fmt: skip


def test_per_user_active_job_limit(client: TestClient, held_queue: None) -> None:
    headers = _signup(client)
    upload_id = _upload(client, headers)
    assert [_submit(client, headers, upload_id) for _ in range(3)] == [202, 202, 202]

    blocked = client.post("/jobs", headers=headers, json={"upload_id": upload_id, "operation": "upscale"})  # fmt: skip
    assert blocked.status_code == 429 and blocked.headers["retry-after"] == "10"

    other = _signup(client, "other@example.com")  # another user is unaffected
    assert _submit(client, other, _upload(client, other)) == 202


def test_queue_depth_sheds_load(
    client: TestClient, held_queue: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    from backend.config import get_settings

    monkeypatch.setattr(get_settings(), "max_queue_depth", 2)
    for email in ("a@example.com", "b@example.com"):
        headers = _signup(client, email)
        assert _submit(client, headers, _upload(client, headers)) == 202

    headers = _signup(client, "c@example.com")
    response = client.post("/jobs", headers=headers, json={"upload_id": _upload(client, headers), "operation": "upscale"})  # fmt: skip
    assert response.status_code == 503 and response.headers["retry-after"] == "30"


def test_daily_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.config import get_settings

    monkeypatch.setattr(get_settings(), "daily_job_limit", 2)
    headers = _signup(client)
    upload_id = _upload(client, headers)
    assert [_submit(client, headers, upload_id) for _ in range(3)] == [202, 202, 429]


def test_unreachable_broker_fails_the_job_instead_of_leaving_it_queued(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from backend import queue

    def down(job_id: str) -> None:
        raise ConnectionError("redis is down")

    monkeypatch.setattr(queue, "enqueue", down)
    headers = _signup(client)
    assert _submit(client, headers, _upload(client, headers)) == 503

    [job] = client.get("/jobs", headers=headers).json()
    assert job["status"] == "failed" and "could not enqueue" in job["error"]


# ----------------------------------------------------------------------- storage


def test_storage_keys_cannot_escape_the_root(tmp_path: Path) -> None:
    from backend.storage import LocalStorage

    storage = LocalStorage(tmp_path / "root")
    storage.save("uploads/u/a.png", b"x")
    assert storage.read("uploads/u/a.png") == b"x"
    with pytest.raises(ValueError):
        storage.local_path("../outside.txt")
