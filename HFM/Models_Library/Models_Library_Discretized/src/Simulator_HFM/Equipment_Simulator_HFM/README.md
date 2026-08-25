# HFMMembrane

> **UnitOperation wrapper for the hollow-fiber membrane (HFM) axial solver.**  
> This is the class that **assigns ports** to the membrane and bridges the internal `SimulatorRunHFM` solver with the `Process_Simulator` flowsheet engine.

---

## 📁 Location

```
Simulator_HFM/Equipment_Simulator_HFM/Equipment_HFM.py
```

---

## 🎯 Purpose

`HFMMembrane` is a **reusable, scenario-agnostic** `UnitOperation` that wraps your existing `SimulatorRunHFM` axial membrane solver. Its only job is to:

1. **Expose three ports** to the flowsheet: `feed`, `retentate`, `permeate`.
2. **Feed the internal solver** with the inlet stream at solve time.
3. **Run the internal solver** (mesh generation, mass/energy balance, pressure drop, fugacity, etc.).
4. **Extract exit conditions** from the axial profiles and write them to the outlet streams.
5. **Store diagnostics** (stage cut, solver path, flows) for reporting.

The caller is responsible for configuring `SimulatorRunHFM` (geometry, permeance, solver tolerances, energy flags, etc.) **before** passing it in. `HFMMembrane` does not know or care about the physics inside the solver.

---

## 🏗️ Class: `HFMMembrane`

Inherits from `UnitOperation` (see `Common/Process_Simulator`).

### Constructor

```python
HFMMembrane(
    name: str,
    simulator,
    tag: str = "",
    description: str = "",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | **required** | Unit name in the flowsheet (e.g., `"HFM1"`). |
| `simulator` | `SimulatorRunHFM` | **required** | Fully configured membrane solver instance. |
| `tag` | `str` | `""` | Equipment tag (e.g., `"ME-101"`). |
| `description` | `str` | `""` | Human-readable description. |

### Ports

| Port | Direction | Description |
|------|-----------|-------------|
| `feed` | `INPUT` | Inlet stream entering the bore side of the membrane. Must be connected before solving. |
| `retentate` | `OUTPUT` | Exit stream from the bore side (z = L, last axial node). |
| `permeate` | `OUTPUT` | Exit stream from the shell side (z = 0, first axial node). |

> **Note on permeate port direction:** The permeate is collected at `z = 0` (counter-current assumption). If your geometry collects permeate at `z = L`, change the index in `solve()` from `0` to `-1`.

Ports are exposed as attributes:

```python
membrane.feed        # Port object
membrane.retentate   # Port object
membrane.permeate    # Port object
membrane.feed.stream # attached Stream
```

---

## ⚙️ How `solve()` Works

```
┌─────────────┐     set_feed()       ┌─────────────────────┐
│ feed.stream │ ───────────────────► │                     │
└─────────────┘                      │   SimulatorRunHFM   │
                                     │   (internal solver) │
┌──────────────────┐   run()         │                     │
│ retentate.stream │ ◄────────────── │  • mesh generation  │
│ (updated)        │                 │  • mass balance     │
└──────────────────┘                 │  • energy balance   │
                                     │  • pressure drop    │
┌──────────────────┐   run()         │  • fugacity         │
│ permeate.stream  │ ◄────────────── │  • convergence      │
│ (updated)        │                 │                     │
└──────────────────┘                 └─────────────────────┘
```

### Step-by-step

1. **Read feed** from `self.feed.stream`.
2. **Pass feed** to the internal solver via `self._sim.set_feed(feed_stream)`.
3. **Run solver** via `self._sim.run()`.
4. **Check feasibility.** If the solver reports infeasible, append a warning and abort (outlet streams keep their initial state).
5. **Extract exit conditions** from the axial profiles:
   - **Retentate:** last node (`results.FRet[-1]`, `results.ZRet[-1]`, `results.PRetCell[-1]`, `results.T_ret[-1]`)
   - **Permeate:** first node (`results.FPerm[0]`, `results.ZPerm[0]`, `results.PPermCell[0]`, `results.T_per[0]`)
6. **Write to outlet streams** via `Stream.update()` (refreshes CoolProp-derived properties automatically).
7. **Store diagnostics** in `self.results`.

---

## 🚀 Usage

### In a flowsheet (manual)

```python
from Common.Process_Simulator import Flowsheet, SequentialSolver
from Common.Stream.stream import Stream, ThermoBackend
from Simulator_HFM.Simulator_Run_HFM import SimulatorRunHFM
from Simulator_HFM.Simulator_Geometry_HFM import SimulatorGeometryHFM
from Simulator_HFM.Equipment_Simulator_HFM.Equipment_HFM import HFMMembrane
from Common.Membrane_Properties.Permeance.Membrane_Permeance import Membrane_Permeance

# --- 1. Configure the internal solver ---
sim = SimulatorRunHFM()
sim.set_feed(Stream(...))
sim.PPerm = 1e5
sim.set_membrane_permeance(Membrane_Permeance(...))
sim.geometry = SimulatorGeometryHFM(...)
sim.energy = True
sim.pressure_drop = True
# ... (configure all solver flags)

