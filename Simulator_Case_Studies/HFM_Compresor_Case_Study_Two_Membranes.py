"""
hfm_config_with_compressor.py
==============================
Example: HFM1 → Compressor → HFM2 cascade.

The permeate of HFM1 is recompressed before entering HFM2,
so HFM2 can operate at the same PPerm as HFM1 (or higher).
"""

import numpy as np
from Common.Stream.stream import ThermoBackend


# =============================================================================
# 1. FEED
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
# 2. COMMON HFM PARAMETERS
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
# 3. EQUIPMENT CONFIGURATION — mixed HFM + Compressor
# =============================================================================
#
# Use "type": "HFM" for membranes and "type": "Compressor" for compressors.
# Compressor-specific keys:
#   P_out      : discharge pressure [Pa]
#   efficiency : isentropic efficiency (0–1), default 0.8
#   gamma      : heat capacity ratio, default 1.3

EQUIPMENT_CONFIG = [
    {
        "type": "HFM",
        "name": "HFM1",
        "description": "Stage 1 — CO2/Propane separation",
        "DiamShell": 0.0394,
        "FiberLengthInElement": 0.2,
        "N": 3380,
    },
    {
        "type": "Compressor",
        "name": "COMP1",
        "description": "Permeate recompression",
        "P_out": 5e5,          # 5 bar — compress permeate from 1 bar
        "efficiency": 0.75,
        "gamma": 1.3,
    },
    {
        "type": "HFM",
        "name": "HFM2",
        "description": "Stage 2 — compressed permeate polishing",
        "DiamShell": 0.0300,
        "FiberLengthInElement": 0.1,
        "N": 1500,
        # Now HFM2 feed is ~5 bar, so PPerm can be 1 bar again (driving force!)
        "PPerm": 1e5,
    },
]


# =============================================================================
# 4. CONNECTIONS
# =============================================================================
#
# Compressor ports: "inlet", "outlet"
# HFM ports:       "feed", "retentate", "permeate"

CONNECTIONS = [
    {"from": "Feed", "to": ("HFM1", "feed")},
    {"from": ("HFM1", "retentate"), "to": "Retentate1"},
    {"from": ("HFM1", "permeate"), "to": "Permeate1_to_Comp"},

    {"from": "Permeate1_to_Comp", "to": ("COMP1", "inlet")},
    {"from": ("COMP1", "outlet"), "to": "Compressed_to_HFM2"},

    {"from": "Compressed_to_HFM2", "to": ("HFM2", "feed")},
    {"from": ("HFM2", "retentate"), "to": "Retentate2"},
    {"from": ("HFM2", "permeate"), "to": "Permeate2"},
]
