
"""
hfm_equipment.py
================
Reusable HFMMembrane UnitOperation.

Wraps SimulatorRunHFM (your real axial membrane solver) and exposes it
as a UnitOperation with three ports:
    feed       (INPUT)  : receives the feed Stream from the flowsheet.
    retentate  (OUTPUT) : produces the retentate Stream (bore-side exit).
    permeate   (OUTPUT) : produces the permeate Stream (shell-side exit).

This class is scenario-agnostic. The caller configures SimulatorRunHFM
(geometry, permeance, flags, etc.) and passes it in. HFMMembrane only
handles the interface between the internal solver and the flowsheet.
"""

from Common.Process_Simulator import UnitOperation, PortDirection


class HFMMembrane(UnitOperation):
    """
    Hollow-Fiber Membrane unit.

    Wraps an existing SimulatorRunHFM solver and exposes it as a UnitOperation
    that the Flowsheet can connect to other equipment (or to system boundaries).

    Parameters
    ----------
    name : str
        Unit name inside the flowsheet (e.g. "HFM1").
    simulator : SimulatorRunHFM
        Your real membrane solver, fully configured (geometry, permeance,
        energy flags, tolerances, etc.).
    tag : str, optional
        Equipment tag for reporting (e.g. "ME-101").
    description : str, optional
        Human-readable description.
    """

    def __init__(
        self,
        name: str,
        simulator,
        tag: str = "",
        description: str = "",
    ):
        # Initialize base equipment (ports, status, results, diagnostics)
        super().__init__(name, tag=tag, description=description)

        # Store the internal solver. Leading underscore = internal API.
        self._sim = simulator

        # Register the three ports exposed to the flowsheet.
        self.add_port("feed", PortDirection.INPUT)
        self.add_port("retentate", PortDirection.OUTPUT)
        self.add_port("permeate", PortDirection.OUTPUT)

    def solve(self) -> None:
        """
        Execute the internal HFM solver and write outlet conditions
        to the connected retentate and permeate streams.

        Steps:
            1. Read the feed stream from the flowsheet.
            2. Pass it to the internal simulator (set_feed).
            3. Run the internal solver (run).
            4. Check feasibility.
            5. Extract exit conditions from the axial profiles.
            6. Write them to the outlet streams via Stream.update().
            7. Store diagnostics in self.results.
        """
        # --- 1. Read feed from the flowsheet ---
        feed_stream = self.feed.stream
        if feed_stream is None:
            raise RuntimeError(f"{self.name}.feed is not connected to any stream")

        # --- 2. Feed the internal solver ---
        self._sim.set_feed(feed_stream)

        # --- 3. Run the internal solver (black box) ---
        # This is YOUR code: mesh generation, mass balance, energy balance,
        # fugacity, pressure drop, convergence ladder, etc.
        results = self._sim.run()

        self._last_result = results

        # --- 4. Check feasibility ---
        # Defensive: older SimulatorResultsHFM may not have .feasible.
        # If the attribute is missing, we assume the run succeeded.
        is_feasible = getattr(results, "feasible", True)
        if not is_feasible:
            reason = getattr(results, "infeasible_reason", "unknown reason")
            self.warnings.append(f"HFM solver infeasible: {reason}")
            # Do NOT write to outlet streams; they keep their initial state.
            return

        # --- 5. Extract outlet conditions from axial profiles ---
        #
        # The internal solver returns profiles along the membrane axis (z).
        # We pick the correct node for each outlet:
        #
        #   Retentate: exits at z = L (last node, index -1)
        #   Permeate:  exits at z = 0 (first node, index 0)
        #              Counter-current assumption. If your geometry collects
        #              permeate at z = L, change the index to -1.
        #
        n_cells = results.NCells
        components = results.components

        # Retentate exit (bore side, z = L)
        ret_flow = float(results.FRet[-1])          # total molar flow [mol/s]
        ret_comp_arr = results.ZRet[-1]             # mole fraction array
        ret_P = float(results.PRetCell[-1])         # pressure [Pa]
        # ret_T = float(results.T_ret[-1]) \
        #     if results.T_ret is not None else feed_stream.T
        ret_T = float(results.T_ret[-1]) \
            if (results.T_ret is not None and len(results.T_ret) > 0) else feed_stream.T


        ret_composition = {
            comp: float(frac)
            for comp, frac in zip(components, ret_comp_arr)
        }

        # Permeate exit (shell side, z = 0)
        perm_flow = float(results.FPerm[0])         # total molar flow [mol/s]
        perm_comp_arr = results.ZPerm[0]            # mole fraction array
        perm_P = float(results.PPermCell[0])        # pressure [Pa]
        # perm_T = float(results.T_per[0]) \
        #     if results.T_per is not None else feed_stream.T
        perm_T = float(results.T_per[0]) \
            if (results.T_per is not None and len(results.T_per) > 0) else feed_stream.T


        perm_composition = {
            comp: float(frac)
            for comp, frac in zip(components, perm_comp_arr)
        }

        # --- 6. Write to flowsheet outlet streams ---
        # These streams were pre-created and connected in the flowsheet.
        # We mutate them in-place using Stream.update(), which refreshes
        # all CoolProp-derived properties automatically.
        if self.retentate.stream:
            self.retentate.stream.update(
                P=ret_P,
                T=ret_T,
                molar_flow=ret_flow,
                composition=ret_composition,
            )

        if self.permeate.stream:
            self.permeate.stream.update(
                P=perm_P,
                T=perm_T,
                molar_flow=perm_flow,
                composition=perm_composition,
            )

        # --- 7. Store diagnostics for reporting ---
        self.results["n_cells"] = n_cells
        self.results["solver_paths"] = results.solver_paths
        self.results["retentate_molar_flow"] = ret_flow
        self.results["permeate_molar_flow"] = perm_flow
        self.results["stage_cut"] = (
            perm_flow / (perm_flow + ret_flow)
            if (perm_flow + ret_flow) > 0 else 0.0
        )

        print(f"  [{self.name}] Converged via: {results.solver_paths}")
        print(f"  [{self.name}] Retentate: {ret_flow:.6f} mol/s, T={ret_T:.2f} K, P={ret_P/1e5:.3f} bar")
        print(f"  [{self.name}] Permeate:  {perm_flow:.6f} mol/s, T={perm_T:.2f} K, P={perm_P/1e5:.3f} bar")
        print(f"  [{self.name}] Stage cut: {self.results['stage_cut']:.4f}")
