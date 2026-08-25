
"""Verified external resource layer for first-class Elara X NRLMSIS 2.0."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Mapping, Optional, Union

from . import parameters

PathLike = Union[str, os.PathLike]
EXPECTED_PARAMETER_SHA256 = "a322a749f368e73117dd20f3fdcf7389dabc5509f4c27073cc5580999381b508"
EXPECTED_PARAMETER_BYTES = 536576
EXPECTED_PARAMETER_BASENAME = "msis21.parm"
ENV_PRIMARY = "ELARA_X_NRLMSIS20_PARM"
ENV_COMPAT = "ELARA_X_NRLMSIS21_PARM"


class ResourceError(RuntimeError):
    pass


class ResourceNotConfiguredError(ResourceError):
    pass


class ResourceNotFoundError(ResourceError):
    pass


class ResourceIdentityError(ResourceError):
    pass


class ResourceInitializationError(ResourceError):
    pass


@dataclass(frozen=True)
class VerifiedParameterResource:
    path: Path
    sha256: str
    size: int


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_parameter_resource(
    resource_file: Optional[PathLike] = None,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> Path:
    env = os.environ if environ is None else environ
    candidate = resource_file
    if candidate is None:
        candidate = env.get(ENV_PRIMARY) or env.get(ENV_COMPAT)
    if candidate is None:
        raise ResourceNotConfiguredError(
            "NRLMSIS 2.0 compatibility resource is not configured. "
            "Provide the verified external msis21.parm explicitly, via "
            "ELARA_X_NRLMSIS20_PARM, or via ELARA_X_NRLMSIS21_PARM."
        )
    path = Path(candidate).expanduser().resolve()
    if not path.is_file():
        raise ResourceNotFoundError(str(path))
    return path


def verify_parameter_resource(path: PathLike) -> VerifiedParameterResource:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise ResourceNotFoundError(str(p))
    size = p.stat().st_size
    digest = _sha256(p)
    if size != EXPECTED_PARAMETER_BYTES:
        raise ResourceIdentityError(
            "Unexpected NRLMSIS compatibility resource size: " + str(size)
        )
    if digest != EXPECTED_PARAMETER_SHA256:
        raise ResourceIdentityError(
            "Unexpected NRLMSIS compatibility resource SHA-256: " + digest
        )
    return VerifiedParameterResource(p, digest, size)


def resolve_and_verify_parameter_resource(
    resource_file: Optional[PathLike] = None,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> VerifiedParameterResource:
    return verify_parameter_resource(
        resolve_parameter_resource(resource_file, environ=environ)
    )


def initialize_nrlmsis20(
    resource_file: Optional[PathLike] = None,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> VerifiedParameterResource:
    verified = resolve_and_verify_parameter_resource(
        resource_file,
        environ=environ,
    )
    before = _sha256(verified.path)
    compatibility_species = [True] * 9 + [False]
    compatibility_mass = [True] * 9 + [False]
    try:
        parameters.msisinit(
            parmpath=str(verified.path.parent) + os.sep,
            parmfile=verified.path.name,
            lspec_select=compatibility_species,
            lmass_include=compatibility_mass,
        )
    except Exception as exc:
        raise ResourceInitializationError(str(exc)) from exc
    after = _sha256(verified.path)
    if before != after or after != EXPECTED_PARAMETER_SHA256:
        raise ResourceInitializationError(
            "Verified external NRLMSIS resource changed during initialization."
        )
    if not bool(getattr(parameters, "initflag", False)):
        raise ResourceInitializationError(
            "NRLMSIS initflag is false after initialization."
        )
    if not bool(getattr(parameters, "haveparmspace", False)):
        raise ResourceInitializationError(
            "NRLMSIS parameter space is unavailable after initialization."
        )
    return verified
