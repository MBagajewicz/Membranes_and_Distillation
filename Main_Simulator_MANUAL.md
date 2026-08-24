# Process Simulator — Main Simulator & Case Studies Manual

HELP ONLINE
https://chatgpt.com/g/g-6a771ffe34f0819195fc4046fbafda6c-optiprocess-framework

This repository contains a flexible, modular framework for building and solving process flowsheets composed of multiple unit operations, including **Hollow Fiber Membranes (HFM)**, **Compressors**, **Shell-and-Tube Heat Exchangers (STHE)**, and future equipment implemented through the common `UnitOperation` architecture.

The entry point is **`Main_Simulator.py`**.

All process-specific configurations are defined in Python case-study files under:

```text
Simulator_Case_Studies/
```

The framework is designed so that:

- `STREAM_CONFIGS` defines the physical inlet streams of the flowsheet.
- `EQUIPMENT_CONFIG` defines the equipment and their parameters.
- `CONNECTIONS` defines the flowsheet topology.
- `COMMON_PARAMS` contains shared HFM parameters.
- There is **no global `FEED_CONFIG`**. A flowsheet may have one inlet stream or many independent inlet streams.

---

## Repository Structure

```text
root/
├── Main_Simulator.py                  # Main entry point
├── Simulator_Case_Studies/            # Process configuration files
│   ├── HFM_Case_Study_1.py
│   ├── HFM_Case_Study_2.py
│   ├── HFM_Case_Study_Two_Membranes.py
│   ├── HFM_Compresor_Case_Study_Two_Membranes.py
│   ├── STHE_Case_Study_1.py
│   └── ...
└── Main_Simulator_MANUAL.md           # This manual
```

> **Important:** `Main_Simulator.py` dynamically imports the selected case-study module. To create a new case, add a `.py` file under `Simulator_Case_Studies/`; the runner itself normally does not need to be modified.

---

# Quick Start

## 1. Select a case study

Open `Main_Simulator.py` and set:

```python
CASE_STUDY = "HFM_Case_Study_1"
```

The value is the Python module name **without** `.py`.

For example:

```python
CASE_STUDY = "STHE_Case_Study_1"
```

runs:

```text
Simulator_Case_Studies/STHE_Case_Study_1.py
```

## 2. Run the simulator

From the project root:

```bash
python Main_Simulator.py
```

The simulator will:

1. Import the selected case-study configuration.
2. Read `STREAM_CONFIGS`, `EQUIPMENT_CONFIG`, and `CONNECTIONS`.
3. Create all explicitly configured streams.
4. Create required intermediate/unit-output stream objects before building equipment.
5. Build the configured unit operations.
6. Apply `CONNECTIONS` to bind streams to unit-operation ports.
7. Solve the resulting flowsheet.
8. Print stream and unit-operation results.
9. Export HFM-specific axial results when applicable.

> **Important:** The order of entries in `EQUIPMENT_CONFIG` is not used as the definition of process connectivity. Connectivity is determined by `CONNECTIONS`.

---

# Creating a New Case Study

A case-study module should define the following top-level variables:

| Variable | Required | Purpose |
|---|---:|---|
| `STREAM_CONFIGS` | Yes | Defines the physical streams used by the flowsheet |
| `COMMON_PARAMS` | Yes for HFM cases | Default HFM parameters shared by units |
| `EQUIPMENT_CONFIG` | Yes | Defines the unit operations |
| `CONNECTIONS` | Yes | Defines the flowsheet topology |

## Important architectural rule

**Do not define `FEED_CONFIG`.**

The previous framework used a single global `FEED_CONFIG`. That design was ambiguous for equipment such as STHE, which can have multiple independent inlet streams.

The new architecture treats every stream explicitly:

```text
STREAM_CONFIGS
      |
      v
Flowsheet streams
      |
      v
CONNECTIONS
      |
      v
Unit-operation ports
```

A simple HFM flowsheet may still have only one inlet stream:

```text
Feed --> HFM1 --> Retentate
              \
               --> Permeate
```

while an STHE can have two:

```text
HotFeed  --> STHE1 --> HotProduct
ColdFeed --> STHE1 --> ColdProduct
```

Both are represented using the same framework concepts.

---

# 1. `STREAM_CONFIGS`

`STREAM_CONFIGS` is the authoritative definition of configured process streams.

Example:

