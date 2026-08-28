# NRLMSIS 2.0 — Physical Model and Process

## Physical interpretation

Whole-atmosphere empirical temperature and neutral-species model. This repository preserves the accepted Elara X NRLMSIS 2.0 compatibility state.

The model is empirical/semi-empirical rather than a first-principles global fluid simulation. Observations and physical thermospheric structure are represented through fitted basis functions, temperature profiles, constituent behaviour and external solar/geomagnetic forcing.

## Process chain

```text
epoch + spacecraft position
            |
            v
solar / geomagnetic drivers
            |
            v
model-specific temporal and spatial basis
            |
            v
temperature / constituent state
            |
            v
total neutral mass density
            |
            v
orbit, drag, validation or daily-product workflow
```

## Environmental forcing

Solar, geomagnetic, seasonal, latitude and local-time basis functions evaluated through the accepted NRLMSIS formulation.

The timing/history semantics of the forcing are scientific inputs. A wrapper must not silently replace delayed, averaged or history-resolved quantities with an unrelated instantaneous value.

## Model boundary

The repository model provides atmospheric state. Orbit propagation, spacecraft geometry, drag coefficient estimation, force integration and inverse-density retrieval are separate downstream processes unless the repository explicitly contains such utilities.

## What is empirical and what is physical

The model combines:

- hydrostatic/diffusive atmospheric structure;
- temperature-dependent scale-height behaviour;
- observationally fitted spatial and temporal variations;
- solar heating proxies;
- geomagnetic-response proxies;
- seasonal and local-time structure.

The accepted source code remains the numerical authority whenever this explanatory document omits implementation detail.
