"""The image operations a job can run, with validated parameters.

Each operation maps a request's ``params`` onto one of the ``ai.models``
pipelines. Parameters are validated here, when the job is submitted, so a bad
request fails with a 422 instead of failing later inside the worker.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class _Params(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RemoveBackgroundParams(_Params):
    model: Literal[
        "u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "birefnet-general"
    ] = "u2net"


class UpscaleParams(_Params):
    scale: Literal[2, 4, 8] = 4
    face_optimized: bool = False
    engine: Literal["auto", "realesrgan", "lanczos"] = "auto"


class EnhanceFacesParams(_Params):
    pass


class RestoreParams(_Params):
    colorize: bool = True
    repair_scratches: bool = True


class RemoveObjectParams(_Params):
    pass


def _remove_background(src: Path, dst: Path, p: RemoveBackgroundParams) -> None:
    from ai.models.background_removal import remove_background

    remove_background(src, dst, model=p.model)


def _upscale(src: Path, dst: Path, p: UpscaleParams) -> None:
    from ai.models.upscaler import upscale_image

    upscale_image(src, dst, scale=p.scale, face_optimized=p.face_optimized, engine=p.engine)


def _enhance_faces(src: Path, dst: Path, p: EnhanceFacesParams) -> None:
    from ai.models.face_enhance import enhance_faces

    enhance_faces(src, dst)


def _restore(src: Path, dst: Path, p: RestoreParams) -> None:
    from ai.models.restoration import restore_photo

    restore_photo(src, dst, colorize=p.colorize, repair_scratches=p.repair_scratches)


def _remove_object(src: Path, dst: Path, p: RemoveObjectParams) -> None:
    from ai.models.object_remove import remove_object

    remove_object(src, dst, auto=True)


# operation name → (parameter schema, runner)
OPERATIONS: dict[str, tuple[type[_Params], Callable[[Path, Path, Any], None]]] = {
    "remove_background": (RemoveBackgroundParams, _remove_background),
    "upscale": (UpscaleParams, _upscale),
    "enhance_faces": (EnhanceFacesParams, _enhance_faces),
    "restore": (RestoreParams, _restore),
    "remove_object": (RemoveObjectParams, _remove_object),
}


def validate_params(operation: str, params: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalise ``params`` for ``operation`` (fills in defaults).

    Raises ``KeyError`` for an unknown operation and ``pydantic.ValidationError``
    for bad parameters.
    """
    schema, _ = OPERATIONS[operation]
    return schema.model_validate(params).model_dump()


def run_operation(operation: str, params: dict[str, Any], src: Path, dst: Path) -> None:
    """Run one operation, reading ``src`` and writing the result image to ``dst``."""
    schema, runner = OPERATIONS[operation]
    runner(src, dst, schema.model_validate(params))
