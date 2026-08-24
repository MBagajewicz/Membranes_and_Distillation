"""Flowsheet — pure data container for units, streams, and connections."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from .port import Port, PortDirection
from .unit_operation import UnitOperation


class Flowsheet:
    """
    The Flowsheet owns:
      - units   : all equipment objects (BaseEquipment / UnitOperation)
      - streams : all Stream objects (your CoolProp-backed Stream)
    It does NOT solve anything. It does NOT know about solvers.
    Connections are implicit: a Stream knows its producer and consumer.
    ALL connection logic is centralized here.
    """

    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.units: Dict[str, UnitOperation] = {}
        self.streams: Dict[str, Stream] = {}

    # -------------------------------------------------------------------------
    # Building methods
    # -------------------------------------------------------------------------

    def add_unit(self, name: str, unit: UnitOperation) -> UnitOperation:
        """Register a unit instance. The unit's .name attribute is updated to match."""
        unit.name = name
        self.units[name] = unit
        return unit

    def add_stream(self, name: str, stream: Stream) -> Stream:
        """
        Register a Stream.
        The Stream is expected to have .producer and .consumer attributes
        (declared directly in the Stream class, not attached dynamically).
        """
        stream.name = name
        self.streams[name] = stream
        return stream

    def connect(self, *,
                source: Optional[Tuple[str, str]] = None,
                stream: str,
                destination: Optional[Tuple[str, str]] = None) -> None:
        """
        Connect the process graph. This is the ONLY public way to create connections.

        A connection links:
          - an OUTPUT port (source)     -> a Stream
          - a Stream                    -> an INPUT port (destination)

        Either source or destination can be None:
          - source=None     : the stream is a FEED to the system
          - destination=None: the stream is a PRODUCT of the system

        Examples:
          fs.connect(source=("HFM1", "retentate"), stream="RetGas", destination=("STHE1", "tube_in"))
          fs.connect(stream="Feed", destination=("HFM1", "feed"))
          fs.connect(source=("STHE1", "shell_out"), stream="Product")
        """
        # Resolve the Stream object from its name
        stream_obj = self.streams[stream]

        # --- Resolve SOURCE port (must be an OUTPUT port) ---
        source_port: Optional[Port] = None
        if source is not None:
            unit_name, port_name = source
            source_port = self.units[unit_name].ports[port_name]

            if source_port.direction != PortDirection.OUTPUT:
                raise ValueError(f"Source '{source_port}' must be an OUTPUT port")

            if source_port.stream is not None and source_port.stream is not stream_obj:
                raise ValueError(
                    f"Source '{source_port}' is already connected to '{source_port.stream.name}'"
                )

        # --- Resolve DESTINATION port (must be an INPUT port) ---
        dest_port: Optional[Port] = None
        if destination is not None:
            unit_name, port_name = destination
            dest_port = self.units[unit_name].ports[port_name]

            if dest_port.direction != PortDirection.INPUT:
                raise ValueError(f"Destination '{dest_port}' must be an INPUT port")

            if dest_port.stream is not None and dest_port.stream is not stream_obj:
                raise ValueError(
                    f"Destination '{dest_port}' is already connected to '{dest_port.stream.name}'"
                )

        # --- Perform the connections (internal method, validated above) ---
        if source_port:
            source_port._connect(stream_obj)
        if dest_port:
            dest_port._connect(stream_obj)

    # -------------------------------------------------------------------------
    # Diagnostic / reporting
    # -------------------------------------------------------------------------

    def report(self) -> str:
        """Generate a human-readable summary of the flowsheet state."""
        lines = [f"{'='*60}", f"  FLOWSHEET: {self.name}", f"{'='*60}"]

        # FEEDS: streams with no producer
        lines.append("\n  FEEDS (streams with no producer):")
        for s in self.streams.values():
            if s.producer is None:
                lines.append(f"    • {s.name}")

        # PRODUCTS: streams with no consumer
        lines.append("\n  PRODUCTS (streams with no consumer):")
        for s in self.streams.values():
            if s.consumer is None:
                lines.append(f"    • {s.name}")

        # CONNECTIONS: full graph view
        lines.append("\n  CONNECTIONS:")
        for s in self.streams.values():
            prod = f"{s.producer.unit.name}.{s.producer.name}" if s.producer else "FEED"
            cons = f"{s.consumer.unit.name}.{s.consumer.name}" if s.consumer else "PRODUCT"
            lines.append(f"    [OK] {prod:20} -- {s.name:15} --> {cons}")

        # UNITS: port status + equipment diagnostics
        lines.append("\n  UNITS:")
        for name, unit in self.units.items():
            ins = ", ".join(f"{p.name}={p.stream.name if p.stream else '?'}" for p in unit.input_ports)
            outs = ", ".join(f"{p.name}={p.stream.name if p.stream else '?'}" for p in unit.output_ports)
            lines.append(f"    • {name} [{unit.status}]: IN({ins}) -> OUT({outs})")
            if unit.warnings:
                for w in unit.warnings:
                    lines.append(f"      ⚠ {w}")

        lines.append("=" * 60)
        return "\n".join(lines)