```python
from Common.Stream.stream import ThermoBackend

STREAM_CONFIGS = {
    "Feed": {
        "composition": {
            "CO2": 0.50,
            "Propane": 0.50,
        },
        "P": 10e5,                         # Pa
        "T": 313.0,                        # K
        "molar_flow": 0.0033,              # mol/s
        "backend": ThermoBackend.HEOS,
    }
}
```

A mass-flow specification can be used instead:

```python
STREAM_CONFIGS = {
    "Feed": {
        "composition": {
            "CO2": 0.50,
            "Propane": 0.50,
        },
        "P": 10e5,
        "T": 313.0,
        "mass_flow": 0.10,                 # kg/s
        "backend": ThermoBackend.HEOS,
    }
}
```

Use either `molar_flow` or `mass_flow` for a stream.

## Multiple inlet streams

Multiple independent feeds are fully supported:

```python
STREAM_CONFIGS = {
    "HotFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 393.15,
        "mass_flow": 0.50,
        "backend": ThermoBackend.HEOS,
    },

    "ColdFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 293.15,
        "mass_flow": 0.50,
        "backend": ThermoBackend.HEOS,
    },
}
```

This is the recommended pattern for STHE and any future multi-inlet equipment.

## Stream names

Stream names are identifiers used by `CONNECTIONS`.

For example:

```python
"HotFeed"
"ColdFeed"
"HotProduct"
"ColdProduct"
```

Names should be unique within a case study.

---

# 2. `COMMON_PARAMS`

`COMMON_PARAMS` contains default parameters shared by HFM units.

For a case containing only STHE, it can simply be:

```python
COMMON_PARAMS = {}
```

For HFM cases, a typical configuration is:

```python
COMMON_PARAMS = {
    # --- Physics & solver ---
    "PressureDrop": True,
    "EnergyBalance": True,
    "UseFugacity": True,
    "PRet": None,
    "ForceGasPhase": True,
    "DewTemperatureCalculation": False,

    # --- Component properties ---
    "M": np.array([0.044009, 0.044097]),
    "MU": np.array([1.48e-5, 8.5e-6]),

    # --- Membrane permeance ---
    "Q": np.array([6.8e-8, 7.71e-11]),

    # --- HFM geometry ---
    "DiamFiber_o": 4.15e-4,
    "DiamFiber_i": 3.41e-4,
    "FiberLengthInElement": 0.2,
    "NumberOfElementsPerTube": 1,
    "NTubes": 1,
    "N": 3380,
    "Void_Frac": 0.625,
    "DiamShell": 0.0394,

    # --- Numerics ---
    "Discretizations": 20,
    "LeastSquareSolverTolerance": 1e-6,
    "MassBalanceLoopIterationTolerance": 1e-6,
    "NumberOfIterationsInLoop": 150,
    "EnergyBalanceLoopIterationTolerance": 1e-2,
    "LeastSquaresVerbose": 0,

    # --- Heat transfer ---
    "HeatTransferCoef": 4,
    "MembranePolymerThermalConductivity": 0.2,
    "MembranePorosity": 0.5,

    # --- Thermodynamic / transport ---
    "EnergyBalanceStateEquation": "PR",
    "ViscosityCalculationMethod": "HZ",
    "PPerm": 1e5,
}
```

`EQUIPMENT_CONFIG` may override applicable HFM parameters for an individual unit.

---

# 3. `EQUIPMENT_CONFIG`

`EQUIPMENT_CONFIG` is a list of dictionaries.

Each dictionary defines one unit operation.

Every unit must have a unique `"name"`.

---

## Hollow Fiber Membrane (`"type": "HFM"`)

Example:

```python
EQUIPMENT_CONFIG = [
    {
        "type": "HFM",
        "name": "HFM1",
        "description": "CO2 removal membrane",

        "DiamShell": 0.0394,
        "FiberLengthInElement": 0.2,
        "N": 3380,
        "PPerm": 1e5,
    }
]
```

The HFM-specific parameters are merged with `COMMON_PARAMS`.

The inlet stream is determined by `CONNECTIONS`; it is not stored globally in `FEED_CONFIG`.

---

## Compressor (`"type": "Compressor"`)

Example:

```python
{
    "type": "Compressor",
    "name": "COMP1",
    "description": "Intermediate recompression",
    "P_out": 5e5,
    "efficiency": 0.75,
    "gamma": 1.3,
}
```

