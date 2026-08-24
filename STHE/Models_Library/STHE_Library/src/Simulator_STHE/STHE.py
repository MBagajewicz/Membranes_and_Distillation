"""
Shell-and-Tube Heat Exchanger simulator.
"""

from .Geometry_STHE import Geometry
from .Stream_STHE import Streams
from .Options_STHE import Options

from Common.HEX_Calculations.Calculations_HEX_heatload import HEX_heat_load
from Common.HEX_Calculations.Calculations_HEX_LMTD import HEX_lmtd
from .Calculations_STHE.Calculations_STHE_correction_factor import STHE_correction_factor
from .Calculations_STHE.Calculations_STHE_DeltaPtubeside import STHE_tubeside_DeltaP
from .Calculations_STHE.Calculations_STHE_DeltaPshellside import STHE_shellside_DeltaP
from .Calculations_STHE.Calculations_STHE_U import STHE_overall_coefficient
from .Calculations_STHE.Calculations_STHE_required_area import STHE_required_area
from .Calculations_STHE.Calculations_STHE_area import STHE_area
from .Calculations_STHE.Calculations_STHE_NTU import STHE_NTU
from .Calculations_STHE.Calculations_STHE_NoNTU import STHE_NoNTU
from .Calculations_STHE.Calculations_STHE_NoNTU_iteration import STHE_NoNTU_iteration


import numpy as np

