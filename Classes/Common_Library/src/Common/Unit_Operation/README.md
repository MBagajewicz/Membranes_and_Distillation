# Common Unit Operations

This package contains steady-state unit operations for the Process Simulator flowsheet engine.

---

## 📁 Location

```
Common/Unit_Operation/
├── Compressor.py
└── Mixer.py
```

---

# 1. Compressor

A simple **isentropic compressor** implemented as a `UnitOperation`. It computes discharge temperature, real (non-isentropic) outlet conditions, and compression power from an inlet stream.

---

## 🏗️ Class: `Compressor`

Inherits from `UnitOperation` (see `Process_Simulator` framework).

### Constructor

```python
Compressor(
    name: str,
    P_out: float,
    efficiency: float = 0.8,
    gamma: float = 1.3,
    tag: str = "",
    description: str = "",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | **required** | Unit name in the flowsheet (e.g., `"COMP1"`). |
| `P_out` | `float` | **required** | Discharge pressure **[Pa]**. |
| `efficiency` | `float` | `0.8` | Isentropic efficiency **(0–1)**. |
| `gamma` | `float` | `1.3` | Heat capacity ratio **cp / cv**. Typical values: ~1.2–1.3 for CO₂ / light-hydrocarbon mixtures. |
| `tag` | `str` | `""` | Equipment tag (e.g., `"K-101"`). |
| `description` | `str` | `""` | Human-readable description. |

### Ports

| Port | Direction | Description |
|------|-----------|-------------|
| `inlet` | `INPUT` | Suction stream. Must be connected before solving. |
| `outlet` | `OUTPUT` | Discharge stream. Must be connected before solving. |

Ports are exposed as attributes:

```python
comp.inlet    # Port object
comp.outlet   # Port object
comp.inlet.stream   # attached Stream
```

---

## ⚙️ Physics

### Isentropic outlet temperature

```
T_isen = T_in * (P_out / P_in)^((gamma - 1) / gamma)
```

### Real outlet temperature (accounting for inefficiency)

```
delta_T_isen = T_isen - T_in
delta_T_real = delta_T_isen / efficiency
T_out = T_in + delta_T_real
```

### Compression power

```
W = n_dot * cp * delta_T_real     [W]
```

Where:
- `n_dot` = inlet molar flow [mol/s]
- `cp` = molar heat capacity [J/(mol·K)] — fetched from the inlet stream if available, otherwise falls back to `35.0 J/(mol·K)`.

---

## 🚀 Usage

### Standalone in a flowsheet

```python
from Common.Process_Simulator import Flowsheet
from Common.Unit_Operation.Compressor import Compressor
from Common.Stream.stream import Stream, ThermoBackend

# --- Streams ---
feed = Stream(
    composition={"CO2": 0.5, "Propane": 0.5},
    P=1e5,               # 1 bar
    T=313.0,             # K
    molar_flow=0.0033,   # mol/s
    backend=ThermoBackend.HEOS,
)
discharge = Stream(
    composition={"CO2": 0.5, "Propane": 0.5},
    P=5e5,               # will be overwritten by compressor
    T=313.0,
    molar_flow=0.0033,
    backend=ThermoBackend.HEOS,
)

# --- Unit ---
comp = Compressor(
    name="COMP1",
    P_out=5e5,           # 5 bar discharge
    efficiency=0.75,
    gamma=1.3,
    tag="K-101",
    description="Permeate recompression",
)

# --- Flowsheet ---
fs = Flowsheet(name="Compression Stage")
fs.add_stream("S_in", feed)
fs.add_stream("S_out", discharge)
fs.add_unit("COMP1", comp)

fs.connect(stream="S_in", destination=("COMP1", "inlet"))
fs.connect(source=("COMP1", "outlet"), stream="S_out")

