"""Release loaded models so a long-running worker's memory stays bounded.

Each pipeline caches its network after first use, which is right for a single
script but wrong for a worker that serves every operation: Real-ESRGAN, GFPGAN,
LaMa and a rembg session together need more RAM than the worker is allowed,
and it ends up swapping. Jobs run one at a time, so the worker simply drops
all cached models after each job; reloading costs a second or two.
"""

from __future__ import annotations

import contextlib
import ctypes
import gc
import sys


def release_models() -> None:
    """Drop every cached model and hand the freed memory back to the OS."""
    # only touch modules that were actually imported — never import a model here
    loaded = sys.modules

    if (module := loaded.get("ai.models.realesrgan")) is not None:
        module.load_model.cache_clear()
    if (module := loaded.get("ai.models.gfpgan")) is not None:
        module._session.cache_clear()
    if (module := loaded.get("ai.models.lama")) is not None:
        module.load_model.cache_clear()
    if (module := loaded.get("ai.models.background_removal")) is not None:
        module._SESSION_CACHE.clear()

    gc.collect()
    _trim_heap()


def _trim_heap() -> None:
    """glibc keeps freed blocks in its arenas; ask it to return them (Linux only)."""
    with contextlib.suppress(OSError, AttributeError):
        ctypes.CDLL("libc.so.6").malloc_trim(0)
