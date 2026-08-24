# Common Library

> Shared infrastructure for the HFM (Hollow-Fiber Membrane) process simulator.  
> This package contains thermodynamic, physical-property, and flowsheet-engine modules used by all case studies and equipment models.
---
## ✅ Library Installation
Fast installation. From this folder in terminal write: 

```python
python pip install -e .
```

for installation in edit mode 


## 📁 Package Structure

```
src/
└── Common/
    ├── HEX_Calculations/
    │   ├── Calculations_HEX_heatload.py
    │   ├── Calculations_HEX_LMTD.py
    │   └── README.md              ← Heat-exchanger design utilities
    │
    ├── Membrane_Properties/
    │   └── Permeance/
    │       ├── Membrane_Permeance.py
    │       └── README.md          ← Membrane permeance data container
    │
    ├── Physical_Properties/
    │   └── Viscosity/
    │       ├── Mixture_Properties.py
    │       └── README.md          ← Gas-mixture viscosity calculator
    │
    ├── Process_Simulator/
    │   ├── flowsheet.py
    │   ├── unit_operation.py
    │   ├── base_equipment.py
    │   ├── port.py
    │   ├── solvers.py
    │   └── README.md              ← Flowsheet engine & sequential solver
    │
    ├── Stream/
    │   ├── stream.py
    │   ├── thermo_backend.py
    │   ├── exceptions.py
    │   ├── units.py
    │   ├── constants.py
    │   └── README.md              ← Thermodynamic state representation
    │
    └── Unit_Operation/
        ├── Compressor.py
        └── README.md              ← Isentropic compressor unit
```

---

## 🏗️ Architecture Overview

The `Common` library is organised into six sub-packages, each with a single, well-defined responsibility:

| Sub-package | Role | Who uses it |
|-------------|------|-------------|
| **`HEX_Calculations`** | Heat-exchanger sizing utilities (heat load, LMTD) | Equipment models and case studies that need HEX design | 
| **`Stream`** | Thermodynamic state representation (P, T, composition, derived properties) | Every unit operation, solver, and case study |
| **`Process_Simulator`** | Flowsheet topology, unit-operation base classes, and sequential solver | Case-study runner (`Run_Case_Study.py`) and custom flowsheets |
| **`Unit_Operation`** | Concrete equipment models (compressor, pump, etc.) | Flowsheets that need process units |
| **`Membrane_Properties`** | Membrane-specific data containers (permeance, permeability) | HFM membrane simulator and case studies |
| **`Physical_Properties`** | Physical-property calculators (viscosity, etc.) | HFM simulator, local transport correlations |

**Design rule:** downstream code (case studies, equipment models) imports from `Common` but never the reverse. `Common` has zero knowledge of `Simulator_HFM` or `Case_Study_Collection`.

---

## 🔗 Module Dependencies

```
                    ┌─────────────────┐
                    │   Case Studies  │
                    │  (user scripts) │
                    └────────┬────────┘
                             │ imports
                             ▼
┌───────────────┐    ┌───────────────────┐    ┌─────────────────────┐
│   Stream      │◄──►│ Process_Simulator │◄──►│  Unit_Operation     │
│ (thermo state)│    │ (flowsheet engine)│    │ (Compressor, etc.)  │
└───────────────┘    └───────────────────┘    └─────────────────────┘

```

- **`Stream`** is the foundation. Every unit operation reads from and writes to `Stream` objects.
- **`Process_Simulator`** orchestrates units and streams but contains zero thermodynamics.
- **`Unit_Operation`** implements physics (compression, separation, etc.) using `Stream` properties.
- **`HEX_Calculations`** provides sizing equations for heat-exchanger equipment (heat load and LMTD).
- **`Membrane_Properties`** and **`Physical_Properties`** provide specialised data and calculations consumed by the HFM simulator.

---

## 📦 Sub-packages

### 1. `HEX_Calculations` — Heat-Exchanger Design Utilities

Pure-math utilities for preliminary heat-exchanger sizing and thermal analysis.

**Key functions:**

| Function | File | Purpose |
|----------|------|---------|
| `HEX_heat_load` | `Calculations_HEX_heatload.py` | Computes exchanged heat load from mass flow, specific heat, and temperature change. |
| `HEX_lmtd` | `Calculations_HEX_LMTD.py` | Computes the Log Mean Temperature Difference (LMTD) for counter-current or co-current HEX arrangements. |

**Quick example:**