# --- Solve ---
from Common.Process_Simulator import SequentialSolver
solver = SequentialSolver(fs)
solver.solve()
```

### In a multi-stage membrane cascade

A common pattern: permeate from an upstream membrane is at low pressure and must be recompressed before entering a downstream membrane.

```python
EQUIPMENT_CONFIG = [
    {"type": "HFM", "name": "HFM1", ...},
    {
        "type": "Compressor",
        "name": "COMP1",
        "P_out": 5e5,
        "efficiency": 0.75,
        "gamma": 1.3,
    },
    {"type": "HFM", "name": "HFM2", "PPerm": 1e5, ...},
]

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "permeate"), "to": "Permeate1_to_Comp"},
    {"from": "Permeate1_to_Comp", "to": ("COMP1", "inlet")},
    {"from": ("COMP1", "outlet"), "to": "Compressed_to_HFM2"},
    {"from": "Compressed_to_HFM2", "to": ("HFM2", "feed")},
    # ...
]
```

---

## 📊 Results & Diagnostics

After `solve()`, the following values are stored in `comp.results`:

| Key | Unit | Description |
|-----|------|-------------|
| `work_W` | W | Compression power |
| `T_isentropic_K` | K | Isentropic discharge temperature |
| `pressure_ratio` | — | `P_out / P_in` |
| `cp_molar_J_mol_K` | J/(mol·K) | Molar heat capacity used in the power calculation |

Access them like this:

```python
print(f"Power: {comp.results['work_W']:.2f} W")
print(f"Isentropic T: {comp.results['T_isentropic_K']:.2f} K")
```

Console output during solve:
```
  [COMP1] Compressed 1.000 → 5.000 bar
  [COMP1] T: 313.00 → 385.42 K  (isen: 367.57 K)
  [COMP1] Power: 8.456 W  (0.008 kW)
