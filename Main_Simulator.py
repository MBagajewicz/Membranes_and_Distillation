"""
Main_Simulator.py
==================
Entry point for running mixed HFM / Compressor / Mixer / STHE process configurations.

Supports mixed equipment: HFM membranes + Compressors + Mixers + STHEs.

HOW TO USE:
    1. Create your config file inside Simulator_Case_Studies/ (e.g. hfm_config.py)
    2. Set CASE_STUDY below to the name of your config file (WITHOUT .py)
    3. Run: python Main_Simulator.py

EXAMPLE:
    CASE_STUDY = "hfm_config"                  # uses Simulator_Case_Studies/hfm_config.py
    CASE_STUDY = "hfm_config_case7"              # uses Simulator_Case_Studies/hfm_config_case7.py
    CASE_STUDY = "hfm_config_with_compressor"    # uses Simulator_Case_Studies/hfm_config_with_compressor.py
    CASE_STUDY = "hfm_config_with_mixer"          # uses Simulator_Case_Studies/hfm_config_with_mixer.py
"""

# =============================================================================
# REQUIRED LOCAL LIBRARIES
# =============================================================================

from Local_Libraries_Check import ensure_local_libraries

REQUIRED_LOCAL_LIBRARIES = [
    "Common",
    "Simulator_HFM",
    "Simulator_STHE",
]

ensure_local_libraries(REQUIRED_LOCAL_LIBRARIES)

import importlib
import sys
import os
import shutil

import numpy as np

from Simulator_HFM.Simulator_Run_HFM import SimulatorRunHFM
from Simulator_HFM.Simulator_Geometry_HFM import SimulatorGeometryHFM
from Common.Stream.stream import Stream
from Common.Membrane_Properties.Permeance.Membrane_Permeance import Membrane_Permeance
from Common.Process_Simulator import Flowsheet, SequentialSolver, IterativeSolver
from Simulator_HFM.Equipment_Simulator_HFM.Equipment_HFM import HFMMembrane
from Simulator_STHE import STHE
from Simulator_STHE.Equipment_Simulator_STHE import STHEHeatExchanger

# Import additional equipment (adjust path if you place it elsewhere)
from Common.Unit_Operation.Compressor import Compressor
from Common.Unit_Operation.Mixer import Mixer

# =============================================================================
# USER INPUT — change ONLY this line to switch configurations
# =============================================================================

CASE_STUDY = "HFM_Case_Study_1_Benzene_Toluene"   # <-- Write Case Study file name (without .py)
# CASE_STUDY = "STHE_Case_Study_1"   # <-- Write Case Study file name (without .py)


# =============================================================================
# DYNAMIC IMPORT (do not touch)
# =============================================================================

def load_config(module_name: str):
    """Import a config module by name and validate required variables."""
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(f"\n❌ ERROR: file not found '{module_name}.py'")
        print(f"   Make sure the file is located in the Simulator_Case_Studies folder")
        sys.exit(1)

    required = ["STREAM_CONFIGS", "COMMON_PARAMS", "EQUIPMENT_CONFIG", "CONNECTIONS"]
    missing = [attr for attr in required if not hasattr(module, attr)]
    if missing:
        print(f"\n❌ ERROR: file '{module_name}.py' does not have the following variables:")
        for attr in missing:
            print(f"   - {attr}")
        sys.exit(1)

    return (
        module.STREAM_CONFIGS,
        module.COMMON_PARAMS,
        module.EQUIPMENT_CONFIG,
        module.CONNECTIONS,
        getattr(module, "ITERATIVE_SOLVER_CONFIG", None),
    )


