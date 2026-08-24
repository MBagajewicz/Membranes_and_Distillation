# Stream

> A backend-agnostic thermodynamic state representation for process simulation.

`Stream` is a single, focused Python class that encapsulates a thermodynamic
state — composition, pressure, temperature, and flow — and exposes derived
properties (density, enthalpy, viscosity, heat capacity, etc.) through a clean,
read-only interface backed by [CoolProp](http://www.coolprop.org/).

It is **not** a process simulator, a unit operation, or a flowsheet node. It is
strictly a thermodynamic state: a set of intensive and extensive properties that
fully characterise a flowing mixture at a given point in time.

---

## Design Principles

These principles are non-negotiable and guide every design decision in the
package.

1. **Stream represents a thermodynamic state, not equipment.**  
   It is not a heat exchanger, a membrane module, or a process cell. It is a
   material stream.

2. **The user supplies only independent information.**  
   - Components and composition  
   - Pressure and temperature  
   - **Exactly one** flow specification (mass or molar)  
   - Backend choice  
   Everything else is derived automatically.

3. **The user never calculates properties.**  
   There is no `stream.calculate_properties()` and no
   `stream.update_properties()`. Every state mutation triggers an automatic
   internal refresh.

4. **Properties are read-only.**  
   ```python
   stream.viscosity      # OK
   stream.cp_mass        # OK
   stream.viscosity = x  # AttributeError — properties are consequences, not inputs
   ```

5. **The state can be modified.**  
   `set_PT()`, `set_P()`, `set_T()`, `set_mass_flow()`, `set_molar_flow()`,
   `set_composition()`, and `update()` are the public mutation API. The class
   guarantees internal consistency after every call.

6. **Backend-agnostic architecture.**  
   Downstream models (heat exchangers, membrane modules, etc.) simply read
   `stream.cp_mass`, `stream.viscosity`, `stream.density_mass`, and remain
   completely unaware of whether CoolProp, REFPROP, or a custom EOS is running
   underneath.

---

## Installation

```bash
pip install CoolProp
```

Then copy the `stream/` package into your project or install it in editable mode:

```bash
cd stream/
pip install -e .
```

> **REFPROP backend:** If you want to use `ThermoBackend.REFPROP`, you must have
> a licensed REFPROP installation that CoolProp can discover.

---

## Quick Start

```python
from stream import Stream, ThermoBackend

# Define a natural-gas-like mixture
natural_gas = {
    "Methane":       0.9067,
    "Nitrogen":      0.0313,
    "CO2":           0.0047,   # alias -> CarbonDioxide
    "Ethane":        0.0453,
    "Propane":       0.0083,   # alias -> n-Propane
    "IsoButane":     0.0010,
    "Butane":        0.0016,   # alias -> n-Butane
}

# Create the stream
feed = Stream(
    composition=natural_gas,
    P=50e5,            # 50 bar
    T=300.0,           # 300 K
    molar_flow=1000.0, # 1000 mol/s
    backend=ThermoBackend.HEOS,
)

# Read properties — they are cached and instantaneous
print(feed.cp_mass)        # J/kg·K
print(feed.viscosity)      # Pa·s
print(feed.density_mass)   # kg/m³
print(feed.enthalpy_mass)  # J/kg
print(feed.prandtl)        # dimensionless
```

---

## Fluid Aliases

CoolProp is strict with fluid names. `Stream` includes an internal alias table
so you can write natural names:

| User-friendly name | CoolProp canonical name |
|---|---|
| `CO2` | `CarbonDioxide` |
| `N2` | `Nitrogen` |
| `Propane` | `n-Propane` |
| `Butane` | `n-Butane` |
| `Isobutane` | `IsoButane` |
| `H2O` | `Water` |
| `CH4` | `Methane` |
| ... | ... |

If a name is not in the alias table, `Stream` tries an exact match and then a
case-insensitive match against CoolProp's full fluid list before raising an
error.

---

## Mixture Fallback: When CoolProp Cannot Build the EOS

### The Problem

CoolProp's **HEOS** backend works perfectly for pure fluids and small mixtures
with well-parameterised binary pairs. However, for large natural-gas mixtures
(10–20 components including `CO2`, `N2`, `H2S`, `COS`, water, etc.), CoolProp
often lacks one or more binary interaction parameters and raises:

```
ValueError: Could not match the binary pair [463-58-1, 7727-37-9]
```

`Stream` does **not** crash. It catches this error, emits a `UserWarning`, and
**falls back to pure-component calculations with ideal mixing rules**.

### The Warning

```
[Stream] CoolProp HEOS does not support the binary interaction matrix for
this 16-component mixture.
  -> Falling back to PURE-COMPONENT calculations only.
  -> Mixture properties (density, enthalpy, cp, etc.) will be estimated via
     IDEAL MIXING rules.
  -> For exact mixture EOS, use ThermoBackend.REFPROP or reduce the component
     list.
```

### Ideal Mixing Rules

When the full mixture EOS is unavailable, `Stream` evaluates every supported
property from the pure-component states at the stream $P$ and $T$, then combines
them according to the property type:

#### 1. Molar properties — mole-fraction weighted average

For properties that are naturally **per mole** (e.g. molar enthalpy, molar heat
capacity, molar density):

$$
\phi_{\text{mix}} = \sum_i x_i \, \phi_i^{\text{pure}}
$$

where $x_i$ is the mole fraction of component $i$.

**Properties computed this way:**
- `density_molar` $[\text{mol}/\text{m}^3]$
- `enthalpy_molar` $[\text{J}/\text{mol}]$
- `entropy_molar` $[\text{J}/\text{mol}\cdot\text{K}]$
- `cp_molar`, `cv_molar` $[\text{J}/\text{mol}\cdot\text{K}]$
- `internal_energy_molar`, `gibbs_molar` $[\text{J}/\text{mol}]$

#### 2. Specific (mass) properties — mass-fraction weighted average

For properties that are naturally **per unit mass** (e.g. specific enthalpy,
specific heat capacity, mass density), the weighting uses mass fractions $w_i$:

$$
w_i = \frac{x_i \, M_i}{M_{\text{mix}}}
$$

$$
\phi_{\text{mix}} = \sum_i w_i \, \phi_i^{\text{pure}}
$$

where $M_i$ is the pure-component molar mass and $M_{\text{mix}}$ is the
mixture molar mass.

**Properties computed this way:**
- `density_mass` $[\text{kg}/\text{m}^3]$
- `enthalpy_mass` $[\text{J}/\text{kg}]$
- `entropy_mass` $[\text{J}/\text{kg}\cdot\text{K}]$
- `cp_mass`, `cv_mass` $[\text{J}/\text{kg}\cdot\text{K}]$
- `internal_energy_mass`, `gibbs_mass` $[\text{J}/\text{kg}]$

#### 3. Viscosity — mole-fraction weighted average with NaN handling

Some fluids (e.g. `CarbonylSulfide`, `HydrogenSulfide`) lack transport models
in CoolProp HEOS. Their pure-component viscosities are stored as `NaN`.
The mixture viscosity is computed by **ignoring the NaN components** and
re-normalising the weight over the valid subset:

$$
\mu_{\text{mix}} = \frac{\sum_i x_i \, \mu_i}{\sum_i x_i \, \mathbb{1}_{[\mu_i \neq \text{NaN}]}}
$$

If **no** component has a valid viscosity, the mixture viscosity returns `NaN`.

**Downstream equipment models** (e.g. membrane simulators using the
Herning–Zipperer correlation) should sanitise the `component_viscosities` array
before passing it to local mixture correlations:

```python
mu = feed.component_viscosities.copy()
mu[~np.isfinite(mu)] = 1e-5   # default gas viscosity [Pa·s]
```

#### 4. Unavailable properties

The following properties require mixture-specific models that cannot be
reconstructed from pure-component data alone. In fallback mode they return
`NaN`:

- `conductivity` $[\text{W}/\text{m}\cdot\text{K}]$
- `prandtl` $[-]$
- `speed_of_sound` $[\text{m}/\text{s}]$
- `surface_tension` $[\text{N}/\text{m}]$

### Accuracy Note

The ideal mixing fallback is **sufficient for reporting, initial guesses, and
process simulation where the exact EOS is not critical**. It is **not**
sufficient for:
- High-pressure dew-point calculations near the phase boundary
- Dense-phase property prediction
- Custody-transfer metering

For those applications, use `ThermoBackend.REFPROP`.

---

## Modifying the State

Every setter refreshes the internal thermodynamic state and the property cache
automatically.

```python
# Change pressure and temperature simultaneously
feed.set_PT(P=30e5, T=350.0)

# Change only pressure
feed.set_P(20e5)

# Change only temperature
feed.set_T(400.0)

# Change composition (molar mass and flows are recalculated automatically)
feed.set_composition({"Methane": 0.95, "Ethane": 0.05})

# Change the flow specification
feed.set_mass_flow(50.0)   # kg/s

# Batch update
feed.update(P=25e5, T=320.0, composition={"Water": 1.0})
```

---

## Cloning Streams

Cloning is a fundamental operation in process simulation. It lets you create
outlet streams from an inlet without manual reconstruction.

```python
feed = Stream(...)

retentate = feed.clone()
permeate  = feed.clone()

retentate.set_PT(P=30e5, T=350.0)
permeate.set_composition({"Methane": 0.99, "Ethane": 0.01})
```

Each clone owns an independent `AbstractState` instance. Modifying one never
affects the other.

> **Note:** `copy.deepcopy()` does **not** work on `Stream` because CoolProp's
> `AbstractState` is a C++ object without a Python `__reduce__`. Always use
> `stream.clone()`.

---

## Serialization

Streams can be serialized to plain dictionaries (JSON-ready) and reconstructed
deterministically.

```python
# To dictionary
data = feed.to_dict()
# {
#     "composition": {"Methane": 0.9067, ...},
#     "P": 5000000.0,
#     "T": 300.0,
#     "mass_flow": 18.234,
#     "molar_flow": 1000.0,
#     "backend": "HEOS",
#     "independent_flow": "molar"
# }

# From dictionary
restored = Stream.from_dict(data)
assert restored.cp_mass == feed.cp_mass
```

The `independent_flow` field guarantees that `from_dict()` knows which flow was
the original user input, ensuring bit-perfect reconstruction.

---

## Unit Conversions

The package includes a lightweight, extensible unit conversion module. It is
intentionally minimal today but structured to grow.

```python
from stream.units import Pressure, Temperature, MassFlow, MolarFlow

# Pressure
p_pa = Pressure.to_pa(50, "bar")          # 5_000_000.0
p_bar = Pressure.from_pa(5e6, "bar")      # 50.0

# Temperature
t_k = Temperature.to_k(25, "C")           # 298.15
t_c = Temperature.from_k(300, "C")        # 26.85

# Flow
m_kgs = MassFlow.to_kg_s(180, "kg/h")     # 0.05
n_mols = MolarFlow.to_mol_s(1, "kmol/s")  # 1000.0
```

Supported families:
- **Pressure:** Pa, kPa, MPa, bar, mbar, atm, psi, torr
- **Temperature:** K, °C, °F, °R
- **Mass flow:** kg/s, g/s, kg/h, lb/s, lb/h
- **Molar flow:** mol/s, kmol/s, kmol/h, lbmol/s

---

## Package Structure

```
stream/
├── __init__.py         # Public API exports
├── stream.py           # Stream class (core)
├── thermo_backend.py   # ThermoBackend enum
├── exceptions.py       # StreamError hierarchy
├── units.py            # Unit conversion utilities
└── constants.py        # Physical constants (R, STP)
```

This separation is deliberate. It keeps the core class focused while leaving
room for future growth: pandas integration, JSON schemas, database adapters,
export formats, etc.

---

## Available Properties

All properties are read-only, cached, and returned in SI units.

| Property | Unit | Description |
|----------|------|-------------|
| `viscosity` | Pa·s | Dynamic viscosity |
| `conductivity` | W/m·K | Thermal conductivity |
| `surface_tension` | N/m | Surface tension |
| `prandtl` | — | Prandtl number |
| `speed_of_sound` | m/s | Speed of sound |
| `density_mass` | kg/m³ | Mass density |
| `density_molar` | mol/m³ | Molar density |
| `enthalpy_mass` | J/kg | Specific enthalpy |
| `enthalpy_molar` | J/mol | Molar enthalpy |
| `entropy_mass` | J/kg·K | Specific entropy |
| `entropy_molar` | J/mol·K | Molar entropy |
| `internal_energy_mass` | J/kg | Specific internal energy |
| `internal_energy_molar` | J/mol | Molar internal energy |
| `gibbs_mass` | J/kg | Specific Gibbs free energy |
| `gibbs_molar` | J/mol | Molar Gibbs free energy |
| `cp_mass` | J/kg·K | Specific heat capacity at constant pressure |
| `cp_molar` | J/mol·K | Molar heat capacity at constant pressure |
| `cv_mass` | J/kg·K | Specific heat capacity at constant volume |
| `cv_molar` | J/mol·K | Molar heat capacity at constant volume |
| `molar_mass` | kg/mol | Mixture molar mass |

### Extensive (flow-based) properties

| Property | Unit | Description |
|----------|------|-------------|
| `total_enthalpy_mass` | W | Total enthalpy flow (mass basis) |
| `total_enthalpy_molar` | W | Total enthalpy flow (molar basis) |
| `total_cp_mass` | W/K | Total heat capacity flow (mass basis) |
| `total_cp_molar` | W/K | Total heat capacity flow (molar basis) |

### Pure-component properties

| Property | Unit | Description |
|----------|------|-------------|
| `component_molar_masses` | kg/mol | Array of pure-component molar masses |
| `component_viscosities` | Pa·s | Array of pure-component viscosities at stream $P,T$ |

---

## Exceptions

All exceptions inherit from `StreamError`.

| Exception | Raised when... |
|-----------|----------------|
| `CompositionError` | Composition is empty or contains unknown fluids |
| `FlowSpecificationError` | Both or neither of `mass_flow`/`molar_flow` are given |
| `BackendError` | CoolProp cannot instantiate the requested backend |

This hierarchy allows upstream code to catch all stream-related errors with a
single `except StreamError`.

---

## Listing Available Fluids

```python
from stream import Stream

fluids = Stream.list_fluids()
print(fluids[:5])
# ['1-Butene', 'Acetone', 'Air', 'Ammonia', 'Argon']
```

---

## Backends

| Backend | Description |
|---------|-------------|
| `ThermoBackend.HEOS` | Full Helmholtz equation of state (default, most accurate for supported mixtures) |
| `ThermoBackend.REFPROP` | REFPROP backend (requires installation; supports all natural-gas mixtures) |
| `ThermoBackend.TTSE` | TTSE tabulated interpolation (faster) |
| `ThermoBackend.BICUBIC` | Bicubic tabulated interpolation (faster) |

### When to use REFPROP

- Mixtures with $>5$ components
- Presence of `H2S`, `COS`, water, or heavy hydrocarbons ($C_7+$)
- High-pressure dense-phase calculations
- Custody-transfer or regulatory compliance

### When HEOS + ideal fallback is enough

- Process simulation where the exact EOS is not the binding constraint
- Quick screening and sensitivity studies
- Cases where only pure-component viscosities and molar masses are consumed by
downstream equipment models (e.g. membrane modules with local HZ correlations)

---

## Why not `get_property()`?

The package intentionally does **not** provide a generic `get_property("name")`
method. Every supported property is exposed as a typed, documented `@property`.
This eliminates string-lookup errors, enables IDE autocompletion, and makes the
API self-describing.

---

## License

MIT

---

## Acknowledgements

Built on top of [CoolProp](http://www.coolprop.org/), an open-source
thermophysical property library.
