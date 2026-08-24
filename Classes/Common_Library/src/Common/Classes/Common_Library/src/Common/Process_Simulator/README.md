# Process Flowsheet Framework

A lightweight, modular Python framework for building and solving chemical process flowsheets. It follows a clean **separation of concerns**: the `Flowsheet` manages topology, `UnitOperation` subclasses contain physics, and `Solver` classes orchestrate execution.

---

## 📦 What's Inside

| File | Purpose |
|------|---------|
| `flowsheet.py` | The `Flowsheet` class — owns units, streams, and connections. Pure data container, zero physics. |
| `unit_operation.py` | The `UnitOperation` base class — equipment with input/output ports and a `solve()` contract. |
| `base_equipment.py` | `BaseEquipment` — common metadata, status, diagnostics, and runtime state for every piece of equipment. |
| `port.py` | `Port` and `PortDirection` — typed connection points between units and streams. |
| `solvers.py` | `SequentialSolver` — topological sort (Kahn's algorithm) + sequential modular execution. |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Flowsheet                             │
│  ┌─────────┐   Stream   ┌─────────┐   Stream   ┌─────────┐  │
│  │ Unit A  │◄──────────►│ Unit B  │◄──────────►│ Unit C  │  │
│  │(ports)  │            │(ports)  │            │(ports)  │  │
│  └────┬────┘            └────┬────┘            └────┬────┘  │
│       │                      │                      │         │
│       └──────────────────────┴──────────────────────┘         │
│                         (connections)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ SequentialSolver│
                    │  • topo sort    │
                    │  • solve_unit() │
                    │  • hooks        │
                    └─────────────────┘
```

**Design principles:**

1. **Flowsheet knows topology, not physics.** It connects ports to streams but never calls `solve()`.
2. **UnitOperation knows physics, not topology.** It reads from input ports and writes to output ports.
3. **Solver knows order, not physics.** It decides *when* to call `solve()` via topological sort.
4. **Ports are typed.** Every port is `INPUT` or `OUTPUT`. Connections are validated at wiring time.

---

## 🚀 Quick Start

### 1. Define a custom unit

Inherit from `UnitOperation`, register ports in `__init__`, and implement `solve()`.

```python
from unit_operation import UnitOperation, PortDirection
from stream import Stream  # your Stream class (CoolProp-backed, etc.)

class Mixer(UnitOperation):
    '''Simple isothermal, isobaric mixer.'''

    def __init__(self, name: str):
        super().__init__(name, tag="MX", description="Isothermal mixer")
        self.add_port("in1", PortDirection.INPUT)
        self.add_port("in2", PortDirection.INPUT)
        self.add_port("out", PortDirection.OUTPUT)

    def solve(self) -> None:
        s1 = self.in1.stream
        s2 = self.in2.stream

        # Mole-balance mixing
        total_flow = s1.molar_flow + s2.molar_flow
        mixed_comp = {
            c: (s1.composition[c] * s1.molar_flow + s2.composition[c] * s2.molar_flow) / total_flow
            for c in s1.composition
        }

        self.out.stream.composition = mixed_comp
        self.out.stream.molar_flow = total_flow
        self.out.stream.T = s1.T          # isothermal
        self.out.stream.P = s1.P          # isobaric
```

### 2. Build a flowsheet

```python
from flowsheet import Flowsheet
from stream import Stream, ThermoBackend

# --- Streams ---
feed_a = Stream(composition={"CO2": 0.5, "N2": 0.5}, P=10e5, T=300, molar_flow=1.0,
                backend=ThermoBackend.HEOS)
feed_b = Stream(composition={"CO2": 0.2, "CH4": 0.8}, P=10e5, T=300, molar_flow=0.5,
                backend=ThermoBackend.HEOS)
product = Stream(composition={"CO2": 0.0, "N2": 0.0, "CH4": 0.0}, P=10e5, T=300, molar_flow=0.0,
                 backend=ThermoBackend.HEOS)

# --- Units ---
mixer = Mixer("MIX-101")

# --- Flowsheet ---
fs = Flowsheet(name="Simple Mixer")
fs.add_stream("FeedA", feed_a)
fs.add_stream("FeedB", feed_b)
fs.add_stream("Product", product)
fs.add_unit("MIX-101", mixer)

# --- Connect ---
fs.connect(stream="FeedA", destination=("MIX-101", "in1"))
fs.connect(stream="FeedB", destination=("MIX-101", "in2"))
fs.connect(source=("MIX-101", "out"), stream="Product")
```

### 3. Solve

```python
from solvers import SequentialSolver

solver = SequentialSolver(fs)
solver.solve()

print(fs.report())
```

---

## 🔌 Port & Connection API

### Adding ports to a unit

```python
self.add_port("feed", PortDirection.INPUT)
self.add_port("retentate", PortDirection.OUTPUT)
```

Ports are exposed as attributes:

```python
unit.feed          # Port object
unit.feed.stream   # attached Stream (None if not connected)
```

### Connecting in the Flowsheet

```python
# Feed stream -> unit inlet
fs.connect(stream="Feed", destination=("HFM1", "feed"))

# Unit outlet -> intermediate stream
fs.connect(source=("HFM1", "retentate"), stream="Retentate")

# Full pass-through
fs.connect(source=("HFM1", "retentate"), stream="RetGas", destination=("STHE1", "tube_in"))

# System product (no downstream unit)
fs.connect(source=("STHE1", "shell_out"), stream="Product")
```

> **Validation:** `Flowsheet.connect()` enforces that sources are `OUTPUT` ports, destinations are `INPUT` ports, and no port is double-connected.

---

## 🧮 Solver

### SequentialSolver

The default solver:
1. Builds a dependency graph from `stream.producer` / `stream.consumer`.
2. Runs **Kahn's topological sort**.
3. Solves each unit in order via `solve_unit()`.
4. Raises `RuntimeError` with tear-stream candidates if a **recycle loop** is detected.

```python
solver = SequentialSolver(flowsheet)
order = solver.solve()   # returns the execution order
```

### Hooks

Override hooks to add logging, timing, or convergence checks without touching equipment code:

```python
class MySolver(SequentialSolver):
    def before_solve(self, unit):
        print(f"Solving {unit.name}...")
        super().before_solve(unit)

    def after_solve(self, unit):
        print(f"  -> converged in {unit.solve_time*1e3:.2f} ms")
        super().after_solve(unit)
```

---

## 🧬 Inheritance Tree

```
BaseEquipment (ABC)
    └── UnitOperation (ABC)
            ├── HFMMembrane
            ├── Compressor
            ├── Mixer
            ├── HeatExchanger
            └── ...your custom units
```

### BaseEquipment

Every equipment has:
- `name`, `tag`, `description`
- `status`: `"uninitialized"` → `"solving"` → `"converged"` / `"error"`
- `warnings`: list of strings
- `results`: dict for arbitrary post-processed data
- `solve_time`: float (seconds)
- `calculation_options`: dict for solver knobs

### UnitOperation

Extends `BaseEquipment` with:
- `_ports`: dict of `Port` objects
- `input_ports` / `output_ports`: filtered lists
- `add_port(name, direction)` — creates and exposes the port
- `solve()` — **abstract method** you must implement

---

## 📊 Diagnostics & Reporting

### Flowsheet report

```python
print(fs.report())
```

Produces:
```
============================================================
  FLOWSHEET: CO2 Capture
============================================================

  FEEDS (streams with no producer):
    • Feed

  PRODUCTS (streams with no consumer):
    • Retentate
    • Permeate

  CONNECTIONS:
    [OK] FEED                 -- Feed            --> HFM1.feed
    [OK] HFM1.retentate       -- Retentate       --> PRODUCT
    [OK] HFM1.permeate        -- Permeate        --> PRODUCT

  UNITS:
    • HFM1 [converged]: IN(feed=Feed) -> OUT(retentate=Retentate, permeate=Permeate)
============================================================
```

### Unit diagnostics

```python
unit.status        # "converged", "error", "solving", ...
unit.solve_time    # seconds
unit.warnings      # list of strings
unit.results       # dict of post-processed data
```

---

## ⚠️ Error Handling

| Exception | When | Message hints |
|-----------|------|---------------|
| `ValueError` | Port already exists on unit | `"Port 'X' already exists on unit 'Y'"` |
| `ValueError` | Bad connection direction | `"Source '...' must be an OUTPUT port"` |
| `ValueError` | Double-connected port | `"Source '...' is already connected to '...'"` |
| `ValueError` | Unconnected INPUT port at solve time | `"INPUT port not connected: U.port"` |
| `RuntimeError` | Recycle loop detected | `"Cycle detected in units: [...]"` + tear-stream candidates |

---

## 🧪 Testing a New Unit

Minimal test scaffold:

```python
def test_mixer():
    from flowsheet import Flowsheet
    from solvers import SequentialSolver
    from stream import Stream, ThermoBackend

    fs = Flowsheet("Test")
    # ... create streams, unit, connect ...

    solver = SequentialSolver(fs)
    order = solver.solve()

    assert "MIX-101" in order
    assert fs.units["MIX-101"].status == "converged"
    assert fs.streams["Product"].molar_flow > 0
```

---

## 📝 Checklist: Adding a New Unit

- [ ] Inherit from `UnitOperation`
- [ ] Call `super().__init__(...)` with `name`, `tag`, `description`
- [ ] Register all ports with `self.add_port(name, PortDirection.INPUT/OUTPUT)`
- [ ] Implement `solve(self) -> None`
- [ ] Read from `self.<input_port>.stream` (do not modify input streams in-place unless intended)
- [ ] Write results to `self.<output_port>.stream`
- [ ] (Optional) Populate `self.results` for post-processing
- [ ] Add the unit to a `Flowsheet` and connect streams before solving

---

## 🔄 Extending the Framework

### Tear-stream / recycle solver

`SequentialSolver` detects cycles and raises an error with candidate tear streams. To handle recycles, subclass `SequentialSolver`:

```python
class RecycleSolver(SequentialSolver):
    def solve(self):
        # 1. Identify tear streams from the cycle error
        # 2. Guess tear-stream values
        # 3. Run SequentialSolver on the acyclic subgraph
        # 4. Update tear streams and iterate until convergence
        ...
```

### New equipment categories

If you need equipment without ports (e.g., a pure calculator or cost estimator), inherit directly from `BaseEquipment`. If it interacts with streams, inherit from `UnitOperation`.

---

## 📄 License

*(Add your license here)*

## 👤 Contact

*(Add maintainer info here)*
