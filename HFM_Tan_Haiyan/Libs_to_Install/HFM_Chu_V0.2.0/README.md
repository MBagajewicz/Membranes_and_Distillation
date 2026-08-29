# HFM Simulator

NEW IMPLEMENTATION in 0.1.1
- Permeance and permeability options added in example (test_simulation.py and scenarios.py)
- Energy packages modified to HEOS to manage properties in U variable
- Energy balance modified (energy_module.pý) to manage U variable
 

A modular Python framework for simulating **Hollow Fiber Membrane (HFM)** systems, including:

* Mass balance (multi-component)
* Optional energy balance
* Optional pressure drop
* Stream-based connectivity between unit operations

---

## 🚀 Installation

From the root of the project:

```bash
pip install -e .
```

This installs the package in **editable mode**, allowing you to modify the code without reinstalling.

---

## ⚠️ Required folders for examples

To run the provided examples, you must create the following folders inside `run_examples/`:

```
run_examples/
├── scenarios_examples/
│   └── scenarios.py
│
├── properties_examples/
│   ├── Calculations_prop_Viscosity_gas_mix.py
│   └── Mixture_Properties.py
```

These are **NOT part of the package** by design.

### Why?

* `scenarios_examples` → literature cases, user-defined inputs
* `properties_examples` → thermophysical models (customizable)

This keeps the core simulator **clean and reusable**.

---

## 🧠 Architecture

The simulator is built around three main objects:

### 1. `Stream`

Represents a material stream connecting unit operations.

```python
from hfm_simulator.stream import Stream
```

Contains:

* flow [mol/s]
* composition [-]
* pressure [Pa]
* temperature [K]
* permeability
* viscosity
* molecular weight

---

### 2. `HFMSimulator`

Main simulation engine.

```python
from hfm_simulator import HFMSimulator
```

Responsibilities:

* Build geometry
* Assemble mass model
* Solve nonlinear system
* Optionally solve energy balance
* Return results

---

### 3. `SimulationResults`

Container for all outputs.

Includes:

* Profiles: F, G, x, y, P, T, etc.
* Component-wise access
* Excel export
* Outlet streams (for chaining units)

👉 Defined in: 

---

## ⚡ Quick Start (Single Membrane)

```python
from hfm_simulator import HFMSimulator
from hfm_simulator.stream import Stream

from scenarios_examples.scenarios import SCENARIOS, STREAMS
from properties_examples.Mixture_Properties import MixtureProperties

# Scenario
scenario = SCENARIOS[11]
s = STREAMS[11]

# Feed stream
feed = Stream(
    flow=s["flow"],
    composition=s["composition"],
    pressure=s["pressure"],
    temperature=s["temperature"],
    components=s["components"],
    permeability=s["permeability"],
    viscosity=s["viscosity"],
    molecularweight=s["molecularweight"]
)

# Properties
props = MixtureProperties(
    components=feed.components,
    MU=feed.viscosity,
    M=feed.molecularweight,
    method="HZ"
)

# Simulator
sim = HFMSimulator()
sim.energy = True
sim.pressure_drop = False
sim.segments = 50
sim.heat_transfer_coef = 4

sim.set_scenario(scenario)
sim.set_feed(feed)
sim.set_properties(props)

# Run
results = sim.run()

print("Recovery:", results.recovery)
```

---

## 🔗 Connecting Units (Membranes in Series)

You can connect units using `Stream`.

Example:

```python
# First membrane
res1 = sim1.run()

# Use permeate or retentate as feed to next unit
feed2 = res1.outlet("permeate")

sim2.set_feed(feed2)
res2 = sim2.run()
```

👉 This is possible because `SimulationResults.outlet()` returns a full `Stream`.

---

## 📊 Available Results

The `SimulationResults` object contains:

### Profiles

* `F`, `G` → total flows
* `x_ret`, `y_per` → compositions
* `P`, `p` → pressures
* `J`, `J_comp`, `z_J` → fluxes

### Energy (if enabled)

* `T_ret`, `T_per`
* `h_ret`, `h_per`, `h_J`
* `UA`

### Derived

```python
results.recovery
```

---

## 🔍 Component-wise access

```python
results.component_flux("CO2")
results.retentate_composition("CH4")
results.component_permeate_flow(0)
```

---

## 📤 Export to Excel

```python
results.export_mass_excel("mass.xlsx")

results.export_energy_excel("energy.xlsx")

# or both
results.export_all()
```

---

## ⚙️ Design Philosophy

* **Modular** → mass and energy separated
* **Extensible** → easy to add new units
* **Stream-based** → ready for process simulation
* **Solver-independent physics**
* **Clean API for external users**

---

## 🧪 Examples

See:

```
run_examples/
├── test_simulation.py
├── test_two_membranes_series.py
```

👉 Example implementation: 

---

## 📌 Notes

* Feed **must be a `Stream` object**
* Properties are **user-defined**
* Scenarios are **external by design**
* Energy model is optional (`sim.energy = True`)

---

## 👨‍🔬 Author

Developed for advanced simulation of hollow fiber membrane systems with focus on:

* flexibility
* clarity
* research-level modeling