print(f"📄 Loading configuration from: {CASE_STUDY}.py")
CASE_STUDY_RELATIVE = "Simulator_Case_Studies." + CASE_STUDY
STREAM_CONFIGS, COMMON_PARAMS, EQUIPMENT_CONFIG, CONNECTIONS, ITERATIVE_SOLVER_CONFIG = load_config(CASE_STUDY_RELATIVE)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _build_stream(spec: dict) -> Stream:
    """Create a Common.Stream from a stream configuration dictionary."""
    flow_kwargs = {}
    if spec.get("mass_flow") is not None:
        flow_kwargs["mass_flow"] = spec["mass_flow"]
    elif spec.get("molar_flow") is not None:
        flow_kwargs["molar_flow"] = spec["molar_flow"]
    else:
        raise ValueError("Stream configuration requires mass_flow or molar_flow")

    return Stream(
        composition=spec["composition"],
        P=spec["P"],
        T=spec["T"],
        backend=spec.get("backend", next(iter(STREAM_CONFIGS.values())).get("backend")),
        **flow_kwargs,
    )


def get_stream_spec(name: str) -> dict:
    """Return the explicit configuration for a process stream."""
    if name not in STREAM_CONFIGS:
        raise ValueError(f"No STREAM_CONFIGS entry found for external stream '{name}'.")
    return STREAM_CONFIGS[name]


def _default_stream_spec() -> dict:
    """Return a configured stream used only to initialize unsolved outlets."""
    if not STREAM_CONFIGS:
        raise ValueError("STREAM_CONFIGS cannot be empty.")
    return next(iter(STREAM_CONFIGS.values()))


def _unit_inlet_stream_name(unit_name: str, inlet_port: str) -> str | None:
    """Find the stream connected to a unit inlet port."""
    for conn in CONNECTIONS:
        if (isinstance(conn["from"], str)
                and isinstance(conn["to"], tuple)
                and conn["to"] == (unit_name, inlet_port)):
            return conn["from"]
    return None


def _set_configured_attributes(target, values: dict, section: str) -> None:
    for key, value in values.items():
        if not hasattr(target, key):
            raise ValueError(f"Unknown STHE {section} parameter: '{key}'")
        setattr(target, key, value)


def build_sthe(cfg):
    """Build a configured STHE physics model."""
    sim = STHE()
    geometry = cfg.get("geometry", {})
    _set_configured_attributes(sim.geometry.shell, geometry.get("shell", {}), "shell geometry")
    _set_configured_attributes(sim.geometry.tubes, geometry.get("tubes", {}), "tube geometry")
    _set_configured_attributes(sim.geometry.baffles, geometry.get("baffles", {}), "baffle geometry")
    _set_configured_attributes(sim.options.correlations, cfg.get("correlations", {}), "correlation")
    _set_configured_attributes(sim.options.solver, cfg.get("solver", {}), "solver")
    return sim


def merge_params(common, individual, components=None):
    merged = dict(common)
    merged.update(individual)
    if components is None:
        raise ValueError("HFM component list must be derived from its inlet stream.")
    merged["Components"] = list(components)
    return merged