The compressor inlet and outlet are defined through `CONNECTIONS`.

---

## Shell-and-Tube Heat Exchanger (`"type": "STHE"`)

Example:

```python
{
    "type": "STHE",
    "name": "STHE1",
    "tag": "E-101",
    "description": "Single shell-and-tube heat exchanger",

    "geometry": {
        "shell": {
            "diameter": 0.50,
            "fouling_factor": 1.0e-4,
        },
        "tubes": {
            "length": 5.0,
            "outside_diameter": 0.025,
            "inside_diameter": 0.021,
            "pitch_ratio": 1.25,
            "layout": 1,
            "passes": 2,
            "wall_conductivity": 16.0,
            "fouling_factor": 1.0e-4,
        },
        "baffles": {
            "number": 8,
            "cut": 0.25,
            "sealing_strips": 1,
        },
    },

    "correlations": {
        "tube_method": "Gnielinski",
        "shell_method": "Bell",
        "Xp": 0.9,
    },
}
```

STHE does not use `COMMON_PARAMS` for its physical model. Its configuration is kept local to the equipment entry.

An STHE has two independent inlet ports and two outlet ports:

| Equipment | Ports |
|---|---|
| STHE | `"hot_in"`, `"hot_out"`, `"cold_in"`, `"cold_out"` |

---

# 4. `CONNECTIONS`

`CONNECTIONS` defines the topology of the flowsheet.

It is the authoritative description of how streams connect to unit-operation ports.

Two forms are used:

| Syntax | Meaning |
|---|---|
| `{"from": "StreamName", "to": ("UnitName", "port")}` | Stream → unit inlet |
| `{"from": ("UnitName", "port"), "to": "StreamName"}` | Unit outlet → stream |

The same stream can subsequently be connected to another unit.

---

## HFM ports

| Equipment | Ports |
|---|---|
| HFM | `"feed"`, `"retentate"`, `"permeate"` |

Example:

```python
CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate"},
    {"from": ("HFM1", "permeate"), "to": "Permeate"},
]
```

---

## Compressor ports

| Equipment | Ports |
|---|---|
| Compressor | `"inlet"`, `"outlet"` |

Example:

```python
CONNECTIONS = [
    {"from": "Feed", "to": ("COMP1", "inlet")},
    {"from": ("COMP1", "outlet"), "to": "CompressedFeed"},
]
```

---

## STHE ports

| Equipment | Ports |
|---|---|
| STHE | `"hot_in"`, `"hot_out"`, `"cold_in"`, `"cold_out"` |

Example:

```python
CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},

    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
```

This is the canonical pattern for a two-stream STHE case.

---

# Example: Single HFM

A complete minimal HFM case can be structured as:

```python
from Common.Stream.stream import ThermoBackend

STREAM_CONFIGS = {
    "Feed": {
        "composition": {
            "CO2": 0.50,
            "Propane": 0.50,
        },
        "P": 10e5,
        "T": 313.0,
        "molar_flow": 0.0033,
        "backend": ThermoBackend.HEOS,
    }
}

COMMON_PARAMS = {
    # HFM parameters...
}

EQUIPMENT_CONFIG = [
    {
        "type": "HFM",
        "name": "HFM1",
        "PPerm": 1e5,
    }
]

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate"},
    {"from": ("HFM1", "permeate"), "to": "Permeate"},
]
```

There is no `FEED_CONFIG`.

---

# Example: Two HFM Units in Series

```text
Feed
  |
  v
HFM1
 /  \
Ret1 Permeate1
 |
 v
HFM2
 /  \
Ret2 Permeate2
```

Configuration:

```python
CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},

    {"from": ("HFM1", "retentate"), "to": "Feed_HFM2"},
    {"from": ("HFM1", "permeate"), "to": "Permeate1"},

    {"from": "Feed_HFM2", "to": ("HFM2", "feed")},

    {"from": ("HFM2", "retentate"), "to": "Retentate2"},
    {"from": ("HFM2", "permeate"), "to": "Permeate2"},
]
```

> Ensure that each downstream HFM has an appropriate permeate pressure (`PPerm`) so that the membrane has a physically meaningful driving force.

---

# Example: HFM → Compressor → HFM

```text
Feed
  |
  v
HFM1
  |
  | permeate
  v
COMP1
  |
  v
HFM2
```

