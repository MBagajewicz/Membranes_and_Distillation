"""
Thermodynamic backend identifiers for CoolProp.

Using an Enum instead of raw strings prevents typos at import time
and makes autocompletion work in any IDE.
"""

from enum import Enum


class ThermoBackend(Enum):
    """
    Supported CoolProp backends.

    Each member maps to the exact string that CoolProp expects when
    building an AbstractState.
    """

    PR = "PR"
    HEOS = "HEOS"
    REFPROP = "REFPROP"
    TTSE = "TTSE&HEOS"
    BICUBIC = "BICUBIC&HEOS"