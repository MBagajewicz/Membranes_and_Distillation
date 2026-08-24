"""
HFM_Case_Study_11_Vuong.py
============================================================
Single-membrane flowsheet.
"""

import numpy as np
from Common.Stream.stream import ThermoBackend

# =============================================================================
# 1. FEED CONFIGURATION
# =============================================================================

# =============================================================================
# 1. PROCESS STREAMS
# =============================================================================

STREAM_CONFIGS = {
    "Feed": {
        "composition": dict(zip(['CO2', 'CH4', 'C2H6', 'C3H8', 'N2'], np.array([0.1, 0.774, 0.077, 0.039, 0.01]))),
        "P": 6000000.0,
        "T": 303.15,
        "molar_flow": 13.88888888888889,
        "backend": ThermoBackend.HEOS,
    },
}

# =============================================================================
# 2. COMMON EQUIPMENT PARAMETERS
# =============================================================================

COMMON_PARAMS = {
    "PressureDrop": True,
    "EnergyBalance": False,
    "UseFugacity": False,
    "PRet": None,  # If None: automatic Hagen-Poiseuille pressure drop calculation
    "M": np.array([0.04401, 0.01604, 0.03007, 0.0441 , 0.02802]),
    "MU": np.array([0.000015, 0.000011, 0.000009, 0.000008, 0.000018]),
    "T": 303.15,
    "PPerm": 1.000000e+05,
    "Q": np.array([
                3.283e-8,   # CO2
                1.641e-9,   # CH4
                1.094e-9,   # C2H6
                5.469e-10,  # C3H8
                3.283e-9    # N2
            ]),
    "DiamShell": 0.1,
    "DiamFiber_o": 0.0002,
    "DiamFiber_i": 0.00015,
    "FiberLengthInElement": 1.2,
    "N": 125000,
    "Void_Frac": 0.5,
    "NumberOfElementsPerTube": 1,
    "NTubes": 1,
    "Discretizations": 20,  # Number of finite volumes along the membrane
    "LeastSquareSolverTolerance": 1.000000e-06,
    "LeastSquaresVerbose": 0,  # 2=Print all iterations, 1=Print final, 0=Silent
    "MassBalanceLoopIterationTolerance": 1.000000e-06,
    "NumberOfIterationsInLoop": 150,
    "EnergyBalanceLoopIterationTolerance": 0.01,
    "HeatTransferCoef": 4,  # W/(m2 K)
    "EnergyBalanceStateEquation": 'PR',
    "ViscosityCalculationMethod": 'HZ',
    "DewTemperatureCalculation": False,
    "ForceGasPhase": True,
    "MembranePolymerThermalConductivity": 0.2,  # W/(m K)
    "MembranePorosity": 0.5
}

# =============================================================================
# 3. EQUIPMENT CONFIGURATION
# =============================================================================

EQUIPMENT_CONFIG = [
    {
        "type": "HFM",
        "name": "HFM1",
        "description": "Scenario 'Vuong'",
    },
]

# =============================================================================
# 4. CONNECTIONS
# =============================================================================

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate"},
    {"from": ("HFM1", "permeate"), "to": "Permeate"},
]
