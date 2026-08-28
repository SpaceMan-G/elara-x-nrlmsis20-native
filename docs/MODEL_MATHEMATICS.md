# NRLMSIS 2.0 — Governing Mathematics

## Purpose

Whole-atmosphere empirical temperature and neutral-species model. This repository preserves the accepted Elara X NRLMSIS 2.0 compatibility state.

The equations below explain the physical and mathematical structure of the model. They are intentionally separated from the accepted implementation source: documentation must not silently become a second, divergent implementation.

## Empirical state dependence

A thermospheric empirical model can be represented schematically as a mapping

$$
\mathcal{M}:
(t,\mathbf{r},\mathbf{s})
\longrightarrow
(T,\rho,\mathbf{n}),
$$

where $t$ is epoch, $\mathbf{r}$ is position, $\mathbf{s}$ contains the required space-weather drivers, $T$ is temperature, $\rho$ is total mass density and $\mathbf{n}$ denotes constituent densities where provided.


## Thermospheric temperature structure

A useful representation of the upper-atmosphere temperature branch is the Bates-type form

$$
T(z) = T_\infty - \left(T_\infty - T_\ell\right)
\exp\!\left[-s\left(z-z_\ell\right)\right],
$$

where $T_\infty$ is exospheric temperature, $T_\ell$ is the temperature at a lower reference level, and $s$ controls the vertical temperature gradient.

The precise accepted implementation contains the fitted model basis and transition logic. This equation is therefore explanatory rather than a replacement implementation.

## Hydrostatic/diffusive structure

For a constituent $i$, hydrostatic balance can be written as

$$
\frac{dp_i}{dz} = -\rho_i g,
$$

with

$$
p_i = n_i k_B T,
\qquad
\rho_i = m_i n_i.
$$

Above the mixed lower thermosphere, the constituent profiles approach species-dependent diffusive behaviour; lower down, the model transitions toward mixed-atmosphere behaviour using the formulation encoded in the accepted scientific implementation.

## Total density

Total mass density is obtained from the constituent number densities:

$$
\rho = \sum_i m_i n_i.
$$

The species set and any model-version-specific terms are defined by the accepted implementation.

## Elara X NRLMSIS 2.0 compatibility identity

The accepted public repository implements the frozen Elara X NRLMSIS 2.0 compatibility contract using the accepted NRLMSIS 2.1 scientific core with the 2.1 nitric-oxide contribution disabled/excluded as defined by the repository's validation provenance. The compatibility layer must therefore not be interpreted as adding NO to the NRLMSIS 2.0 mass-density result.


## Unit discipline

Density is normally exposed by the Elara X public interfaces in SI units of kg m$^{-3}$ unless the interface explicitly documents a model-native unit. Angles, altitude and space-weather indices must follow the repository interface contract. Do not infer units from a variable name alone.

## Scientific reference

Emmert et al. (2021), NRLMSIS 2.0: A Whole-Atmosphere Empirical Model of Temperature and Neutral Species Densities.
