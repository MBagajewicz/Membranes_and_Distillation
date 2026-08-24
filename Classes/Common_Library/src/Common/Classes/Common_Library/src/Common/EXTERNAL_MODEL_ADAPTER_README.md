# External Model Adapter Guide

## Purpose

This document is a development guide for integrating an
already-developed specialized process model into the Common Process
Simulator flowsheet.

The intended use case is:

``` text
Existing specialized model
        |
        | already contains the real physics
        v
+---------------------------+
| External Model Adapter    |
|                           |
| - UnitOperation           |
| - Ports                   |
| - Stream -> model mapping |
| - model -> Stream mapping |
| - diagnostics             |
+-------------+-------------+
              |
              v
        Common Flowsheet
```

The adapter is **not** the physical model.

Its responsibility is to expose the existing model through the
`UnitOperation` interface used by `Common_Library`.

This pattern is based on the current `Common_Library` and the
`STHEHeatExchanger` implementation in `STHE_Library`.

`STHEHeatExchanger` is the **canonical reference implementation** for
new external-model adapters. `HFMMembrane` remains a valuable reference
for specialized models with multiple outlet streams and richer solver
diagnostics.

------------------------------------------------------------------------

## 1. When should an External Model Adapter be used?

Use an adapter when the physical model already exists outside
`Common_Library`, for example:

-   a membrane simulator
-   a detailed heat exchanger model
-   a reactor simulator
-   a custom numerical model
-   a proprietary calculation engine
-   a specialized equipment solver

The external model can have its own:

-   classes
-   numerical solvers
-   calculation modules
-   convergence logic
-   internal state
-   specialized result objects
-   technology-specific configuration

The flowsheet should not need to know any of those implementation
details.

Instead, it should see a normal `UnitOperation`.

------------------------------------------------------------------------

## 2. The architectural contract

The Common framework defines the following boundary:

``` text
                    COMMON FLOWSHEET
                           |
                           v
                    UnitOperation
                           |
                  +--------+--------+
                  |                 |
               INPUTS            OUTPUTS
                  |                 |
                  v                 ^
             Stream state       Stream state
                  |                 |
                  v                 ^
             +-------------------------+
             |   External Model       |
             |                        |
             |  physics               |
             |  numerical solver      |
             |  correlations          |
             |  convergence            |
             +-------------------------+
```

`UnitOperation.solve()` is the boundary between the flowsheet and the
equipment model.

The framework expects the unit to:

1.  read connected input Streams
2.  pass the required information to the internal model
3.  execute the internal model
4.  inspect the result
5.  map model outputs back to output Streams
6.  store useful diagnostics in `self.results`

The `Flowsheet` and `SequentialSolver` should not know how the physical
model works.

------------------------------------------------------------------------

## 3. Recommended adapter structure

A specialized library can keep its own internal architecture.

For example:

``` text
Specialized_Library/
|
+-- Calculations/
|   +-- ...
|
+-- Mass_Balance/
|   +-- ...
|
+-- Energy_Balance/
|   +-- ...
|
+-- Solver/
|   +-- ...
|
+-- Equipment_Simulator/
    +-- Equipment_Specialized.py
    +-- README.md
```

The adapter normally belongs in the specialized library when the unit is
specific to that technology.

The canonical STHE implementation follows a strict separation between
the specialized physical model and the Common adapter:

``` text
STHE_Library
|
+-- Simulator_STHE/
|   +-- calculations
|   +-- geometry.py
|   +-- options.py
|   +-- rating.py
|   +-- simulation.py
|   +-- sthe.py
|   +-- ...
|
+-- Simulator_STHE/Equipment_Simulator_STHE/
    +-- Equipment_STHE.py
```

The responsibilities are:

``` text
Common.Stream
      |
      v
STHEHeatExchanger : Common.UnitOperation
      |
      +-- ports
      +-- Stream -> STHE mapping
      +-- STHE.simulate()
      +-- STHE result -> Stream mapping
      +-- diagnostics
      |
      v
Simulator_STHE.STHE
      |
      +-- geometry
      +-- heat-transfer calculations
      +-- pressure-drop calculations
      +-- rating
      +-- numerical/physical model
```

