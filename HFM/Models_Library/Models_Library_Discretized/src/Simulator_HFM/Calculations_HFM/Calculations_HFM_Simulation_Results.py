#
# HFM Simulation Results Runner
# Adapted for Common.Stream.stream API (CoolProp-backed, property-derived)
# =============================================================================

import numpy as np
import time

from Simulator_HFM.Simulator_Run_HFM import SimulatorRunHFM
from Simulator_HFM.Simulator_Geometry_HFM import SimulatorGeometryHFM

from Common.Stream.stream import Stream, ThermoBackend
from Common.Membrane_Properties.Permeance.Membrane_Permeance import Membrane_Permeance

_WARM_START = None


def HFM_Simulation_Results(L, D, dfo, dfi, Void_Frac, Material, m_p, Ntf):
    """
    Run an HFM simulation using the new CoolProp-backed Stream API.

    Parameters
    ----------
    L : float
        Fiber length [m].
    D : float
        Shell diameter [m].
    dfo : float
        Fiber outer diameter [m].
    dfi : float
        Fiber inner diameter [m].
    Void_Frac : float
        Shell-side void fraction [-].
    Material : list or array
        Material identifier(s) per candidate (e.g. ['PI', 'CA']).
    m_p : dict
        Scenario parameters dictionary. Must contain:
            - COMPONENTS : list[str] — component names (CoolProp-compatible)
            - M          : np.ndarray — molar masses [kg/mol] (for trimming calcs)
            - MU         : np.ndarray — pure viscosities [Pa·s] (for trimming calcs)
            - T          : float — feed temperature [K]
            - P_Feed     : float — feed pressure [Pa]
            - P_Permeate : float — permeate pressure [Pa]
            - f_total    : float — total feed molar flow [mol/s]
            - comp_f     : np.ndarray — feed mole fractions (sum to 1)
            - Q          : dict or np.ndarray — component permeances [mol/(m²·Pa·s)]
            - N_Partitions : int — number of axial cells
            - Energy_bool  : bool
            - Pressure_Drop_bool : bool
            - UseFugacity  : bool
            - EnthalpyMode : str
            - EOS          : str — 'PR' or 'HEOS'
            - K_POLYMER    : float — polymer thermal conductivity [W/(m·K)]
            - SUPPORT_POROSITY : float — membrane support porosity [-]
            - U            : float — global heat transfer coefficient [W/(m²·K)]
            - iteration_tolerance       : float
            - max_num_iterations        : int
            - solver_tolerance          : float
            - ENERGY_CONVERGENCE_TOL    : float
            - SIM_TIME_BUDGET_S         : float or None
            - CALC_TDEW_REPORT          : bool (optional)
            - APPROACH_T_DEW            : float (optional)
            - check_dew_permeate        : bool (optional)
    Ntf : int
        Number of fibers.

    Returns
    -------
    results : SimulatorResultsHFM
        Simulation results object.
    """

    print_results_screen = False
    print_results_excel = False

    global _WARM_START

    # ------------------------------------------------------------------
    # Build scenario dictionary from parameters
    # ------------------------------------------------------------------
    scenario = {
        'Components': m_p['COMPONENTS'],
        'M': m_p['M'],                          # [kg/mol] — kept for trimming calcs
        'MU': m_p['MU'],                        # [Pa·s] — kept for trimming calcs
        "T": m_p['T'],                          # [K]
        "PFeed": m_p['P_Feed'],                 # [Pa]
        "PPerm": m_p['P_Permeate'],             # [Pa]
        "FFeed": m_p['f_total'],                # [mol/s]
        "s_flow": 0.0,                          # [mol/s]
        "ZFeed": m_p['comp_f'],                 # [-] mole fractions
        "Q": m_p['Q'][Material[0]] if isinstance(m_p['Q'], dict) else m_p['Q'],
        "DiamShell": D,                         # [m]
        "DiamFiber_o": dfo,                     # [m]
        "DiamFiber_i": dfi,                     # [m]
        "t_mem": (dfo - dfi) / 2.0,             # [m]
        "LHidraulic": L,                        # [m]
        "N": Ntf,
        "Feed": "Shell",
        "Current": "Co",
        "Void_Frac": Void_Frac
    }

    # ------------------------------------------------------------------
    # Create Feed Stream (new CoolProp-backed API)
    # ------------------------------------------------------------------
    # The new Stream only needs: composition, P, T, molar_flow, backend.
    # Viscosity and molar mass are derived internally by CoolProp.
    # We pass component names as CoolProp-compatible strings.

    feed = Stream(
        composition={
            comp: float(frac)
            for comp, frac in zip(scenario["Components"], scenario["ZFeed"])
        },
        P=scenario["PFeed"],
        T=scenario["T"],
        molar_flow=scenario["FFeed"],
        backend=ThermoBackend.HEOS,
    )

    # ------------------------------------------------------------------
    # Membrane permeance
    # ------------------------------------------------------------------
    permeance = Membrane_Permeance(
        components=scenario["Components"],
        permeance=np.asarray(scenario["Q"], dtype=float)
    )

    # ------------------------------------------------------------------
    # Geometry
    # ------------------------------------------------------------------
    geometry = SimulatorGeometryHFM(
        LSingleMembrane=L,
        DiamShell=D,
        DiamFiber_o=dfo,
        DiamFiber_i=dfi,
        NFibers=scenario['N'],
        Void_Frac=scenario['Void_Frac'],
        NCells=m_p['N_Partitions'],
        NumberOfMembranesInSerie=1,
        NumberOfTubesInParallel=1
    )

    # ------------------------------------------------------------------
    # Configure simulator
    # ------------------------------------------------------------------
    sim = SimulatorRunHFM()

    sim.set_feed(feed)
    sim.set_membrane_permeance(permeance)
    sim.geometry = geometry

    sim.PPerm = scenario['PPerm']

    # Physics flags
    sim.energy = m_p['Energy_bool']
    sim.pressure_drop = m_p['Pressure_Drop_bool']

    # Dew-point reporting (optional, expensive)
    sim.calculate_dew_temperature = bool(
        m_p.get('CALC_TDEW_REPORT', False)) and m_p['Energy_bool']
    sim.dew_approach_K = m_p.get('APPROACH_T_DEW', 0.0)
    sim.check_dew_permeate = m_p.get('check_dew_permeate', True)

    sim.use_fugacity = m_p['UseFugacity']
    sim.enthalpy_method = m_p['EnthalpyMode']

    # Thermodynamics & transport
    sim.eospackage = m_p['EOS']
    sim.VISCOSITY_METHOD = "HZ"           # "HZ" or "CoolProp"
    sim.heat_transfer_coef = m_p['U']       # [W/(m² K)]
    sim.K_POLYMER = m_p['K_POLYMER']        # [W/(m K)]
    sim.SUPPORT_POROSITY = m_p['SUPPORT_POROSITY']  # [-]

    # Wall-clock budget per candidate (None = unlimited)
    sim.time_budget_s = m_p.get('SIM_TIME_BUDGET_S', None)

    # Solver tolerances
    sim.iteration_tolerance = m_p['iteration_tolerance']
    sim.max_num_iterations = m_p['max_num_iterations']
    sim.solver_tolerance = m_p['solver_tolerance']
    sim.ENERGY_CONVERGENCE_TOL = m_p['ENERGY_CONVERGENCE_TOL']

    # Warm start (reuse previous convergence state if geometry matches)
    _sig = (m_p['N_Partitions'], len(scenario["Components"]))
    if _WARM_START is not None and _WARM_START.get("_sig") == _sig:
        sim.set_warm_start(_WARM_START["payload"])

    # ------------------------------------------------------------------
    # Run simulation
    # ------------------------------------------------------------------
    t0 = time.time()
    results = sim.run()
    elapsed = time.time() - t0
    print(f"Computation time simulation: {elapsed:.2f} s")

    # Store warm start for next call
    if getattr(results, "warm_start", None) is not None:
        _WARM_START = {"_sig": _sig, "payload": results.warm_start}

    return results
