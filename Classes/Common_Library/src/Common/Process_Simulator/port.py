"""Port and PortDirection definitions."""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class PortDirection(Enum):
    """Every port is either an INPUT (consumes a stream) or OUTPUT (produces a stream)."""
    INPUT = auto()
    OUTPUT = auto()


class Port:
    """
    A Port belongs to a UnitOperation and can hold one Stream.

    The ONLY way to connect a Port to a Stream is through Flowsheet.connect().
    Port._connect() is an internal method; calling it directly bypasses
    Flowsheet validation and is strongly discouraged.
    """

    def __init__(self, name: str, direction: PortDirection, unit: UnitOperation):
        self.name = name
        self.direction = direction
        self.unit = unit          # parent unit (e.g. HFM1, STHE1)
        self._stream: Optional[Stream] = None

    @property
    def stream(self) -> Optional[Stream]:
        """The Stream currently attached to this port."""
        return self._stream

    def _connect(self, stream: Stream) -> None:
        """
        INTERNAL METHOD. Do not call directly.
        Called exclusively by Flowsheet.connect() after validation.
        Updates the Stream's producer or consumer link.
        """
        self._stream = stream

        if self.direction == PortDirection.OUTPUT:
            stream.producer = self
        elif self.direction == PortDirection.INPUT:
            stream.consumer = self

    def __repr__(self) -> str:
        status = f" -> {self._stream.name}" if self._stream else " -> None"
        return f"{self.unit.name}.{self.name}({self.direction.name}){status}"