def build_hfmmembrane(cfg, feed_stream):
    """Build an HFMMembrane simulator from a config dict and inlet stream."""
    params = merge_params(COMMON_PARAMS, cfg, feed_stream.components)

    if "S" in params and params["S"] is not None and np.any(params["S"]):
        permeance = Membrane_Permeance(
            components=params["Components"],
            permeability=params["S"],
            thickness=params["t_mem"],
        )
    else:
        permeance = Membrane_Permeance(
            components=params["Components"],
            permeance=params["Q"],
        )

    geometry = SimulatorGeometryHFM(
        LSingleMembrane=params["FiberLengthInElement"],
        DiamShell=params["DiamShell"],
        DiamFiber_o=params["DiamFiber_o"],
        DiamFiber_i=params["DiamFiber_i"],
        NFibers=params["N"],
        Void_Frac=params["Void_Frac"],
        NCells=params["Discretizations"],
        NumberOfMembranesInSerie=params["NumberOfElementsPerTube"],
        NumberOfTubesInParallel=params["NTubes"],
    )

    sim = SimulatorRunHFM()
    sim.set_feed(feed_stream)
    sim.PPerm = params["PPerm"]
    sim.set_membrane_permeance(permeance)
    sim.geometry = geometry
    sim.energy = params["EnergyBalance"]
    sim.pressure_drop = params["PressureDrop"]
    sim.force_phase = params["ForceGasPhase"]
    sim.heat_transfer_coef = params["HeatTransferCoef"]
    sim.calculate_dew_temperature = params["DewTemperatureCalculation"]
    sim.EndRetentatePressure = params["PRet"]
    sim.eospackage = params["EnergyBalanceStateEquation"]
    sim.use_fugacity = params["UseFugacity"]
    sim.iteration_tolerance = params["MassBalanceLoopIterationTolerance"]
    sim.max_num_iterations = params["NumberOfIterationsInLoop"]
    sim.solver_tolerance = params["LeastSquareSolverTolerance"]
    sim.ENERGY_CONVERGENCE_TOL = params["EnergyBalanceLoopIterationTolerance"]
    sim.verbose_least_squares = params["LeastSquaresVerbose"]
    sim.VISCOSITY_METHOD = params["ViscosityCalculationMethod"]
    sim.K_POLYMER = params["MembranePolymerThermalConductivity"]
    sim.SUPPORT_POROSITY = params["MembranePorosity"]

    return sim


def auto_tag_hfm(index):
    """Generate HFM equipment tag: ME-101, ME-102, ..."""
    return f"ME-{100 + index + 1}"


def auto_tag_compressor(index):
    """Generate Compressor equipment tag: K-101, K-102, ..."""
    return f"K-{100 + index + 1}"


def auto_tag_mixer(index):
    """Generate Mixer equipment tag: M-101, M-102, ..."""
    return f"M-{100 + index + 1}"


def create_dummy_stream(pressure=None, template_name=None):
    """Create an initialization stream for an unsolved outlet."""
    spec = dict(STREAM_CONFIGS.get(template_name, _default_stream_spec()))
    if pressure is not None:
        spec["P"] = pressure
    return _build_stream(spec)


# =============================================================================
# BUILD FLOWSHEET
# =============================================================================

