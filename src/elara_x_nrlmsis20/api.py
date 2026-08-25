
"""First-class private Elara X NRLMSIS 2.0 compatibility API."""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

from . import parameters
from .legacy_interface import gtd8d as _native_gtd8d
from .model import msiscalc as _native_msiscalc
from .resources import (
    ResourceError,
    ResourceNotConfiguredError,
    ResourceNotFoundError,
    ResourceIdentityError,
    ResourceInitializationError,
    VerifiedParameterResource,
    initialize_nrlmsis20,
)


class ModelNotInitializedError(RuntimeError):
    pass


def initialize(resource_file=None, *, environ: Optional[Mapping[str, str]] = None):
    return initialize_nrlmsis20(resource_file, environ=environ)


def is_initialized() -> bool:
    return bool(
        getattr(parameters, "initflag", False)
        and getattr(parameters, "haveparmspace", False)
    )


def _require_initialized() -> None:
    if not is_initialized():
        raise ModelNotInitializedError(
            "NRLMSIS 2.0 has not been initialized with its verified "
            "compatibility resource."
        )


def calculate(
    day: float,
    utsec: float,
    z: float,
    lat: float,
    lon: float,
    sfluxavg: float,
    sflux: float,
    ap: Sequence[float],
    *,
    return_tex: bool = False,
):
    """Evaluate the NRLMSIS 2.0 common native output surface.

    The accepted translated engine has DN(1:10), with DN(10)=NO in
    NRLMSIS 2.1. NRLMSIS 2.0 deliberately exposes only DN(1:9).
    """
    _require_initialized()
    result = _native_msiscalc(
        day, utsec, z, lat, lon, sfluxavg, sflux, ap,
        return_tex=return_tex,
    )
    if return_tex:
        tn, dn, tex = result
        return tn, tuple(dn[:9]), tex
    tn, dn = result
    return tn, tuple(dn[:9])


def gtd8d(
    iyd: int,
    sec: float,
    alt: float,
    glat: float,
    glong: float,
    stl: float,
    f107a: float,
    f107: float,
    ap: Sequence[float],
    mass: int,
):
    """Evaluate legacy NRLMSIS 2.0 D(1:9), T(1:2)."""
    _require_initialized()
    result = _native_gtd8d(
        iyd, sec, alt, glat, glong, stl,
        f107a, f107, ap, mass,
    )
    if not isinstance(result, (tuple, list)) or len(result) != 2:
        raise RuntimeError("Unexpected translated GTD8D return structure.")
    a, b = result
    if len(a) >= 9 and len(b) == 2:
        d, t = list(a), list(b)
    elif len(a) == 2 and len(b) >= 9:
        t, d = list(a), list(b)
    else:
        raise RuntimeError("Unexpected translated GTD8D D/T widths.")
    return tuple(d[:9]), tuple(t)
