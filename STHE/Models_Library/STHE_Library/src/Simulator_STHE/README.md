# Shell-and-Tube Heat Exchanger (STHE) Simulator

A modular **shell-and-tube heat exchanger simulator** that performs thermal rating and simulation using classical literature correlations (Kern, Bell-Delaware, Gnielinski, etc.).

---

## 📁 Package Structure

```
Common/Unit_Operation/STHE/
├── __init__.py
├── STHE.py                 # Main simulator class
├── Geometry_STHE.py        # Exchanger geometry definitions
├── Stream_STHE.py          # Process stream definitions
├── Options_STHE.py         # Solver & correlation options
├── Methods_STHE.py         # Available correlation enumerations
└── Calculations_STHE/      # Classical literature correlations
    ├── Calculations_HEX_heatload.py
    ├── Calculations_HEX_LMTD.py
    ├── Calculations_STHE_correction_factor.py
    ├── Calculations_STHE_DeltaPtubeside.py
    ├── Calculations_STHE_DeltaPshellside.py
    ├── Calculations_STHE_U.py
    ├── Calculations_STHE_required_area.py
    ├── Calculations_STHE_area.py
    └── Calculations_STHE_NTU.py
```

---

## 🏗️ Class: `STHE`

Main entry point of the library. Encapsulates geometry, process streams, and calculation options.

### Constructor

```python
from Common.Unit_Operation.STHE import STHE

sthe = STHE()
```

No arguments are required at instantiation. All data are attached via the three public containers described below.

---

## 📐 Geometry (`STHE.geometry`)

Instance of `Geometry` (from `Geometry_STHE.py`).

```python
sthe.geometry.shell.diameter           # Shell inside diameter [m]
sthe.geometry.shell.fouling_factor     # Shell-side fouling factor [m²·K/W]

sthe.geometry.tubes.length             # Tube length [m]
sthe.geometry.tubes.outside_diameter   # Tube OD [m]
sthe.geometry.tubes.inside_diameter    # Tube ID [m]
sthe.geometry.tubes.pitch_ratio        # Pitch ratio (-)
sthe.geometry.tubes.layout             # Layout pattern (e.g. "triangular", "square")
sthe.geometry.tubes.passes             # Number of tube passes (-)
sthe.geometry.tubes.wall_conductivity  # Tube wall conductivity [W/(m·K)]
sthe.geometry.tubes.fouling_factor     # Tube-side fouling factor [m²·K/W]
sthe.geometry.tubes.stream             # "hot_stream" or "cold_stream"

sthe.geometry.baffles.number           # Number of baffles (-)
sthe.geometry.baffles.cut              # Baffle cut fraction (-)
sthe.geometry.baffles.sealing_strips   # Number of sealing strips (-)
```

---

## 🌊 Streams (`STHE.streams`)

Instance of `Streams` (from `Stream_STHE.py`). Each stream (`hot` / `cold`) has an `inlet` and `outlet` `State`.

```python
# Hot stream inlet
sthe.streams.hot.inlet.temperature     # [K]
sthe.streams.hot.inlet.pressure        # [Pa]
sthe.streams.hot.inlet.flow            # [kg/s]
sthe.streams.hot.inlet.fluid           # Fluid name / mixture identifier
sthe.streams.hot.inlet.density         # [kg/m³]
sthe.streams.hot.inlet.viscosity       # [Pa·s]
sthe.streams.hot.inlet.cp              # [J/(kg·K)]
sthe.streams.hot.inlet.conductivity    # [W/(m·K)]

# Hot stream outlet (set by simulator in simulation mode)
sthe.streams.hot.outlet.temperature    # [K]

# Same structure for cold stream
sthe.streams.cold.inlet.temperature
sthe.streams.cold.outlet.temperature
```

---

## ⚙️ Options (`STHE.options`)

Instance of `Options` (from `Options_STHE.py`).

