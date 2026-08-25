"""
Native NRLMSIS 2.1 constants and hardwired parameters.

Authoritative counterpart
-------------------------
NRL NRLMSIS 2.1 ``msis_constants.F90``.

Derivative translation notice
-----------------------------
This file is a Python translation for the Elara X NRLMSIS native component.
The scientific formulation, indexing semantics, hardwired parameter values,
and double-precision intent of the authoritative source are preserved.

Use and modification are governed by ``LICENSE_NRLMSIS21.txt`` in the
repository root. See the repository provenance and translation-governance
documents for the controlled translation and verification process.

This module intentionally contains no runtime model evaluation logic.
"""

from __future__ import annotations

import math

# Python float is IEEE-754 binary64 on supported CPython platforms.
rp = 8

# Missing density value
dmissing = 9.999e-38

# Trigonometric constants
pi = 3.1415926535897932384626433832795
deg2rad = pi / 180.0
doy2rad = 2.0 * pi / 365.0
lst2rad = pi / 12.0
tanh1 = math.tanh(1.0)

# Thermodynamic constants
kB = 1.380649e-23
NA = 6.02214076e23
g0 = 9.80665

# Species molecular masses (kg/molecule)
specmass = tuple(
    value / (1.0e3 * NA)
    for value in (
        0.0,           # Mass density (dummy)
        28.0134,       # N2
        31.9988,       # O2
        31.9988 / 2.0, # O
        4.0,           # He
        1.0,           # H
        39.948,        # Ar
        28.0134 / 2.0, # N
        31.9988 / 2.0, # Anomalous O
        (28.0134 + 31.9988) / 2.0,  # NO
    )
)

# Dry air mean mass in fully mixed atmosphere (kg/molecule)
Mbar = 28.96546 / (1.0e3 * NA)

# Dry air log volume mixing ratios
lnvmr = tuple(
    math.log(value)
    for value in (
        1.0,
        0.780848,
        0.209390,
        1.0,
        0.0000052,
        1.0,
        0.009332,
        1.0,
        1.0,
        1.0,
    )
)

# Natural log of global average surface pressure (Pa)
# The authoritative source intentionally omits the _rp suffix here. In the
# DBLE build, Fortran therefore rounds the literal as default REAL first and
# then promotes it to real(kind=8). Preserve that source-level semantics.
lnP0 = 11.515613555908203125

# Derived constants
g0divkB = g0 / kB * 1.0e3
Mbarg0divkB = Mbar * g0 / kB * 1.0e3

# Vertical profile parameters
nspec = 11
nd = 27
p = 4
nl = nd - p
nls = 9

bwalt = 122.5
zetaF = 70.0
zetaB = bwalt
zetaA = 85.0
zetagamma = 100.0
Hgamma = 1.0 / 30.0

nodesTN = (
    -15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0,
    35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0,
    85.0, 92.5, 102.5, 112.5, 122.5, 132.5, 142.5, 152.5, 162.5,
    172.5,
)

izfmx = 13
izfx = 14
izax = 17
itex = nl
itgb0 = nl - 1
itb0 = nl - 2

# O1 spline parameters
ndO1 = 13
nsplO1 = ndO1 - 5
nodesO1 = (
    35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0,
    85.0, 92.5, 102.5, 112.5,
)
zetarefO1 = zetaA

# NO spline parameters
ndNO = 13
nsplNO = ndNO - 5
nodesNO = (
    47.5, 55.0, 62.5, 70.0, 77.5, 85.0, 92.5, 100.0, 107.5, 115.0,
    122.5, 130.0, 137.5, 145.0,
)
zetarefNO = zetaB

# Fortran RESHAPE uses column-major filling. The Python nested tuples below
# are row-major representations of the same mathematical matrices.
c2tn = (
    (1.0, 1.0, 1.0),
    (-10.0, 0.0, 10.0),
    (33.333333333333336, -16.666666666666668, 33.333333333333336),
)

c1o1 = (
    (1.75, -1.624999900076852),
    (-2.916666573405061, 21.458332647194382),
)
c1o1adj = (0.257142857142857, -0.102857142686844)

c1NO = (
    (1.5, 0.0),
    (-3.75, 15.0),
)
c1NOadj = (0.166666666666667, -0.066666666666667)

# Anomalous oxygen parameters
zetarefOA = zetaB
TOA = 4000.0
HOA = (kB * TOA) / ((16.0 / (1.0e3 * NA)) * g0) * 1.0e-3

# Horizontal and time-dependent basis function parameters
maxnbf = 512
maxn = 6
maxl = 3
maxm = 2
maxs = 2
amaxn = 6
amaxs = 2
tmaxl = 3
tmaxn = 6
tmaxs = 2
pmaxm = 2
pmaxn = 6
pmaxs = 2
nsfx = 5
nsfxmod = 5
nmag = 54
nut = 12

ctimeind = 0
cintann = ctimeind + (amaxn + 1)
ctide = cintann + ((amaxn + 1) * 2 * amaxs)
cspw = ctide + (4 * tmaxs + 2) * (
    tmaxl * (tmaxn + 1) - (tmaxl * (tmaxl + 1)) // 2
)
csfx = cspw + (4 * pmaxs + 2) * (
    pmaxm * (pmaxn + 1) - (pmaxm * (pmaxm + 1)) // 2
)
cextra = csfx + nsfx
mbf = 383
cnonlin = mbf + 1
csfxmod = cnonlin
cmag = csfxmod + nsfxmod
cut = cmag + nmag

# Weights for log-pressure spline coefficients
gwht = (5.0 / 24.0, 55.0 / 24.0, 55.0 / 24.0, 5.0 / 24.0)

# Analytical-integration weights for the hydrostatic effective-mass profile
wbeta = tuple(
    (nodesTN[i + 4] - nodesTN[i]) / 4.0
    for i in range(nl + 1)
)
wgamma = tuple(
    (nodesTN[i + 5] - nodesTN[i]) / 5.0
    for i in range(nl + 1)
)

# Non-zero B-spline values and derivative weights
S5zetaB = (
    0.041666666666667,
    0.458333333333333,
    0.458333333333333,
    0.041666666666667,
)
S6zetaB = (
    0.008771929824561,
    0.216228070175439,
    0.550000000000000,
    0.216666666666667,
    0.008333333333333,
)

wghtAxdz = (-0.102857142857, 0.0495238095238, 0.053333333333)

S4zetaA = (0.257142857142857, 0.653968253968254, 0.088888888888889)
S5zetaA = (
    0.085714285714286,
    0.587590187590188,
    0.313020313020313,
    0.013675213675214,
)
S6zetaA = (
    0.023376623376623,
    0.378732378732379,
    0.500743700743701,
    0.095538448479625,
    0.001608848667672,
)

S4zetaF = (0.166666666666667, 0.666666666666667, 0.166666666666667)
S5zetaF = (
    0.041666666666667,
    0.458333333333333,
    0.458333333333333,
    0.041666666666667,
)
S5zeta0 = (0.458333333333333, 0.458333333333333, 0.041666666666667)
