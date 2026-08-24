# Equipment_Simulator_STHE

`Equipment_Simulator_STHE` is the **Common_Library integration layer** for the shell-and-tube heat exchanger model contained in `Simulator_STHE`.

Its purpose is deliberately narrow:

> Adapt the STHE physics model to the `Common_Library.UnitOperation` interface without duplicating heat-exchanger physics.

---

## Architecture

```text
Common_Library
     |
     v
UnitOperation
     |
     v
STHEHeatExchanger
     |
     v
Simulator_STHE.STHE
     |
     +--> geometry
     +--> correlations
     +--> thermal calculations
     +--> hydraulic calculations
     +--> rating / simulation
```

The adapter is located in:

```text
Simulator_STHE/
└── Equipment_Simulator_STHE/
    ├── __init__.py
    ├── Equipment_STHE.py
    └── README.md
```

---

# Public Class

The public framework-facing class is:

```python
from Simulator_STHE.Equipment_Simulator_STHE import STHEHeatExchanger
```

Class:

```python
STHEHeatExchanger
```

It inherits from:

```python
Common.Process_Simulator.UnitOperation
```

---

# Ports

The equipment exposes four ports:

| Port | Direction | Description |
|---|---|---|
| `hot_in` | INPUT | Hot-side inlet |
| `hot_out` | OUTPUT | Hot-side outlet |
| `cold_in` | INPUT | Cold-side inlet |
| `cold_out` | OUTPUT | Cold-side outlet |

The port names are part of the flowsheet interface and should be used by `CONNECTIONS`.

Example:

```python
CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},

    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
```

---

# Constructor

The constructor is:

```python
STHEHeatExchanger(
    name: str,
    simulator: STHE | None = None,
    tag: str = "",
    description: str = "",
)
```

Parameters:

### `name`

Unique unit-operation name inside the flowsheet.

Example:

```python
name="STHE1"
```

### `simulator`

Configured `Simulator_STHE.STHE` model.

If omitted, the adapter creates a default:

```python
STHE()
```

The returned unit exposes the internal model through:

```python
unit.simulator
```

### `tag`

Optional process-equipment tag:

```python
tag="E-101"
```

### `description`

Optional equipment description.

---

# Example

```python
from Simulator_STHE import STHE
from Simulator_STHE.Equipment_Simulator_STHE import STHEHeatExchanger

sim = STHE()

sim.geometry.shell.diameter = 0.50
sim.geometry.shell.fouling_factor = 1.0e-4

sim.geometry.tubes.length = 5.0
sim.geometry.tubes.outside_diameter = 0.025
sim.geometry.tubes.inside_diameter = 0.021
sim.geometry.tubes.pitch_ratio = 1.25
sim.geometry.tubes.layout = 1
sim.geometry.tubes.passes = 2
sim.geometry.tubes.wall_conductivity = 16.0
sim.geometry.tubes.fouling_factor = 1.0e-4
sim.geometry.tubes.stream = "hot_stream"

sim.geometry.baffles.number = 8
sim.geometry.baffles.cut = 0.25
sim.geometry.baffles.sealing_strips = 1

sim.options.correlations.tube_method = "Gnielinski"
sim.options.correlations.shell_method = "Bell"

unit = STHEHeatExchanger(
    name="STHE1",
    simulator=sim,
    tag="E-101",
    description="Shell-and-tube heat exchanger",
)
```

The unit can then be registered in the same `Flowsheet` as other `Common_Library` equipment.

---

# What the Adapter Does

The adapter performs four main tasks.

## 1. Exposes framework ports

It creates:

```python
self.add_port("hot_in", PortDirection.INPUT)
self.add_port("hot_out", PortDirection.OUTPUT)
self.add_port("cold_in", PortDirection.INPUT)
self.add_port("cold_out", PortDirection.OUTPUT)
```

This gives the STHE the same unit-operation interface used by the rest of the framework.

## 2. Reads `Common.Stream`

During `solve()`, the adapter validates and reads the connected inlet streams.

The current implementation consumes:

```text
T
P
mass_flow
cp_mass
density_mass
viscosity
conductivity
```

for both hot and cold streams.

These values are mapped into the internal STHE stream representation.

## 3. Runs the STHE model

The adapter calls:

```python
calc = self._sim.simulate()
```

The physical model calculates the exchanger performance.

The adapter does not implement the heat-transfer correlations itself.

## 4. Updates outlet streams

The calculated outlet temperature and pressure are written back to:

```text
hot_out
cold_out
```

using the connected `Common.Stream` objects.

This update occurs in place, allowing downstream equipment to consume the resulting stream state.

---

# Validation Performed by the Adapter

Before simulation, the adapter checks that:

- `hot_in` is connected;
- `cold_in` is connected;
- `hot_out` is connected;
- `cold_out` is connected;
- hot-side mass flow is positive;
- cold-side mass flow is positive;
- `hot_in.T > cold_in.T`;
- `geometry.tubes.stream` is either `"hot_stream"` or `"cold_stream"`.

Examples of errors include:

```text
STHE1.hot_in is not connected to a stream
```

or:

```text
STHE inlet mass flows must be > 0
```

or:

```text
STHE requires hot_in.T > cold_in.T
```

---

# Pressure-Drop Mapping

The physical STHE model calculates pressure drop by exchanger side:

```text
ΔP_tube
ΔP_shell
```

The adapter maps those values to the physical hot/cold sides according to:

```python
sim.geometry.tubes.stream
```

If:

```python
sim.geometry.tubes.stream == "hot_stream"
```

then:

```text
ΔP_hot  = ΔP_tube
ΔP_cold = ΔP_shell
```

If:

```python
sim.geometry.tubes.stream == "cold_stream"
```

then:

```text
ΔP_hot  = ΔP_shell
ΔP_cold = ΔP_tube
```

The resulting outlet pressures are:

```text
P_hot_out  = P_hot_in  - ΔP_hot
P_cold_out = P_cold_in - ΔP_cold
```

with non-negative pressure protection applied by the adapter.

---

# Results

After `solve()`, the unit stores results in:

```python
unit.results
```

Current result keys include:

```python
{
    "heat_duty_W": ...,
    "U_W_m2K": ...,
    "area_m2": ...,
    "NTU": ...,
    "effectiveness": ...,
    "deltaP_tube_Pa": ...,
    "deltaP_shell_Pa": ...,
    "deltaP_hot_Pa": ...,
    "deltaP_cold_Pa": ...,
    "hot_outlet_temperature_K": ...,
    "cold_outlet_temperature_K": ...,
    "hot_outlet_pressure_Pa": ...,
    "cold_outlet_pressure_Pa": ...,
}
```

If available from the STHE model, the adapter also records:

```python
"LMTD_K"
"correction_factor"
```

An energy consistency diagnostic is stored as:

```python
"energy_balance_relative_error"
```

---

# Energy-Balance Diagnostic

The adapter calculates a simple consistency check using:

```text
Q_hot  = m_hot  * cp_hot  * (T_hot,in  - T_hot,out)
Q_cold = m_cold * cp_cold * (T_cold,out - T_cold,in)
```

The relative discrepancy is stored in:

```python
unit.results["energy_balance_relative_error"]
```

If the discrepancy exceeds the current diagnostic threshold, the adapter adds a warning to:

```python
unit.warnings
```

This is a diagnostic and should not be confused with a separate nonlinear energy-balance solver.

---

# Interaction with `Main_Simulator`

`Main_Simulator.py` should treat `STHEHeatExchanger` as a normal `UnitOperation`.

A case study defines the streams independently:

```python
STREAM_CONFIGS = {
    "HotFeed": {...},
    "ColdFeed": {...},
}
```

The equipment configuration defines the STHE model:

```python
EQUIPMENT_CONFIG = [
    {
        "type": "STHE",
        "name": "STHE1",
        ...
    }
]
```

The topology connects streams to ports:

```python
CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},
    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
```

There is no `FEED_CONFIG`.

The `Main_Simulator` creates the required stream objects before constructing equipment, then applies the connections. This allows STHE to work with independently configured streams or streams generated by upstream units.

---

# Design Boundary

The adapter should remain intentionally thin.

### Belongs in `Equipment_Simulator_STHE`

- `UnitOperation` integration
- port definitions
- stream validation
- framework-to-model data mapping
- model-to-framework data mapping
- result exposure
- framework-level diagnostics

### Belongs in `Simulator_STHE`

- geometry calculations
- Reynolds-number calculations
- Nusselt correlations
- heat-transfer coefficients
- overall heat-transfer coefficient
- NTU/effectiveness
- heat duty
- pressure-drop calculations
- rating/simulation algorithms

Do not duplicate physical calculations in the adapter.

---

# Extending the Adapter

When adding functionality:

1. Keep the public port interface stable unless a new process topology requires a deliberate interface change.
2. Add model-specific calculations to `Simulator_STHE`, not to the adapter.
3. Add only the minimum required mapping code to `Equipment_STHE.py`.
4. Preserve `Common.Stream` as the process-stream abstraction.
5. Expose important model outputs through `unit.results`.
6. Add warnings for diagnostics that are useful to the flowsheet solver.
7. Add or update a case study in `Simulator_Case_Studies`.

---

# Relationship to Other Equipment

The STHE adapter follows the same conceptual pattern as other framework equipment:

```text
Physical Model
     |
     v
Equipment Adapter
     |
     v
Common_Library.UnitOperation
     |
     v
Flowsheet
```

This means STHE can coexist with:

```text
HFM
Compressor
STHE
```

and future units without introducing STHE-specific flowsheet concepts.

---

# Current Scope

The adapter currently represents one shell-and-tube exchanger with:

- one hot inlet
- one hot outlet
- one cold inlet
- one cold outlet

It is intended for steady-state flowsheet simulation.

Phase-change services and specialized exchanger configurations should be validated against the physical model before being used in production flowsheets.

---

# License

*(Add license information here.)*

# Contact

*(Add maintainer / author information here.)*
