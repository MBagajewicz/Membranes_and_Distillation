"""
STHE UnitOperation adapter for the Common_Library flowsheet.

This is the integration boundary between the STHE physics and the framework.
The STHE physics remains in Simulator_STHE.STHE; this class only:
- exposes Common_Library ports,
- reads Common.Stream objects,
- maps their properties into the STHE solver,
- writes outlet T/P back to the connected Common.Stream objects.
"""

from __future__ import annotations

from typing import Any

from Common.Process_Simulator import UnitOperation, PortDirection

from ..STHE import STHE


class STHEHeatExchanger(UnitOperation):
    """
    Shell-and-tube heat exchanger UnitOperation.

    Ports
    -----
    hot_in : INPUT
        Hot-side inlet stream.
    hot_out : OUTPUT
        Hot-side outlet stream.
    cold_in : INPUT
        Cold-side inlet stream.
    cold_out : OUTPUT
        Cold-side outlet stream.

    Parameters
    ----------
    name:
        Flowsheet unit name.
    simulator:
        Configured :class:`Simulator_STHE.STHE` instance. If omitted, a
        default STHE object is created and can be configured through
        ``unit.simulator.geometry`` and ``unit.simulator.options``.
    tag, description:
        Common_Library equipment metadata.
    """

    def __init__(
        self,
        name: str,
        simulator: STHE | None = None,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(name, tag=tag, description=description)

        self._sim = simulator if simulator is not None else STHE()

        self.add_port("hot_in", PortDirection.INPUT)
        self.add_port("hot_out", PortDirection.OUTPUT)
        self.add_port("cold_in", PortDirection.INPUT)
        self.add_port("cold_out", PortDirection.OUTPUT)

    @property
    def simulator(self) -> STHE:
        """Configured internal STHE physics model."""
        return self._sim

    @staticmethod
    def _scalar(value: Any) -> float:
        """Convert scalar / zero-dimensional NumPy results to float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            import numpy as np
            return float(np.asarray(value).squeeze())

    @staticmethod
    def _require_stream(port, label: str):
        stream = port.stream
        if stream is None:
            raise RuntimeError(f"{port.unit.name}.{label} is not connected to a stream")
        return stream

    def _sync_streams(self, hot, cold) -> None:
        """Map Common.Stream states into the STHE legacy calculation API."""
        sim = self._sim

        sim.streams.hot.inlet.temperature = float(hot.T)
        sim.streams.hot.inlet.pressure = float(hot.P)
        sim.streams.hot.inlet.flow = float(hot.mass_flow)
        sim.streams.hot.inlet.cp = float(hot.cp_mass)
        sim.streams.hot.inlet.density = float(hot.density_mass)
        sim.streams.hot.inlet.viscosity = float(hot.viscosity)
        sim.streams.hot.inlet.conductivity = float(hot.conductivity)
        sim.streams.hot.inlet.fluid = "hot_stream"

        sim.streams.cold.inlet.temperature = float(cold.T)
        sim.streams.cold.inlet.pressure = float(cold.P)
        sim.streams.cold.inlet.flow = float(cold.mass_flow)
        sim.streams.cold.inlet.cp = float(cold.cp_mass)
        sim.streams.cold.inlet.density = float(cold.density_mass)
        sim.streams.cold.inlet.viscosity = float(cold.viscosity)
        sim.streams.cold.inlet.conductivity = float(cold.conductivity)
        sim.streams.cold.inlet.fluid = "cold_stream"

        # Outlet states are populated by STHE.simulate().
        sim.streams.hot.outlet.temperature = None
        sim.streams.cold.outlet.temperature = None

    def solve(self) -> None:
        """Run the STHE model and update the two output Common.Streams."""
        hot = self._require_stream(self.hot_in, "hot_in")
        cold = self._require_stream(self.cold_in, "cold_in")
        hot_out = self.hot_out.stream
        cold_out = self.cold_out.stream

        if hot_out is None:
            raise RuntimeError(f"{self.name}.hot_out is not connected to a stream")
        if cold_out is None:
            raise RuntimeError(f"{self.name}.cold_out is not connected to a stream")

        if hot.mass_flow <= 0 or cold.mass_flow <= 0:
            raise ValueError("STHE inlet mass flows must be > 0")
        if hot.T <= cold.T:
            raise ValueError(
                f"STHE requires hot_in.T > cold_in.T; got "
                f"{hot.T:.3f} K <= {cold.T:.3f} K"
            )

        self._sync_streams(hot, cold)


        # Internal solver: calculates U, installed area, NTU, duty,
        # outlet temperatures and both-side pressure drops.
        calc = self._sim.simulate()

        tube_is_hot = self._sim.geometry.tubes.stream == "hot_stream"
        dp_tube = self._scalar(self._sim.DeltaP_tube)
        dp_shell = self._scalar(self._sim.DeltaP_shell)

        if tube_is_hot:
            dp_hot, dp_cold = dp_tube, dp_shell
        elif self._sim.geometry.tubes.stream == "cold_stream":
            dp_hot, dp_cold = dp_shell, dp_tube
        else:
            raise ValueError(
                "geometry.tubes.stream must be 'hot_stream' or 'cold_stream'"
            )

        hot_P_out = max(0.0, float(hot.P) - dp_hot)
        cold_P_out = max(0.0, float(cold.P) - dp_cold)

        hot_T_out = self._scalar(self._sim.streams.hot.outlet.temperature)
        cold_T_out = self._scalar(self._sim.streams.cold.outlet.temperature)
        Q = self._scalar(self._sim.Q)


        # Preserve composition and mass flow. The Common.Stream recomputes all
        # dependent properties after each update.
        hot_out.update(P=hot_P_out, T=hot_T_out, mass_flow=float(hot.mass_flow))
        cold_out.update(P=cold_P_out, T=cold_T_out, mass_flow=float(cold.mass_flow))



        # ------------------------------------------------------------
        # ENERGY CONSISTENCY CHECK
        # ------------------------------------------------------------

        Q_hot_h = (
            float(hot.mass_flow)
            * (
                float(hot.enthalpy_mass)
                - float(hot_out.enthalpy_mass)
            )
        )

        Q_cold_h = (
            float(cold.mass_flow)
            * (
                float(cold_out.enthalpy_mass)
                - float(cold.enthalpy_mass)
            )
        )

        print("=" * 70)
        print(f"[ENERGY CHECK AFTER UPDATE] {self.name}")
        print(f"Q_STHE      = {Q:.6f} W")
        print(f"Q_hot(h)    = {Q_hot_h:.6f} W")
        print(f"Q_cold(h)   = {Q_cold_h:.6f} W")
        print(f"Q_hot-Q     = {Q_hot_h - Q:.6f} W")
        print(f"Q_cold-Q    = {Q_cold_h - Q:.6f} W")
        print("=" * 70)







        self.results.update({
            "heat_duty_W": Q,
            "U_W_m2K": self._scalar(self._sim.U),
            "area_m2": self._scalar(self._sim.Area),
            "NTU": self._scalar(self._sim.NTU),
            "effectiveness": self._scalar(self._sim.Effectiveness),
            "deltaP_tube_Pa": dp_tube,
            "deltaP_shell_Pa": dp_shell,
            "deltaP_hot_Pa": dp_hot,
            "deltaP_cold_Pa": dp_cold,
            "hot_outlet_temperature_K": hot_T_out,
            "cold_outlet_temperature_K": cold_T_out,
            "hot_outlet_pressure_Pa": hot_P_out,
            "cold_outlet_pressure_Pa": cold_P_out,
        })

        # Optional rating quantities are available after simulation.
        if hasattr(self._sim, "LMTD"):
            self.results["LMTD_K"] = self._scalar(self._sim.LMTD)
        if hasattr(self._sim, "F"):
            self.results["correction_factor"] = self._scalar(self._sim.F)

        # A simple energy consistency diagnostic.
        q_hot = float(hot.mass_flow) * float(hot.cp_mass) * (float(hot.T) - hot_T_out)
        q_cold = float(cold.mass_flow) * float(cold.cp_mass) * (cold_T_out - float(cold.T))
        q_ref = max(abs(q_hot), abs(q_cold), 1.0)
        energy_error = abs(q_hot - q_cold) / q_ref
        self.results["energy_balance_relative_error"] = energy_error

        if energy_error > 1e-3:
            self.warnings.append(
                f"STHE energy balance relative error = {energy_error:.3e}"
            )

        print(
            f"  [{self.name}] Q={Q/1000:.3f} kW | "
            f"Th,out={hot_T_out:.2f} K | Tc,out={cold_T_out:.2f} K"
        )
        print(
            f"  [{self.name}] ΔP hot={dp_hot/1e5:.4f} bar | "
            f"ΔP cold={dp_cold/1e5:.4f} bar"
        )
