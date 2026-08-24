# MixtureProperties

> **Scope:** Single-file viscosity calculator for gas mixtures.  
> Designed as a drop-in adapter for the HFM (hollow-fiber membrane) simulator.

---

## What it does

Calculates the **dynamic viscosity** of a gas mixture given its composition. Two calculation routes are supported:

| Route | Speed | Inputs needed | Best for |
|---|---|---|---|
| **Herning–Zipperer (HZ)** | Very fast (no flash) | `MU` (pure viscosities), `M` (molecular weights) | Hot loops (pressure drop inside iterative solvers) |
| **CoolProp** | Slow (pure-component PT flash per call) | `T` [K], `P` [Pa] | Validation / cross-check against HZ |

The class is a thin **adapter**: the caller (`SimulatorRunHFM`, or any other module) only ever calls `viscosity(mol_fractions, T, P)` and the implementation is chosen automatically via the `method` constructor argument.

---

## Quick start

```python
from Mixture_Properties import MixtureProperties

# Herning–Zipperer (default) — fast, composition-only
props = MixtureProperties(
    components=["CO2", "CH4", "N2"],
    MU=[1.49e-5, 1.10e-5, 1.78e-5],   # Pa·s
    M=[44.01, 16.04, 28.01],          # kg/kmol
    method="HZ"
)

mu = props.viscosity(mol_fractions=[0.5, 0.4, 0.1])
# → float, mixture viscosity in Pa·s

# CoolProp — slower, uses T and P
props_cp = MixtureProperties(
    components=["CO2", "CH4", "N2"],
    method="CoolProp"
)

mu = props_cp.viscosity(mol_fractions=[0.5, 0.4, 0.1], T=300.0, P=1e5)
```

---

## API

### `MixtureProperties(components, MU=None, M=None, method="HZ")`

Constructor.

- `components` — `list[str]` — CoolProp-compatible fluid names.
- `MU` — `array-like` — Pure-component viscosities `[Pa·s]`. Required for `method="HZ"`.
- `M` — `array-like` — Molecular weights `[kg/kmol]`. Required for `method="HZ"`.
- `method` — `"HZ"` or `"CoolProp"`.

### `viscosity(mol_fractions, T=None, P=None) → float`

Returns mixture viscosity `[Pa·s]`.

- `mol_fractions` — mole fractions of each component (need not sum to 1.0; internally normalised).
- `T` — temperature `[K]`. Required only for `method="CoolProp"`.
- `P` — pressure `[Pa]`. Required only for `method="CoolProp"`.

---

## Design notes

- **Self-contained:** No external dependencies beyond `numpy` and (optionally) `CoolProp`. The old separate file `Calculations_Prop_Viscosity_gas_mix.py` has been merged here and can be deleted.
- **Degenerate safeguard:** If the mole fractions sum to essentially zero (can happen in the permeate dead zone of an oversized membrane module), the method returns the arithmetic mean of the pure viscosities instead of `NaN`. This keeps the pressure-drop evaluation well-posed even when the local flow is numerically zero.
- **Threading:** The class holds no mutable state beyond the input arrays. It is safe to share across threads, though the CoolProp route is not thread-safe (CoolProp’s C++ layer uses global state).

---

## Credits

- **Original author:** Diego Gabriel Oliva  
- **Herning–Zipperer implementation:** João Tupinambá  
- **Refactoring & merge:** AI Assistant (30-Jul-2026)