`Equipment_STHE.py` is the flowsheet adapter. `sthe.py` and the rest of
`Simulator_STHE` contain the specialized physics. The adapter must not
reimplement those calculations.

------------------------------------------------------------------------

# 4. Canonical adapter template --- STHE pattern

For a new specialized model, use the STHE adapter as the canonical
starting point.

The canonical pattern has four explicit steps:

``` text
Common input Streams
        |
        v
UnitOperation adapter
        |
        +--> validate ports / inputs
        |
        +--> map Stream state -> specialized model API
        |
        +--> run existing specialized model unchanged
        |
        +--> map model results -> output Streams
        |
        +--> store equipment diagnostics
        |
        v
Common output Streams
```

The adapter owns the **interface**. The specialized model owns the
**physics**.

A canonical implementation looks like:

``` python
from __future__ import annotations

from typing import Any

from Common.Process_Simulator import UnitOperation, PortDirection

from ..specialized_model import SpecializedModel


class MyEquipment(UnitOperation):
    """
    Adapter between a specialized process model and the Common flowsheet.

    The specialized model remains independent of Common_Library as far as
    practical. This class only exposes the model through UnitOperation,
    maps Common.Stream state into the model, executes the model, and maps
    results back to Common.Stream objects.
    """

    def __init__(
        self,
        name: str,
        simulator: SpecializedModel | None = None,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(
            name,
            tag=tag,
            description=description,
        )

        self._sim = (
            simulator
            if simulator is not None
            else SpecializedModel()
        )

        # Declare the physical interface of the equipment.
        self.add_port("inlet_1", PortDirection.INPUT)
        self.add_port("outlet_1", PortDirection.OUTPUT)

    @property
    def simulator(self) -> SpecializedModel:
        """Configured specialized physical model."""
        return self._sim

    @staticmethod
    def _scalar(value: Any) -> float:
        """Convert scalar / zero-dimensional numerical results to float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            import numpy as np
            return float(np.asarray(value).squeeze())

    @staticmethod
    def _require_stream(port, label: str):
        stream = port.stream
        if stream is None:
            raise RuntimeError(
                f"{port.unit.name}.{label} is not connected to a stream"
            )
        return stream

    def _sync_inputs(self, inlet_1) -> None:
        """
        Map Common.Stream state into the specialized model API.

        Replace this method with the actual interface of the specialized
        model. Do not duplicate the model's physical calculations here.
        """
        self._sim.streams.inlet.temperature = float(inlet_1.T)
        self._sim.streams.inlet.pressure = float(inlet_1.P)
        self._sim.streams.inlet.flow = float(inlet_1.mass_flow)
        self._sim.streams.inlet.cp = float(inlet_1.cp_mass)
        self._sim.streams.inlet.density = float(inlet_1.density_mass)
        self._sim.streams.inlet.viscosity = float(inlet_1.viscosity)

    def solve(self) -> None:
        """Run the specialized model and update Common output Streams."""
        inlet_1 = self._require_stream(self.inlet_1, "inlet_1")
        outlet_1 = self.outlet_1.stream

        if outlet_1 is None:
            raise RuntimeError(
                f"{self.name}.outlet_1 is not connected to a stream"
            )

        # Validate physical inputs before entering the specialized solver.
        if inlet_1.mass_flow <= 0:
            raise ValueError(
                f"{self.name} inlet mass flow must be > 0"
            )

        # 1. Common Stream -> specialized model.
        self._sync_inputs(inlet_1)

        # 2. Execute the existing specialized model unchanged.
        results = self._sim.simulate()

        # 3. Extract the physical output state.
        P_out = self._scalar(results.P_out)
        T_out = self._scalar(results.T_out)
        mass_flow_out = self._scalar(results.mass_flow_out)

        # 4. Common Stream update. Derived thermodynamic properties should
        #    be recalculated by Stream.update().
        outlet_1.update(
            P=P_out,
            T=T_out,
            mass_flow=mass_flow_out,
        )

        # 5. Store equipment-specific diagnostics.
        self.results.update({
            "P_out": P_out,
            "T_out": T_out,
            "mass_flow_out": mass_flow_out,
        })
```

