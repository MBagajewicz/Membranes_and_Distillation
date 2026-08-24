"""
HFM_Case_Study_9.py
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
        "composition": dict(zip(['CarbonDioxide', 'Nitrogen', 'Methane', 'Ethane', 'Propane', 'Isobutane', 'n-Butane', 'Isopentane', 'n-Pentane', 'n-Hexane', 'n-Heptane', 'n-Octane', 'n-Nonane', 'Water', 'HydrogenSulfide', 'CarbonylSulfide'], np.array([0.24117, 0.00322, 0.60129, 0.07544, 0.05384, 0.00693, 0.01361, 0.00162, 0.00212, 0.00057, 0.00013, 4e-05, 1.4e-05, 1e-06, 5e-06, 2.5e-07]))),
        "P": 5118000.0,
        "T": 331.04999999999995,
        "molar_flow": 2899.722222222222,
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
    "M": np.array([0.04401 , 0.02802 , 0.01604 , 0.03007 , 0.0441  , 0.05812 , 0.05812 ,
 0.07215 , 0.07215 , 0.08618 , 0.1002  , 0.11423 , 0.12826 , 0.018015,
 0.03408 , 0.06008 ]),
    "MU": np.array([0.000015, 0.000029, 0.000011, 0.000013, 0.000015, 0.000017, 0.000017,
 0.000018, 0.000018, 0.000021, 0.000024, 0.000029, 0.000032, 0.000013,
 0.000014, 0.000013]),
    "T": 331.04999999999995,
    "PPerm": 3.900000e+05,
    "Q": np.array([
            3.8246E-08, 2.2622E-09, 1.3769E-09, 2.5364E-10, 4.9529E-11,
            4.2575E-11, 2.9734E-11, 2.5735E-23, 1.5130E-20, 1.9806E-23,
            2.0619E-23, 1.9806E-23, 1.4491E-18, 1.5625E-07, 2.7022E-08, 2.7022E-08
        ]),
    "DiamShell": 0.33,
    "DiamFiber_o": 0.0002494,
    "DiamFiber_i": 0.000138,
    "FiberLengthInElement": 0.95,
    "NumberOfElementsPerTube": 5,
    "N": 180000,
    "Void_Frac": 0.8969,
    "NTubes": 80,
    "Discretizations": 100,  # Number of finite volumes along the membrane
    "LeastSquareSolverTolerance": 1.000000e-08,
    "LeastSquaresVerbose": 2,  # 2=Print all iterations, 1=Print final, 0=Silent
    "MassBalanceLoopIterationTolerance": 1.000000e-08,
    "NumberOfIterationsInLoop": 5000,
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
        "description": "Scenario 9",
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
