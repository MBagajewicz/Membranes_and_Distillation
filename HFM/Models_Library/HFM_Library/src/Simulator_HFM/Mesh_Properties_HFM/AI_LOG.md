# AI Log – MixPropertiesCoolPropHEOS

> **Audience:** AI assistants (including future instances of this model) helping a developer who does NOT know this codebase.  
> **Purpose:** Prevent foot-guns, explain non-obvious design decisions, and provide a fast onboarding path for code modification.

---

## 1. Executive Summary

This is a **narrow-scope property calculator** for gas mixtures along the axial nodes of a hollow-fiber membrane module. It is NOT a general thermo library. It wraps CoolProp (`AbstractState`) and adds:
- Vectorized P/T/Z handling with broadcasting
- Safe gas-phase PT flashes with fallback attempts
- HEOS fallback for transport properties when using cubic EOS (PR/SRK)
- Phase-stability testing (`single_phase_at`) used as a design constraint
- In-place condition updates to avoid reconstructing `AbstractState` objects

The class is a **stateful orchestrator** (`core.py`) that delegates to two mixins (`state_updater.py`, `phase.py`). There is no external orchestrator by design.

---

## 2. Critical Design Decisions (Why Things Are the Way They Are)

### 2.1 Mixins instead of single file or composition
- **Why:** The original was one 400+ line class. Splitting into mixins keeps responsibilities physically separate without breaking the public API.
- **Trade-off:** Mixins rely on instance attributes created in `__init__` (`self.states`, `self.P`, `self.T`, `self.Z`, `self.props`, `self._fb_states`). They are NOT self-contained classes. Do not instantiate mixins standalone.
- **Rule:** If adding a new responsibility (e.g. diffusivity calculation), create a new mixin. Do NOT bloat `core.py`.

### 2.2 No external orchestrator
- **Why:** The class itself holds all shared state (`AbstractState` objects, property cache, composition dirty flag). Adding a wrapper class would just add indirection.
- **When to add one:** Only if the caller needs to manage multiple `MixPropertiesCoolPropHEOS` instances (e.g. retentate + permeate sides) or swap backends (CoolProp vs. custom). Not needed today.

### 2.3 `_BULK_GETTERS` in `constants.py`
- **Why:** The constructor accepts `bulk_props` (list of property names). The original code hardcoded two dictionaries (one per EOS) with most entries commented out, making `bulk_props` dead configuration. `_BULK_GETTERS` makes `bulk_props` actually work.
- **Trap:** If adding a new property, register it in `_BULK_GETTERS`. Otherwise `update_state()` silently skips it.

### 2.4 `_fallback_state` (lazy HEOS states)
- **Why:** PR/SRK backends in CoolProp raise `"type not set"` for viscosity and conductivity. Rather than forcing the entire calculation onto HEOS (slow), only transport properties fall back to HEOS. Thermodynamics (enthalpy, density, fugacity) stay on the primary EOS.
- **Trap:** `_fb_states` is `None` until first needed. If `eos="HEOS"`, it is never created. Do not pre-allocate it in `__init__`.

### 2.5 `single_phase_at` vs `dew_temperature`
- **Why:** `dew_temperature()` root-finds on the phase boundary (PQ with Q=1). On CO₂/CH₄/N₂ retentate compositions it returned 476 K at one node (above all critical temperatures) and 6 K at others (below all triple points). It is **deprecated for constraints** and kept only for reporting.
- **Correct approach:** `single_phase_at(T_eval)` does a PT flash and checks `Q < 0` or `Q > 1`. It is the design constraint `T >= T_dew + approach` rewritten as "is the mixture still single-phase at T - approach?"
- **Performance:** ~0.8 ms/node far from boundary, ~9 ms/node close to it. Self-regulating cost.

### 2.6 `set_conditions` (in-place update)
- **Why:** In membrane simulations, outer loops update P/T/Z iteratively. Reconstructing `NStates` `AbstractState` objects (especially HEOS) is expensive. `set_conditions()` updates arrays in place and sets `_comp_dirty=True` only if Z changes.
- **Trap:** If Z changes, the caller must still call `update_all()` to push new mole fractions to CoolProp. `set_conditions()` does NOT flash.

---

## 3. Mutable State & Thread Safety

| Attribute | Mutable after `__init__`? | Thread-safe? | Notes |
|---|---|---|---|
| `self.states` | ❌ No (list of AbstractState) | ❌ No | CoolProp objects are not thread-safe. Do not share across threads. |
| `self.P`, `self.T`, `self.Z` | ✅ Yes (via `set_conditions`) | ❌ No | NumPy arrays modified in place. |
| `self.props` | ✅ Yes (via `update_state` / `update_all`) | ❌ No | Cache invalidated on every update. |
| `self._fb_states` | ✅ Lazy init | ❌ No | Created on first transport-property fallback. |
| `self.unavailable_props` | ✅ Yes (grows over time) | ❌ No | Set of strings. Used to warn consumers once. |
| `self._comp_dirty` | ✅ Yes | ❌ No | Flag. If True, `update_state` must re-push Z to CoolProp. Currently always pushed; flag reserved for future optimization. |

**Conclusion:** This class is NOT thread-safe. If parallelizing membrane nodes, instantiate one object per thread or use process-based parallelism.