def build_flowsheet() -> Flowsheet:
    """
    Build the flowsheet in three explicit phases:

    1. Create every stream object (configured inlets and intermediate/outlet
       streams used by CONNECTIONS).
    2. Create every unit operation using the already-existing inlet Stream
       objects.
    3. Apply CONNECTIONS to bind streams to unit-operation ports.

    This ordering is important for flowsheets such as HFM -> Compressor -> HFM:
    the downstream HFM must be able to receive the Stream object produced by the
    upstream compressor before the equipment itself is constructed.
    """
    fs = Flowsheet(name="Generic Process Flowsheet")

    # ------------------------------------------------------------------
    # STREAM GRAPH HELPERS
    # ------------------------------------------------------------------
    # A stream may be an explicitly configured inlet or an intermediate/outlet
    # stream produced by a unit.  For initialization we trace the stream
    # backwards until we find a configured stream.  This gives downstream
    # units a physically compatible Stream object before the solver runs.
    upstream_connection = {}
    for conn in CONNECTIONS:
        src, dst = conn["from"], conn["to"]
        if isinstance(src, tuple) and isinstance(dst, str):
            if dst in upstream_connection:
                raise ValueError(
                    f"Stream '{dst}' has multiple upstream connections."
                )
            upstream_connection[dst] = src

    unit_configs = {cfg["name"]: cfg for cfg in EQUIPMENT_CONFIG}

    def _initial_stream_info(stream_name: str, visited=None):
        """
        Return (template_name, initial_pressure) for a stream.

        The template is ultimately taken from STREAM_CONFIGS.  Pressure is
        adjusted when the immediate upstream unit has a known outlet pressure
        (compressor or HFM permeate).
        """
        if stream_name in STREAM_CONFIGS:
            return stream_name, STREAM_CONFIGS[stream_name]["P"]

        if visited is None:
            visited = set()
        if stream_name in visited:
            raise ValueError(
                f"Circular stream dependency detected while initializing "
                f"'{stream_name}'."
            )
        visited.add(stream_name)

        if stream_name not in upstream_connection:
            raise ValueError(
                f"Stream '{stream_name}' is neither configured in STREAM_CONFIGS "
                f"nor produced by a unit through CONNECTIONS."
            )

        unit_name, port_name = upstream_connection[stream_name]
        if unit_name not in unit_configs:
            raise ValueError(
                f"Stream '{stream_name}' references unknown upstream unit "
                f"'{unit_name}'."
            )

        cfg = unit_configs[unit_name]
        eq_type = cfg.get("type", "HFM").upper()

        # Find the upstream inlet stream of the unit.  This is the stream whose
        # thermodynamic composition is the best initialization template for
        # the unit's outlet.
        inlet_port = {
            "HFM": "feed",
            "COMPRESSOR": "inlet",
            "MIXER": "inlet_1",
            "STHE": {
                "hot_out": "hot_in",
                "cold_out": "cold_in",
            }.get(port_name),
        }

        if isinstance(inlet_port, dict):
            inlet_port = inlet_port.get(port_name)

        if inlet_port is None:
            # For an unsupported output port, use the first connected inlet
            # only as an initialization fallback.


            if eq_type == "STHE":
                if port_name == "hot_out":
                    inlet_ports = ["hot_in"]
                elif port_name == "cold_out":
                    inlet_ports = ["cold_in"]
                else:
                    raise ValueError(
                        f"Unsupported STHE output port '{port_name}' "
                        f"for unit '{unit_name}'."
                    )
            else:
                inlet_ports = {
                    "HFM": ["feed"],
                    "COMPRESSOR": ["inlet"],
                    "MIXER": ["inlet_1"],
                }.get(eq_type, [])

        
            # inlet_ports = {
            #     "HFM": ["feed"],
            #     "COMPRESSOR": ["inlet"],
            #     "MIXER": ["inlet_1"],
            #     "STHE": ["hot_in", "cold_in"],
            # }.get(eq_type, [])
        else:
            inlet_ports = [inlet_port]

        inlet_stream_name = None
        for port in inlet_ports:
            candidate = _unit_inlet_stream_name(unit_name, port)
            if candidate is not None:
                inlet_stream_name = candidate
                break

        if inlet_stream_name is None:
            raise ValueError(
                f"Unit '{unit_name}' has no connected inlet required to "
                f"initialize output stream '{stream_name}'."
            )


        template_name, inlet_pressure = _initial_stream_info(
            inlet_stream_name, visited.copy()
        )

        # Use the unit's known outlet pressure where available.  These are
        # initialization values only; the unit solver overwrites the Stream
        # with the actual result.
        if eq_type == "COMPRESSOR" and port_name == "outlet":
            return template_name, cfg["P_out"]

        if eq_type == "HFM" and port_name == "permeate":
            inlet_template = get_stream_spec(template_name)
            components = list(inlet_template["composition"].keys())
            params = merge_params(COMMON_PARAMS, cfg, components)
            return template_name, params["PPerm"]

        if eq_type == "MIXER" and port_name == "outlet":
            pressure_mode = cfg.get("pressure_mode", "lowest_inlet")
            pressure_drop = float(cfg.get("pressure_drop", 0.0))

            if pressure_mode == "fixed":
                if cfg.get("P_out") is None:
                    raise ValueError(
                        f"Mixer '{unit_name}' requires 'P_out' when "
                        "pressure_mode='fixed'."
                    )
                return template_name, float(cfg["P_out"]) - pressure_drop

            if pressure_mode != "lowest_inlet":
                raise ValueError(
                    f"Mixer '{unit_name}' has invalid pressure_mode "
                    f"'{pressure_mode}'."
                )

            inlet_pressures = []
            number_of_inlets = int(cfg.get("number_of_inlets", 2))
            for index in range(1, number_of_inlets + 1):
                mixer_inlet_name = _unit_inlet_stream_name(
                    unit_name, f"inlet_{index}"
                )
                if mixer_inlet_name is None:
                    raise ValueError(
                        f"Mixer '{unit_name}' has no connected "
                        f"'inlet_{index}' stream."
                    )
                _, mixer_inlet_pressure = _initial_stream_info(
                    mixer_inlet_name, visited.copy()
                )
                inlet_pressures.append(float(mixer_inlet_pressure))

            outlet_pressure = min(inlet_pressures) - pressure_drop
            if outlet_pressure <= 0.0:
                raise ValueError(
                    f"Mixer '{unit_name}' has non-positive initialized "
                    "outlet pressure."
                )
            return template_name, outlet_pressure

        if eq_type == "STHE":
            return template_name, inlet_pressure

        return template_name, inlet_pressure

    # ------------------------------------------------------------------
    # PHASE 1 — CREATE ALL STREAM OBJECTS
    # ------------------------------------------------------------------
    destination_stream_names = {
        conn["to"] for conn in CONNECTIONS if isinstance(conn["to"], str)
    }
    external_inlet_names = {
        conn["from"] for conn in CONNECTIONS
        if isinstance(conn["from"], str)
        and conn["from"] not in destination_stream_names
    }

    # Validate that every explicitly configured stream used as an inlet is
    # actually available.  STREAM_CONFIGS may contain extra named streams, but
    # a connection cannot silently invent an external inlet.
    for stream_name in sorted(external_inlet_names):
        if stream_name not in STREAM_CONFIGS:
            raise ValueError(
                f"External inlet stream '{stream_name}' is not defined in "
                f"STREAM_CONFIGS."
            )

    all_stream_names = {
        x
        for conn in CONNECTIONS
        for x in (conn["from"], conn["to"])
        if isinstance(x, str)
    }

    # Explicitly configured streams are also created, even if a particular
    # case does not use them in CONNECTIONS.  This keeps STREAM_CONFIGS as the
    # source of truth for configured physical streams.
    all_stream_names.update(STREAM_CONFIGS.keys())

    for stream_name in sorted(all_stream_names):
        if stream_name in STREAM_CONFIGS:
            stream = _build_stream(get_stream_spec(stream_name))
            fs.add_stream(stream_name, stream)
            if stream_name in external_inlet_names:
                print(f"  Created inlet stream: {stream_name}")
            else:
                print(f"  Created configured stream: {stream_name}")
            continue

        template_name, init_P = _initial_stream_info(stream_name)


        stream = create_dummy_stream(
            pressure=init_P,
            template_name=template_name,
        )


        fs.add_stream(stream_name, stream)
        print(
            f"  Created stream: {stream_name} "
            f"(init P={stream.P/1e5:.2f} bar; template={template_name})"
        )

    # ------------------------------------------------------------------
    # PHASE 2 — CREATE ALL UNIT OPERATIONS
    # ------------------------------------------------------------------
    hfm_counter = comp_counter = mixer_counter = sthe_counter = 0

    for cfg in EQUIPMENT_CONFIG:
        eq_type = cfg.get("type", "HFM").upper()
        name = cfg["name"]
        description = cfg.get("description", f"Equipment {name}")

        if eq_type == "HFM":
            hfm_counter += 1
            tag = auto_tag_hfm(hfm_counter - 1)
            inlet_name = _unit_inlet_stream_name(name, "feed")
            if inlet_name is None or inlet_name not in fs.streams:
                raise ValueError(
                    f"HFM '{name}' has no connected/configured 'feed' inlet."
                )
            inlet_stream = fs.streams[inlet_name]
            sim = build_hfmmembrane(cfg, inlet_stream)
            unit = HFMMembrane(
                name=name,
                simulator=sim,
                tag=tag,
                description=description,
            )
            params = merge_params(
                COMMON_PARAMS, cfg, inlet_stream.components
            )
            print(
                f"  Registered {name} [HFM] | tag={tag} | "
                f"PPerm={params['PPerm']/1e5:.2f} bar | {description}"
            )

        elif eq_type == "COMPRESSOR":
            comp_counter += 1
            tag = auto_tag_compressor(comp_counter - 1)
            inlet_name = _unit_inlet_stream_name(name, "inlet")
            if inlet_name is None or inlet_name not in fs.streams:
                raise ValueError(
                    f"Compressor '{name}' has no connected/configured 'inlet' "
                    f"stream."
                )
            unit = Compressor(
                name=name,
                P_out=cfg["P_out"],
                efficiency=cfg.get("efficiency", 0.8),
                gamma=cfg.get("gamma", 1.3),
                tag=tag,
                description=description,
            )
            print(
                f"  Registered {name} [Compressor] | tag={tag} | "
                f"P_out={cfg['P_out']/1e5:.2f} bar | {description}"
            )

        elif eq_type == "MIXER":
            mixer_counter += 1
            tag = cfg.get("tag", auto_tag_mixer(mixer_counter - 1))

            number_of_inlets = int(cfg.get("number_of_inlets", 2))
            if number_of_inlets < 2:
                raise ValueError(
                    f"Mixer '{name}' requires at least two inlet streams."
                )

            for index in range(1, number_of_inlets + 1):
                port = f"inlet_{index}"
                inlet_name = _unit_inlet_stream_name(name, port)
                if inlet_name is None or inlet_name not in fs.streams:
                    raise ValueError(
                        f"Mixer '{name}' has no connected/configured "
                        f"'{port}' inlet."
                    )

            outlet_name = None
            for conn in CONNECTIONS:
                if (
                    isinstance(conn["from"], tuple)
                    and conn["from"] == (name, "outlet")
                    and isinstance(conn["to"], str)
                ):
                    outlet_name = conn["to"]
                    break

            if outlet_name is None or outlet_name not in fs.streams:
                raise ValueError(
                    f"Mixer '{name}' has no connected/configured "
                    "'outlet' stream."
                )

            unit = Mixer(
                name=name,
                number_of_inlets=number_of_inlets,
                pressure_mode=cfg.get("pressure_mode", "lowest_inlet"),
                P_out=cfg.get("P_out"),
                pressure_drop=cfg.get("pressure_drop", 0.0),
                tag=tag,
                description=description,
            )
            print(
                f"  Registered {name} [Mixer] | tag={tag} | "
                f"inlets={number_of_inlets} | "
                f"pressure_mode={cfg.get('pressure_mode', 'lowest_inlet')} | "
                f"{description}"
            )

        elif eq_type == "STHE":
            sthe_counter += 1
            tag = cfg.get("tag", f"E-{100 + sthe_counter}")

            for port in ("hot_in", "cold_in"):
                inlet_name = _unit_inlet_stream_name(name, port)
                if inlet_name is None or inlet_name not in fs.streams:
                    raise ValueError(
                        f"STHE '{name}' has no connected/configured "
                        f"'{port}' inlet."
                    )

            sim = build_sthe(cfg)
            unit = STHEHeatExchanger(
                name=name,
                simulator=sim,
                tag=tag,
                description=description,
            )
            g = sim.geometry
            print(
                f"  Registered {name} [STHE] | tag={tag} | "
                f"shell={g.shell.diameter:.3f} m | "
                f"L={g.tubes.length:.2f} m | {description}"
            )

        else:
            raise ValueError(
                f"Unknown equipment type: '{eq_type}' for unit '{name}'"
            )

        fs.add_unit(name, unit)

    # ------------------------------------------------------------------
    # PHASE 3 — CONNECT STREAMS TO UNIT PORTS
    # ------------------------------------------------------------------
    for conn in CONNECTIONS:
        src, dst = conn["from"], conn["to"]

        if isinstance(src, str) and isinstance(dst, tuple):
            if src not in fs.streams:
                raise ValueError(
                    f"Connection references unknown source stream '{src}'."
                )
            fs.connect(stream=src, destination=dst)

        elif isinstance(src, tuple) and isinstance(dst, str):
            if dst not in fs.streams:
                raise ValueError(
                    f"Connection references unknown destination stream '{dst}'."
                )
            fs.connect(source=src, stream=dst)

        else:
            raise ValueError(f"Invalid connection: {conn}")

    return fs


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"Flowsheet simulation: {CASE_STUDY}")
    print("=" * 60)
    print(f"\n  Inlet streams: {sorted([name for name in STREAM_CONFIGS])}")
    print(f"  Equipments: {[e['name'] for e in EQUIPMENT_CONFIG]}")
    print(f"  Config: {CASE_STUDY}.py")
    print()

    fs = build_flowsheet()


    print("\nSolving...")

    if ITERATIVE_SOLVER_CONFIG is not None:
        solver_config = ITERATIVE_SOLVER_CONFIG

        solver = IterativeSolver(
            fs,
            tear_streams=solver_config["tear_streams"],
            tolerance=solver_config.get("tolerance", 1e-6),
            max_iterations=solver_config.get("max_iterations", 100),
            relaxation=solver_config.get("relaxation", 1.0),
            initial_guesses=solver_config.get("initial_guesses"),
        )
    else:
        solver = SequentialSolver(fs)

    solver.solve()

    print("\n" + fs.report())

    # ------------------------------------------------------------------
    # STHE RESULTS
    # ------------------------------------------------------------------
    for cfg in EQUIPMENT_CONFIG:
        if cfg.get("type", "HFM").upper() != "STHE":
            continue
        unit = fs.units[cfg["name"]]
        print(f"\n--- {cfg['name']} STHE results ---")
        for key, value in unit.results.items():
            print(f"  {key}: {value}")

    # ------------------------------------------------------------------
    # EXPORT TO EXCEL
    # ------------------------------------------------------------------
    OUTPUT_DIR = "Simulator_Case_Studies"   # destination folder
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\nExporting Excel results in '{OUTPUT_DIR}/'...")
    try:
        for cfg in EQUIPMENT_CONFIG:
            name = cfg["name"]
            unit = fs.units[name]

            # Only HFM units export to Excel (Compressor has no axial profiles)
            if cfg.get("type", "HFM").upper() != "HFM":
                continue

            if unit.warnings:
                print(f"  ⚠️  {name}: solver infeasible — excel file export aborted.")
                print(f"      Warnings: {unit.warnings}")
                continue

            if hasattr(unit, '_last_result') and unit._last_result is not None:
                unit._last_result.export_results_to_excel(case_name=f"generic_{name}")
                src = "HFM_Results.xlsx"
                dst = os.path.join(OUTPUT_DIR, f"{CASE_STUDY}_{name}_Results.xlsx")
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"  🎉 {name} → {dst}")
                else:
                    print(f"  ⚠️  {name}: excel file not found.")
            else:
                print(f"  ⚠️  {name}: without results.")
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Excel ERROR: {e}")
        print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # STREAM PROPERTIES
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  STREAM PROPERTIES")
    print("=" * 60)

    for stream_name in fs.streams:
        stream = fs.streams[stream_name]
        print(f"\n--- {stream_name} ---")
        print(f"  Mass flow:      {stream.mass_flow:.6f} kg/s")
        print(f"  Molar flow:     {stream.molar_flow:.6f} mol/s")
        print(f"  Temperature:    {stream.T:.2f} K  ({stream.T - 273.15:.2f} °C)")
        print(f"  Pressure:       {stream.P:.2f} Pa  ({stream.P/1e5:.3f} bar)")
        print(f"  Density:        {stream.density_mass:.4f} kg/m³")
        print(f"  Enthalpy:       {stream.enthalpy_mass/1e3:.2f} kJ/kg")
        print(f"  Viscosity:      {stream.viscosity:.6e} Pa·s")
        print(f"  Composition:    {stream.composition}")
