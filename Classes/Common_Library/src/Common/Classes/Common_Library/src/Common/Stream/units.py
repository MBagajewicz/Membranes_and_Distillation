"""
Unit conversion utilities.

This module provides a lightweight, extensible unit conversion system.
It is intentionally minimal today but structured so that adding new
unit families (e.g. energy, viscosity) is a matter of adding entries
to the internal conversion tables.

All conversions are handled in pure Python; no external dependencies.
"""

from typing import Union
from decimal import Decimal


Number = Union[int, float, Decimal]


class UnitError(Exception):
    """Raised when a unit conversion is requested for an unsupported unit."""
    pass


class _UnitFamily:
    """Internal descriptor for a family of convertible units."""

    def __init__(self, base_unit: str, conversions: dict):
        self.base_unit = base_unit
        # conversions: {unit_name: factor_to_base}
        self.conversions = conversions

    def to_base(self, value: Number, unit: str) -> float:
        if unit not in self.conversions:
            raise UnitError(
                f"Unknown unit '{unit}' for family '{self.base_unit}'. "
                f"Supported: {list(self.conversions.keys())}"
            )
        return float(value) * self.conversions[unit]

    def from_base(self, value: Number, unit: str) -> float:
        if unit not in self.conversions:
            raise UnitError(
                f"Unknown unit '{unit}' for family '{self.base_unit}'. "
                f"Supported: {list(self.conversions.keys())}"
            )
        return float(value) / self.conversions[unit]


# ----------------------------------------------------------------------
# Conversion tables
# ----------------------------------------------------------------------
_PRESSURE = _UnitFamily(
    base_unit="Pa",
    conversions={
        "Pa": 1.0,
        "kPa": 1e3,
        "MPa": 1e6,
        "bar": 1e5,
        "mbar": 1e2,
        "atm": 101325.0,
        "psi": 6894.757293168,
        "torr": 133.322368421,
    },
)

_MASS_FLOW = _UnitFamily(
    base_unit="kg/s",
    conversions={
        "kg/s": 1.0,
        "g/s": 1e-3,
        "kg/h": 1.0 / 3600.0,
        "lb/s": 0.45359237,
        "lb/h": 0.45359237 / 3600.0,
    },
)

_MOLAR_FLOW = _UnitFamily(
    base_unit="mol/s",
    conversions={
        "mol/s": 1.0,
        "kmol/s": 1e3,
        "kmol/h": 1e3 / 3600.0,
        "lbmol/s": 453.59237,
    },
)


class Pressure:
    """Convert pressure values to/from the SI base unit (Pa)."""

    @staticmethod
    def to_pa(value: Number, unit: str = "Pa") -> float:
        """Convert ``value`` from ``unit`` to pascals."""
        return _PRESSURE.to_base(value, unit)

    @staticmethod
    def from_pa(value: Number, unit: str = "Pa") -> float:
        """Convert ``value`` from pascals to ``unit``."""
        return _PRESSURE.from_base(value, unit)


class Temperature:
    """Convert temperature values to/from the SI base unit (K)."""

    @staticmethod
    def to_k(value: Number, unit: str = "K") -> float:
        """Convert ``value`` from ``unit`` to kelvin."""
        unit = unit.upper()
        if unit == "K":
            return float(value)
        if unit == "C":
            return float(value) + 273.15
        if unit == "F":
            return (float(value) - 32.0) * 5.0 / 9.0 + 273.15
        if unit == "R":
            return float(value) * 5.0 / 9.0
        raise UnitError(
            f"Unknown temperature unit '{unit}'. Supported: K, C, F, R."
        )

    @staticmethod
    def from_k(value: Number, unit: str = "K") -> float:
        """Convert ``value`` from kelvin to ``unit``."""
        unit = unit.upper()
        if unit == "K":
            return float(value)
        if unit == "C":
            return float(value) - 273.15
        if unit == "F":
            return (float(value) - 273.15) * 9.0 / 5.0 + 32.0
        if unit == "R":
            return float(value) * 9.0 / 5.0
        raise UnitError(
            f"Unknown temperature unit '{unit}'. Supported: K, C, F, R."
        )


class MassFlow:
    """Convert mass flow values to/from the SI base unit (kg/s)."""

    @staticmethod
    def to_kg_s(value: Number, unit: str = "kg/s") -> float:
        return _MASS_FLOW.to_base(value, unit)

    @staticmethod
    def from_kg_s(value: Number, unit: str = "kg/s") -> float:
        return _MASS_FLOW.from_base(value, unit)


class MolarFlow:
    """Convert molar flow values to/from the SI base unit (mol/s)."""

    @staticmethod
    def to_mol_s(value: Number, unit: str = "mol/s") -> float:
        return _MOLAR_FLOW.to_base(value, unit)

    @staticmethod
    def from_mol_s(value: Number, unit: str = "mol/s") -> float:
        return _MOLAR_FLOW.from_base(value, unit)