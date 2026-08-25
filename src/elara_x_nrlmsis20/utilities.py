"""Native NRLMSIS 2.1 support utilities.

This module is a Python translation of the NRLMSIS 2.1 utility-layer
algorithms.  The authoritative implementation remains the locked NRL Fortran
source used by the Elara X verification programme.

The repository licence and provenance documents govern this derivative work.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TypeAlias

from .constants import pi

SplineTable: TypeAlias = dict[tuple[int, int], float]
EtaTable: TypeAlias = Mapping[tuple[int, int], float]

_DEG2RAD = 0.017453292519943295

# WGS84 defining and derived quantities used by the authoritative utility.
_A = 6378.1370 * 1.0e3
_FINV = 298.257223563
_W = 7292115.0e-11
# The authoritative Fortran declares GM = 398600.4418 * 1d9.
# The unsuffixed 398600.4418 literal is rounded as default REAL before
# promotion by the double-precision multiplier, yielding 398600.4375.
_GM = 398600.4375 * 1.0e9
_ASQ = _A * _A
_WSQ = _W * _W
_F = 1.0 / _FINV
_ESQ = 2.0 * _F - _F * _F
_E = math.sqrt(_ESQ)
_ELIN = _A * _E
_ELINSQ = _ELIN * _ELIN
_EPR = _E / (1.0 - _F)
_Q0 = ((1.0 + 3.0 / (_EPR * _EPR)) * math.atan(_EPR) - 3.0 / _EPR) / 2.0
_U0 = -_GM * math.atan(_EPR) / _ELIN - _WSQ * _ASQ / 3.0
_G0 = 9.80665
_GM_DIV_ELIN = _GM / _ELIN
_X0SQ = (2.0e7) ** 2
_HSQ = (1.2e7) ** 2


def alt2gph(lat: float, alt: float) -> float:
    """Convert geodetic altitude (km) to geopotential height (km)."""

    altm = alt * 1000.0
    sinsqlat = math.sin(lat * _DEG2RAD) ** 2

    v = _A / math.sqrt(1.0 - _ESQ * sinsqlat)
    xsq = (v + altm) ** 2 * (1.0 - sinsqlat)
    zsq = (v * (1.0 - _ESQ) + altm) ** 2 * sinsqlat

    rsqmin_elinsq = xsq + zsq - _ELINSQ
    usq = (
        rsqmin_elinsq / 2.0
        + math.sqrt(rsqmin_elinsq ** 2 / 4.0 + _ELINSQ * zsq)
    )
    cossqdelta = zsq / usq

    epru = _ELIN / math.sqrt(usq)
    atanepru = math.atan(epru)
    q = ((1.0 + 3.0 / (epru * epru)) * atanepru - 3.0 / epru) / 2.0

    potential = (
        -_GM_DIV_ELIN * atanepru
        - _WSQ * (_ASQ * q * (cossqdelta - 1.0 / 3.0) / _Q0) / 2.0
    )

    if xsq <= _X0SQ:
        centrifugal = (_WSQ / 2.0) * xsq
    else:
        centrifugal = (
            (_WSQ / 2.0)
            * (_HSQ * math.tanh((xsq - _X0SQ) / _HSQ) + _X0SQ)
        )

    potential = potential - centrifugal
    return (potential - _U0) / _G0 / 1000.0


def gph2alt(theta: float, gph: float) -> float:
    """Convert geopotential height (km) to geodetic altitude (km)."""

    maxn = 10
    epsilon = 0.0005

    x = gph
    n = 0
    dx = epsilon + epsilon

    while abs(dx) > epsilon and n < maxn:
        y = alt2gph(theta, x)
        dydz = (alt2gph(theta, x + dx) - y) / dx
        dx = (gph - y) / dydz
        x = x + dx
        n += 1

    return x


def _empty_spline_table() -> SplineTable:
    return {(l, k): 0.0 for k in range(2, 7) for l in range(-5, 1)}


def bspline(
    x: float,
    nodes: Sequence[float],
    nd: int,
    kmax: int,
    eta: EtaTable,
) -> tuple[SplineTable, int]:
    """Evaluate the non-zero B-splines used by NRLMSIS 2.1.

    ``SplineTable`` preserves the logical Fortran indices directly:
    use ``s[l, k]`` for relative spline index ``l`` (-5..0) and order
    ``k`` (2..6). ``eta`` is likewise keyed by ``(node_index, order)``.
    """

    s = _empty_spline_table()

    if x >= nodes[nd]:
        return s, nd
    if x <= nodes[0]:
        return s, -1

    low = 0
    high = nd
    i = (low + high) // 2
    while x < nodes[i] or x >= nodes[i + 1]:
        if x < nodes[i]:
            high = i
        else:
            low = i
        i = (low + high) // 2

    s[0, 2] = (x - nodes[i]) * eta[i, 2]
    if i > 0:
        s[-1, 2] = 1.0 - s[0, 2]
    if i >= nd - 1:
        s[0, 2] = 0.0

    w = {l: 0.0 for l in range(-4, 1)}

    w[0] = (x - nodes[i]) * eta[i, 3]
    if i != 0:
        w[-1] = (x - nodes[i - 1]) * eta[i - 1, 3]

    if i < nd - 2:
        s[0, 3] = w[0] * s[0, 2]
    if 0 <= i - 1 < nd - 2:
        s[-1, 3] = w[-1] * s[-1, 2] + (1.0 - w[0]) * s[0, 2]
    if i - 2 >= 0:
        s[-2, 3] = (1.0 - w[-1]) * s[-1, 2]

    for l in range(0, -3, -1):
        j = i + l
        if j < 0:
            break
        w[l] = (x - nodes[j]) * eta[j, 4]

    if i < nd - 3:
        s[0, 4] = w[0] * s[0, 3]
    for l in range(-1, -3, -1):
        if 0 <= i + l < nd - 3:
            s[l, 4] = w[l] * s[l, 3] + (1.0 - w[l + 1]) * s[l + 1, 3]
    if i - 3 >= 0:
        s[-3, 4] = (1.0 - w[-2]) * s[-2, 3]

    for l in range(0, -4, -1):
        j = i + l
        if j < 0:
            break
        w[l] = (x - nodes[j]) * eta[j, 5]

    if i < nd - 4:
        s[0, 5] = w[0] * s[0, 4]
    for l in range(-1, -4, -1):
        if 0 <= i + l < nd - 4:
            s[l, 5] = w[l] * s[l, 4] + (1.0 - w[l + 1]) * s[l + 1, 4]
    if i - 4 >= 0:
        s[-4, 5] = (1.0 - w[-3]) * s[-3, 4]

    if kmax == 5:
        return s, i

    for l in range(0, -5, -1):
        j = i + l
        if j < 0:
            break
        w[l] = (x - nodes[j]) * eta[j, 6]

    if i < nd - 5:
        s[0, 6] = w[0] * s[0, 5]
    for l in range(-1, -5, -1):
        if 0 <= i + l < nd - 5:
            s[l, 6] = w[l] * s[l, 5] + (1.0 - w[l + 1]) * s[l + 1, 5]
    if i - 5 >= 0:
        s[-5, 6] = (1.0 - w[-4]) * s[-4, 5]

    return s, i


def dilog(x0: float) -> float:
    """Evaluate the NRLMSIS 2.1 truncated dilogarithm approximation."""

    x = x0
    pi2_6 = pi * pi / 6.0

    if x > 0.5:
        lnx = math.log(x)
        x = 1.0 - x
        xx = x * x
        x4 = 4.0 * x
        return (
            pi2_6
            - lnx * math.log(x)
            - (
                4.0
                * xx
                * (23.0 / 16.0 + x / 36.0 + xx / 576.0 + xx * x / 3600.0)
                + x4
                + 3.0 * (1.0 - xx) * lnx
            )
            / (1.0 + x4 + xx)
        )

    xx = x * x
    x4 = 4.0 * x
    return (
        4.0 * xx * (23.0 / 16.0 + x / 36.0 + xx / 576.0 + xx * x / 3600.0)
        + x4
        + 3.0 * (1.0 - xx) * math.log(1.0 - x)
    ) / (1.0 + x4 + xx)
