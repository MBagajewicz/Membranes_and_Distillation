"""
Stream - Thermodynamic state representation for process simulation.

This package provides a single, backend-agnostic class ``Stream`` that
encapsulates a thermodynamic state and exposes derived properties
through a clean, read-only interface.

Example
-------
>>> from stream import Stream, ThermoBackend
>>> s = Stream(
...     composition={"Water": 1.0},
...     P=101325,
...     T=373.15,
...     mass_flow=1.0,
...     backend=ThermoBackend.HEOS,
... )
>>> s.cp_mass
4216.3...
"""

from .stream import Stream
from .thermo_backend import ThermoBackend
from .exceptions import (
    StreamError,
    CompositionError,
    FlowSpecificationError,
    BackendError,
)
from . import units
from . import constants

__all__ = [
    "Stream",
    "ThermoBackend",
    "StreamError",
    "CompositionError",
    "FlowSpecificationError",
    "BackendError",
    "units",
    "constants",
]

__version__ = "0.1.0"