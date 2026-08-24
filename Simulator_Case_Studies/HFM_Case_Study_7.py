"""
HFM_Case_Study_7.py
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
        "composition": dict(zip(['CarbonDioxide', 'Nitrogen', 'Methane', 'Ethane', 'n-Propane', 'IsoButane', 'n-Butane', 'Isopentane', 'n-Pentane', 'n-Hexane', 'n-Heptane', 'n-Octane', 'n-Nonane', 'Water', 'HydrogenSulfide', 'CarbonylSulfide'], np.array([0.24117, 0.00322, 0.60129, 0.07544, 0.05384, 0.00693, 0.01361, 0.00162, 0.00212, 0.00057, 0.00013, 4e-05, 1e-05, 1e-06, 5e-06, 2.5e-07]))),
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
    "EnergyBalance": True,
    "UseFugacity": True,
    "PRet": None,  # If None: automatic Hagen-Poiseuille pressure drop calculation
    "M": np.array([0.04401 , 0.02802 , 0.01604 , 0.03007 , 0.0441  , 0.05812 , 0.05812 ,
 0.07215 , 0.07215 , 0.08618 , 0.1002  , 0.11423 , 0.12826 , 0.018015,
 0.03408 , 0.06008 ]),
    "MU": np.array([0.000015, 0.000029, 0.000011, 0.000013, 0.000015, 0.000017, 0.000017,
 0.000018, 0.000018, 0.000021, 0.000024, 0.000029, 0.000032, 0.000013,
 0.000014, 0.000013]),
    "T": 331.04999999999995,
    "PPerm": 2.900000e+05,
    "Q": np.array([
            4.801086E-03 * 1000.0 / 3600.0 / 1e5,   # CO2
            1.664280E-04 * 1000.0 / 3600.0 / 1e5,   # N2
            1.664280E-04 * 1000.0 / 3600.0 / 1e5,   # CH4
            1.688400E-05 * 1000.0 / 3600.0 / 1e5,   # C2H6
            1.206000E-06 * 1000.0 / 3600.0 / 1e5,   # C3H8
            1.206000E-07 * 1000.0 / 3600.0 / 1e5,   # C4H10-2
            1.206000E-08 * 1000.0 / 3600.0 / 1e5,   # C4H10-1
            1.206000E-08 * 1000.0 / 3600.0 / 1e5,   # C5H12-2
            1.206000E-08 * 1000.0 / 3600.0 / 1e5,   # C5H12-1
            1.206000E-10 * 1000.0 / 3600.0 / 1e5,   # C6H14-1
            1.206000E-11 * 1000.0 / 3600.0 / 1e5,   # C7H16
            1.206000E-12 * 1000.0 / 3600.0 / 1e5,   # C8H18-1
            1.206000E-13 * 1000.0 / 3600.0 / 1e5,   # C9H20-1
            1.664280E-02 * 1000.0 / 3600.0 / 1e5,   # H2O
            4.801086E-03 * 1000.0 / 3600.0 / 1e5,   # H2S
            1.206000E-13 * 1000.0 / 3600.0 / 1e5,   # COS (fallback default)
        ]),
    "DiamShell": 0.33,
    "DiamFiber_o": 0.0002494,
    "DiamFiber_i": 0.000138,
    "FiberLengthInElement": 0.95,
    "NumberOfElementsPerTube": 5,
    "N": 180000,
    "Void_Frac": 0.8969,
    "NTubes": 80,
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
        "description": "Scenario 7",
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