The exact port names, input mapping, execution method, and result fields
must follow the specialized model. The **architecture** above should
remain stable.

### Canonical STHE interface

The actual STHE adapter exposes:

``` python
self.add_port("hot_in", PortDirection.INPUT)
self.add_port("hot_out", PortDirection.OUTPUT)
self.add_port("cold_in", PortDirection.INPUT)
self.add_port("cold_out", PortDirection.OUTPUT)
```

Its `solve()` method follows this sequence:

``` text
hot_in / cold_in
      |
      v
_validate connected streams
      |
      v
_sync_streams()
      |
      v
self._sim.simulate()
      |
      +--> outlet temperatures
      +--> tube/shell pressure drops
      +--> Q
      +--> U
      +--> area
      +--> NTU
      +--> effectiveness
      |
      v
hot_out / cold_out
      |
      v
self.results + warnings
```

This is the canonical pattern for new adapters because it demonstrates
both sides of the boundary clearly:

-   `Common.Stream` remains the flowsheet state representation.
-   `STHE` remains the specialized physical model.
-   `STHEHeatExchanger` is only the translation/execution boundary.
-   Equipment-specific diagnostics remain in `self.results`.
-   Topology remains outside the adapter.

### What to copy and what not to copy

When creating a new adapter, copy the **architectural pattern**, not the
STHE-specific calculations.

Copy:

``` text
UnitOperation inheritance
port declaration
input validation
_stream synchronization
specialized model execution
output Stream update
results / warnings
```

Do not copy:

``` text
STHE heat-transfer equations
STHE pressure-drop equations
STHE geometry calculations
STHE rating equations
STHE convergence/physical calculations
```

Those belong to the specialized model.

# 5. The adapter should be thin

A good adapter looks like:

``` text
Stream
  |
  v
adapter
  |
  +--> set inputs
  |
  +--> simulator.run()
  |
  +--> read results
  |
  v
Stream
```

A bad adapter starts duplicating the specialized model:

``` text
Specialized model
       |
       +---- physical equations
       |
       +---- numerical solver
       |
       +---- duplicated physical equations  <--- avoid
       |
       +---- adapter
```

The adapter should not become a second implementation of the physics.

If the external model already calculates pressure drop, the adapter
should read the calculated pressure drop.

If the external model already performs an energy balance, the adapter
should not reproduce that balance.

------------------------------------------------------------------------

# 6. Canonical reference: STHEHeatExchanger

`STHEHeatExchanger` is the preferred reference implementation for
building a new external-model adapter.

Its relationship with the specialized model is:

``` text
Common Flowsheet
      |
      v
STHEHeatExchanger : UnitOperation
      |
      +-- hot_in
      +-- hot_out
      +-- cold_in
      +-- cold_out
      |
      v
Simulator_STHE.STHE
      |
      +-- geometry
      +-- heat-transfer calculations
      +-- pressure-drop calculations
      +-- rating
      +-- specialized simulation
```

The adapter does not implement shell-side or tube-side physics.

It translates the Common framework representation into the existing STHE
model, calls:

``` python
calc = self._sim.simulate()
```

and maps the resulting outlet temperatures and pressures back to the
Common Streams.

It also records equipment-specific quantities such as:

``` python
self.results["heat_duty_W"]
self.results["U_W_m2K"]
self.results["area_m2"]
self.results["NTU"]
self.results["effectiveness"]
self.results["deltaP_hot_Pa"]
self.results["deltaP_cold_Pa"]
```

This makes STHE the best template when the new technology has:

