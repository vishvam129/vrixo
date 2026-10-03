"""End-to-end check against a running stack (``docker compose up -d``).

Signs up, uploads a photo, submits jobs, polls them through the queue and
downloads the results — exactly what a client would do.

    python scripts/e2e.py [--base http://127.0.0.1:58000] [--out /tmp/vrixo-e2e]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


class Client:
    def __init__(self, base: str) -> None:
        self.base, self.token = base.rstrip("/"), ""

    def call(
        self,
        method: str,
        path: str,
        *,
        body: dict | None = None,
        raw: bytes | None = None,
        content_type: str = "application/json",
    ) -> tuple[int, bytes, dict[str, str]]:
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        headers = {"Content-Type": content_type} if data is not None else {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(
            self.base + path, data=data, method=method, headers=headers
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, response.read(), dict(response.headers)
        except urllib.error.HTTPError as error:
            return error.code, error.read(), dict(error.headers)

    def upload(self, path: Path) -> str:
        boundary = uuid.uuid4().hex
        payload = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n"
            ).encode()
            + path.read_bytes()
            + f"\r\n--{boundary}--\r\n".encode()
        )
        status, body, _ = self.call(
            "POST",
            "/uploads",
            raw=payload,
            content_type=f"multipart/form-data; boundary={boundary}",
        )
        assert status == 201, (status, body)
        return json.loads(body)["id"]

    def wait(self, job_id: str, timeout: float = 300) -> dict:
        deadline = time.monotonic() + timeout
        seen: list[str] = []
        while time.monotonic() < deadline:
            _, body, _ = self.call("GET", f"/jobs/{job_id}")
            job = json.loads(body)
            if not seen or seen[-1] != job["status"]:
                seen.append(job["status"])
            if job["status"] in ("succeeded", "failed"):
                job["_states"] = seen
                return job
            time.sleep(0.25)
        raise TimeoutError(f"job {job_id} did not finish; states seen: {seen}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:58000")
    parser.add_argument("--out", default="/tmp/vrixo-e2e")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    client = Client(args.base)

    status, body, _ = client.call("GET", "/health")
    print(f"health            {status} {body.decode()}")

    email = f"e2e-{uuid.uuid4().hex[:8]}@example.com"
    status, body, _ = client.call(
        "POST", "/auth/signup", body={"email": email, "password": "correct-horse"}
    )
    assert status == 201, (status, body)
    client.token = json.loads(body)["access_token"]
    print(f"signup            {status} {email}")

    face = client.upload(FIXTURES / "real_face.jpg")
    scene = client.upload(FIXTURES / "with_object.jpg")
    print("uploads           2 images stored")

    jobs = [
        ("upscale + faces", face, "upscale", {"scale": 4, "face_optimized": True}),
        ("enhance faces", face, "enhance_faces", {}),
        ("remove object", scene, "remove_object", {}),
    ]
    failures = 0
    for label, upload_id, operation, params in jobs:
        status, body, _ = client.call(
            "POST", "/jobs", body={"upload_id": upload_id, "operation": operation, "params": params}
        )
        assert status == 202, (status, body)
        submitted = json.loads(body)
        job = client.wait(submitted["id"])
        line = f"{label:17} submit→{submitted['status']:7} states={'→'.join(job['_states'])} {job['duration_ms']} ms"
        if job["status"] != "succeeded":
            failures += 1
            print(line, "ERROR:", job["error"])
            continue
        status, image, headers = client.call("GET", f"/jobs/{job['id']}/result")
        (out / f"{operation}.png").write_bytes(image)
        print(line, f"result={len(image) // 1024} KB {headers.get('content-type')}")

    # admission control: the 4th concurrent job from one user is refused
    codes = []
    for _ in range(5):
        status, _, headers = client.call(
            "POST", "/jobs", body={"upload_id": scene, "operation": "remove_object"}
        )
        codes.append(status)
    print(f"burst of 5        {codes} (429 = per-user limit of 3 active jobs)")

    status, body, _ = client.call("GET", "/jobs?limit=50")
    listed = json.loads(body)
    for job in listed:
        if job["status"] in ("queued", "running"):
            client.wait(job["id"])
    status, body, _ = client.call("GET", "/jobs?limit=50")
    summary: dict[str, int] = {}
    for job in json.loads(body):
        summary[job["status"]] = summary.get(job["status"], 0) + 1
    print(f"final job states  {summary}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