class STHE:
    """
    Shell-and-Tube Heat Exchanger.

    Main entry point of the library.
    """

    @staticmethod
    def _legacy(value):
        """Convert scalar values to the array format expected by Calculations."""
        return np.atleast_1d(value)


    def __init__(self):

        # ==========================================================
        # Geometry
        # ==========================================================
        self.geometry = Geometry()

        # ==========================================================
        # Process streams
        # ==========================================================
        self.streams = Streams()

        # ==========================================================
        # Calculation options
        # ==========================================================
        self.options = Options()


    def rating(self):
        """
        Perform the heat exchanger rating.
        """
        # ==========================================================
        # Adapt scalar geometry to legacy Calculations API
        # ==========================================================
        lay = np.asarray([self.geometry.tubes.layout])
        Npt = np.asarray([self.geometry.tubes.passes])



        # ==========================================================
        # Calculation parameters
        # ==========================================================
        m_p = {
            "Tube_Method": self.options.correlations.tube_method,
            "Shell_Method": self.options.correlations.shell_method,

            # Bell Method
            "Nss": self.geometry.baffles.sealing_strips,
        }

        # ==========================================================
        # Tube wall thickness
        # ==========================================================
        thk = (
            self.geometry.tubes.outside_diameter
            - self.geometry.tubes.inside_diameter
        ) / 2

        # ==========================================================
        # Heat Load
        # ==========================================================
        self.Q_hot = HEX_heat_load(
            mass_flow_rate=self.streams.hot.inlet.flow,
            specific_heat=self.streams.hot.inlet.cp,
            inlet_temperature=self.streams.hot.inlet.temperature,
            outlet_temperature=self.streams.hot.outlet.temperature,
        )

        self.Q_cold = HEX_heat_load(
            mass_flow_rate=self.streams.cold.inlet.flow,
            specific_heat=self.streams.cold.inlet.cp,
            inlet_temperature=self.streams.cold.outlet.temperature,
            outlet_temperature=self.streams.cold.inlet.temperature,
        )


        energy_error = abs(self.Q_hot - self.Q_cold) / max(
            abs(self.Q_hot),
            abs(self.Q_cold),
        )

        if energy_error > 1e-3:
            print(
                f"Warning: Energy balance not satisfied "
                f"({100*energy_error:.2f} % difference)"
            )



        # ==========================================================
        # Log Mean Temperature Difference (LMTD)
        # ==========================================================
        self.LMTD = HEX_lmtd(
            Thi=self.streams.hot.inlet.temperature,
            Tho=self.streams.hot.outlet.temperature,
            Tci=self.streams.cold.inlet.temperature,
            Tco=self.streams.cold.outlet.temperature,
        )


        # ==========================================================
        # LMTD correction factor
        # ==========================================================
        self.F = STHE_correction_factor(
            Thi=self.streams.hot.inlet.temperature,
            Tho=self.streams.hot.outlet.temperature,
            Tci=self.streams.cold.inlet.temperature,
            Tco=self.streams.cold.outlet.temperature,
            Npt=self.geometry.tubes.passes,
            Xp=self.options.correlations.Xp,
        )

        # ==========================================================
        # Tube-side pressure drop
        # ==========================================================
        # Tube-side stream
        if self.geometry.tubes.stream == "hot_stream":
            stream = self.streams.hot
        elif self.geometry.tubes.stream == "cold_stream":
            stream = self.streams.cold
        else:
            raise ValueError(
                "geometry.tubes.stream must be 'hot_stream' or 'cold_stream'."
            )

        # Tube wall thickness
        thk = (
            self.geometry.tubes.outside_diameter
            - self.geometry.tubes.inside_diameter
        ) / 2

        # Tube-side pressure drop
        self.DeltaP_tube = STHE_tubeside_DeltaP(
            mt=self._legacy(stream.inlet.flow),
            rot=self._legacy(stream.inlet.density),
            mit=self._legacy(stream.inlet.viscosity),
            thk=self._legacy(thk),
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            m_p=m_p,
        )

        # ==========================================================
        # Shell-side pressure drop
        # ==========================================================
        # Shell-side stream
        if self.geometry.tubes.stream == "hot_stream":
            stream = self.streams.cold
        else:
            stream = self.streams.hot

        self.DeltaP_shell = STHE_shellside_DeltaP(
            ms=self._legacy(stream.inlet.flow),
            ros=self._legacy(stream.inlet.density),
            mis=self._legacy(stream.inlet.viscosity),
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            Nb=self._legacy(self.geometry.baffles.number),
            Bc=self._legacy(self.geometry.baffles.cut),
            m_p=m_p,
        )

        # ==========================================================
        # Overall heat-transfer coefficient
        # ==========================================================

        # Tube-side stream
        if self.geometry.tubes.stream == "hot_stream":
            tube = self.streams.hot
            shell = self.streams.cold
        else:
            tube = self.streams.cold
            shell = self.streams.hot

        self.U = STHE_overall_coefficient(
            mt=self._legacy(tube.inlet.flow),
            rot=self._legacy(tube.inlet.density),
            Cpt=self._legacy(tube.inlet.cp),
            mit=self._legacy(tube.inlet.viscosity),
            kt=self._legacy(tube.inlet.conductivity),
            Rft=self._legacy(self.geometry.tubes.fouling_factor),

            ms=self._legacy(shell.inlet.flow),
            ros=self._legacy(shell.inlet.density),
            Cps=self._legacy(shell.inlet.cp),
            mis=self._legacy(shell.inlet.viscosity),
            ks=self._legacy(shell.inlet.conductivity),
            Rfs=self._legacy(self.geometry.shell.fouling_factor),

            thk=self._legacy(thk),
            ktube=self._legacy(self.geometry.tubes.wall_conductivity),

            yfluid=tube.inlet.fluid,

            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            Nb=self._legacy(self.geometry.baffles.number),
            Bc=self._legacy(self.geometry.baffles.cut),

            m_p=m_p,
        )

        # ==========================================================
        # Required heat-transfer area
        # ==========================================================

        self.RequiredArea = STHE_required_area(
            heat_load=self.Q_hot,
            overall_coefficient=self.U,
            lmtd=self.LMTD,
            correction_factor=self.F,
        )

        # ==========================================================
        # Installed heat-transfer area
        # ==========================================================

        self.Area = STHE_area(
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            m_p=m_p,
        ).item()

        # ==========================================================
        # Oversurface
        # ==========================================================

        self.Oversurface = (
            (
                (self.Area - self.RequiredArea)
                / self.RequiredArea
                * 100.0
            ).item()
        )


    def simulate(self):
        """
        Simulates the thermal performance of the heat exchanger.

        Known:
            - Geometry
            - Inlet stream conditions

        Calculated:
            - Outlet temperatures
            - Heat duty
            - Pressure drops
        """
        # ==========================================================
        # Calculation parameters
        # ==========================================================
        m_p = {
            "Tube_Method": self.options.correlations.tube_method,
            "Shell_Method": self.options.correlations.shell_method,

            # Bell Method
            "Nss": self.geometry.baffles.sealing_strips,
        }

        # ==========================================================
        # Tube wall thickness
        # ==========================================================
        thk = (
            self.geometry.tubes.outside_diameter
            - self.geometry.tubes.inside_diameter
        ) / 2

        # ==========================================================
        # Tube-side pressure drop
        # ==========================================================
        # Tube-side stream
        if self.geometry.tubes.stream == "hot_stream":
            stream = self.streams.hot
        elif self.geometry.tubes.stream == "cold_stream":
            stream = self.streams.cold
        else:
            raise ValueError(
                "geometry.tubes.stream must be 'hot_stream' or 'cold_stream'."
            )

        # Tube wall thickness
        thk = (
            self.geometry.tubes.outside_diameter
            - self.geometry.tubes.inside_diameter
        ) / 2

        # Tube-side pressure drop
        self.DeltaP_tube = STHE_tubeside_DeltaP(
            mt=self._legacy(stream.inlet.flow),
            rot=self._legacy(stream.inlet.density),
            mit=self._legacy(stream.inlet.viscosity),
            thk=self._legacy(thk),
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            m_p=m_p,
        )

        # ==========================================================
        # Shell-side pressure drop
        # ==========================================================
        # Shell-side stream
        if self.geometry.tubes.stream == "hot_stream":
            stream = self.streams.cold
        else:
            stream = self.streams.hot

        self.DeltaP_shell = STHE_shellside_DeltaP(
            ms=self._legacy(stream.inlet.flow),
            ros=self._legacy(stream.inlet.density),
            mis=self._legacy(stream.inlet.viscosity),
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            Nb=self._legacy(self.geometry.baffles.number),
            Bc=self._legacy(self.geometry.baffles.cut),
            m_p=m_p,
        )

        # ==========================================================
        # Overall heat-transfer coefficient
        # ==========================================================

        # Tube-side stream
        if self.geometry.tubes.stream == "hot_stream":
            tube = self.streams.hot
            shell = self.streams.cold
        else:
            tube = self.streams.cold
            shell = self.streams.hot

        self.U = STHE_overall_coefficient(
            mt=self._legacy(tube.inlet.flow),
            rot=self._legacy(tube.inlet.density),
            Cpt=self._legacy(tube.inlet.cp),
            mit=self._legacy(tube.inlet.viscosity),
            kt=self._legacy(tube.inlet.conductivity),
            Rft=self._legacy(self.geometry.tubes.fouling_factor),

            ms=self._legacy(shell.inlet.flow),
            ros=self._legacy(shell.inlet.density),
            Cps=self._legacy(shell.inlet.cp),
            mis=self._legacy(shell.inlet.viscosity),
            ks=self._legacy(shell.inlet.conductivity),
            Rfs=self._legacy(self.geometry.shell.fouling_factor),

            thk=self._legacy(thk),
            ktube=self._legacy(self.geometry.tubes.wall_conductivity),

            yfluid=tube.inlet.fluid,

            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            Nb=self._legacy(self.geometry.baffles.number),
            Bc=self._legacy(self.geometry.baffles.cut),

            m_p=m_p,
        )

        # ==========================================================
        # Installed heat-transfer area
        # ==========================================================

        self.Area = STHE_area(
            Ds=self._legacy(self.geometry.shell.diameter),
            dte=self._legacy(self.geometry.tubes.outside_diameter),
            Npt=self._legacy(self.geometry.tubes.passes),
            rp=self._legacy(self.geometry.tubes.pitch_ratio),
            lay=self._legacy(self.geometry.tubes.layout),
            L=self._legacy(self.geometry.tubes.length),
            m_p=m_p,
        ).item()


        # ==========================================================
        # Thermal calculation
        # ==========================================================
        # The Stream/flowsheet interface is independent of the
        # thermal calculation method.
        #
        # "NoNTU" -> NoNTU Eq. (32), currently with F_T = 1.
        # "NTU"   -> Effectiveness-NTU method.
        # ==========================================================
        thermal_method = self.options.thermal.method

        if thermal_method == "NoNTU":

            F_method = self.options.thermal.F_method

            if F_method == "fixed":

                results = STHE_NoNTU(
                    U=self.U.item(),
                    InstalledArea=self.Area,
                    m_hot=self.streams.hot.inlet.flow,
                    cp_hot=self.streams.hot.inlet.cp,
                    Tin_hot=self.streams.hot.inlet.temperature,
                    m_cold=self.streams.cold.inlet.flow,
                    cp_cold=self.streams.cold.inlet.cp,
                    Tin_cold=self.streams.cold.inlet.temperature,
                    F_T=self.options.thermal.F_T,
                )

                results.update(
                    {
                        "F_method": "fixed",
                        "F_converged": True,
                        "F_iterations": 0,
                        "F_error": 0.0,
                        "F_history": [self.options.thermal.F_T],
                    }
                )

            elif F_method == "STHE_correction_factor":

                results = STHE_NoNTU_iteration(
                    U=self.U.item(),
                    InstalledArea=self.Area,
                    m_hot=self.streams.hot.inlet.flow,
                    cp_hot=self.streams.hot.inlet.cp,
                    Tin_hot=self.streams.hot.inlet.temperature,
                    m_cold=self.streams.cold.inlet.flow,
                    cp_cold=self.streams.cold.inlet.cp,
                    Tin_cold=self.streams.cold.inlet.temperature,
                    Npt=self.geometry.tubes.passes,
                    Xp=self.options.correlations.Xp,
                    tolerance=self.options.thermal.F_tolerance,
                    maximum_iterations=(
                        self.options.thermal.F_maximum_iterations
                    ),
                    relaxation=self.options.thermal.F_relaxation,
                    F_initial=self.options.thermal.F_T,
                )

            else:
                raise ValueError(
                    f"Unknown NoNTU F_method: {F_method!r}. "
                    "Available methods: 'fixed' and "
                    "'STHE_correction_factor'."
                )

        elif thermal_method == "NTU":

            results = STHE_NTU(
                U=self.U.item(),
                InstalledArea=self.Area,
                m_hot=self.streams.hot.inlet.flow,
                cp_hot=self.streams.hot.inlet.cp,
                Tin_hot=self.streams.hot.inlet.temperature,
                m_cold=self.streams.cold.inlet.flow,
                cp_cold=self.streams.cold.inlet.cp,
                Tin_cold=self.streams.cold.inlet.temperature,
                shell_passes=1,
            )

        else:
            raise ValueError(
                f"Unknown STHE thermal calculation method: {thermal_method!r}. "
                "Available methods: 'NTU' and 'NoNTU'."
            )

        self.Q = results["HeatDuty"]

        self.NTU = results["NTU"]

        self.Effectiveness = results["Effectiveness"]

        # Store the thermal correction factor used by the simulation.
        self.F = results["F_T"]

        self.streams.hot.outlet.temperature = results["ToutHot"]

        self.streams.cold.outlet.temperature = results["ToutCold"]

        return results