-   more than one physical inlet or outlet
-   a pre-existing specialized solver
-   model-specific configuration
-   pressure/temperature transformations
-   equipment-specific diagnostics
-   derived results that should remain outside `Stream`

## 7. STHE adapter pattern

A simplified version of the current canonical adapter is:

``` python
from Common.Process_Simulator import UnitOperation, PortDirection
from ..sthe import STHE


class STHEHeatExchanger(UnitOperation):

    def __init__(
        self,
        name: str,
        simulator: STHE | None = None,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(
            name,
            tag=tag,
            description=description,
        )

        self._sim = simulator if simulator is not None else STHE()

        self.add_port("hot_in", PortDirection.INPUT)
        self.add_port("hot_out", PortDirection.OUTPUT)
        self.add_port("cold_in", PortDirection.INPUT)
        self.add_port("cold_out", PortDirection.OUTPUT)

    def solve(self) -> None:
        hot = self.hot_in.stream
        cold = self.cold_in.stream

        if hot is None:
            raise RuntimeError(
                f"{self.name}.hot_in is not connected to a stream"
            )

        if cold is None:
            raise RuntimeError(
                f"{self.name}.cold_in is not connected to a stream"
            )

        hot_out = self.hot_out.stream
        cold_out = self.cold_out.stream

        if hot_out is None:
            raise RuntimeError(
                f"{self.name}.hot_out is not connected to a stream"
            )

        if cold_out is None:
            raise RuntimeError(
                f"{self.name}.cold_out is not connected to a stream"
            )

        # Map Common.Stream -> STHE.
        self._sync_streams(hot, cold)

        # Run the specialized model.
        self._sim.simulate()

        # Extract model results.
        hot_T_out = float(self._sim.streams.hot.outlet.temperature)
        cold_T_out = float(self._sim.streams.cold.outlet.temperature)

        # Pressure-drop mapping depends on the configured tube side.
        dp_tube = float(self._sim.DeltaP_tube)
        dp_shell = float(self._sim.DeltaP_shell)

        # Update Common output Streams.
        hot_out.update(
            P=hot.P - dp_tube,
            T=hot_T_out,
            mass_flow=hot.mass_flow,
        )

        cold_out.update(
            P=cold.P - dp_shell,
            T=cold_T_out,
            mass_flow=cold.mass_flow,
        )

        # Store specialized equipment results.
        self.results["heat_duty_W"] = float(self._sim.Q)
        self.results["U_W_m2K"] = float(self._sim.U)
        self.results["area_m2"] = float(self._sim.Area)
        self.results["NTU"] = float(self._sim.NTU)
```

The production implementation contains additional validation, tube/shell
side pressure-drop mapping, optional rating quantities, and an energy
balance diagnostic. New adapters should preserve the same architectural
separation.

------------------------------------------------------------------------

# 8. Secondary reference: HFMMembrane

`HFMMembrane` remains a useful reference when the specialized model has
multiple product streams and richer solver diagnostics.

Its relationship with the specialized model is:

``` text
Common Flowsheet
      |
      v
HFMMembrane : UnitOperation
      |
      +-- feed
      +-- retentate
      +-- permeate
      |
      v
SimulatorRunHFM
      |
      +-- mesh
      +-- mass balance
      +-- energy balance
      +-- fugacity
      +-- pressure drop
      +-- convergence
      |
      v
SimulatorResultsHFM
```

The important distinction is:

-   use **STHE** as the default architectural template;
-   use **HFM** as a secondary reference for complex multi-output models
    and solver diagnostics.

# 8. Mapping model inputs

There are two common approaches.

## Approach A: The model accepts a Stream

This is the pattern already used by HFM:

``` python
self._sim.set_feed(feed_stream)
```

Advantages:

-   minimal adapter code
-   the specialized model can access the same thermodynamic state
-   useful when the specialized model is already designed around
    `Stream`

Use this when the external model naturally works with the Common
`Stream`.

------------------------------------------------------------------------

## Approach B: The adapter extracts primitive values