```python
from Common.HEX_Calculations.Calculations_HEX_heatload import HEX_heat_load
from Common.HEX_Calculations.Calculations_HEX_LMTD import HEX_lmtd

# Heat load
Q = HEX_heat_load(
    mass_flow_rate=2.5,      # kg/s
    specific_heat=4180,      # J/(kg·K)
    inlet_temperature=350,   # K
    outlet_temperature=320,  # K
)
print(f"Heat load: {Q/1000:.2f} kW")

# LMTD
lmtd = HEX_lmtd(
    Thi=350, Tho=330,   # Hot side (K)
    Tci=300, Tco=320,   # Cold side (K)
)
print(f"LMTD: {lmtd:.2f} K")
```

📄 [Full documentation → `src/Common/HEX_Calculations/README.md`](src/Common/HEX_Calculations/README.md)

---

### 2. `Stream` — Thermodynamic State

A backend-agnostic thermodynamic state representation backed by CoolProp.

**Key class:** `Stream`

- Stores composition, pressure, temperature, and flow.
- Exposes derived properties: density, enthalpy, viscosity, heat capacity, Prandtl number, etc.
- Supports CoolProp backends: `HEOS`, `REFPROP`, `TTSE`, `BICUBIC`.
- Automatic fallback to **ideal mixing rules** when CoolProp HEOS cannot build the full mixture EOS (common for large natural-gas mixtures).
- Immutable properties, mutable state via `set_PT()`, `set_composition()`, `update()`, `clone()`.
- JSON-serialisable via `to_dict()` / `from_dict()`.

**Quick example:**

```python
from Common.Stream.stream import Stream, ThermoBackend

feed = Stream(
    composition={"CO2": 0.5, "Propane": 0.5},
    P=10e5,
    T=313.0,
    molar_flow=0.0033,
    backend=ThermoBackend.HEOS,
)

print(feed.density_mass)   # kg/m³
print(feed.viscosity)      # Pa·s
print(feed.cp_molar)       # J/(mol·K)
```

📄 [Full documentation → `src/Common/Stream/README.md`](src/Common/Stream/README.md)

---

### 3. `Process_Simulator` — Flowsheet Engine

A lightweight, modular framework for building and solving chemical process flowsheets.

**Key classes:**

