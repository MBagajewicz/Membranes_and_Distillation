"""
HFM_Case_Study_10_chu3.py
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
        "composition": dict(zip(['CO2', 'CH4', 'N2'], np.array([0.1, 0.9, 0.0]))),
        "P": 1500000.0,
        "T": 308,
        "molar_flow": 0.35,
        "backend": ThermoBackend.HEOS,
    },
}

# =============================================================================
# 2. COMMON EQUIPMENT PARAMETERS
# =============================================================================

COMMON_PARAMS = {
    "PressureDrop": True,
    "EnergyBalance": True,
    "UseFugacity": True,
    "PRet": None,  # If None: automatic Hagen-Poiseuille pressure drop calculation
    "M": np.array([0.04401, 0.01604, 0.02802]),
    "MU": np.array([0.000015, 0.000011, 0.000029]),
    "T": 308,
    "PPerm": 1.000000e+05,
    "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]), # permeance [mol/(m² Pa s)]
    "DiamShell": 0.08,
    "DiamFiber_o": 0.00011,
    "DiamFiber_i": 7.000000e-05,
    "FiberLengthInElement": 0.9,
    "N": 386115,
    "Void_Frac": 0.27,
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
        "description": "Scenario 'Chu_3'",
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