```python
CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},

    {"from": ("HFM1", "retentate"), "to": "Retentate1"},
    {"from": ("HFM1", "permeate"), "to": "Permeate1"},

    {"from": "Permeate1", "to": ("COMP1", "inlet")},
    {"from": ("COMP1", "outlet"), "to": "CompressedPermeate"},

    {"from": "CompressedPermeate", "to": ("HFM2", "feed")},

    {"from": ("HFM2", "retentate"), "to": "Retentate2"},
    {"from": ("HFM2", "permeate"), "to": "Permeate2"},
]
```

---

# Example: Single STHE

A complete two-feed STHE case:

```python
from Common.Stream.stream import ThermoBackend

STREAM_CONFIGS = {
    "HotFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 393.15,
        "mass_flow": 0.50,
        "backend": ThermoBackend.HEOS,
    },

    "ColdFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 293.15,
        "mass_flow": 0.50,
        "backend": ThermoBackend.HEOS,
    },
}

COMMON_PARAMS = {}

EQUIPMENT_CONFIG = [
    {
        "type": "STHE",
        "name": "STHE1",
        "tag": "E-101",
        "description": "Single shell-and-tube heat exchanger",

        "geometry": {
            "shell": {
                "diameter": 0.50,
                "fouling_factor": 1.0e-4,
            },
            "tubes": {
                "length": 5.0,
                "outside_diameter": 0.025,
                "inside_diameter": 0.021,
                "pitch_ratio": 1.25,
                "layout": 1,
                "passes": 2,
                "wall_conductivity": 16.0,
                "fouling_factor": 1.0e-4,
            },
            "baffles": {
                "number": 8,
                "cut": 0.25,
                "sealing_strips": 1,
            },
        },

        "correlations": {
            "tube_method": "Gnielinski",
            "shell_method": "Bell",
            "Xp": 0.9,
        },
    }
]

CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},

    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
```

This demonstrates an important design principle:

> **A case study does not have a single "feed". It has a set of configured streams, and the connections determine which streams are actual inlet streams.**

---

# Flowsheet Construction Lifecycle

`Main_Simulator.py` builds a case in three distinct phases.

```text
Case Study
    |
    +--> STREAM_CONFIGS
    |
    +--> EQUIPMENT_CONFIG
    |
    +--> CONNECTIONS
             |
             v
    1. Create all streams
             |
             v
    2. Create all equipment
             |
             v
    3. Apply all connections
             |
             v
        Solve flowsheet
```

## Phase 1 — Create streams

Every stream explicitly defined in `STREAM_CONFIGS` is created first.

Streams that are not independently configured but appear in `CONNECTIONS` are also created when needed. These include unit-operation outlet streams and intermediate streams.

For example:

```text
HFM1.permeate
      |
      v
Permeate_to_COMP
      |
      v
COMP1.inlet
```

`Permeate_to_COMP` must exist as a stream object before the downstream equipment is built.

For intermediate streams, the simulator can use upstream stream information to initialize the stream object. The upstream unit later updates that same stream object when the flowsheet is solved.

This allows downstream units to be constructed even when their inlet conditions are generated by an upstream unit.

## Phase 2 — Create equipment

After the required stream objects exist, the simulator creates the configured unit operations.

For example:

```text
HFM1
COMP1
HFM2
```

can be created even though `HFM2` is fed by the output of `COMP1`.

The equipment declaration order therefore does not need to be a topological ordering of the process.

## Phase 3 — Apply connections

The entries in `CONNECTIONS` bind stream objects to the named equipment ports.

For:

```python
{"from": "Compressed_to_HFM2", "to": ("HFM2", "feed")}
```

the simulator connects the existing `Compressed_to_HFM2` stream object to the `feed` port of `HFM2`.

For:

```python
{"from": ("COMP1", "outlet"), "to": "Compressed_to_HFM2"}
```

the compressor outlet is associated with that same stream object.

Consequently, when `COMP1` solves and updates its outlet stream, `HFM2` sees the updated state through its connected inlet stream.

## Why this matters

This design supports flowsheets such as:

```text
Feed
  |
  v
HFM1
  |
  | permeate
  v
COMP1
  |
  v
HFM2
```

without requiring a global feed definition or special-case logic for downstream units.

It also supports multi-inlet equipment naturally:

```text
HotFeed  ─────→ STHE1 ─────→ HotProduct
ColdFeed ─────→ STHE1 ─────→ ColdProduct
```

The same stream/port mechanism is used for both cases.

> **Design rule:** `STREAM_CONFIGS` defines independently specified stream states; `CONNECTIONS` defines how streams and equipment ports are related; unit operations update their connected outlet streams during simulation.

---

# How the Framework Interprets Streams

The simulator distinguishes between:

### Configured streams

Defined explicitly in:

```python
STREAM_CONFIGS = {...}
```

These are the streams for which the case study supplies independent initial thermodynamic conditions.

They are normally the external inlet streams of the flowsheet, but a configured stream can be used wherever the case-study topology requires it.

### Unit-operation outlet streams

Created by the flowsheet topology:

```python
{"from": ("HFM1", "retentate"), "to": "Retentate"}
```

or:

```python
{"from": ("STHE1", "hot_out"), "to": "HotProduct"}
```

These streams obtain their state from the upstream unit operation.

### Intermediate streams

An intermediate stream can connect two units:

```text
HFM1 --> Intermediate --> COMP1
```

The intermediate stream is named in `CONNECTIONS`. The simulator creates the stream object before the equipment is built when necessary, so downstream equipment can reference it during construction.

When the upstream unit solves, it updates the connected stream object. The downstream unit then consumes the updated state through its inlet port.

---

# Outputs

## Console Report

After solving, the simulator reports the flowsheet and stream states, including where available:

- Mass flow
- Molar flow
- Temperature
- Pressure
- Density
- Enthalpy
- Viscosity
- Component composition
- Unit-operation results and diagnostics

For STHE, results may include quantities such as:

- Heat duty
- Outlet temperatures
- Overall heat-transfer coefficient
- Effective heat-transfer area
- Effectiveness / NTU-related results
- Shell-side pressure drop
- Tube-side pressure drop

## HFM Excel Output

For HFM units that successfully produce axial simulation results, the simulator exports an Excel file under:

```text
Simulator_Case_Studies/
```

with a name similar to:

```text
HFM_Case_Study_1_HFM1_Results.xlsx
```

The file can contain axial profiles such as:

- Pressure
- Temperature
- Composition
- Flux
- Other HFM solver variables

Compressors and STHEs do not use the HFM axial-profile export mechanism.

---

# Case-Study Checklist

Before running a new case:

- [ ] The file is saved under `Simulator_Case_Studies/`.
- [ ] `CASE_STUDY` matches the filename without `.py`.
- [ ] `STREAM_CONFIGS` is defined.
- [ ] `EQUIPMENT_CONFIG` is defined.
- [ ] `CONNECTIONS` is defined.
- [ ] `COMMON_PARAMS` is defined for HFM cases; use `{}` for cases that do not require shared HFM parameters.
- [ ] **No `FEED_CONFIG` is defined.**
- [ ] Every configured stream has a valid composition.
- [ ] Each stream has `P` and `T`.
- [ ] Each stream has either `mass_flow` or `molar_flow`.
- [ ] The selected thermodynamic backend is valid.
- [ ] Every equipment unit has a unique `"name"`.
- [ ] Every connection references an existing stream or unit port.
- [ ] Every equipment port is connected according to the unit-operation requirements.
- [ ] Do not rely on `EQUIPMENT_CONFIG` ordering to define process sequence; define the sequence through `CONNECTIONS`.
- [ ] HFM component-property arrays have consistent lengths.
- [ ] HFM permeate pressures provide a physically meaningful driving force.
- [ ] STHE hot and cold inlet streams are explicitly defined in `STREAM_CONFIGS`.

---

# Troubleshooting

| Problem | Likely cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Case-study name or package path is incorrect | Check `CASE_STUDY` and the `Simulator_Case_Studies` package |
| Missing `STREAM_CONFIGS` | Case study still uses the old configuration format | Replace `FEED_CONFIG` with explicit `STREAM_CONFIGS` |
| Unknown equipment type | `"type"` is not supported by `Main_Simulator.py` | Check the equipment type name |
| Unknown port | Connection uses an invalid unit port | Check the unit's port table above |
| Stream not found | A connection references an undeclared or incorrectly named stream | Check spelling and stream names |
| Downstream unit reports a missing inlet | The inlet connection is missing or references the wrong unit port | Verify the corresponding `CONNECTIONS` entry; intermediate streams are created by the runner when referenced correctly |
| HFM solver does not converge | Pressure, permeate pressure, or numerical settings are unsuitable | Check `PPerm`, pressure drop, discretization, and solver tolerances |
| STHE solver fails | Geometry, correlations, or inlet conditions are unsuitable | Check shell/tube geometry, flow rates, temperatures, and correlation settings |
| Excel HFM results are not created | HFM did not converge or did not produce axial results | Check the console output for solver warnings |