```python
sthe.options.solver.tolerance            # Numerical tolerance (default: 1e-6)
sthe.options.solver.maximum_iterations   # Max iterations (default: 100)
sthe.options.solver.verbosity            # "normal" | ...

sthe.options.properties.flow_basis       # "mass" (default)
sthe.options.properties.property_package # "CoolProp" (default)

sthe.options.correlations.tube_method    # "Gnielinski" (default)
sthe.options.correlations.shell_method   # "Bell" (default)
sthe.options.correlations.Xp             # LMTD correction parameter (default: 0.9)

sthe.options.report.summary              # Print summary (default: True)
sthe.options.report.log                  # Save log (default: True)
```

### Available Correlations

| Side | Enum | Values |
|------|------|--------|
| **Tube-side heat transfer** | `TubeMethod` | `Dewiit_Saunders`, `Gnielinski`, `Hausen`, `Sieder_Tate`, `Dittus_Boelter` |
| **Shell-side heat transfer** | `ShellMethod` | `Bell`, `Kern` |

```python
from Common.Unit_Operation.STHE.Methods_STHE import TubeMethod, ShellMethod

sthe.options.correlations.tube_method = TubeMethod.GNIELINSKI
sthe.options.correlations.shell_method = ShellMethod.BELL
```

---

## 🔬 Calculation Modes

### 1. Rating

**Known:** Geometry, inlet *and* outlet temperatures (both sides).  
**Calculated:** Heat duty, LMTD, correction factor, overall coefficient, required vs. installed area, pressure drops, oversurface.

```python
sthe.rating()
```

**Results stored as attributes:**

| Attribute | Unit | Description |
|-----------|------|-------------|
| `sthe.Q_hot` | W | Hot-side heat duty |
| `sthe.Q_cold` | W | Cold-side heat duty |
| `sthe.LMTD` | K | Log-mean temperature difference |
| `sthe.F` | — | LMTD correction factor |
| `sthe.U` | W/(m²·K) | Overall heat-transfer coefficient |
| `sthe.RequiredArea` | m² | Heat-transfer area required by duty |
| `sthe.Area` | m² | Installed (geometric) heat-transfer area |
| `sthe.Oversurface` | % | `(Area − RequiredArea) / RequiredArea × 100` |
| `sthe.DeltaP_tube` | Pa | Tube-side pressure drop |
| `sthe.DeltaP_shell` | Pa | Shell-side pressure drop |

**Energy balance check:** If `|Q_hot − Q_cold| / max(|Q_hot|, |Q_cold|) > 1e-3`, a warning is printed.

---

### 2. Simulation

**Known:** Geometry, inlet temperatures and flows (both sides).  
**Calculated:** Outlet temperatures, heat duty, effectiveness, NTU, pressure drops, overall coefficient.

```python
results = sthe.simulate()
```

**Returns a dictionary with:**

| Key | Unit | Description |
|-----|------|-------------|
| `HeatDuty` | W | Actual heat transfer rate |
| `NTU` | — | Number of transfer units |
| `Effectiveness` | — | Thermal effectiveness |
| `ToutHot` | K | Hot outlet temperature |
| `ToutCold` | K | Cold outlet temperature |

**Also stored as attributes:**

| Attribute | Unit | Description |
|-----------|------|-------------|
| `sthe.Q` | W | Heat duty |
| `sthe.NTU` | — | Number of transfer units |
| `sthe.Effectiveness` | — | Effectiveness |
| `sthe.U` | W/(m²·K) | Overall coefficient |
| `sthe.Area` | m² | Installed area |
| `sthe.DeltaP_tube` | Pa | Tube-side pressure drop |
| `sthe.DeltaP_shell` | Pa | Shell-side pressure drop |
| `sthe.streams.hot.outlet.temperature` | K | Updated hot outlet |
| `sthe.streams.cold.outlet.temperature` | K | Updated cold outlet |

---

## 🚀 Complete Usage Example

