# STHE_Library

A modular **Shell-and-Tube Heat Exchanger (STHE)** library designed for integration with the `Common_Library` process-simulation framework.

The library separates the heat-exchanger physics from the framework integration layer:

```text
STHE_Library
└── Simulator_STHE
    ├── STHE physics/model
    ├── geometry and options
    ├── correlations and calculations
    ├── rating/simulation logic
    └── Equipment_Simulator_STHE
        └── STHEHeatExchanger
            └── Common_Library UnitOperation adapter
```

This separation follows the same architectural principle used by `HFM_Library`: the physical model remains independent from the flowsheet framework, while a dedicated equipment adapter exposes the model through `Common_Library`.

---

## Features

The STHE model provides calculations for:

- Shell-and-tube heat-exchanger geometry
- Tube-side and shell-side flow
- Reynolds numbers
- Velocities
- Friction factors
- Tube-side and shell-side heat-transfer coefficients
- Overall heat-transfer coefficient
- Heat-transfer area
- LMTD / correction factor
- NTU and effectiveness
- Heat duty
- Tube-side pressure drop
- Shell-side pressure drop
- Basic energy-balance diagnostics

The library is intended for **rating-style process simulation**: inlet stream conditions and exchanger geometry are supplied, and the model calculates the resulting thermal and hydraulic performance.

---

## Package Structure

```text
Simulator_STHE/
├── __init__.py
├── sthe.py
├── simulation.py
├── rating.py
├── geometry.py
├── options.py
├── methods.py
├── constants.py
├── stream.py
│
├── Calculations/
│   ├── Calculations_STHE_Area.py
│   ├── Calculations_STHE_NTU.py
│   ├── Calculations_STHE_U.py
│   ├── Calculations_STHE_correction_factor.py
│   ├── Calculations_STHE_DeltaPshellside.py
│   ├── Calculations_STHE_DeltaPtubeside.py
│   ├── Calculations_STHE_Nusselt_shellside.py
│   ├── Calculations_STHE_Nusselt_tubeside.py
│   ├── Calculations_STHE_Reynolds_shellside.py
│   ├── Calculations_STHE_Reynolds_tubeside.py
│   └── ...
│
└── Equipment_Simulator_STHE/
    ├── __init__.py
    ├── Equipment_STHE.py
    └── README.md
```

---

# Framework Integration

The public `Common_Library` equipment adapter is:

```python
from Simulator_STHE.Equipment_Simulator_STHE import STHEHeatExchanger
```

The adapter exposes four ports:

```text
hot_in
hot_out
cold_in
cold_out
```

These are standard `Common_Library` unit-operation ports:

| Port | Direction | Meaning |
|---|---|---|
| `hot_in` | INPUT | Hot-side inlet stream |
| `hot_out` | OUTPUT | Hot-side outlet stream |
| `cold_in` | INPUT | Cold-side inlet stream |
| `cold_out` | OUTPUT | Cold-side outlet stream |

The physics itself remains encapsulated in:

```python
Simulator_STHE.STHE
```

The adapter does not duplicate the heat-exchanger calculations.

---

# Using the Physics Model Directly

The physics layer can be used independently of the flowsheet framework.

```python
from Simulator_STHE import STHE

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
```

The internal stream data can then be configured and the model simulated through the STHE API.

For flowsheet applications, prefer the `STHEHeatExchanger` adapter so that stream states are exchanged through `Common.Stream`.

---

# Using the `Common_Library` Adapter

The recommended framework-facing pattern is:

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

The resulting `unit` is a `Common_Library.Process_Simulator.UnitOperation` and can be registered in the same `Flowsheet` used by HFM and Compressor.

---

# Stream Mapping

The adapter maps `Common.Stream` properties into the STHE physics model.

For each inlet stream, the adapter reads properties such as:

```text
T
P
mass_flow
cp_mass
density_mass
viscosity
conductivity
```

The STHE model uses these values for the corresponding hot-side and cold-side calculations.

After simulation, the adapter updates the connected outlet streams **in place**.

The outlet streams preserve their incoming composition and mass flow while receiving the calculated:

```text
Temperature
Pressure
```

from the STHE model.

This is important for flowsheet integration because downstream equipment references the same stream objects.

---

# STHE Results

After `solve()`, the `STHEHeatExchanger.results` dictionary contains calculated quantities including:

```text
heat_duty_W
U_W_m2K
area_m2
NTU
effectiveness
deltaP_tube_Pa
deltaP_shell_Pa
deltaP_hot_Pa
deltaP_cold_Pa
hot_outlet_temperature_K
cold_outlet_temperature_K
hot_outlet_pressure_Pa
cold_outlet_pressure_Pa
```

Additional rating quantities may include:

```text
LMTD_K
correction_factor
```

The adapter also records an energy-balance diagnostic:

```text
energy_balance_relative_error
```

Warnings are generated when the relative energy-balance error exceeds the configured diagnostic threshold.

