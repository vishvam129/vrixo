"""File storage for uploads and results.

``Storage`` is the small interface the API and worker depend on. The local
filesystem implementation is used today; an S3-compatible one (Cloudflare R2)
can be added behind the same interface without touching the callers.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Protocol

from backend.config import get_settings


class Storage(Protocol):
    def save(self, key: str, data: bytes) -> None: ...
    def read(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...
    def local_path(self, key: str) -> Path: ...


class LocalStorage:
    """Stores objects as files under a root directory."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def local_path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root):  # no "../" escapes out of the root
            raise ValueError(f"invalid storage key: {key!r}")
        return path

    def save(self, key: str, data: bytes) -> None:
        path = self.local_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def read(self, key: str) -> bytes:
        return self.local_path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self.local_path(key).is_file()


@lru_cache(maxsize=1)
def get_storage() -> Storage:
    return LocalStorage(get_settings().storage_dir)