```python
from Common.Unit_Operation.STHE import STHE
from Common.Unit_Operation.STHE.Methods_STHE import TubeMethod, ShellMethod

# --- Create instance ---
sthe = STHE()

# --- Geometry ---
sthe.geometry.shell.diameter = 0.5          # m
sthe.geometry.shell.fouling_factor = 1e-4   # m²·K/W

sthe.geometry.tubes.length = 4.0
sthe.geometry.tubes.outside_diameter = 0.01905  # 3/4 inch
sthe.geometry.tubes.inside_diameter = 0.015748  # 16 BWG
sthe.geometry.tubes.pitch_ratio = 1.25
sthe.geometry.tubes.layout = "triangular"
sthe.geometry.tubes.passes = 2
sthe.geometry.tubes.wall_conductivity = 45.0   # Carbon steel
sthe.geometry.tubes.fouling_factor = 1e-4
sthe.geometry.tubes.stream = "hot_stream"      # Hot fluid inside tubes

sthe.geometry.baffles.number = 10
sthe.geometry.baffles.cut = 0.25
sthe.geometry.baffles.sealing_strips = 1

# --- Streams (Rating mode: all four temperatures known) ---
sthe.streams.hot.inlet.temperature = 393.15   # 120 °C
sthe.streams.hot.outlet.temperature = 353.15  # 80 °C
sthe.streams.hot.inlet.flow = 5.0             # kg/s
sthe.streams.hot.inlet.cp = 2100.0            # J/(kg·K)
sthe.streams.hot.inlet.density = 850.0
sthe.streams.hot.inlet.viscosity = 0.001
sthe.streams.hot.inlet.conductivity = 0.15

sthe.streams.cold.inlet.temperature = 298.15  # 25 °C
sthe.streams.cold.outlet.temperature = 333.15 # 60 °C
sthe.streams.cold.inlet.flow = 10.0
sthe.streams.cold.inlet.cp = 4180.0
sthe.streams.cold.inlet.density = 1000.0
sthe.streams.cold.inlet.viscosity = 0.00089
sthe.streams.cold.inlet.conductivity = 0.6

# --- Options ---
sthe.options.correlations.tube_method = TubeMethod.GNIELINSKI
sthe.options.correlations.shell_method = ShellMethod.BELL
sthe.options.correlations.Xp = 0.9

# --- Run rating ---
sthe.rating()

print(f"U            = {sthe.U:.2f} W/(m²·K)")
print(f"RequiredArea = {sthe.RequiredArea:.2f} m²")
print(f"Area         = {sthe.Area:.2f} m²")
print(f"Oversurface  = {sthe.Oversurface:.1f} %")
print(f"ΔP tube      = {sthe.DeltaP_tube/1e5:.3f} bar")
print(f"ΔP shell     = {sthe.DeltaP_shell/1e5:.3f} bar")
```

---

## ⚠️ Error Handling

| Exception | When |
|-----------|------|
| `ValueError` | `geometry.tubes.stream` is not `"hot_stream"` or `"cold_stream"` |
| `ValueError` | Calculated outlet pressure ≤ 0 (implied by correlation internals) |
| `RuntimeError` | Missing required stream or geometry attributes (`None` values passed to calculations) |

---

## 📝 Notes

- **Classical correlations:** All heat-transfer and pressure-drop calculations rely on established literature methods (Kern, Bell-Delaware, Gnielinski, Dittus–Boelter, etc.) implemented under `Calculations_STHE/`.
- **Legacy API bridge:** The simulator internally wraps scalar inputs with `np.atleast_1d(...)` to remain compatible with the array-based legacy calculation layer.
- **Energy balance:** Rating mode checks energy closure between hot and cold sides. A mismatch > 0.1 % triggers a console warning.
- **TEMA E assumption:** The NTU simulation routine assumes a single shell pass (`shell_passes = 1`).
- **Flow basis:** The current implementation expects **mass-flow basis** (`kg/s`) and mass-specific properties (`J/(kg·K)`, etc.).

---

## 🔗 Related Classes

| Class | File | Description |
|-------|------|-------------|
| `Geometry` | `Geometry_STHE.py` | Shell, tube bundle, and baffle geometry containers |
| `Streams` / `State` | `Stream_STHE.py` | Hot / cold stream inlet & outlet state containers |
| `Options` | `Options_STHE.py` | Solver, property, correlation, and report settings |

---

## 📄 License

*(Add your license here)*

## 👤 Contact

*(Add maintainer info here)*