For a model that should remain independent from Common:

``` python
self._sim.set_feed(
    P=feed_stream.P,
    T=feed_stream.T,
    molar_flow=feed_stream.molar_flow,
    composition=dict(feed_stream.composition),
)
```

This creates a stronger separation:

``` text
Common Stream
     |
     v
External Model Adapter
     |
     v
Technology-independent model API
```

This can be preferable when the specialized library should not depend on
`Common_Library`.

------------------------------------------------------------------------

# 9. Mapping model outputs

The adapter should convert the model's result object into the physical
state required by a `Stream`.

The minimum state normally consists of:

``` python
outlet_stream.update(
    P=P_out,
    T=T_out,
    molar_flow=molar_flow_out,
    composition=composition_out,
)
```

Do not manually populate derived thermodynamic properties if
`Stream.update()` already calculates them.

For example, avoid doing this:

``` python
outlet.enthalpy = calculated_enthalpy
outlet.density = calculated_density
outlet.viscosity = calculated_viscosity
```

when those properties are derived by the Stream thermodynamic backend.

The adapter should provide the independent state and let `Stream`
refresh its derived properties.

------------------------------------------------------------------------

# 10. Multiple outlet streams

Specialized models often have several physical exits.

The pattern is simply to expose one output Port per physical outlet.

For example:

``` python
self.add_port("retentate", PortDirection.OUTPUT)
self.add_port("permeate", PortDirection.OUTPUT)
```

Then map each model result independently:

``` python
self.retentate.stream.update(...)
self.permeate.stream.update(...)
```

The same principle applies to:

-   vapor/liquid
-   hot/cold sides
-   product/byproduct
-   gas/liquid
-   multiple branches

The Port structure should represent the physical interface of the
equipment.

------------------------------------------------------------------------

# 11. Results versus Stream state

Keep these concepts separate.

### Stream state

Represents the physical state leaving the equipment:

``` text
P
T
molar_flow
composition
```

### Unit results

Represent equipment-specific information useful for reporting or
analysis:

``` text
power
area
stage_cut
pressure_drop
heat_duty
solver_iterations
convergence_path
performance_factor
```

For example:

``` python
self.results["stage_cut"] = stage_cut
self.results["pressure_drop"] = pressure_drop
self.results["solver_paths"] = results.solver_paths
```

Do not use `self.results` as a replacement for the outlet Stream.

------------------------------------------------------------------------

# 12. Diagnostics and infeasible results

An external solver may distinguish between:

``` text
successful
infeasible
failed
```

The adapter should preserve that distinction as much as the external
model allows.

A common pattern is:

``` python
results = self._sim.run()

if not results.feasible:
    self.warnings.append(
        f"External solver infeasible: "
        f"{results.infeasible_reason}"
    )
    return
```

Do not overwrite output Streams with invalid results.

If the model raises an exception, the `SequentialSolver` already
provides the framework-level error handling:

``` text
SequentialSolver
      |
      v
unit.solve()
      |
      +---- success --> after_solve()
      |
      +---- exception --> on_solve_error()
```

The adapter should therefore raise exceptions for genuine execution
errors rather than silently hiding them.

------------------------------------------------------------------------

# 13. Connection to the flowsheet

The adapter does not connect Streams itself.

The correct pattern is:

``` python
fs.add_unit("HFM1", hfm)
fs.add_stream("Feed", feed)
fs.add_stream("Retentate", retentate)
fs.add_stream("Permeate", permeate)

fs.connect(
    stream="Feed",
    destination=("HFM1", "feed"),
)

fs.connect(
    source=("HFM1", "retentate"),
    stream="Retentate",
)

fs.connect(
    source=("HFM1", "permeate"),
    stream="Permeate",
)
```

The adapter only declares Ports.

`Flowsheet.connect()` owns the topology.

This separation is important because `Flowsheet` is explicitly designed
as the central connection manager.

------------------------------------------------------------------------

# 14. Execution

The adapter is executed by the solver like any other UnitOperation:

``` python
from Common.Process_Simulator import SequentialSolver

solver = SequentialSolver(fs)
solver.solve()
```

The execution path is:

``` text
SequentialSolver.solve()
        |
        v
topological ordering
        |
        v
solve_unit(unit)
        |
        v
unit.solve()
        |
        v
External Model Adapter
        |
        v
specialized_model.run()
```

The solver does not need to know that the unit is an HFM membrane, a
reactor, a heat exchanger, or any other technology.

------------------------------------------------------------------------

# 15. Adapter checklist

When integrating an existing model, verify the following.

## Model interface

-   [ ] Can the model receive all required input information?
-   [ ] Is the model already fully configured before `run()`?
-   [ ] Is there a clear method such as `run()`?
-   [ ] Is there a well-defined result object?
-   [ ] Can successful and unsuccessful calculations be distinguished?

## UnitOperation interface

-   [ ] Does the adapter inherit from `UnitOperation`?
-   [ ] Are all physical inlet ports registered?
-   [ ] Are all physical outlet ports registered?
-   [ ] Are port names stable and meaningful?
-   [ ] Is `solve()` the only place where execution occurs?

## Input mapping

-   [ ] Are input Streams checked for connection?
-   [ ] Is the required Stream state passed to the model?
-   [ ] Are units consistent?
-   [ ] Is composition mapped consistently?

## Output mapping

-   [ ] Are model results mapped to the correct output Streams?
-   [ ] Are `P`, `T`, `molar_flow`, and composition updated as
    appropriate?
-   [ ] Is `Stream.update()` used?
-   [ ] Are derived thermodynamic properties left to `Stream`?

## Diagnostics

-   [ ] Are important model results stored in `self.results`?
-   [ ] Are infeasible cases reported through `warnings`?
-   [ ] Are genuine execution failures allowed to raise exceptions?
-   [ ] Are invalid output states prevented from reaching the flowsheet?

## Flowsheet integration

-   [ ] Is all topology created through `Flowsheet.connect()`?
-   [ ] Can the unit be inserted between other units without special
    solver logic?
-   [ ] Does `SequentialSolver` execute it without knowing its
    internals?

------------------------------------------------------------------------

# 16. Common mistakes

## Mistake 1: Put the physics in the adapter

Avoid:

``` python
class HFMMembrane(UnitOperation):

    def solve(self):
        # Reimplement membrane mass balance here
        # Reimplement fugacity here
        # Reimplement pressure drop here
        # Reimplement energy balance here
```

If the specialized model already exists, this creates two sources of
truth.

------------------------------------------------------------------------

## Mistake 2: Let the adapter modify flowsheet topology

Avoid:

``` python
self.connect(...)
```

inside `solve()`.

Connections belong to:

``` python
fs.connect(...)
```

------------------------------------------------------------------------

## Mistake 3: Manually calculate Stream-derived properties

Avoid duplicating thermodynamic calculations already provided by
`Stream`.

Prefer:

``` python
outlet.update(
    P=P_out,
    T=T_out,
    molar_flow=flow_out,
    composition=composition_out,
)
```

------------------------------------------------------------------------

## Mistake 4: Expose the entire specialized model to the flowsheet

The flowsheet should not need to know:

``` python
simulator.mesh
simulator.mass_balance_solver
simulator.energy_balance_solver
simulator.fugacity_model
```

It should only interact with:

``` python
unit.ports
unit.solve()
unit.results
unit.warnings
```

------------------------------------------------------------------------

## Mistake 5: Put technology-specific code into Common

If a model is specific to one technology, keep the specialized
implementation in its own library.

For example:

``` text
Common_Library
    |
    +-- generic process infrastructure
    +-- generic unit operations
    +-- generic Stream functionality

HFM_Library
    |
    +-- HFM physics
    +-- HFM numerical solvers
    +-- HFMMembrane adapter
```

A generic model such as `Mixer` belongs in Common.

A detailed HFM solver does not.

