"""
Compressor.py
===============
Simple isentropic compressor as a UnitOperation.

Compatible with the Process_Simulator flowsheet engine and Stream objects.

Physics:
    - Isentropic temperature: T_isen = T_in * (P_out / P_in)^((gamma-1)/gamma)
    - Real temperature:     T_out  = T_in + (T_isen - T_in) / efficiency
    - Power:              W = n_dot * cp * (T_out - T_in)   [W]

Usage in a flowsheet:
    from Compressor import Compressor

    comp = Compressor(
        name="COMP1",
        P_out=5e5,          # Pa — discharge pressure
        efficiency=0.75,    # isentropic efficiency
        gamma=1.3,          # heat capacity ratio (optional)
        tag="K-101",
        description="Permeate recompression",
    )
    fs.add_unit("COMP1", comp)
    fs.add_stream("S_in",  Stream(...))
    fs.add_stream("S_out", Stream(...))
    fs.connect(stream="S_in",  destination=("COMP1", "inlet"))
    fs.connect(source=("COMP1", "outlet"), stream="S_out")
"""

from Common.Process_Simulator import UnitOperation, PortDirection


class Compressor(UnitOperation):
    """
    Simple isentropic compressor.

    Parameters
    ----------
    name : str
        Unit name in the flowsheet.
    P_out : float
        Discharge pressure [Pa].
    efficiency : float, optional
        Isentropic efficiency (0–1). Default 0.8.
    gamma : float, optional
        Heat capacity ratio cp/cv. Default 1.3.
        For CO2/Propane mixtures ~1.2–1.3 is reasonable.
    tag : str, optional
        Equipment tag (e.g. "K-101").
    description : str, optional
        Human-readable description.
    """

    def __init__(
        self,
        name: str,
        P_out: float,
        efficiency: float = 0.8,
        gamma: float = 1.3,
        tag: str = "",
        description: str = "",
    ):
        super().__init__(name, tag=tag, description=description)

        self.P_out = float(P_out)
        self.efficiency = float(efficiency)
        self.gamma = float(gamma)

        self.add_port("inlet", PortDirection.INPUT)
        self.add_port("outlet", PortDirection.OUTPUT)

        # Diagnostics
        self.results["work_W"] = 0.0
        self.results["T_isentropic_K"] = 0.0
        self.results["pressure_ratio"] = 0.0

    def _get_cp_molar(self, stream) -> float:
        """Try to get molar heat capacity [J/(mol K)] from the stream."""
        if hasattr(stream, "cp_molar") and stream.cp_molar is not None:
            return float(stream.cp_molar)
        if hasattr(stream, "cp_mass") and hasattr(stream, "molar_mass"):
            if stream.cp_mass is not None and stream.molar_mass is not None:
                return float(stream.cp_mass * stream.molar_mass)
        # Fallback: typical value for light hydrocarbon / CO2 mixtures
        return 35.0  # J/(mol K)

    def solve(self) -> None:
        """
        Run the compressor calculation and update the outlet stream.
        """
        # --- Read inlet ---
        inlet = self.inlet.stream
        if inlet is None:
            raise RuntimeError(f"{self.name}.inlet is not connected to any stream")

        outlet = self.outlet.stream
        if outlet is None:
            raise RuntimeError(f"{self.name}.outlet is not connected to any stream")

        P_in = float(inlet.P)
        T_in = float(inlet.T)
        P_out = self.P_out

        if P_out <= P_in:
            raise ValueError(
                f"Compressor {self.name}: P_out ({P_out/1e5:.3f} bar) must be "
                f"greater than P_in ({P_in/1e5:.3f} bar)"
            )

        # --- Isentropic temperature ---
        ratio = P_out / P_in
        exponent = (self.gamma - 1.0) / self.gamma
        T_isen = T_in * (ratio ** exponent)

        # --- Real temperature (accounting for efficiency) ---
        delta_T_isen = T_isen - T_in
        delta_T_real = delta_T_isen / self.efficiency
        T_out = T_in + delta_T_real

        # --- Power ---
        cp = self._get_cp_molar(inlet)
        n_dot = float(inlet.molar_flow)
        work = n_dot * cp * delta_T_real  # W

        # --- Update outlet stream ---
        outlet.update(
            P=P_out,
            T=T_out,
            molar_flow=n_dot,
            composition=dict(inlet.composition),
        )

        # --- Store diagnostics ---
        self.results["work_W"] = work
        self.results["T_isentropic_K"] = T_isen
        self.results["pressure_ratio"] = ratio
        self.results["cp_molar_J_mol_K"] = cp

        print(f"  [{self.name}] Compressed {P_in/1e5:.3f} → {P_out/1e5:.3f} bar")
        print(f"  [{self.name}] T: {T_in:.2f} → {T_out:.2f} K  (isen: {T_isen:.2f} K)")
        print(f"  [{self.name}] Power: {work:.3f} W  ({work/1e3:.3f} kW)")
