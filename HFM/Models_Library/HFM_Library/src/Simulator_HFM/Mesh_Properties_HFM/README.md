# MixPropertiesCoolPropHEOS

> **⚠️ Limited Scope:** This package is **not a general-purpose thermodynamic library.**  
> It is designed exclusively for calculating physical and transport properties of gas mixtures **along the spatial domain of a hollow-fiber membrane module**.

---

## What does this code do?

It resolves thermodynamic and transport properties (enthalpy, density, viscosity, thermal conductivity, heat capacity, fugacity and fugacity coefficients) of a multicomponent mixture **at each axial node** of a hollow-fiber membrane module.

The typical workflow is:

1. **Define the mixture** (e.g. CO₂ / CH₄ / N₂) and feed conditions (P, T, composition).
2. **Discretize the module** into `NStates` axial nodes.
3. **Instantiate** `MixPropertiesCoolPropHEOS` with `P`, `T`, `Z` vectors of length `NStates`.
4. **Update** all states with `update_all()`.
5. **Query** properties at each node with `get_properties(k)`.

The results are consumed directly by the mass, energy and momentum balances of the membrane model (not included in this package).

---

## What is it NOT for?

| Scenario | Supported? | Reason |
|---|---|---|
| Liquids or condensed phases | ❌ No | Enforces gas phase (`force_gas_phase=True`) and clips temperatures to [150, 1000] K |
| Generic VLE / VLLE flash | ❌ No | Does not expose phase equilibrium; only evaluates gas-phase properties |
| Pure-substance properties outside a membrane module | ⚠️ Partial | Works technically, but the API (`P`, `T`, `Z` vectors per node) is designed for axial profiles |
| Substances not supported by CoolProp | ❌ No | Entirely dependent on the HEOS or cubic (PR/SRK) backend of CoolProp |
| Dew-point calculations as design constraints | ⚠️ Partial | `dew_temperature()` is **deprecated** for constraints; use `single_phase_at()` instead |

---

## Architecture

```
mixprop/
├── __init__.py              # Entry point: exports the public class
├── constants.py             # _BULK_GETTERS mapping (property → CoolProp getter)
├── core.py                  # Orchestrator: __init__, set_conditions
│                              Coordinates state, broadcasting and validation.
│                              Inherits from mixins.
└── mixins/
    ├── state_updater.py     # safe_update_gas, _fallback_state, update_state,
    │                          update_all, get_properties
    └── phase.py             # single_phase_at, dew_temperature, _T_dew_bounds
```

**There is no external orchestrator.** `MixPropertiesCoolPropHEOS` in `core.py` is the natural orchestrator: it holds the shared internal state (`self.states`, `self.P`, `self.T`, `self.Z`, `self.props`) and delegates flash logic and phase-stability checks to the mixins.

---

## Dependencies

- `numpy`
- `CoolProp`

---

## Typical Usage (Hollow-Fiber Membrane)

```python
from mixprop import MixPropertiesCoolPropHEOS

# Retentate / permeate mixture components
components = ["CO2", "CH4", "N2"]

# Axial profiles: 50 nodes along the module
N = 50
P_profile = np.linspace(10e5, 9.5e5, N)   # Pa, small pressure drop
T_profile = np.full(N, 300.0)             # K, approximately isothermal

# Composition at each node (e.g. CO₂ enrichment towards permeate)
Z_profile = np.zeros((N, 3))
Z_profile[:, 0] = np.linspace(0.50, 0.65, N)   # CO2
Z_profile[:, 1] = np.linspace(0.40, 0.30, N)   # CH4
Z_profile[:, 2] = np.linspace(0.10, 0.05, N)   # N2

# Instantiate with HEOS (more accurate, slower) or PR (cubic, faster)
mp = MixPropertiesCoolPropHEOS(
    components=components,
    P=P_profile,
    T=T_profile,
    Z=Z_profile,
    eos="HEOS",               # or "PR" for Peng-Robinson
    force_gas_phase=True,
    bulk_props=["hmolar", "rhomass", "viscosity", "conductivity", "cpmolar"]
)

# Calculate properties at all nodes
mp.update_all()

# Query at node 0
props = mp.get_properties(0)
print(props["bulk"]["hmolar"])          # J/mol
print(props["bulk"]["viscosity"])       # Pa·s
print(props["components"]["fugacity"])  # Pa

# Verify the mixture remains single-phase along the module
ok, Q = mp.single_phase_at(T_profile - 5.0)  # 5 K margin
if not ok.all():
    print("Warning! Possible condensation at some node.")
```

---

## Design Notes

- **State reuse:** `set_conditions()` allows updating `P`, `T` or `Z` without reconstructing CoolProp `AbstractState` objects. This is critical in iterative membrane simulations (fugacity and energy loops).
- **HEOS fallback:** When using `eos="PR"`, transport properties (viscosity, conductivity) are automatically computed via a secondary HEOS flash, while thermodynamics (enthalpy, density, fugacity) remain on PR.
- **Phase stability:** `single_phase_at()` performs a PT flash at the evaluated temperature and checks `Q < 0` or `Q > 1`. It is more robust than searching for the dew temperature (`dew_temperature`), which can converge to spurious roots near the phase boundary.

---

## Credits

- **Original author:** Diego Gabriel Oliva
- **Date:** 16-May-2025
- **Refactoring & documentation:** AI Assistant (mixin structure, preserving original names and comments)