------------------------------------------------------------------------

# 17. Runner integration and equipment registration

The adapter architecture is independent of the flowsheet topology.

A new adapter should declare its Ports and be connectable through the
normal `Flowsheet.connect()` mechanism. However, the current
`Main_Simulator` runner may still contain an explicit dispatch/registry
for supported equipment types.

Therefore, when adding a new equipment type, verify both layers:

``` text
Specialized Library
      |
      +-- physical model
      +-- UnitOperation adapter
      |
      v
Common Flowsheet
      |
      v
Main_Simulator equipment factory / registry
      |
      v
Case Study
```

Do not add technology-specific physics to `Main_Simulator`. If a new
equipment type requires runner support, add only the minimum
registration or construction logic needed to instantiate the adapter.

The long-term architectural goal is that equipment discovery/creation is
registry-based rather than a growing hard-coded `if/elif` chain.

------------------------------------------------------------------------

# 18. Recommended development workflow

When a new specialized model is ready, use this sequence (following the
STHE pattern):

``` text
1. Existing model is working independently
              |
              v
2. Define its flowsheet interface
              |
              +-- input ports
              +-- output ports
              |
              v
3. Create UnitOperation adapter
              |
              v
4. Map Stream -> model input
              |
              v
5. Run existing model unchanged
              |
              v
6. Map model result -> output Stream
              |
              v
7. Store equipment-specific diagnostics
              |
              v
8. Add adapter to a small flowsheet
              |
              v
9. Run SequentialSolver
              |
              v
10. Validate balances and outputs
```

The key principle is:

> **Adapt the model to the framework; do not adapt the framework to the
> model.**

------------------------------------------------------------------------

# 19. Minimal adapter skeleton

When starting a new integration, this is the smallest useful template:

``` python
from Common.Process_Simulator import UnitOperation, PortDirection


class MyEquipment(UnitOperation):

    def __init__(self, name: str, simulator, tag: str = "", description: str = ""):
        super().__init__(
            name,
            tag=tag,
            description=description,
        )

        self._sim = simulator

        self.add_port("feed", PortDirection.INPUT)
        self.add_port("product", PortDirection.OUTPUT)

    def solve(self) -> None:
        feed = self.feed.stream

        if feed is None:
            raise RuntimeError(
                f"{self.name}.feed is not connected to any stream"
            )

        self._sim.set_feed(feed)

        results = self._sim.run()

        if not getattr(results, "feasible", True):
            reason = getattr(
                results,
                "infeasible_reason",
                "unknown reason",
            )
            self.warnings.append(
                f"External model infeasible: {reason}"
            )
            return

        self.product.stream.update(
            P=results.P_out,
            T=results.T_out,
            molar_flow=results.molar_flow_out,
            composition=results.composition_out,
        )

        self.results["model_result"] = results
```

From this point, the developer should replace only the
interface-specific parts:

``` text
ports
input mapping
model execution
result extraction
output mapping
diagnostics
```

The Common architecture remains unchanged.

------------------------------------------------------------------------

# 20. Canonical rule for new equipment

For future specialized units, use this decision rule:

``` text
Does the physical model already exist?
        |
       yes
        |
        v
Keep it in its specialized library
        |
        v
Create a thin UnitOperation adapter
        |
        +-- define physical Ports
        +-- validate inputs
        +-- map Stream -> model
        +-- execute model
        +-- map model -> Stream
        +-- expose diagnostics
        |
        v
Connect it through Common.Flowsheet
        |
        v
Register the equipment with the runner if required
```

The canonical implementation to consult first is:

``` text
STHE_Library/
└── Simulator_STHE/
    └── Equipment_Simulator_STHE/
        └── Equipment_STHE.py
```

For multi-output and solver-diagnostic patterns, consult:

``` text
HFM_Library/
└── Equipment_Simulator_HFM/
    └── Equipment_HFM.py
```

The guiding principle remains:

> **Adapt the model to the framework; do not adapt the framework to the
> model.**