---

# Configuration in `Main_Simulator`

The `Main_Simulator` framework configures an STHE through an `EQUIPMENT_CONFIG` entry.

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

The two inlet streams are configured independently through `STREAM_CONFIGS`:

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

The topology is defined separately:

```python
CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},

    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
```

There is deliberately no global `FEED_CONFIG`.

---

# Geometry and Configuration

The main geometry groups are:

## Shell

```text
diameter
fouling_factor
```

## Tubes

```text
length
outside_diameter
inside_diameter
pitch_ratio
layout
passes
wall_conductivity
fouling_factor
stream
```

The `stream` setting identifies which side of the exchanger is assigned to the tubes:

```python
"hot_stream"
```

or:

```python
"cold_stream"
```

## Baffles

```text
number
cut
sealing_strips
```

---

# Heat-Transfer Correlations

The STHE options expose the selected heat-transfer methods.

For example:

```python
sim.options.correlations.tube_method = "Gnielinski"
sim.options.correlations.shell_method = "Bell"
```

The available implementations are defined in the `Calculations` modules and should be treated as the authoritative source for supported method names.

When adding a new correlation:

1. Implement it in the appropriate calculation module.
2. Expose it through the STHE options/method selection.
3. Validate it independently.
4. Add or update a representative case study.
5. Document the new method here.

---

# Pressure Drop

The model calculates pressure losses independently for:

```text
Tube side
Shell side
```

The equipment adapter maps those losses to the physical hot/cold sides according to:

```python
sim.geometry.tubes.stream
```

For example:

```text
tubes.stream = "hot_stream"

ΔP_hot  = ΔP_tube
ΔP_cold = ΔP_shell
```

while:

```text
tubes.stream = "cold_stream"

ΔP_hot  = ΔP_shell
ΔP_cold = ΔP_tube
```

The resulting outlet pressures are written back to the connected `Common.Stream` objects.

---

# Design Boundary

The library has a deliberate two-layer architecture:

```text
                    STHE_Library
                         |
              +----------+----------+
              |                     |
              v                     v
       Simulator_STHE       Equipment_Simulator_STHE
       Physics/model              Adapter
              |                     |
              |                     v
              |              Common_Library
              |                     |
              +---------------------+
                         |
                      Flowsheet
```

### `Simulator_STHE.STHE`

Responsible for:

- exchanger physics
- geometry
- correlations
- thermal calculations
- hydraulic calculations
- rating/simulation

### `STHEHeatExchanger`

Responsible for:

- `Common_Library.UnitOperation` inheritance
- named ports
- stream validation
- mapping `Common.Stream` → STHE model
- mapping STHE results → `Common.Stream`
- exposing results and warnings to the flowsheet

The adapter should remain thin. Physics should not be duplicated in the framework layer.

---

# Example Flowsheet

A minimal process-level STHE flowsheet is:

```text
             ┌─────────────────────┐
HotFeed ────>│                     │────> HotProduct
             │       STHE1         │
ColdFeed ───>│                     │────> ColdProduct
             └─────────────────────┘
```

The case-study configuration is responsible for defining:

```text
STREAM_CONFIGS
EQUIPMENT_CONFIG
CONNECTIONS
```

The `Main_Simulator` is responsible for constructing the flowsheet and solving the connected unit operations.

---

# Current Scope and Assumptions

The current implementation is a rating-oriented exchanger model with:

- one hot-side inlet/outlet
- one cold-side inlet/outlet
- positive inlet mass flows
- `hot_in.T > cold_in.T`
- tube-side / shell-side pressure-drop calculations
- configurable tube and shell correlations
- outlet temperatures and pressures calculated from the exchanger model

For unusual operating regimes, phase-change service, or configurations outside the implemented correlation ranges, the model should be validated before use.

---

# Development Guidelines

When extending `STHE_Library`:

- Keep physical calculations inside `Simulator_STHE`.
- Keep `STHEHeatExchanger` focused on framework integration.
- Reuse `Common.Stream` rather than introducing a second process-stream abstraction.
- Use explicit named ports.
- Keep configuration independent from flowsheet topology.
- Do not introduce a global feed concept.
- Add focused case studies for new capabilities.
- Preserve the interface expected by `Main_Simulator`.

---

# License

*(Add license information here.)*

# Contact

*(Add maintainer / author information here.)*


## Thermal calculation with NoNTU Eq. (32)

The STHE simulation uses Eq. (32) from NoNTU and Bagajewicz (2004)
for the thermal calculation, with the LMTD correction factor fixed at
`F_T = 1.0`. The inlet stream conditions, overall heat-transfer
coefficient, and installed area are used to calculate the hot outlet
temperature directly; the heat duty and cold outlet temperature then
follow from the energy balances.

The existing `Calculations_STHE_NTU.py` module is retained for reference
and validation. Calculation of `F_T` for multipass configurations and
iteration of that factor are intentionally left for a later step.