---

# Design Principles

The current case-study architecture follows four principles.

## 1. Streams are explicit

All independently specified inlet conditions belong in:

```python
STREAM_CONFIGS
```

Do not use a global feed variable.

## 2. Equipment is independent from topology

`EQUIPMENT_CONFIG` describes what a unit is and how it is configured.

`CONNECTIONS` describes where it is connected.

This avoids duplicating topology information in equipment definitions.

## 3. Ports define unit interfaces

Each unit operation exposes named ports.

Examples:

```text
HFM:
    feed
    retentate
    permeate

Compressor:
    inlet
    outlet

STHE:
    hot_in
    hot_out
    cold_in
    cold_out
```

New equipment should follow the same interface-oriented architecture.

## 4. Equipment declaration order is not process topology

`EQUIPMENT_CONFIG` is a collection of unit definitions. It should not be treated as the process sequence.

The process topology belongs exclusively to `CONNECTIONS`.

For example, this is valid:

```python
EQUIPMENT_CONFIG = [
    {"type": "HFM", "name": "HFM2", ...},
    {"type": "HFM", "name": "HFM1", ...},
    {"type": "Compressor", "name": "COMP1", ...},
]
```

provided that `CONNECTIONS` correctly describes:

```text
HFM1 → COMP1 → HFM2
```

The simulator creates the required stream objects before equipment construction and then applies the declared connections.

## 5. The architecture supports arbitrary flowsheets

The framework should not assume that a flowsheet has:

- one feed,
- one outlet,
- one process path,
- or one unit operation.

For example, the same configuration mechanism can represent:

```text
Feed --> HFM
```

or:

```text
HotFeed  --> STHE --> HotProduct
ColdFeed --> STHE --> ColdProduct
```

or a larger mixed-unit flowsheet:

```text
Feed
  |
  v
HFM1 ----permeate----> Compressor ----> HFM2
  |
  v
STHE
  ^
  |
Utility / ColdFeed
```

The topology is expressed through `CONNECTIONS`.

---

# Adding New Equipment Types

When adding a new unit operation to the framework:

1. Implement the physical model in its own library.
2. Provide a `UnitOperation`-compatible wrapper.
3. Define clear named input/output ports.
4. Add the equipment type to `Main_Simulator.py`.
5. Document its configuration and ports here.
6. Create at least one focused case study.
7. Prefer explicit `STREAM_CONFIGS` for every independent inlet stream.

The goal is that a new equipment type can be inserted into an existing flowsheet without introducing special global concepts such as `FEED_CONFIG`.

---

# Example Case Studies

Typical cases include:

| Case | Description |
|---|---|
| `HFM_Case_Study_1.py` | Single HFM membrane |
| `HFM_Case_Study_2.py` | HFM process variation |
| `HFM_Case_Study_Two_Membranes.py` | Two HFM units in series |
| `HFM_Compresor_Case_Study_Two_Membranes.py` | Two HFM units with intermediate compression |
| `STHE_Case_Study_1.py` | Single STHE with independent hot and cold feeds |

Use the existing case studies as templates when creating new flowsheets.

---

# Configuration Migration: Old vs. New

## Old architecture

The old case-study format used:

```python
FEED_CONFIG = {
    ...
}
```

This implicitly assumed one global inlet stream.

## New architecture

The new format uses:

```python
STREAM_CONFIGS = {
    "Feed": {
        ...
    }
}
```

For multiple feeds:

```python
STREAM_CONFIGS = {
    "HotFeed": {
        ...
    },
    "ColdFeed": {
        ...
    }
}
```

This removes the ambiguity and makes the stream topology explicit.

**All current case studies should use the new format. No legacy `FEED_CONFIG` compatibility is intended.**

---

# License

*(Add license information here.)*

---

# Contact

*(Add maintainer / author information here.)*
