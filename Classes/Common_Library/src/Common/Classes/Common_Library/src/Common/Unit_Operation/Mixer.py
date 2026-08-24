"""
Mixer.py
========
Generic steady-state adiabatic material mixer.

The mixer combines multiple inlet streams into a single outlet stream
using total and component molar balances together with an adiabatic
energy balance.
"""

from __future__ import annotations

from typing import List

from Common.Process_Simulator import PortDirection, UnitOperation


class Mixer(UnitOperation):
    """
    Generic steady-state adiabatic material mixer.

    The mixer accepts a configurable number of material inlet streams
    and produces one outlet stream.

    The model assumes:
        - steady state
        - no chemical reaction
        - no heat transfer
        - no shaft work
        - negligible accumulation

    Parameters
    ----------
    name : str
        Unit name in the flowsheet.
    number_of_inlets : int, optional
        Number of material inlet ports. Default is 2.
    pressure_mode : str, optional
        Method used to determine outlet pressure:
            - "lowest_inlet"
            - "fixed"
        Default is "lowest_inlet".
    P_out : float, optional
        Fixed outlet pressure [Pa]. Required when pressure_mode="fixed".
    pressure_drop : float, optional
        Additional pressure drop applied to the reference pressure [Pa].
        Default is 0.
    tag : str, optional
        Equipment tag.
    description : str, optional
        Human-readable description.
    """

    def __init__(
        self,
        name: str,
        number_of_inlets: int = 2,
        pressure_mode: str = "lowest_inlet",
        P_out: float | None = None,
        pressure_drop: float = 0.0,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(name, tag=tag, description=description)

        if number_of_inlets < 2:
            raise ValueError(
                "Mixer requires at least two inlet streams."
            )

        if pressure_mode not in {"lowest_inlet", "fixed"}:
            raise ValueError(
                "pressure_mode must be 'lowest_inlet' or 'fixed'."
            )

        if pressure_mode == "fixed" and P_out is None:
            raise ValueError(
                "P_out must be provided when pressure_mode='fixed'."
            )

        if pressure_drop < 0.0:
            raise ValueError(
                "pressure_drop must be non-negative."
            )

        self.number_of_inlets = int(number_of_inlets)
        self.pressure_mode = pressure_mode
        self.P_out = None if P_out is None else float(P_out)
        self.pressure_drop = float(pressure_drop)

        for index in range(1, self.number_of_inlets + 1):
            self.add_port(
                f"inlet_{index}",
                PortDirection.INPUT,
            )

        self.add_port(
            "outlet",
            PortDirection.OUTPUT,
        )

    def _get_inlet_streams(self) -> List:
        """
        Return all connected inlet streams.

        Raises
        ------
        RuntimeError
            If one or more inlet ports are not connected.
        """
        streams = []

        for index in range(1, self.number_of_inlets + 1):
            port = self.ports[f"inlet_{index}"]

            if port.stream is None:
                raise RuntimeError(
                    f"{self.name}.{port.name} is not connected to a stream."
                )

            streams.append(port.stream)

        return streams

    def _get_outlet_pressure(self, inlet_streams: List) -> float:
        """
        Determine the outlet pressure according to the configured mode.
        """
        if self.pressure_mode == "fixed":
            pressure = float(self.P_out)
        else:
            pressure = min(float(stream.P) for stream in inlet_streams)

        pressure -= self.pressure_drop

        if pressure <= 0.0:
            raise ValueError(
                f"{self.name}: calculated outlet pressure must be positive."
            )

        return pressure

    def _calculate_mixed_composition(
        self,
        inlet_streams: List,
        total_molar_flow: float,
    ) -> dict[str, float]:
        """
        Calculate outlet mole fractions from component molar balances.
        """
        component_flows: dict[str, float] = {}

        for stream in inlet_streams:
            molar_flow = float(stream.molar_flow)

            for component, fraction in stream.composition.items():
                component_flows[component] = (
                    component_flows.get(component, 0.0)
                    + molar_flow * float(fraction)
                )

        return {
            component: flow / total_molar_flow
            for component, flow in component_flows.items()
        }

    def _solve_outlet_temperature(
        self,
        outlet,
        target_enthalpy_molar: float,
        P_out: float,
        composition: dict[str, float],
    ) -> float:
        """
        Solve outlet temperature from the adiabatic energy balance.

        A bisection method is used to avoid adding an external numerical
        dependency to Common_Library.
        """
        temperature_low = 50.0
        temperature_high = 2000.0

        tolerance = 1.0e-6
        max_iterations = 100

        outlet.update(
            P=P_out,
            T=temperature_low,
            composition=composition,
        )
        enthalpy_low = float(outlet.enthalpy_molar)

        outlet.update(
            P=P_out,
            T=temperature_high,
            composition=composition,
        )
        enthalpy_high = float(outlet.enthalpy_molar)

        if not (
            min(enthalpy_low, enthalpy_high)
            <= target_enthalpy_molar
            <= max(enthalpy_low, enthalpy_high)
        ):
            raise ValueError(
                f"{self.name}: target outlet enthalpy is outside the "
                "temperature search interval [50, 2000] K."
            )

        increasing = enthalpy_high >= enthalpy_low

        for _ in range(max_iterations):
            temperature_mid = 0.5 * (
                temperature_low + temperature_high
            )

            outlet.update(
                P=P_out,
                T=temperature_mid,
                composition=composition,
            )

            enthalpy_mid = float(outlet.enthalpy_molar)

            if abs(enthalpy_mid - target_enthalpy_molar) <= tolerance:
                return temperature_mid

            if increasing:
                if enthalpy_mid < target_enthalpy_molar:
                    temperature_low = temperature_mid
                else:
                    temperature_high = temperature_mid
            else:
                if enthalpy_mid > target_enthalpy_molar:
                    temperature_low = temperature_mid
                else:
                    temperature_high = temperature_mid

        return 0.5 * (temperature_low + temperature_high)

    def solve(self) -> None:
        """
        Solve the mixer and update the outlet stream.
        """
        self.reset_diagnostics()

        inlet_streams = self._get_inlet_streams()

        outlet = self.outlet.stream

        if outlet is None:
            raise RuntimeError(
                f"{self.name}.outlet is not connected to a stream."
            )

        total_molar_flow = sum(
            float(stream.molar_flow)
            for stream in inlet_streams
        )

        if total_molar_flow <= 0.0:
            raise ValueError(
                f"{self.name}: total inlet molar flow must be positive."
            )

        outlet_composition = self._calculate_mixed_composition(
            inlet_streams,
            total_molar_flow,
        )

        total_enthalpy_flow = sum(
            float(stream.total_enthalpy_molar)
            for stream in inlet_streams
        )

        target_enthalpy_molar = (
            total_enthalpy_flow / total_molar_flow
        )

        outlet_pressure = self._get_outlet_pressure(
            inlet_streams
        )

        outlet_temperature = self._solve_outlet_temperature(
            outlet=outlet,
            target_enthalpy_molar=target_enthalpy_molar,
            P_out=outlet_pressure,
            composition=outlet_composition,
        )

        outlet.update(
            P=outlet_pressure,
            T=outlet_temperature,
            molar_flow=total_molar_flow,
            composition=outlet_composition,
        )

        self.results["molar_flow"] = total_molar_flow
        self.results["mass_flow"] = float(outlet.mass_flow)
        self.results["P_out"] = outlet_pressure
        self.results["T_out"] = outlet_temperature
        self.results["enthalpy_flow"] = total_enthalpy_flow

        self.status = "solved"
