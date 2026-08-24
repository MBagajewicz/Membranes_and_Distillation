"""UnitOperation — equipment with input/output ports and a solve() contract."""

from __future__ import annotations

from abc import abstractmethod
from typing import Dict, List

from .base_equipment import BaseEquipment
from .port import Port, PortDirection


class UnitOperation(BaseEquipment):
    """
    Base class for process units that have input/output ports.
    Inherits common equipment attributes from BaseEquipment.
    Each unit registers its own ports.
    Ports are exposed as attributes for easy access:  unit.feed, unit.retentate, etc.
    """

    def __init__(
        self,
        name: str,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(name, tag, description)
        self._ports: Dict[str, Port] = {}

    def add_port(self, name: str, direction: PortDirection) -> Port:
        """
        Create a new port on this unit.
        Raises ValueError if a port with this name already exists.
        """
        if name in self._ports:
            raise ValueError(f"Port '{name}' already exists on unit '{self.name}'")

        port = Port(name, direction, self)
        self._ports[name] = port

        # Expose as attribute so you can write:  my_unit.feed
        setattr(self, name, port)
        return port

    @property
    def ports(self) -> Dict[str, Port]:
        """Dictionary of all ports on this unit."""
        return self._ports

    @property
    def input_ports(self) -> List[Port]:
        """All INPUT ports (where streams enter the unit)."""
        return [p for p in self._ports.values() if p.direction == PortDirection.INPUT]

    @property
    def output_ports(self) -> List[Port]:
        """All OUTPUT ports (where streams leave the unit)."""
        return [p for p in self._ports.values() if p.direction == PortDirection.OUTPUT]

    @abstractmethod
    def solve(self) -> None:
        """
        Solve this unit.
        The unit reads from its INPUT ports' streams and writes to its OUTPUT ports' streams.
        The Flowsheet and Solver never touch the physics inside here.
        """
        ...
