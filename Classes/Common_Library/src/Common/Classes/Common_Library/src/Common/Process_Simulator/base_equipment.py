"""BaseEquipment — common metadata and diagnostics for all equipment."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, List


class BaseEquipment(ABC):
    """
    Abstract base for every piece of equipment.
    Holds common metadata, status, and diagnostics.
    Subclasses: UnitOperation, and eventually intermediate layers like
    HeatExchanger, Membrane, Pump, etc.
    """

    def __init__(
        self,
        name: str,
        tag: str = "",
        description: str = "",
    ):
        self.name = name
        self.tag = tag
        self.description = description

        # Runtime state
        self.status: str = "uninitialized"
        self.active: bool = True
        self.warnings: List[str] = []
        self.results: Dict[str, Any] = {}
        self.solve_time: float = 0.0

        # Solver-specific options (e.g. tolerance, max_iter, method)
        self.calculation_options: Dict[str, Any] = {}

    def reset_diagnostics(self) -> None:
        """Clear warnings and results before a new solve."""
        self.warnings.clear()
        self.results.clear()
        self.solve_time = 0.0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, status={self.status})"