```

---

## ⚠️ Error Handling

| Exception | When |
|-----------|------|
| `RuntimeError` | `inlet` or `outlet` port is not connected to a stream |
| `ValueError` | `P_out <= P_in` (compressor would not compress) |

---

## 📝 Notes

- The compressor **copies the inlet composition** to the outlet; it does **not** perform separation.
- Molar flow is conserved (`n_dot_out = n_dot_in`).
- The outlet stream is updated in-place via `outlet.update(...)`.
- If the inlet stream does not expose `cp_molar` or `cp_mass`/`molar_mass`, a fallback of `35.0 J/(mol·K)` is used. For accurate power estimates, ensure your `Stream` class provides heat capacity properties.
- For mixtures with strongly temperature-dependent `cp` or `gamma`, consider subclassing and overriding `_get_cp_molar()` to use a more sophisticated EOS-based calculation.

---

---

# 2. Mixer

A generic **steady-state adiabatic material mixer** implemented as a `UnitOperation`. It combines multiple inlet streams into a single outlet stream using total and component molar balances together with an adiabatic energy balance.

---

## 🏗️ Class: `Mixer`

Inherits from `UnitOperation` (see `Process_Simulator` framework).

### Constructor

```python
Mixer(
    name: str,
    number_of_inlets: int = 2,
    pressure_mode: str = "lowest_inlet",
    P_out: float | None = None,
    pressure_drop: float = 0.0,
    tag: str = "",
    description: str = "",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | **required** | Unit name in the flowsheet (e.g., `"MIX1"`). |
| `number_of_inlets` | `int` | `2` | Number of material inlet ports. Must be ≥ 2. |
| `pressure_mode` | `str` | `"lowest_inlet"` | Method used to determine outlet pressure: `"lowest_inlet"` or `"fixed"`. |
| `P_out` | `float` | `None` | Fixed outlet pressure **[Pa]**. Required when `pressure_mode="fixed"`. |
| `pressure_drop` | `float` | `0.0` | Additional pressure drop applied to the reference pressure **[Pa]**. Must be non-negative. |
| `tag` | `str` | `""` | Equipment tag (e.g., `"MX-101"`). |
| `description` | `str` | `""` | Human-readable description. |

### Ports

| Port | Direction | Description |
|------|-----------|-------------|
| `inlet_1` … `inlet_N` | `INPUT` | Material inlet streams. `N = number_of_inlets`. Must all be connected before solving. |
| `outlet` | `OUTPUT` | Mixed outlet stream. Must be connected before solving. |

---

## ⚙️ Physics

### Assumptions

- Steady state
- No chemical reaction
- No heat transfer (adiabatic)
- No shaft work
- Negligible accumulation

### Molar balance

```
n_dot_out = Σ n_dot_in,i
```

### Component molar balance

```
z_j,out = (Σ n_dot_in,i * z_j,in,i) / n_dot_out
```

Where `z_j` is the mole fraction of component `j`.

### Adiabatic energy balance

```
H_dot_out = Σ H_dot_in,i
h_out = H_dot_out / n_dot_out
```

The outlet temperature is solved iteratively (bisection method, 50–2000 K) so that the outlet molar enthalpy matches the mixed specific enthalpy `h_out` at the calculated outlet pressure and composition.

### Outlet pressure

| Mode | Formula |
|------|---------|
| `lowest_inlet` | `P_out = min(P_in,i) - pressure_drop` |
| `fixed` | `P_out = P_out_fixed - pressure_drop` |

---

## 🚀 Usage

### Standalone in a flowsheet

```python
from Common.Process_Simulator import Flowsheet
from Common.Unit_Operation.Mixer import Mixer
from Common.Stream.stream import Stream, ThermoBackend

# --- Streams ---
feed_a = Stream(
    composition={"CO2": 0.9, "Propane": 0.1},
    P=1e5,
    T=300.0,
    molar_flow=0.002,
    backend=ThermoBackend.HEOS,
)
feed_b = Stream(
    composition={"CO2": 0.3, "Propane": 0.7},
    P=1.2e5,
    T=350.0,
    molar_flow=0.001,
    backend=ThermoBackend.HEOS,
)
mixed = Stream(
    composition={"CO2": 0.5, "Propane": 0.5},  # initial guess, will be overwritten
    P=1e5,
    T=320.0,
    molar_flow=0.003,
    backend=ThermoBackend.HEOS,
)

# --- Unit ---
mix = Mixer(
    name="MIX1",
    number_of_inlets=2,
    pressure_mode="lowest_inlet",
    pressure_drop=500.0,
    tag="MX-101",
    description="Permeate + recycle mixer",
)

# --- Flowsheet ---
fs = Flowsheet(name="Mixing Stage")
fs.add_stream("S_A", feed_a)
fs.add_stream("S_B", feed_b)
fs.add_stream("S_mix", mixed)
fs.add_unit("MIX1", mix)

fs.connect(stream="S_A", destination=("MIX1", "inlet_1"))
fs.connect(stream="S_B", destination=("MIX1", "inlet_2"))
fs.connect(source=("MIX1", "outlet"), stream="S_mix")

# --- Solve ---
from Common.Process_Simulator import SequentialSolver
solver = SequentialSolver(fs)
solver.solve()
```

### Fixed outlet pressure mode

```python
mix = Mixer(
    name="MIX1",
    number_of_inlets=3,
    pressure_mode="fixed",
    P_out=2e5,          # 2 bar
    pressure_drop=1000.0,
)
```

---

## 📊 Results & Diagnostics

After `solve()`, the following values are stored in `mix.results`:

| Key | Unit | Description |
|-----|------|-------------|
| `molar_flow` | mol/s | Total outlet molar flow |
| `mass_flow` | kg/s | Total outlet mass flow |
| `P_out` | Pa | Outlet pressure |
| `T_out` | K | Outlet temperature |
| `enthalpy_flow` | W | Total outlet enthalpy flow |

Access them like this:

```python
print(f"Mixed T: {mix.results['T_out']:.2f} K")
print(f"Mixed P: {mix.results['P_out']:.2f} Pa")
print(f"Total flow: {mix.results['molar_flow']:.4f} mol/s")
```

---

## ⚠️ Error Handling

| Exception | When |
|-----------|------|
| `ValueError` | `number_of_inlets < 2` |
| `ValueError` | `pressure_mode` not in `{"lowest_inlet", "fixed"}` |
| `ValueError` | `pressure_mode="fixed"` and `P_out` is `None` |
| `ValueError` | `pressure_drop < 0` |
| `RuntimeError` | Any inlet port is not connected to a stream |
| `RuntimeError` | `outlet` port is not connected to a stream |
| `ValueError` | Calculated outlet pressure ≤ 0 |
| `ValueError` | Total inlet molar flow ≤ 0 |
| `ValueError` | Target outlet enthalpy outside the temperature search interval [50, 2000] K |

---

## 📝 Notes

- The mixer **does not perform separation or reaction**; it only blends streams.
- Molar and component flows are strictly conserved.
- The outlet stream is updated in-place via `outlet.update(...)`.
- Outlet temperature is found with an internal bisection solver (tolerance `1e-6`, max 100 iterations) to avoid adding an external numerical dependency to `Common_Library`.
- For highly non-ideal mixtures or enthalpy functions with discontinuities, the bisection interval [50, 2000] K may need to be adjusted by subclassing and overriding `_solve_outlet_temperature()`.

---

## 🔗 Related Classes

| Class | File | Description |
|-------|------|-------------|
| `UnitOperation` | `Process_Simulator/unit_operation.py` | Base class with port management and `solve()` contract |
| `Flowsheet` | `Process_Simulator/flowsheet.py` | Topology container — owns units and streams |
| `SequentialSolver` | `Process_Simulator/solvers.py` | Topological solver that calls `unit.solve()` in order |
| `Stream` | `Common/Stream/stream.py` | Thermodynamic stream object (CoolProp-backed) |

---

## 📄 License

*(Add your license here)*

## 👤 Contact

*(Add maintainer info here)*