| Class | File | Purpose |
|-------|------|---------|
| `Flowsheet` | `flowsheet.py` | Owns units, streams, and connections. Pure topology, zero physics. |
| `UnitOperation` | `unit_operation.py` | Abstract base for equipment with input/output ports and a `solve()` contract. |
| `BaseEquipment` | `base_equipment.py` | Common metadata, status, diagnostics for every piece of equipment. |
| `Port` / `PortDirection` | `port.py` | Typed connection points between units and streams. |
| `SequentialSolver` | `solvers.py` | Topological sort (Kahn's algorithm) + sequential modular execution. |

**Design principles:**
1. `Flowsheet` knows topology, not physics.
2. `UnitOperation` knows physics, not topology.
3. `Solver` knows order, not physics.
4. `Port` connections are validated at wiring time (no double connections, direction enforced).

**Quick example:**

```python
from Common.Process_Simulator import Flowsheet, SequentialSolver
from Common.Unit_Operation.Compressor import Compressor
from Common.Stream.stream import Stream, ThermoBackend

# Build flowsheet
fs = Flowsheet("Demo")
fs.add_stream("Feed", Stream(...))
fs.add_stream("Product", Stream(...))
fs.add_unit("COMP1", Compressor(name="COMP1", P_out=5e5))

fs.connect(stream="Feed", destination=("COMP1", "inlet"))
fs.connect(source=("COMP1", "outlet"), stream="Product")

# Solve
solver = SequentialSolver(fs)
solver.solve()
print(fs.report())
```

📄 [Full documentation → `src/Common/Process_Simulator/README.md`](src/Common/Process_Simulator/README.md)

---

### 4. `Unit_Operation` — Equipment Models

Concrete process units that inherit from `UnitOperation` and implement `solve()`.

**Current equipment:**

| Equipment | File | Description |
|-----------|------|-------------|
| `Compressor` | `Compressor.py` | Simple isentropic compressor with efficiency correction. Computes discharge T and power. |

**Pattern for adding new units:**

```python
from Common.Process_Simulator import UnitOperation, PortDirection

class MyUnit(UnitOperation):
    def __init__(self, name: str, ...):
        super().__init__(name, tag="U-101", description="My unit")
        self.add_port("feed", PortDirection.INPUT)
        self.add_port("product", PortDirection.OUTPUT)

    def solve(self) -> None:
        inlet = self.feed.stream
        outlet = self.product.stream
        # ... physics ...
        outlet.update(P=..., T=..., composition=...)
```

📄 [Full documentation → `src/Common/Unit_Operation/README.md`](src/Common/Unit_Operation/README.md)

---

### 5. `Membrane_Properties/Permeance` — Membrane Transport Data

Immutable data container for membrane permeance.

**Key class:** `MembranePermeance`

- Two input modes: direct permeance `[mol/(m²·Pa·s)]` or permeability + thickness (`Q = P / δ`).
- Component-indexed lookup: `component_permeance("CO2")`.
- Used by the HFM mass-balance solver to compute trans-membrane molar flux.

**Quick example:**

```python
from Common.Membrane_Properties.Permeance.Membrane_Permeance import MembranePermeance

mp = MembranePermeance(
    components=["CO2", "CH4", "N2"],
    permeance=[1.0e-10, 5.0e-12, 1.0e-12]
)
print(mp.component_permeance("CO2"))   # 1.0e-10
mp.summary()
```

📄 [Full documentation → `src/Common/Membrane_Properties/Permeance/README.md`](src/Common/Membrane_Properties/Permeance/README.md)

---

### 6. `Physical_Properties/Viscosity` — Mixture Viscosity

Gas-mixture viscosity calculator with two calculation routes.

**Key class:** `MixtureProperties`

| Route | Speed | Inputs | Best for |
|-------|-------|--------|----------|
| **Herning–Zipperer (HZ)** | Very fast | `MU` (pure viscosities), `M` (molar masses) | Iterative solvers, pressure-drop loops |
| **CoolProp** | Slow (PT flash per call) | `T`, `P` | Validation, cross-check |

**Quick example:**

```python
from Common.Physical_Properties.Viscosity.Mixture_Properties import MixtureProperties

props = MixtureProperties(
    components=["CO2", "CH4", "N2"],
    MU=[1.49e-5, 1.10e-5, 1.78e-5],
    M=[44.01, 16.04, 28.01],
    method="HZ"
)
mu = props.viscosity(mol_fractions=[0.5, 0.4, 0.1])   # Pa·s
```

📄 [Full documentation → `src/Common/Physical_Properties/Viscosity/README.md`](src/Common/Physical_Properties/Viscosity/README.md)

---

## 🚀 Quick Start: Building a Complete Flowsheet

This example ties all sub-packages together: a feed stream passes through a compressor and the result is inspected.

```python
import numpy as np
from Common.Stream.stream import Stream, ThermoBackend
from Common.Process_Simulator import Flowsheet, SequentialSolver
from Common.Unit_Operation.Compressor import Compressor

# 1. Create streams
feed = Stream(
    composition={"CO2": 0.5, "Propane": 0.5},
    P=1e5,
    T=313.0,
    molar_flow=0.0033,
    backend=ThermoBackend.HEOS,
)
discharge = feed.clone()

# 2. Build flowsheet
fs = Flowsheet(name="Compression Demo")
fs.add_stream("Feed", feed)
fs.add_stream("Discharge", discharge)
fs.add_unit("COMP1", Compressor(name="COMP1", P_out=5e5, efficiency=0.75))

fs.connect(stream="Feed", destination=("COMP1", "inlet"))
fs.connect(source=("COMP1", "outlet"), stream="Discharge")

# 3. Solve
solver = SequentialSolver(fs)
solver.solve()

# 4. Inspect
print(f"Inlet:  {feed.P/1e5:.2f} bar, {feed.T:.2f} K")
print(f"Outlet: {discharge.P/1e5:.2f} bar, {discharge.T:.2f} K")
print(f"Power:  {fs.units['COMP1'].results['work_W']:.3f} W")
```

---

## 🧪 Testing

Each sub-package should be tested independently:

| Sub-package | Suggested test focus |
|-------------|----------------------|
| `HEX_Calculations` | Sign convention (Q positive when fluid cools), LMTD limit cases, zero/negative ΔT error handling |
| `Stream` | Property consistency, clone independence, serialisation round-trip, fallback mode |
| `Process_Simulator` | Topological sort correctness, cycle detection, port validation |
| `Unit_Operation` | Mass/energy balance closure, outlet stream correctness |
| `Membrane_Properties` | Permeance arithmetic, index lookup, immutability |
| `Physical_Properties` | HZ vs CoolProp agreement, degenerate composition handling |

---

## 📝 Adding a New Sub-package or Module

1. Create the folder under `src/Common/`.
2. Add an `__init__.py` that exports the public API.
3. Write a `README.md` documenting the public classes and their contracts.
4. Ensure the new module imports **only** from `Common` (or third-party libraries like `numpy`, `CoolProp`).
5. Update this `README.md` to list the new sub-package in the structure and dependency diagrams.

---

## 📄 License

*Under construction*

## 👤 Contact

- **João Victor Abdala Tupinambá**
- **Diego Gabriel Oliva**
- **Argimiro Resende Secchi**
- **M. J. Bagajewicz**