"""
STHE_Case_Study_1.py
============================================================
Single shell-and-tube heat exchanger flowsheet.

STHE has two inlet streams, one hot side and one cold side.
"""

from Common.Stream.stream import ThermoBackend


# =============================================================================
# 1. COMMON EQUIPMENT PARAMETERS
# =============================================================================

COMMON_PARAMS = {}


# =============================================================================
# 2. PROCESS STREAMS
# =============================================================================

STREAM_CONFIGS = {
    "HotFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 393.15,       # 120 °C
        "mass_flow": 0.50, # kg/s
        "molar_flow": None,
        "backend": ThermoBackend.HEOS,
    },
    "ColdFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 293.15,       # 20 °C
        "mass_flow": 0.50, # kg/s
        "molar_flow": None,
        "backend": ThermoBackend.HEOS,
    },
}


# =============================================================================
# 4. EQUIPMENT CONFIGURATION
# =============================================================================

EQUIPMENT_CONFIG = [
    {
        "type": "STHE",
        "name": "STHE1",
        "tag": "E-101",
        "description": "Single shell-and-tube heat exchanger",

        "geometry": {
            "shell": {
                "diameter": 0.50,             # m
                "fouling_factor": 1.0e-4,     # m2 K/W
            },
            "tubes": {
                "length": 5.0,                # m
                "outside_diameter": 0.025,    # m
                "inside_diameter": 0.021,     # m
                "pitch_ratio": 1.25,
                "layout": 1,
                "passes": 2,
                "wall_conductivity": 16.0,    # W/m/K
                "fouling_factor": 1.0e-4,     # m2 K/W
                "stream": "hot_stream",
            },
            "baffles": {
                "number": 8,
                "cut": 0.25,
                "sealing_strips": 1,
            },
        },

        "correlations": {
            "tube_method": "Gnielinski",
            "shell_method": "Bell",
        },
    },
]


# =============================================================================
# 5. CONNECTIONS
# =============================================================================

CONNECTIONS = [
    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": "ColdFeed", "to": ("STHE1", "cold_in")},

    {"from": ("STHE1", "hot_out"), "to": "HotProduct"},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]