---

## 4. Common Modification Scenarios

### 4.1 "I want to add a new property (e.g. `speed_of_sound`)"
1. Add entry to `_BULK_GETTERS` in `constants.py`:
   ```python
   "speed_of_sound": lambda st: st.speed_of_sound(),
   ```
2. Add to default `bulk_props` in `core.py` `__init__` if it should be included by default for HEOS.
3. Test: PR backend may not support it. The fallback mechanism will catch the exception and try HEOS. If HEOS also fails, it goes into `unavailable_props`.

### 4.2 "I want to change the temperature clamp in `safe_update_gas`"
- Current: `np.clip(T, 150.0, 1000.0)`
- **Warning:** The clamp exists because CoolProp HEOS can fail or return unphysical values outside this range for the mixtures used. If widening, test on all expected component sets (CO₂, CH₄, N₂, H₂, etc.).

### 4.3 "I want to support liquid phase"
- **Do NOT do this lightly.** The entire design assumes gas phase:
  - `force_gas_phase=True` calls `st.specify_phase(CoolProp.iphase_gas)`
  - `safe_update_gas` does PT flashes, not PQ or QT flashes
  - Property getters like `viscosity()` may behave differently in liquid phase
- If absolutely necessary, add a `phase` parameter to `__init__`, but expect ripple effects through `single_phase_at`, `_fallback_state`, and all consumers.

### 4.4 "I want to add a new EOS backend (e.g. SRK)"
- `eos` is passed directly to `AbstractState(eos, fluid_string)`. CoolProp handles it.
- Update default `bulk_props` logic in `__init__` if SRK has different capabilities than PR.
- SRK has the same transport-property limitation as PR (needs HEOS fallback).

### 4.5 "I want to cache results between iterations"
- `self.props` IS the cache. It is a list of dicts, one per node.
- If the caller wants cross-iteration caching, they must manage it externally. Do not add a disk cache or LRU inside this class; it would break the "lightweight stateful object" contract.

---

## 5. Testing Strategy

Because this class wraps CoolProp (an external C++ library), unit tests should:
1. **Mock CoolProp** for logic tests (broadcasting, fallback mechanism, unavailable_props tracking).
2. **Integration test** with real CoolProp on a small set of known mixtures:
   - Pure CO₂ at 300 K, 1 bar → compare against `PropsSI`
   - CO₂/CH₄ 50/50 at 300 K, 10 bar → verify PR and HEOS give similar enthalpy, different viscosity
   - Phase boundary test: run `single_phase_at` at T well above and well below known dew point
3. **Performance benchmark:** `update_all()` on 100 nodes with HEOS should complete in < 1 s. If slower, investigate `_fallback_state` being triggered unnecessarily.

---

## 6. Version & Dependency Notes

- **CoolProp:** Tested with CoolProp's Python wrapper. `AbstractState` API is stable but transport-property support on cubic backends has been inconsistent across versions. If upgrading CoolProp, re-test PR + viscosity/conductivity fallback.
- **NumPy:** Uses `np.atleast_1d`, broadcasting, and in-place mutation. Standard numpy >= 1.20 is fine.
- **Python:** Uses type hints sparingly (not in this codebase). Compatible with Python 3.8+.

---

## 7. Business Context (Why This Exists)

This code lives inside a larger membrane separation model (hollow-fiber gas separation). It is called at every iteration of:
- **Mass balance:** Darcy's law + solution-diffusion model needs fugacity coefficients.
- **Energy balance:** Enthalpy and Cp needed for temperature profile.
- **Heat transfer:** Viscosity and conductivity needed for Nusselt/Sherwood correlations.

The module is discretized axially (typically 20–100 nodes). Speed matters because the property calculator is invoked inside nested loops (outer membrane iteration + inner fugacity/energy solvers). That is why `set_conditions()` and state reuse exist.

---

## 8. Red Flags (If a User Asks for This, Push Back)

| Request | Why Push Back |
|---|---|
| "Make it thread-safe" | Would require deep copies of `AbstractState` per thread or process isolation. Significant refactor. |
| "Add liquid-phase support" | Breaks the gas-phase assumption throughout. Would need new flash routines and phase detection. |
| "Replace CoolProp with REFPROP" | `AbstractState` API is similar, but REFPROP licensing and binary distribution are painful. Not a drop-in replacement. |
| "Add caching to disk" | This object is meant to be lightweight and short-lived per iteration. Disk cache adds complexity and I/O latency. |
| "Remove the mixins and go back to one file" | The original was one file. It was split for maintainability. Reverting would lose the separation of concerns. |

---

## 9. Quick Reference: File Responsibilities

| File | Responsibility | Safe to edit independently? |
|---|---|---|
| `constants.py` | Property name → getter mapping | ✅ Yes |
| `core.py` | `__init__`, `set_conditions`, class declaration | ⚠️ Careful: affects mixin contract |
| `mixins/state_updater.py` | Flash logic, fallback, property evaluation | ✅ Yes (if mixin interface unchanged) |
| `mixins/phase.py` | Phase stability, dew point, component bounds | ✅ Yes |
| `__init__.py` | Public API export | ✅ Yes |
