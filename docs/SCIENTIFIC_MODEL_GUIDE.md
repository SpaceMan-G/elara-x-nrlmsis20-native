# NRLMSIS 2.0 Compatibility — Scientific Model Guide

## Purpose

This repository provides the accepted NRLMSIS 2.0 compatibility state using
the validated native scientific core while preserving a distinct 2.0 model
namespace and output semantics.

The accepted compatibility rule is scientifically important: nitric oxide is
disabled and excluded from the aggregate mass-density calculation so the
result reproduces the official NRLMSIS 2.0 boundary.

## Principal inputs

The calculation uses the same atmospheric drivers as the associated native
MSIS family implementation:

- day of year and UT seconds;
- altitude, latitude and longitude;
- daily and mean F10.7 solar flux;
- geomagnetic activity history.

The model coefficient resource remains external and is verified before use.

## Mathematical structure

The empirical state can be written schematically as

\[
X = X_0 + \sum_j c_j G_j(d,t,\phi,\lambda,F,\bar F,A_p),
\]

where fitted basis functions represent solar, geomagnetic, seasonal,
latitudinal and local-time effects.

The vertical thermosphere combines a fitted upper-temperature state with
diffusive constituent profiles. A constituent number density follows the
hydrostatic/diffusive form

\[
\frac{d n_i}{dz}
=
-n_i\frac{m_i g}{kT}
-
(1+\alpha_i)\frac{n_i}{T}\frac{dT}{dz}.
\]

Aggregate density is a constituent mass sum,

\[
\rho_{2.0} = \sum_{i\in S_{2.0}} m_i n_i,
\]

where \(S_{2.0}\) is the accepted NRLMSIS 2.0 constituent set. In this
compatibility implementation the nitric-oxide contribution used by the 2.1
state is not included.

## Calculation workflow

```text
verify external parameter resource
        ↓
load isolated NRLMSIS 2.0 state
        ↓
evaluate empirical horizontal/activity terms
        ↓
evaluate temperature structure
        ↓
evaluate constituent number densities
        ↓
enforce 2.0 constituent/NO compatibility semantics
        ↓
assemble D(1:9), TEX and TN legacy outputs
```

## Implementation map

- `parameters.py` / `resources.py` — isolated parameter state and external
  verified resource resolver.
- `horizontal.py` — empirical horizontal/activity terms.
- `temperature.py` — temperature profile.
- `density.py` — constituent density calculation.
- `model.py` — assembled model calculation.
- `legacy_interface.py` — accepted GTD8D-compatible boundary.
- `api.py` — standalone public API.

## Accepted scientific result

The frozen validation programme exercised 200 official cases and 2,200 scalar
outputs covering `D(1:9)`, `TEX` and `TN` at the IEEE-754 binary32 compatibility
boundary. The accepted result contained zero bit differences and zero frozen
tolerance mismatches.

That validation result is stronger than a single worked number: it proves the
published compatibility semantics over a controlled multi-case matrix.

## Reproducible paper-result chain

For paper-linked work, the repository should make the result traceable as:

```text
paper figure/table
        ↓
paper result directory
        ↓
RUN_MANIFEST.json
        ↓
exact model repository commit
        ↓
model inputs and units
        ↓
scientific implementation
        ↓
validation authority / accepted test contract
```

A paper-result directory should therefore record the model name, the exact Git
HEAD used for the calculation, input identities/hashes where redistribution is
permitted, configuration, units, output hashes, and the relationship between
derived plots/tables and the underlying CSV/JSON result.

Only publication-safe derived outputs belong in this repository. Restricted
third-party data, model coefficient payloads that are external by policy,
credentials, private machine paths, private application source, caches, and
temporary files must remain outside the repository.
