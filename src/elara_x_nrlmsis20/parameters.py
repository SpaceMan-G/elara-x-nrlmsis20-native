"""
Native NRLMSIS 2.1 initialization, parameter loading, and switch state.

Authoritative counterpart
-------------------------
NRL NRLMSIS 2.1 ``msis_init.F90``.

Derivative translation notice
-----------------------------
This file is a Python translation for the Elara X NRLMSIS native component.
The initialization state, parameter-subset layout, binary parameter loading,
derived pressure coefficients, and legacy-switch semantics of the authoritative
source are preserved.

The binary ``msis21.parm`` resource is intentionally not embedded here. Supply
its directory/path explicitly (or make the authoritative file available under
the default filename) when initializing the model.

Use and modification are governed by ``LICENSE_NRLMSIS21.txt`` in the
repository root. See the repository provenance and translation-governance
documents for the controlled translation and verification process.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import struct
from typing import Iterable, Sequence

from .constants import (
    Hgamma,
    Mbarg0divkB,
    cmag,
    cspw,
    csfx,
    csfxmod,
    ctide,
    cut,
    gwht,
    izfmx,
    maxnbf,
    mbf,
    ndNO,
    ndO1,
    nl,
    nls,
    nodesNO,
    nodesO1,
    nodesTN,
    nsfx,
    nsfxmod,
    nspec,
    nsplNO,
    nsplO1,
    nut,
    specmass,
    zetagamma,
    zetarefNO,
    zetarefO1,
)


def _f32(value: float) -> float:
    """Round *value* to IEEE-754 binary32 and return it as a Python float."""
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


class FortranMatrix:
    """Dense 2-D array with explicit logical column bounds.

    Storage is column-major so that the representation follows the native
    Fortran parameter-file layout. Row indices are always 0-based; columns use
    the logical ``bl:nl`` bounds carried by each ``BasisSubset``.
    """

    __slots__ = ("nrows", "bl", "nl", "_data")

    def __init__(self, nrows: int, bl: int, nl: int, fill=0.0):
        self.nrows = int(nrows)
        self.bl = int(bl)
        self.nl = int(nl)
        if self.nrows <= 0 or self.nl < self.bl:
            raise ValueError("invalid FortranMatrix bounds")
        self._data = [fill] * (self.nrows * (self.nl - self.bl + 1))

    @property
    def ncols(self) -> int:
        return self.nl - self.bl + 1

    @property
    def shape(self) -> tuple[int, int]:
        return (self.nrows, self.ncols)

    def _offset(self, row: int, col: int) -> int:
        row = int(row)
        col = int(col)
        if not 0 <= row < self.nrows:
            raise IndexError(row)
        if not self.bl <= col <= self.nl:
            raise IndexError(col)
        return (col - self.bl) * self.nrows + row

    def __getitem__(self, key):
        row, col = key
        return self._data[self._offset(row, col)]

    def __setitem__(self, key, value) -> None:
        row, col = key
        self._data[self._offset(row, col)] = value

    def fill(self, value) -> None:
        self._data[:] = [value] * len(self._data)

    def set_column(self, col: int, values: Sequence) -> None:
        col = int(col)
        if len(values) != self.nrows:
            raise ValueError("column length mismatch")
        start = self._offset(0, col)
        self._data[start : start + self.nrows] = list(values)

    def column(self, col: int) -> tuple:
        start = self._offset(0, int(col))
        return tuple(self._data[start : start + self.nrows])


@dataclass
class BasisSubset:
    name: str = ""
    bl: int = 0
    nl: int = -1
    beta: FortranMatrix | None = None
    active: FortranMatrix | None = None
    fitb: FortranMatrix | None = None


# Model flags.
initflag = False
haveparmspace = False
zaltflag = True
specflag = [True] * (nspec - 1)
massflag = [True] * (nspec - 1)
N2Rflag = False

zsfx = [False] * (mbf + 1)
tsfx = [False] * (mbf + 1)
psfx = [False] * (mbf + 1)
smod = [False] * (nl + 1)
swg = [True] * maxnbf
masswgt = [0.0] * (nspec - 1)

# Fortran REAL(4) legacy switch arrays.
swleg = [_f32(1.0)] * 25
swc = [_f32(0.0)] * 25
sav = [_f32(0.0)] * 25

# Model parameter subsets.
TN = BasisSubset()
PR = BasisSubset()
N2 = BasisSubset()
O2 = BasisSubset()
O1 = BasisSubset()
HE = BasisSubset()
H1 = BasisSubset()
AR = BasisSubset()
N1 = BasisSubset()
OA = BasisSubset()
NO = BasisSubset()
nvertparm = 0

# Reciprocal node-difference arrays use explicit Fortran logical indices.
etaTN = {(j, k): 0.0 for k in range(2, 7) for j in range(31)}
etaO1 = {(j, k): 0.0 for k in range(2, 7) for j in range(31)}
etaNO = {(j, k): 0.0 for k in range(2, 7) for j in range(31)}

HRfactO1ref = 0.0
dHRfactO1ref = 0.0
HRfactNOref = 0.0
dHRfactNOref = 0.0


def initsubset(subset: BasisSubset, bl: int, upper: int, nbf: int, name: str) -> int:
    subset.name = str(name)
    subset.bl = int(bl)
    subset.nl = int(upper)
    subset.beta = FortranMatrix(nbf, bl, upper, 0.0)
    subset.active = FortranMatrix(nbf, bl, upper, False)
    subset.fitb = FortranMatrix(nbf, bl, upper, 0)
    return 0 if name == "PR" else (upper - bl + 1)


def initparmspace() -> None:
    """Initialize and allocate the model parameter space."""
    global nvertparm, haveparmspace
    global HRfactO1ref, dHRfactO1ref, HRfactNOref, dHRfactNOref

    nvertparm = 0
    nvertparm += initsubset(TN, 0, nl, maxnbf, "TN")
    nvertparm += initsubset(PR, 0, nl, maxnbf, "PR")
    nvertparm += initsubset(N2, 0, nls, maxnbf, "N2")
    nvertparm += initsubset(O2, 0, nls, maxnbf, "O2")
    nvertparm += initsubset(O1, 0, nls + nsplO1, maxnbf, "O1")
    nvertparm += initsubset(HE, 0, nls, maxnbf, "HE")
    nvertparm += initsubset(H1, 0, nls, maxnbf, "H1")
    nvertparm += initsubset(AR, 0, nls, maxnbf, "AR")
    nvertparm += initsubset(N1, 0, nls, maxnbf, "N1")
    nvertparm += initsubset(OA, 0, nls, maxnbf, "OA")
    nvertparm += initsubset(NO, 0, nls + nsplNO, maxnbf, "NO")
    nvertparm += 1  # surface-pressure column

    zsfx[:] = [False] * len(zsfx)
    tsfx[:] = [False] * len(tsfx)
    psfx[:] = [False] * len(psfx)
    for i in (9, 10, 13, 14, 17, 18):
        zsfx[i] = True
    for i in range(ctide, cspw):
        tsfx[i] = True
    for i in range(cspw, cspw + 60):
        psfx[i] = True

    for key in etaTN:
        etaTN[key] = 0.0
        etaO1[key] = 0.0
        etaNO[key] = 0.0

    for k in range(2, 7):
        for j in range(0, nl + 1):
            etaTN[j, k] = 1.0 / (nodesTN[j + k - 1] - nodesTN[j])

    for k in range(2, 5):
        for j in range(0, ndO1 - k + 2):
            etaO1[j, k] = 1.0 / (nodesO1[j + k - 1] - nodesO1[j])
        for j in range(0, ndNO - k + 2):
            etaNO[j, k] = 1.0 / (nodesNO[j + k - 1] - nodesNO[j])

    gammaterm0 = math.tanh((zetarefO1 - zetagamma) * Hgamma)
    HRfactO1ref = 0.5 * (1.0 + gammaterm0)
    dHRfactO1ref = (
        1.0 - (zetarefO1 - zetagamma) * (1.0 - gammaterm0) * Hgamma
    ) / HRfactO1ref

    gammaterm0 = math.tanh((zetarefNO - zetagamma) * Hgamma)
    HRfactNOref = 0.5 * (1.0 + gammaterm0)
    dHRfactNOref = (
        1.0 - (zetarefNO - zetagamma) * (1.0 - gammaterm0) * Hgamma
    ) / HRfactNOref

    haveparmspace = True


def _read_parameter_columns(path: Path) -> tuple[tuple[float, ...], ...]:
    blob = path.read_bytes()
    expected_values = maxnbf * nvertparm
    expected_bytes = expected_values * 8
    if len(blob) != expected_bytes:
        raise ValueError(
            f"NRLMSIS 2.1 parameter file has {len(blob)} bytes; "
            f"expected {expected_bytes} bytes ({maxnbf} x {nvertparm} binary64 values)"
        )
    values = struct.unpack(f"<{expected_values}d", blob)
    return tuple(
        values[col * maxnbf : (col + 1) * maxnbf]
        for col in range(nvertparm)
    )


def loadparmset(name: str | Path, iun: int = 67) -> None:
    """Load the little-endian binary64 model-parameter matrix."""
    del iun  # retained for source-interface parity; Python does not expose file units.

    path = Path(name)
    if not path.is_file():
        raise FileNotFoundError(f"MSIS parameter set {path} not found")

    columns = _read_parameter_columns(path)

    i0 = 0
    i1 = TN.nl - TN.bl
    for z, col in zip(range(TN.bl, TN.nl + 1), range(i0, i1 + 1)):
        TN.beta.set_column(z, columns[col])

    i0 = i1 + 1
    i1 = i0
    PR.beta.set_column(0, columns[i0])

    offset = i1 + 1
    for subset in (N2, O2, O1, HE, H1, AR, N1, OA, NO):
        width = subset.nl - subset.bl + 1
        for z, col in zip(
            range(subset.bl, subset.nl + 1),
            range(offset, offset + width),
        ):
            subset.beta.set_column(z, columns[col])
        offset += width

    smod[:] = [False] * len(smod)
    for z in range(TN.bl, TN.nl + 1):
        smod[z] = (
            TN.beta[csfxmod + 0, z] != 0.0
            or TN.beta[csfxmod + 1, z] != 0.0
            or TN.beta[csfxmod + 2, z] != 0.0
        )

    pressparm()


def pressparm() -> None:
    """Compute log-pressure spline coefficients from temperature coefficients."""
    for j in range(0, mbf + 1):
        lnz = 0.0
        for b in range(0, 4):
            lnz = lnz + TN.beta[j, b] * gwht[b] * Mbarg0divkB
        PR.beta[j, 1] = -lnz

        for iz in range(1, izfmx + 1):
            lnz = 0.0
            for b in range(0, 4):
                lnz = lnz + TN.beta[j, iz + b] * gwht[b] * Mbarg0divkB
            PR.beta[j, iz + 1] = PR.beta[j, iz] - lnz


def _set_range(start: int, stop_inclusive: int, value: bool) -> None:
    for i in range(start, stop_inclusive + 1):
        swg[i] = bool(value)


def _set_indices(indices: Iterable[int], value: bool) -> None:
    for i in indices:
        swg[int(i)] = bool(value)


def tselec(sv: Sequence[float]) -> None:
    """Apply the authoritative 25-element legacy-switch mapping.

    Inputs are rounded to Fortran REAL(4) before any switch arithmetic.
    """
    if len(sv) != 25:
        raise ValueError("legacy switch vector must contain exactly 25 values")

    values = [_f32(x) for x in sv]
    for i, value in enumerate(values):
        sav[i] = value
        swleg[i] = _f32(math.fmod(value, _f32(2.0)))
        absolute = abs(value)
        swc[i] = _f32(1.0 if absolute == _f32(1.0) or absolute == _f32(2.0) else 0.0)

    # Main effects. Fortran switch numbers are one-based; Python list indices
    # for swleg/swc are therefore one lower.
    swg[0] = True
    _set_range(csfx, csfx + nsfx - 1, swleg[0] == _f32(1.0))
    swg[310] = swleg[0] == _f32(1.0)

    _set_range(1, 6, swleg[1] == _f32(1.0))
    _set_range(304, 305, swleg[1] == _f32(1.0))
    _set_range(311, 312, swleg[1] == _f32(1.0))
    _set_range(313, 314, swleg[1] == _f32(1.0))

    _set_indices((7, 8, 11, 12, 15, 16, 19, 20), swleg[2] == _f32(1.0))
    _set_range(306, 307, swleg[2] == _f32(1.0))

    _set_indices((21, 22, 25, 26, 29, 30, 33, 34), swleg[3] == _f32(1.0))
    _set_range(308, 309, swleg[3] == _f32(1.0))

    _set_indices((9, 10, 13, 14, 17, 18), swleg[4] == _f32(1.0))
    _set_indices((23, 24, 27, 28, 31, 32), swleg[5] == _f32(1.0))

    _set_range(35, 94, swleg[6] == _f32(1.0))
    _set_range(300, 303, swleg[6] == _f32(1.0))
    _set_range(95, 144, swleg[7] == _f32(1.0))
    _set_range(145, 184, swleg[13] == _f32(1.0))

    _set_range(cmag, cmag + 1, False)
    if swleg[8] > _f32(0.0) or swleg[12] == _f32(1.0):
        swg[cmag] = True
        swg[cmag + 1] = True
    if swleg[8] < _f32(0.0):
        swg[cmag] = False
        swg[cmag + 1] = True

    _set_range(cmag + 2, cmag + 12, swleg[8] == _f32(1.0))
    _set_range(cmag + 28, cmag + 40, swleg[8] == _f32(-1.0))

    _set_range(cspw, csfx - 1, swleg[10] == _f32(1.0) and swleg[9] == _f32(1.0))
    _set_range(cut, cut + nut - 1, swleg[11] == _f32(1.0) and swleg[9] == _f32(1.0))
    _set_range(cmag + 13, cmag + 25, swleg[12] == _f32(1.0) and swleg[9] == _f32(1.0))
    _set_range(cmag + 41, cmag + 53, swleg[12] == _f32(1.0) and swleg[9] == _f32(1.0))

    # Cross terms.
    _set_range(csfxmod, csfxmod + nsfxmod - 1, swc[0] == _f32(1.0))
    if swc[0] == _f32(0.0):
        _set_range(302, 303, False)
        _set_range(304, 305, False)
        _set_range(306, 307, False)
        _set_range(308, 309, False)
        _set_range(311, 314, False)
        swg[447] = False
        swg[454] = False

    if swc[1] == _f32(0.0):
        _set_range(9, 20, False)
        _set_range(23, 34, False)
        _set_range(35, 184, False)
        _set_range(185, 294, False)
        _set_range(392, 414, False)
        _set_range(420, 442, False)
        _set_range(449, 453, False)

    if swc[2] == _f32(0.0):
        for lo, hi in ((201,204),(209,212),(217,220),(255,258),(263,266),(271,274),(306,307)):
            _set_range(lo, hi, False)

    if swc[3] == _f32(0.0):
        for lo, hi in ((225,228),(233,236),(241,244),(275,278),(283,286),(291,294),(308,309)):
            _set_range(lo, hi, False)

    if swc[4] == _f32(0.0):
        for lo, hi in (
            (47,50),(51,54),(55,58),(59,62),(63,66),(67,70),
            (105,108),(109,112),(113,116),(117,120),(121,124),
            (153,156),(157,160),(161,164),(165,168),
            (197,200),(205,208),(213,216),(259,262),(267,270),
            (394,397),(407,410),(422,425),(435,438),
        ):
            _set_range(lo, hi, False)
        swg[446] = False

    if swc[5] == _f32(0.0):
        for lo, hi in ((221,224),(229,232),(237,240),(279,282),(287,290)):
            _set_range(lo, hi, False)

    if swc[6] == _f32(0.0):
        _set_range(398, 401, False)
        _set_range(426, 429, False)

    if swc[10] == _f32(0.0):
        _set_range(402, 410, False)
        _set_range(430, 438, False)
        _set_range(452, 453, False)

    if swc[11] == _f32(0.0):
        _set_range(411, 414, False)
        _set_range(439, 440, False)


def tretrv() -> tuple[float, ...]:
    """Return the saved legacy switches using Fortran REAL(4) values."""
    return tuple(sav)


def msisinit(
    parmpath: str | Path = "",
    parmfile: str = "msis21.parm",
    iun: int = 67,
    switch_gfn: Sequence[bool] | None = None,
    switch_legacy: Sequence[float] | None = None,
    lzalt_type: bool | None = None,
    lspec_select: Sequence[bool] | None = None,
    lmass_include: Sequence[bool] | None = None,
    lN2_msis00: bool | None = None,
) -> None:
    """Initialize model parameters, switches, and user options."""
    global initflag, zaltflag, N2Rflag

    if not haveparmspace:
        initparmspace()

    parameter_path = Path(str(parmpath) + str(parmfile))
    loadparmset(parameter_path, iun)

    swg[:] = [True] * maxnbf
    swleg[:] = [_f32(1.0)] * 25

    if switch_gfn is not None:
        if len(switch_gfn) != maxnbf:
            raise ValueError(f"switch_gfn must contain exactly {maxnbf} values")
        swg[:] = [bool(x) for x in switch_gfn]
    elif switch_legacy is not None:
        if len(switch_legacy) != 25:
            raise ValueError("switch_legacy must contain exactly 25 values")
        swleg[:] = [_f32(x) for x in switch_legacy]
        tselec(swleg)

    zaltflag = True if lzalt_type is None else bool(lzalt_type)

    if lspec_select is None:
        specflag[:] = [True] * (nspec - 1)
    else:
        if len(lspec_select) != nspec - 1:
            raise ValueError(f"lspec_select must contain exactly {nspec - 1} values")
        specflag[:] = [bool(x) for x in lspec_select]

    if specflag[0]:
        if lmass_include is None:
            massflag[:] = [True] * (nspec - 1)
        else:
            if len(lmass_include) != nspec - 1:
                raise ValueError(f"lmass_include must contain exactly {nspec - 1} values")
            massflag[:] = [bool(x) for x in lmass_include]
    else:
        massflag[:] = [False] * (nspec - 1)

    for i, enabled in enumerate(massflag):
        if enabled:
            specflag[i] = True

    masswgt[:] = [0.0] * (nspec - 1)
    for i, enabled in enumerate(massflag):
        if enabled:
            masswgt[i] = specmass[i]
    masswgt[0] = 0.0
    masswgt[9] = 0.0

    N2Rflag = False if lN2_msis00 is None else bool(lN2_msis00)
    initflag = True
