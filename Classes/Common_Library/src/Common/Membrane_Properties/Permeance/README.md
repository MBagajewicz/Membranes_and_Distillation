# MembranePermeance

> **Scope:** Data container and calculator for membrane permeance.  
> Part of the HFM (hollow-fiber membrane) simulator property stack.

---

## What it does

Stores the permeance of each component across the membrane. Two input modes are supported:

| Mode | Use case |
|---|---|
| **Direct permeance** | Experimental data already in `[mol/(m²·Pa·s)]` |
| **Permeability + thickness** | Material properties known; permeance computed as `Q = P / δ` |

The object is immutable after construction (no setters). It is used by the mass-balance solver to compute the trans-membrane molar flux.

---

## Quick start

```python
from Membrane_Permeance import MembranePermeance

# Mode 1: direct permeance
mp = MembranePermeance(
    components=["CO2", "CH4", "N2"],
    permeance=[1.0e-10, 5.0e-12, 1.0e-12]   # mol/(m2 Pa s)
)

# Mode 2: from permeability and thickness
mp = MembranePermeance(
    components=["CO2", "CH4", "N2"],
    permeability=[5.0e-15, 2.5e-16, 5.0e-17],  # mol/(m Pa s)
    thickness=50.0e-6                            # m
)
# permeance is auto-computed

# Query
print(mp.permeance)          # array [mol/(m2 Pa s)]
print(mp.component_permeance("CO2"))   # scalar
mp.summary()                 # human-readable table
```

---

## API

### `MembranePermeance(components, permeance=None, permeability=None, thickness=None)`

Constructor. Exactly one of the following must be provided:

- `permeance` — `array-like` — Direct permeance values `[mol/(m²·Pa·s)]`.
- `permeability` **and** `thickness` — Permeability `[mol/(m·Pa·s)]` and membrane thickness `[m]`.

**Raises** `ValueError` if neither or both modes are supplied.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `components` | `list[str]` | Component names (same order as arrays) |
| `permeance` | `np.ndarray` | Permeance `[mol/(m²·Pa·s)]` |
| `permeability` | `np.ndarray \| None` | Permeability `[mol/(m·Pa·s)]` (if supplied) |
| `thickness` | `float \| None` | Membrane thickness `[m]` (if supplied) |

### Methods

| Method | Returns | Description |
|---|---|---|
| `component_index(comp)` | `int` | Index of `comp` in `self.components` |
| `component_permeance(comp)` | `float` | Permeance of a single component |
| `component_permeability(comp)` | `float` | Permeability of a single component (raises if not stored) |
| `summary()` | `None` | Prints a formatted table to stdout |

---

## Design notes

- **Immutable:** No setters. If permeance changes (e.g. during an optimisation loop), instantiate a new object. This prevents accidental mutation inside the mass-balance solver.
- **Shape consistency:** `permeance`, `permeability`, and `components` must all have the same length. No runtime check is performed (assumes the caller is consistent).
- **Units:** The class does not enforce units; it merely stores the numbers. The HFM simulator expects `mol/(m²·Pa·s)` for permeance and `m` for thickness.

---

## Credits

- **Author:** Diego Gabriel Oliva  
- **Date:** 14-May-2026
