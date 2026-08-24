"""
HFM_Case_Study_1_With_Compressor.py
============================================================
Single-membrane flowsheet with permeate recompression.

Based on HFM_Case_Study_1 (fast-converging CO2/CH4 separation)
with an added compressor stage on the permeate stream.
"""

import numpy as np
from Common.Stream.stream import ThermoBackend

# =============================================================================
# 1. PROCESS STREAMS
# =============================================================================

STREAM_CONFIGS = {
    "Feed": {
        "composition": dict(zip(['CO2', 'CH4'], np.array([0.1, 0.9]))),
        "P": 3500000.0,
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
    "M": np.array([0.04401, 0.01604]),
    "MU": np.array([0.000015, 0.000011]),
    "T": 308,
    "PPerm": 1.000000e+05,
    "Q": np.array([3.207e-9, 1.33e-10]),  # [mol/(m2 Pa s)] Permeance
    "DiamShell": 0.1,
    "DiamFiber_o": 0.00025,
    "DiamFiber_i": 0.0002,
    "FiberLengthInElement": 0.6,
    "N": 60000,
    "Void_Frac": 0.625,
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
# 3. EQUIPMENT CONFIGURATION — HFM + Compressor
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
        "description": "Stage 1 — CO2/CH4 separation",
    },
    {
        "type": "Compressor",
        "name": "COMP1",
        "description": "Permeate recompression",
        "P_out": 5.000000e+05,  # 5 bar — recompress permeate from 1 bar
        "efficiency": 0.75,
        "gamma": 1.3,
    },
    {
        "type": "HFM",
        "name": "HFM2",
        "description": "Stage 2 — compressed permeate polishing",
        # Override geometry for second stage (smaller, since feed is already enriched)
        "DiamShell": 0.08,
        "FiberLengthInElement": 0.4,
        "N": 30000,
        # Now HFM2 feed is ~5 bar, so PPerm can be 1 bar again (driving force!)
        "PPerm": 1.000000e+05,
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