# --- 2. Create the UnitOperation wrapper ---
hfm = HFMMembrane(
    name="HFM1",
    simulator=sim,
    tag="ME-101",
    description="CO2 separation stage",
)

# --- 3. Build flowsheet ---
fs = Flowsheet(name="Membrane Stage")
fs.add_stream("Feed", feed_stream)
fs.add_stream("Retentate", ret_stream)
fs.add_stream("Permeate", perm_stream)
fs.add_unit("HFM1", hfm)

fs.connect(stream="Feed", destination=("HFM1", "feed"))
fs.connect(source=("HFM1", "retentate"), stream="Retentate")
fs.connect(source=("HFM1", "permeate"), stream="Permeate")

# --- 4. Solve ---
solver = SequentialSolver(fs)
solver.solve()
```

### In a case-study config (declarative)

`Run_Case_Study.py` automates the above. You only provide the config:

```python
# Case_Study_Collection/my_case.py

EQUIPMENT_CONFIG = [
    {
        "type": "HFM",
        "name": "HFM1",
        "description": "CO2 removal stage",
        # Override any COMMON_PARAM:
        "DiamShell": 0.0394,
        "FiberLengthInElement": 0.2,
        "N": 3380,
        "PPerm": 1e5,
    },
]

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate"},
    {"from": ("HFM1", "permeate"), "to": "Permeate"},
]
```

`Run_Case_Study.py` then:
1. Reads `FEED_CONFIG`, `COMMON_PARAMS`, `EQUIPMENT_CONFIG`, `CONNECTIONS`.
2. Calls `build_hfmmembrane(cfg, feed_stream)` to instantiate `SimulatorRunHFM` and wrap it in `HFMMembrane`.
3. Registers the unit in the `Flowsheet` and connects the three ports automatically.

---

## 📊 Results & Diagnostics

After `solve()`, the following values are stored in `hfm.results`:

| Key | Type | Description |
|-----|------|-------------|
| `n_cells` | `int` | Number of axial finite volumes |
| `solver_paths` | `str` | Convergence path description from internal solver |
| `retentate_molar_flow` | `float` | Retentate total molar flow [mol/s] |
| `permeate_molar_flow` | `float` | Permeate total molar flow [mol/s] |
| `stage_cut` | `float` | `perm_flow / (perm_flow + ret_flow)` |

Access them like this:

```python
print(f"Stage cut: {hfm.results['stage_cut']:.4f}")
print(f"Solver path: {hfm.results['solver_paths']}")
```

Console output during solve:
```
  [HFM1] Converged via: path_A
  [HFM1] Retentate: 0.002500 mol/s, T=312.50 K, P=4.850 bar
  [HFM1] Permeate:  0.000800 mol/s, T=310.20 K, P=1.000 bar
  [HFM1] Stage cut: 0.2424
```

---

## ⚠️ Error Handling

| Exception / Condition | When |
|-----------------------|------|
| `RuntimeError` | `feed` port is not connected to any stream |
| `self.warnings` appended | Internal solver reports infeasible (outlet streams are **not** updated) |
| `AttributeError` (defensive) | `results.feasible` missing — assumed `True` for backward compatibility |

---

## 📝 Notes

- `HFMMembrane` is **physics-agnostic**. All membrane physics (permeance, geometry, energy balance, pressure drop, fugacity) live inside `SimulatorRunHFM`.
- The internal solver is stored as `self._sim` (leading underscore = internal API). Do not access it from flowsheet code.
- Outlet streams are updated **in-place** via `Stream.update()`. This refreshes all CoolProp-derived properties (density, enthalpy, viscosity, etc.) automatically.
- Temperature arrays (`results.T_ret`, `results.T_per`) are checked for `None` and non-zero length before indexing. If missing, the feed temperature is used as fallback.
- The `_last_result` attribute stores the raw `SimulatorResultsHFM` object, which can be used for Excel export or detailed post-processing.

---

## 🔗 Related Classes

| Class | File | Role |
|-------|------|------|
| `UnitOperation` | `Common/Process_Simulator/unit_operation.py` | Base class — provides port management and `solve()` contract |
| `Flowsheet` | `Common/Process_Simulator/flowsheet.py` | Topology container — owns units and streams |
| `SequentialSolver` | `Common/Process_Simulator/solvers.py` | Topological solver that calls `unit.solve()` in order |
| `SimulatorRunHFM` | `Simulator_HFM/Simulator_Run_HFM.py` | Internal axial membrane solver (physics engine) |
| `SimulatorGeometryHFM` | `Simulator_HFM/Simulator_Geometry_HFM.py` | Membrane geometry data container |
| `Membrane_Permeance` | `Common/Membrane_Properties/Permeance/Membrane_Permeance.py` | Permeance data container |
| `Stream` | `Common/Stream/stream.py` | Thermodynamic state representation |

---

## 📄 License

*(Add your license here)*

## 👤 Contact

*(Add maintainer info here)*
