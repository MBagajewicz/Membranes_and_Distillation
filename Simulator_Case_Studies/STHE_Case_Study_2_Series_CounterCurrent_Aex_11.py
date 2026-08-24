"""
STHE_Case_Study_2_Series_CounterCurrent.py
============================================================

Two shell-and-tube heat exchangers in series with counter-current flow.

Hot side:
    HotFeed -> STHE1 -> STHE2 -> HotProduct

Cold side:
    ColdFeed -> STHE2 -> ColdTear -> STHE1 -> ColdProduct

ColdTear is used as the tear stream because the counter-current
arrangement creates a dependency loop between STHE1 and STHE2.
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
        "composition": {"Methanol": 1.0},
        "P": 20.0e5,
        "T": 393.15,       # 120 °C
        "mass_flow": 20, # kg/s
        "molar_flow": None,
        "backend": ThermoBackend.HEOS,
    },

    "ColdFeed": {
        "composition": {"Water": 1.0},
        "P": 3.0e5,
        "T": 320.15,       # 47 °C
        "mass_flow": 60, # kg/s
        "molar_flow": None,
        "backend": ThermoBackend.HEOS,
    },
}


# =============================================================================
# 3. EQUIPMENT CONFIGURATION
# =============================================================================

EQUIPMENT_CONFIG = [

    # -------------------------------------------------------------------------
    # First STHE
    # -------------------------------------------------------------------------

    {
        "type": "STHE",
        "name": "STHE1",
        "tag": "E-101",
        "description": "First shell-and-tube heat exchanger",

        "geometry": {
            "shell": {
                "diameter": 0.7874,
                "fouling_factor": 0.0007,
            },

            "tubes": {
                "length": 6.0976,
                "outside_diameter": 0.0508,
                "inside_diameter": 0.0475,
                "pitch_ratio": 1.5,
                "layout": 1,
                "passes": 6,
                "wall_conductivity": 50.0,
                "fouling_factor": 0.0002,
                "stream": "hot_stream",
            },

            "baffles": {
                "number": 13,
                "cut": 0.25,
                "sealing_strips": 1,
            },
        },

        "correlations": {
            "tube_method": "Dittus_Boelter",
            "shell_method": "Kern",
        },
    },


    # -------------------------------------------------------------------------
    # Second STHE
    # -------------------------------------------------------------------------
    {
        "type": "STHE",
        "name": "STHE2",
        "tag": "E-102",
        "description": "First shell-and-tube heat exchanger",

        "geometry": {
            "shell": {
                "diameter": 0.7874,
                "fouling_factor": 0.0007,
            },

            "tubes": {
                "length": 6.0976,
                "outside_diameter": 0.0508,
                "inside_diameter": 0.0475,
                "pitch_ratio": 1.5,
                "layout": 1,
                "passes": 6,
                "wall_conductivity": 50.0,
                "fouling_factor": 0.0002,
                "stream": "hot_stream",
            },

            "baffles": {
                "number": 13,
                "cut": 0.25,
                "sealing_strips": 1,
            },
        },

        "correlations": {
            "tube_method": "Dittus_Boelter",
            "shell_method": "Kern",
        },
    },

]


# =============================================================================
# 4. CONNECTIONS
# =============================================================================

CONNECTIONS = [

    # -------------------------------------------------------------------------
    # Hot side
    # -------------------------------------------------------------------------

    {"from": "HotFeed", "to": ("STHE1", "hot_in")},
    {"from": ("STHE1", "hot_out"), "to": "HotBetween"},
    {"from": "HotBetween", "to": ("STHE2", "hot_in")},
    {"from": ("STHE2", "hot_out"), "to": "HotProduct"},


    # -------------------------------------------------------------------------
    # Cold side - counter-current
    # -------------------------------------------------------------------------

    {"from": "ColdFeed", "to": ("STHE2", "cold_in")},
    {"from": ("STHE2", "cold_out"), "to": "ColdTear"},
    {"from": "ColdTear", "to": ("STHE1", "cold_in")},
    {"from": ("STHE1", "cold_out"), "to": "ColdProduct"},
]


# =============================================================================
# 5. ITERATIVE SOLVER CONFIGURATION
# =============================================================================

ITERATIVE_SOLVER_CONFIG = {
    "tear_streams": "ColdTear",
    "initial_guesses": {
        "ColdTear": {
            "T": 355,  # K; physically valid first estimate for STHE1
        },
    },
    "tolerance": 1.0e-6,
    "max_iterations": 100,
    "relaxation": 0.5,
}
