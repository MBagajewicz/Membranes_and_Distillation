"""
hfm_config.py
===============
Configuration file for the generic HFM flowsheet.

EDIT ONLY THIS FILE to change:
    - Feed composition, pressure, temperature, flow
    - Equipment geometry, permeance, solver flags
    - Flowsheet topology (connections between units)

The execution script (example_hfm_generic.py) imports this file and runs
everything automatically.

You can create multiple config files (e.g. hfm_config_case6.py,
hfm_config_case7.py) and switch between them by changing the import.
"""

import numpy as np
from Common.Stream.stream import ThermoBackend


# =============================================================================
# 1. FEED CONFIGURATION — inlet stream properties
# =============================================================================

# =============================================================================
# 1. PROCESS STREAMS
# =============================================================================

STREAM_CONFIGS = {
    "Feed": {
        "composition": dict(zip(['CO2', 'Propane'], np.array([0.5, 0.5]))),
        "P": 1000000.0,
        "T": 313.0,
        "molar_flow": 0.0033,
        "backend": ThermoBackend.HEOS,
    },
}


# =============================================================================
# 2. COMMON EQUIPMENT PARAMETERS — shared by all membranes
# =============================================================================

COMMON_PARAMS = {
    "PressureDrop": True,
    "EnergyBalance": True,
    "UseFugacity": True,
    "PRet": None,
    "M": np.array([0.044009, 0.044097]),
    "MU": np.array([1.48e-5, 8.5e-6]),
    "PPerm": 1e5,
    "Q": np.array([6.8e-8, 7.71e-11]),
    "S": np.array([6.8e-8, 7.71e-11]) * (4.15e-4 - 3.41e-4) / 2,
    "t_mem": (4.15e-4 - 3.41e-4) / 2,
    "DiamFiber_o": 4.15e-4,
    "DiamFiber_i": 3.41e-4,
    "Void_Frac": 0.625,
    "NumberOfElementsPerTube": 1,
    "NTubes": 1,
    "Discretizations": 20,
    "LeastSquareSolverTolerance": 1e-6,
    "LeastSquaresVerbose": 0,
    "MassBalanceLoopIterationTolerance": 1e-6,
    "NumberOfIterationsInLoop": 150,
    "EnergyBalanceLoopIterationTolerance": 1e-2,
    "HeatTransferCoef": 4,
    "EnergyBalanceStateEquation": "PR",
    "ViscosityCalculationMethod": "HZ",
    "DewTemperatureCalculation": False,
    "ForceGasPhase": True,
    "MembranePolymerThermalConductivity": 0.2,
    "MembranePorosity": 0.5,
}


# =============================================================================
# 3. INDIVIDUAL EQUIPMENT DEFINITIONS
# =============================================================================
#
# Each entry becomes one HFMMembrane.
# Override any COMMON_PARAM per equipment.

EQUIPMENT_CONFIG = [
    {
        "name": "HFM1",
        "description": "Stage 1 — CO2/Propane separation",
        "DiamShell": 0.0394,
        "FiberLengthInElement": 0.2,
        "N": 3380,
    },
    {
        "name": "HFM2",
        "description": "Stage 2 — permeate polishing",
        "DiamShell": 0.0300,
        "FiberLengthInElement": 0.1,
        "N": 3200,
        # IMPORTANT: downstream membrane needs LOWER PPerm than upstream
        # permeate pressure to maintain driving force.
        "PPerm": 0.5e5,   # 0.5 bar
    },
]


# =============================================================================
# 4. CONNECTIONS — declarative topology
# =============================================================================
#
# Syntax:
#   {"from": "StreamName", "to": ("UnitName", "port")}
#   {"from": ("UnitName", "port"), "to": "StreamName"}
#
# Built-in unit ports: "feed", "retentate", "permeate"

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate1"},
    {"from": ("HFM1", "permeate"), "to": "Permeate1_to_Feed2"},
    {"from": "Permeate1_to_Feed2", "to": ("HFM2", "feed")},
    {"from": ("HFM2", "retentate"), "to": "Retentate2"},
    {"from": ("HFM2", "permeate"), "to": "Permeate2"},
]
