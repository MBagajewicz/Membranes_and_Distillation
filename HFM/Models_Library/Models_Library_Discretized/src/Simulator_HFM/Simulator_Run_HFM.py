#region Title: SimulatorRunHFM
# Nature: Run HFM
# Methodology: Oruquestation of simulator
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2026    Diego Gabriel Oliva            Commented
#  0.0       10-May-2026    Diego Gabriel Oliva            Adding fugacity
#  0.0       10-Jun-2026    Qwen                           Applied Type Hinting, DRY, Constants, Docstrings, and organized historical comments
##################################################################################################################
#endregion

import numpy as np
from typing import Optional, Any, Tuple
import copy

# EN: Import mass model components
# PT-BR: Importa componentes do modelo de massa
from .Mass_Balance_HFM.Mass_Balance_Without_Pressure_Drop_HFM import MassBalanceWithoutPressureDropHFM
from .Mass_Balance_HFM.Mass_Balance_With_Fugacity_HFM import MassBalanceWithFugacityHFM
from .Mass_Balance_HFM.Mass_Balance_Solver_HFM import MassBalanceSolverHFM
from .Simulator_Geometry_HFM import (SimulatorGeometryHFM, build_courant_adaptive_mesh,
                                     fixed_ratio_mesh)
from Common.Physical_Properties.Viscosity.Mixture_Properties import MixtureProperties
from .Mesh_Properties_HFM import MixPropertiesCoolPropHEOS 

# EN: Import energy model components
# PT-BR: Importa componentes do modelo de energia
from .Energy_Balance_HFM.Energy_Balance_HFM import EnergyBalanceHFM
from .Energy_Balance_HFM.Energy_Balance_Solver_HFM import EnergyBalanceSolverHFM
from .Energy_Balance_HFM.U_Calculation import UCalculation

# EN: Import results container
# PT-BR: Importa objeto de resultados
from .Simulator_Results_HFM import SimulatorResultsHFM
from . import Simulation_Deadline as _deadline
from .Simulation_Deadline import SimulationTimeout

# EN: Import Stream class (used for feed definition)
# PT-BR: Importa classe Stream (usada para definir a alimentação)
from Common.Stream.stream import Stream
from Common.Membrane_Properties.Permeance.Membrane_Permeance import Membrane_Permeance


class SimulationNotConverged(RuntimeError):
    """Raised when an iterative loop in the simulator fails to converge
    within the allotted number of iterations. Lets the enumeration catch
    non-converged candidates explicitly instead of using garbage results.
    """
    pass


class PressureDropInfeasible(SimulationNotConverged):
    """Raised when the frictional pressure drop exceeds the available driving
    pressure (retentate pressure falling to/below the local permeate pressure
    or below zero). Such a candidate has no positive-pressure solution.
    Subclass of SimulationNotConverged so existing enumeration code keeps
    working; run() converts it into results.feasible = False instead of
    propagating.
    """
    pass


class SimulatorRunHFM:
    """
    Simulator for Hollow Fiber Membrane (HFM) modules.
    Handles mass and energy balances, with optional pressure drop and fugacity calculations.
    """

    # ==========================================
    # CLASS INITIAL CONSTANTS 
    # ==========================================
    GAS_CONSTANT_R: float = 8.314
    # Inexact inner solve for Branch 2 (pressure drop only). There is no
    # independent tolerance for the inner mass-balance fixed point: everything
    # below is expressed as a MULTIPLE of `iteration_tolerance` (times the total
    # feed flow, since the inner error is absolute on flows [mol/s]).
    #   FLOOR_FACTOR : tightest inner tolerance, as a multiple of
    #                  iteration_tolerance. < 1 so the inner solve stays inside
    #                  the outer criterion instead of exactly on it.
    #   RELAX_FACTOR : how much LOOSER than iteration_tolerance the inner solve
    #                  may be while the outer error is still large.
    #   FRACTION     : inner tolerance as a fraction of the current outer error.
    # Set INNER_TOL_RELAX_FACTOR = INNER_TOL_FLOOR_FACTOR to disable the
    # relaxation and always solve the inner fixed point to the tight tolerance.
    # Declare a candidate pressure-infeasible as soon as the outer loop runs out
    # of iterations with the pressure clamp active, WITHOUT trying the remaining
    # solvers.
    #
    # DISABLED because it is unsound, and demonstrably so. Non-convergence of one
    # solver is not a property of the candidate. Measured counter-example
    # (Scenario_S1, L=0.6, D=0.17, d_fo/t = 1.3e-4/5e-5, i.e. a 30 um bore,
    # eps=0.42, PI): the LU rung exhausts its iterations with the clamp active and
    # the shortcut rejected it as pressure-infeasible after a single rung -- yet
    # the MARCHING solver converges the same candidate in 10.7 s. The verdict was
    # a property of the solver, not of the design.
    #
    # With it off, such candidates run the full ladder and, if nothing resolves
    # them, are reported as UNRESOLVED (time budget) and logged -- honest, and
    # revisitable. The cost is real: ~0.3 s becomes ~10 s for that family.
    # Set True to trade correctness for speed, knowingly.
    #
    # The proper fix is the a-priori certified cut that `_update_pressures` refers
    # to as `_certify_pressure_infeasible` and which was never written: a
    # closed-form lower bound on the frictional drop that PROVES infeasibility
    # without simulating. That would be both sound and cheaper than this shortcut.
    PRESSURE_INFEASIBLE_SHORTCUT: bool = False

    INNER_TOL_FRACTION: float = 0.1
    INNER_TOL_FLOOR_FACTOR: float = 1e-2
    INNER_TOL_RELAX_FACTOR: float = 1e3
    # Fraction of `iteration_tolerance` used as the marching solver's
    # composition tolerance. Kept safely inside the outer criterion rather than
    # exactly on it, so the marching solve never becomes the factor that limits
    # the outer loop.
    MARCH_TOL_FRACTION: float = 1e-2
    # Anderson history depth for the OUTER pressure<->flow loop of Branch 2.
    # 0 disables the acceleration (plain damped Picard, the previous behaviour).
    # Measured: depth 3 gives up to ~1.8x fewer outer iterations on the
    # outer-loop-dominated candidates and is neutral on the rest; deeper
    # histories (5, 8) start to HURT (down to 0.64x) on candidates whose cost is
    # in the inner solve, because the extra secants describe a map that has
    # already changed. Keep this small.
    OUTER_ANDERSON_DEPTH: int = 3
    # Give up on the outer Anderson acceleration after this many restarts on a
    # single candidate (each restart means the error rose, i.e. the local linear
    # model failed). Prevents a net slowdown on candidates it cannot help.
    OUTER_ANDERSON_MAX_RESTARTS: int = 2
    # Only start extrapolating after this many plain Picard passes. Anderson
    # takes larger pressure steps, which makes the inner solve more expensive per
    # pass; that only pays off on candidates whose outer loop is genuinely slow.
    # Candidates that converge in fewer passes than this are never touched, so
    # they cannot regress.
    OUTER_ANDERSON_WARMUP: int = 8
    # Branch 3 (fugacity + pressure drop) relaxes the pressure with the same
    # alpha as the flows. Set False to restore the previous undamped pressure
    # update, which put narrow-bore candidates into a period-2 limit cycle --
    # see the comment at the update itself. For A/B measurement only.
    BRANCH3_RELAX_PRESSURE: bool = True
    VISCOSITY_METHOD: str = "HZ" # HZ or CoolProp
    DEFAULT_EOS: str = "PR" # PR or HEOS
    DEFAULT_HEAT_TRANSFER_COEF: float = 4.0 # [W/(m2 K)]
    SUPPORT_POROSITY: float = 0.5
    K_POLYMER: float = 0.2 # W/(m K)
    ENERGY_CONVERGENCE_TOL: float = 1e-2

    def __init__(self):
        # ---------------------------------------------------------
        # 1. Simulation Flags 
        # ---------------------------------------------------------
        self.energy: bool = True
        self.pressure_drop: bool = False
        self.use_fugacity_and_Z: bool = True  # fugacity driving force + real-gas Z in the pressure drop
        self.calculate_dew_temperature: bool = False
        # Dew-point condition, enforced as a PHASE-STABILITY test (see
        # MixPropertiesCoolPropHEOS.single_phase_at). The condition
        # T >= T_dew + approach is equivalent to "still single-phase at
        # T - approach", which avoids root-finding on the phase boundary.
        self.dew_approach_K: float = 0.0
        # Evaluate the condition on the permeate side as well. The permeate is
        # enriched in the fast, light species, so its dew point sits far below
        # the operating temperature (measured: 170-181 K against ~300 K), and the
        # test is normally redundant there. Default True preserves the previous
        # behaviour; the scenarios switch it off.
        self.check_dew_permeate: bool = True
        self.force_phase: bool = True  #### Not included in general input

        # ---------------------------------------------------------
        # 2. Physical & Geometric Parameters 
        # ---------------------------------------------------------
        self.heat_transfer_coef: float = self.DEFAULT_HEAT_TRANSFER_COEF
        self.geometry: Optional[Any] = None
        self.properties: Optional[Any] = None
        self.permeance: Optional[Any] = None

        # ---------------------------------------------------------
        # 3. Feed & Operating Conditions 
        # ---------------------------------------------------------
        self.feed: Optional[Stream] = None
        self.PPerm: Optional[float] = None
        self.EndRetentatePressure: Optional[float] = None  #### Not included in general input
        self.eospackage: str = self.DEFAULT_EOS            #### Not included in general input

        # ---------------------------------------------------------
        # 4. Solver Parameters 
        # ---------------------------------------------------------
        # Wall-clock budget for ONE simulation, in seconds. None = unlimited.
        # Exceeding it returns feasible=False with timed_out=True (unresolved,
        # NOT proven infeasible) instead of running indefinitely.
        self.time_budget_s = None
        self.iteration_tolerance: float = 1e-8
        self.max_num_iterations: int = 5000
        self.solver_tolerance: float = 1e-8
        self.verbose_least_squares: int = 0

        # ---------------------------------------------------------
        # Axial mesh spacing (see mesh_study/).
        #   "uniform" -> uniform spacing (default; safe across all regimes).
        #   "fixed"   -> geometric mesh, dz_last/dz_first = mesh_ratio, fine at
        #                the inlet where the CO2 front is steep; candidate-
        #                agnostic, ~3-4x fewer cells than uniform at equal
        #                outlet-composition accuracy for low-stage-cut candidates
        #                (can be worse than uniform at high stage cut -- opt-in).
        # ---------------------------------------------------------
        self.mesh_type: str = "uniform"
        self.mesh_ratio: float = 40.0

        # Fugacity-coefficient (phi) refresh cadence in the outer loop. phi is a
        # weak coupling, so it is recomputed from CoolProp only every K calls; in
        # between, the cached phi is applied to the current composition. 1 =
        # recompute every call (exact previous behaviour). 2 is validated
        # bit-identical and ~2x faster; K >= 3 can destabilize the
        # pressure/fugacity coupling on some candidates.
        self.phi_refresh_every: int = 2

    # Backward-compatible alias: the flag was renamed use_fugacity ->
    # use_fugacity_and_Z (it now also switches the real-gas compressibility Z in
    # the pressure drop). Old code that sets/reads `use_fugacity` keeps working.
    @property
    def use_fugacity(self):
        return self.use_fugacity_and_Z

    @use_fugacity.setter
    def use_fugacity(self, value):
        self.use_fugacity_and_Z = value

    # ---------------------------------------
    # Setters
    # ---------------------------------------
    def set_feed(self, stream: Stream) -> None:
        if not isinstance(stream, Stream):
            raise TypeError("feed must be a Stream")
        # self.feed = stream
        self.feed = stream.clone()
        # Note: Removed redundant 'self.feed.flow = self.feed.flow' (No-Op)

    def set_membrane_permeance(self, permeance_object: Membrane_Permeance) -> None:
        """Assigns the membrane permeance object."""
        if not isinstance(permeance_object, Membrane_Permeance):
            raise TypeError("permeance_object must be a Membrane_Permeance")
        self.permeance = permeance_object.permeance

    def set_warm_start(self, profiles) -> None:
        """Provide converged profiles from a previous (similar) candidate to be
        used as the initial guess, accelerating convergence. `profiles` is the
        dict returned by `results.warm_start` (or assembled manually) with keys
        FRet, FPerm (each (NCells+1, n_comp)), PRet, PPerm (each (NCells+1,)),
        and T ((2*(NCells+1),)). Shape mismatches are ignored at run time and
        the simulator falls back to the cold linear guess."""
        self._warm_start = profiles

    def clear_warm_start(self) -> None:
        """Discard any previously set warm-start profiles."""
        self._warm_start = None

    def _module_courant(self) -> float:
        """Module-level Courant number: the ratio between what the WHOLE membrane
        could transfer of the fastest component and the axial feed flow,

            Co_module = max_i  Q_i * A_total * P_feed / F_feed_total

        This -- not the per-cell Courant -- is the gain of the outer loops that
        freeze the composition (the damped substitution and the frozen-fugacity
        LU path). It is MESH-INDEPENDENT, which is why refining the mesh never
        rescued those iterations on oversized modules. Large values mean the
        composition-freezing loops will not contract and the marching solver
        should be used from the start.
        """
        try:
            Q = np.asarray(self.permeance, dtype=float)
            A_total = float(self.geometry.AREA_PER_L * self.geometry.LHidraulic)
            P = float(self.feed.P)
            F = float(self.feed.molar_flow) / max(self.geometry.NumberOfTubesInParallel, 1)
            if F <= 0:
                return 0.0
            return float(np.max(Q[np.isfinite(Q)]) * A_total * P / F)
        except Exception:
            return 0.0

    def _rebuild_geometry(self, NCells, cell_sizes):
        """Rebuild self.geometry with a new cell count and/or non-uniform
        spacing, preserving every other geometric parameter."""
        g = self.geometry
        return SimulatorGeometryHFM(
            LSingleMembrane=g.LSingleMembrane, DiamShell=g.DiamShell,
            DiamFiber_o=g.DiamFiber_o, DiamFiber_i=g.DiamFiber_i,
            NFibers=g.NFibers, Void_Frac=g.Void_Frac, NCells=NCells,
            NumberOfMembranesInSerie=g.NumberOfMembranesInSerie,
            NumberOfTubesInParallel=g.NumberOfTubesInParallel,
            cell_sizes=cell_sizes)

    @staticmethod
    def _interpolate_warm_start(ws, NCells, n_comp):
        """Map a warm-start payload (from a candidate with possibly different
        mesh/size) onto the current mesh of NCells cells (NCells+1 nodes).

        Profiles are interpolated over the NORMALIZED axial position
        zeta = z/L in [0, 1], so they transfer across different N and different
        module lengths. If the source payload already matches the current node
        count, it is returned as-is (no interpolation). Boundary conditions are
        re-enforced after interpolation. Returns a payload dict with the right
        shapes, or None if it cannot be built.
        """
        try:
            FRet = np.asarray(ws["FRet"], dtype=float)
            FPerm = np.asarray(ws["FPerm"], dtype=float)
            PRet = np.asarray(ws["PRet"], dtype=float)
            PPerm = np.asarray(ws["PPerm"], dtype=float)
            T = np.asarray(ws["T"], dtype=float)
        except Exception:
            return None

        n_src = FRet.shape[0]                 # source nodes = N_src + 1
        if FRet.shape[1] != n_comp:
            return None                        # different component count: cannot reuse

        n_tgt = NCells + 1                     # target nodes

        # Exact match: use directly (fast path, unchanged behaviour).
        if n_src == n_tgt:
            return {"FRet": FRet.copy(), "FPerm": FPerm.copy(),
                    "PRet": PRet.copy(), "PPerm": PPerm.copy(), "T": T.copy()}

        # Source normalized node positions. Use stored zeta if present (adaptive
        # mesh); otherwise assume the source was uniform.
        zeta_src = ws.get("zeta", None)
        if zeta_src is not None and len(zeta_src) == n_src:
            zeta_src = np.asarray(zeta_src, dtype=float)
        else:
            zeta_src = np.linspace(0.0, 1.0, n_src)
        # Target normalized positions: uniform in zeta is fine as an initial
        # guess; the true target mesh only needs a good starting profile.
        zeta_tgt = np.linspace(0.0, 1.0, n_tgt)

        def interp_cols(M):
            out = np.empty((n_tgt, M.shape[1]), dtype=float)
            for j in range(M.shape[1]):
                out[:, j] = np.interp(zeta_tgt, zeta_src, M[:, j])
            return out

        FRet_i = interp_cols(FRet)
        FPerm_i = interp_cols(FPerm)
        PRet_i = np.interp(zeta_tgt, zeta_src, PRet)
        PPerm_i = np.interp(zeta_tgt, zeta_src, PPerm)

        # Temperature payload is [T_ret (n_src) | T_per (n_src)]; interpolate
        # each half separately.
        if T.shape[0] == 2 * n_src:
            T_ret = np.interp(zeta_tgt, zeta_src, T[:n_src])
            T_per = np.interp(zeta_tgt, zeta_src, T[n_src:])
            T_i = np.concatenate([T_ret, T_per])
        else:
            T_i = None  # unusable; caller will fall back to cold T guess

        payload = {"FRet": FRet_i, "FPerm": FPerm_i,
                   "PRet": PRet_i, "PPerm": PPerm_i}
        if T_i is not None:
            payload["T"] = T_i
        else:
            # Provide a shape-correct T so the shape checks downstream pass;
            # a flat guess is a safe fallback.
            payload["T"] = np.zeros(2 * n_tgt)
        return payload

    def set_properties(self, properties: Any) -> None:
        """Assigns thermophysical properties model."""
        self.properties = properties

    # ---------------------------------------
    # Helper Methods
    # ---------------------------------------
    def _get_stream_compositions(self, FRetCell: np.ndarray, FPermCell: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculates total flows and compositions for retentate and permeate.
        Returns: (FRet, FPerm, ZRet, ZPerm)
        """
        FRet = FRetCell.sum(axis=1)
        FPerm = FPermCell.sum(axis=1)

        # Retentate composition. On oversized / high-permeance modules the
        # retentate can be driven to (numerically) zero total flow, where the
        # composition is undefined (0/0 -> NaN) and would poison the downstream
        # property calls. Where that happens we carry the last valid composition
        # forward: it is physically irrelevant (it multiplies a zero flow) but it
        # keeps the property evaluations well-posed.
        ZRet = np.zeros_like(FRetCell)
        last_valid = None
        for k in range(len(FRet)):
            if FRet[k] > 1e-12:
                ZRet[k] = FRetCell[k] / FRet[k]
                last_valid = ZRet[k]
            elif last_valid is not None:
                ZRet[k] = last_valid
            else:
                # No upstream reference yet: fall back to the feed composition.
                # ZRet[k] = self.feed.composition
                ZRet[k] = np.array(self.feed.mole_fractions)

        # Permeate composition, with the same safeguard. The permeate flow decays
        # toward the closed end (and is exactly zero there), and on oversized
        # modules a whole dead zone can have zero permeate flow. An all-zero
        # composition vector is not a valid state for the property package, so we
        # carry the last valid composition forward from the open end.
        ZPerm = np.zeros_like(FPermCell)
        last_valid_p = None
        for k in range(len(FPerm)):
            if FPerm[k] > 1e-12:
                ZPerm[k] = FPermCell[k] / FPerm[k]
                last_valid_p = ZPerm[k]
            elif last_valid_p is not None:
                ZPerm[k] = last_valid_p
            else:
                # ZPerm[k] = self.feed.composition
                ZRet[k] = np.array(self.feed.mole_fractions)
        return FRet, FPerm, ZRet, ZPerm

    @staticmethod
    def _dew_stability(prop_obj, T_nodes, approach):
        """Is every node clear of the dew point by `approach` kelvin?

        Returns (ok, first_bad_node).

        The evaluation is asymmetric, and deliberately so:

          * a FAILURE at any single node is conclusive -- the candidate violates
            the condition and nothing else needs to be evaluated;
          * FEASIBILITY requires every node to pass, so it cannot be inferred
            from a subset.

        So the inlet and the outlet are probed first. Those are the extremes of
        both the composition path (the retentate is progressively stripped of the
        fast species) and the pressure profile, and in practice the outlet is the
        binding node. If either fails, the answer is already exact and the
        remaining nodes are never touched. Only candidates that survive the probe
        pay for the full sweep -- and in Smart Enumeration those are precisely the
        ones that go on to update the incumbent, which is where exactness matters.

        No interpolation, no extrapolation, no assumed monotonicity of T_dew
        along the module: T_dew is a nonlinear functional of the whole
        composition vector, and the majority species is not itself monotone.
        """
        n = int(prop_obj.NStates)
        T_eval = np.asarray(T_nodes, dtype=float) - float(approach)

        probe = sorted({0, n - 1})
        ok, _ = prop_obj.single_phase_at(T_eval, nodes=probe)
        for k in probe:
            if not ok[k]:
                return False, k

        rest = [k for k in range(n) if k not in probe]
        if rest:
            ok, _ = prop_obj.single_phase_at(T_eval, nodes=rest)
            for k in rest:
                if not ok[k]:
                    return False, k
        return True, None

    @staticmethod
    def _classify_outer(errs):
        """Classify how an outer Picard loop behaved, from its error history.

        A loop that fails to converge can fail in ways that call for completely
        different fixes, and the raise message alone cannot tell them apart:

          * "oscillating" -- the error bounces without a trend. This is a limit
            cycle, and no iteration budget will ever fix it: something in the
            update is taking too large a step. Branch 3 sat in a period-2 cycle
            (0.77, 0.18, 0.71, 0.18, ...) for the whole project because it took
            a full Picard step on the pressure while damping the flows, and the
            candidates affected were written off as infeasible.
          * "descending" -- genuinely converging, just too slowly. More
            iterations, or acceleration, would help.
          * "stalled" -- flat. The iteration has reached a fixed point that is
            not accurate enough, usually a tolerance or conditioning problem.

        Returns (label, stats). Cheap: O(len(errs)) on a list of floats.
        """
        import numpy as _np
        e = _np.asarray([v for v in errs if _np.isfinite(v)], dtype=float)
        stats = {"iters": int(e.size),
                 "first": float(e[0]) if e.size else float("nan"),
                 "last": float(e[-1]) if e.size else float("nan"),
                 "min": float(e.min()) if e.size else float("nan")}
        if e.size < 6:
            return "too_short", stats
        tail = e[-min(len(e), 40):]
        d = _np.diff(tail)
        up = float((d > 0).mean())          # fraction of steps that WORSENED
        # Net progress across the tail, in orders of magnitude.
        decades = _np.log10(max(tail[0], 1e-300) / max(tail[-1], 1e-300))
        stats.update(frac_worse=up, tail_decades=float(decades),
                     tail_span=float(tail.max() / max(tail.min(), 1e-300)))
        if up >= 0.25 and abs(decades) < 0.5 and stats["tail_span"] > 3.0:
            return "oscillating", stats
        if abs(decades) < 0.1 and stats["tail_span"] < 3.0:
            return "stalled", stats
        return "descending", stats

    @staticmethod
    def _anderson_extrapolate(hist: dict, u: np.ndarray, G: np.ndarray,
                              m: int = 5, reg: float = 1e-10) -> np.ndarray:
        """Type-II Anderson extrapolation of a fixed-point sequence u -> G(u).

        Returns a better target than the plain Picard image `G`, by combining the
        last `m` iterates so that the LINEARLY EXTRAPOLATED residual vanishes:
        with dF, dG the successive differences of the residual/image history,
        solve min_gamma ||f - dF gamma||^2 and take G - dG gamma. Degenerates to
        `G` whenever there is not enough history, the least-squares system is
        singular, or the result is not finite -- so the caller can always relax
        toward the returned value exactly as it would toward `G`.

        `reg` is applied RELATIVE to trace(dF^T dF): the residuals here are
        pressures (~1e3 Pa), so a fixed absolute regularization would be either
        negligible or overwhelming depending on the candidate.

        NOTE: this is only appropriate for a WELL-SCALED state. Applied to raw
        component flows (which span many orders of magnitude, down to zero in the
        permeate dead zone) the least-squares system is ill-conditioned and the
        scheme stalls -- measured ~20x SLOWER. Use it on pressures or on
        compositions, not on flows.
        """
        f = G - u
        hist["F"].append(f.copy())
        hist["G"].append(G.copy())
        if len(hist["F"]) > m:
            hist["F"].pop(0)
            hist["G"].pop(0)
        k = len(hist["F"])
        if k < 2:
            return G
        dF = np.column_stack([hist["F"][i + 1] - hist["F"][i] for i in range(k - 1)])
        dG = np.column_stack([hist["G"][i + 1] - hist["G"][i] for i in range(k - 1)])
        A = dF.T @ dF
        lam = reg * max(float(np.trace(A)) / max(A.shape[0], 1), 1e-300)
        try:
            gam = np.linalg.solve(A + lam * np.eye(k - 1), dF.T @ f)
        except np.linalg.LinAlgError:
            return G
        un = G - dG @ gam
        if not np.all(np.isfinite(un)):
            return G
        return un

    def _update_pressures(self, PRetCell: np.ndarray, PPermCell: np.ndarray, FRet: np.ndarray, FPerm: np.ndarray,
                          ZRet: np.ndarray, ZPerm: np.ndarray, T_guess: np.ndarray, NCells: int, 
                          props: Any, R: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates the pressure drop across the membrane cells based on hydraulic correlations.
        Returns: (PRetCell, PPermCell)
        """
        geom = self.geometry
        K_shell = (192 * geom.NFibers * geom.DiamFiber_o * (geom.DiamShell + geom.NFibers * geom.DiamFiber_o)) / \
                  (np.pi * (geom.DiamShell**2 - geom.NFibers * geom.DiamFiber_o**2)**3)
        K_bore = 128 / (np.pi * geom.DiamFiber_i**4 * geom.NFibers)

        TRetAux = T_guess[:NCells+1]
        TPermAux = T_guess[NCells+1:]

        # Reset per call: after the outer loop converges, this flag reflects the
        # CONVERGED pressure evaluation, which is the one that decides feasibility.
        self._pressure_violated = False

        # HZ viscosity depends ONLY on composition (not on T or P), so precompute
        # it for every node at once (vectorized) instead of a per-cell function
        # call inside the sequential pressure recursion below -- that per-node
        # Python call was a hotspot. Falls back to the per-node call for other
        # viscosity methods (e.g. CoolProp), which do depend on T/P.
        viscR_all = viscP_all = None
        if getattr(props, "method", None) == "HZ" and props.MU is not None and props.M is not None:
            _sqrtM = np.sqrt(np.asarray(props.M, dtype=float))
            _muw = np.asarray(props.MU, dtype=float) * _sqrtM
            _mu_mean = float(np.mean(props.MU))

            def _visc_nodes(Z):
                Z = np.asarray(Z, dtype=float)
                s = Z.sum(axis=1)
                Y = Z / np.maximum(s[:, None], 1e-300)
                v = (Y * _muw).sum(axis=1) / np.maximum((Y * _sqrtM).sum(axis=1), 1e-12)
                v[s < 1e-12] = _mu_mean   # mirror _viscosity_HZ trace-composition safeguard
                return v

            viscR_all = _visc_nodes(ZRet)
            viscP_all = _visc_nodes(ZPerm)

        # Real-gas compressibility in the volumetric-flow term (V_m = Z*R*T/P).
        # Z comes free from the fugacity CoolProp evaluation of the PREVIOUS
        # Picard iteration (weak coupling, lagged like the frozen fugacity). It is
        # applied only when use_fugacity_and_Z is on; the partial-pressure / ideal
        # branch keeps Z = 1. (At 40 bar Z~0.91, at 100 bar Z~0.81, so the ideal
        # form overestimates the drop by ~9-19%.)
        _useZ = bool(self.use_fugacity_and_Z) and getattr(self, "_Z_ret_last", None) is not None
        _ZR = np.asarray(self._Z_ret_last, dtype=float) if _useZ else None
        _ZP = np.asarray(self._Z_perm_last, dtype=float) if _useZ else None

        if self.EndRetentatePressure is None:
            for k in range(1, NCells+1):
                viscVRet = viscR_all[k] if viscR_all is not None else props.viscosity(ZRet[k], T=TRetAux[k], P=PRetCell[k])
                viscVPerm = viscP_all[k] if viscP_all is not None else props.viscosity(ZPerm[k], T=TPermAux[k], P=PPermCell[k])
                zr = _ZR[k] if _ZR is not None else 1.0
                zp = _ZP[k] if _ZP is not None else 1.0
                dPCellRet = np.asarray(K_shell).item() * viscVRet * zr * R * TRetAux[k] * FRet[k] / PRetCell[k] * geom.dz[k-1]
                dPCellPerm = np.asarray(K_bore).item() * viscVPerm * zp * R * TPermAux[k] * FPerm[k] / PPermCell[k] * geom.dz[k-1]
                PRetCell[k] = PRetCell[k-1] - dPCellRet
                PPermCell[k] = PPermCell[k-1] + dPCellPerm

                # RUNAWAY GUARD. K_bore scales as 1/d_fi**4, so on the narrowest
                # bores of the grid (30 um and below) a single cell can add an
                # astronomical permeate pressure rise. Left unchecked the profile
                # diverges and is handed to CoolProp, which fails with
                # "Unable to find gaseous density for T: 302 K, p: 1.6e+295 Pa" --
                # a RuntimeError that then propagated all the way out of run()
                # and killed the whole scenario in the batch runner.
                #
                # The permeate is withdrawn at PPerm <= PFeed and gains pressure
                # only by friction, so a permeate pressure above the FEED pressure
                # is physically impossible: such a module cannot operate. Clamp
                # it, record the event, and let the CONVERGED-profile test decide
                # feasibility -- exactly as the crossing clamp below does. A
                # transient excursion therefore cannot reject a viable candidate,
                # since the flag is reset at the top of every call.
                _Pcap = self.feed.P
                if (not np.isfinite(PPermCell[k])) or PPermCell[k] > _Pcap:
                    self._pressure_violated = True
                    PPermCell[k] = _Pcap
                if not np.isfinite(PRetCell[k]):
                    self._pressure_violated = True
                    PRetCell[k] = _Pcap

                # Pressure crossing during an OUTER ITERATION is NOT proof of
                # infeasibility. The retentate flow is largest at the inlet and
                # decays as material permeates, and dP scales with flow, so the
                # early iterates (which still carry near-feed flows) produce the
                # LARGEST pressure drop of the whole iteration history. A
                # high-stage-cut candidate can therefore cross here and still
                # converge with a healthy margin -- raising now would trim a
                # viable candidate.
                #
                # So we do NOT raise: we clamp to keep the property evaluations
                # well-posed, record the event, and let the iteration proceed.
                # Infeasibility is decided later, on the CONVERGED profile
                # (see _check_converged_pressure_feasibility), and certified up
                # front by _certify_pressure_infeasible.
                if PRetCell[k] <= PPermCell[k] or PRetCell[k] <= 0.0:
                    self._pressure_violated = True
                    PRetCell[k] = PPermCell[k] * (1.0 + 1e-4)
        else:
            # Preserved exactly as in original source (uses self.PFeed)
            dPCellRet = (self.feed.P - self.EndRetentatePressure) / NCells
            dPCellPerm = 0
            for k in range(1, NCells+1):
                PRetCell[k] = PRetCell[k-1] - dPCellRet
                PPermCell[k] = PPermCell[k-1] + dPCellPerm

        return PRetCell, PPermCell

    def _get_fugacities(self, components: list, PRetCell: np.ndarray, PPermCell: np.ndarray,
                        T_guess: np.ndarray, ZRet: np.ndarray, ZPerm: np.ndarray, NCells: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates fugacity arrays for retentate and permeate streams.
        Returns: (fug_ret_array, fug_perm_array)
        """
        # Reuse the CoolProp property objects across the outer/fugacity
        # iterations of this candidate instead of rebuilding the NStates
        # AbstractState objects every call (the dominant cost). set_conditions()
        # updates P/T/Z in place; the objects are rebuilt only if the node count
        # changes (adaptive mesh) or the component set differs.
        Tret = T_guess[:NCells + 1]
        Tperm = T_guess[NCells + 1:]
        prop_ret = getattr(self, "_prop_ret_cache", None)
        prop_perm = getattr(self, "_prop_perm_cache", None)
        if (prop_ret is None or prop_ret.NStates != NCells + 1
                or list(prop_ret.components) != list(components)):
            prop_ret = MixPropertiesCoolPropHEOS(
                components=components, P=PRetCell, T=Tret, Z=ZRet,
                force_gas_phase=True, eos=self.eospackage)
            prop_perm = MixPropertiesCoolPropHEOS(
                components=components, P=PPermCell, T=Tperm, Z=ZPerm,
                force_gas_phase=True, eos=self.eospackage)
            self._prop_ret_cache = prop_ret
            self._prop_perm_cache = prop_perm
        else:
            prop_ret.set_conditions(P=PRetCell, T=Tret, Z=ZRet)
            prop_perm.set_conditions(P=PPermCell, T=Tperm, Z=ZPerm)

        prop_ret.update_all()
        prop_perm.update_all()

        fug_ret_array = np.array([state["components"]["fugacity"] for state in prop_ret.props])
        fug_perm_array = np.array([state["components"]["fugacity"] for state in prop_perm.props])
        # Real-gas compressibility Z per node -- free from the states already
        # flashed for the fugacity; consumed by the pressure drop when
        # use_fugacity_and_Z is on.
        Z_ret = np.array([st.compressibility_factor() for st in prop_ret.states])
        Z_perm = np.array([st.compressibility_factor() for st in prop_perm.states])
        return fug_ret_array, fug_perm_array, Z_ret, Z_perm

    def _fugacities(self, components, PRetCell, PPermCell, T_guess, ZRet, ZPerm, NCells):
        """Fugacities for the outer loop with a phi-refresh cadence.

        The fugacity coefficient phi is a WEAK (slowly composition-varying)
        quantity; the composition x it multiplies is the STRONG coupling. So phi
        is recomputed from CoolProp only every `phi_refresh_every` calls; in
        between, the cached phi is applied to the CURRENT composition and
        pressure (f = phi * x * P). This keeps the strong coupling live every
        iteration (no convergence penalty) while skipping the expensive CoolProp
        flash most of the time. phi_refresh_every = 1 recomputes every call
        (exact previous behaviour)."""
        K = int(getattr(self, "phi_refresh_every", 1))
        cnt = getattr(self, "_fug_call_count", 0)
        self._fug_call_count = cnt + 1
        ZR = np.asarray(ZRet, dtype=float)
        ZP = np.asarray(ZPerm, dtype=float)
        PR = np.asarray(PRetCell, dtype=float)[:, None]
        PP = np.asarray(PPermCell, dtype=float)[:, None]
        if K <= 1 or (cnt % K == 0) or getattr(self, "_phi_ret", None) is None:
            fug_ret, fug_perm, Z_ret, Z_perm = self._get_fugacities(
                components, PRetCell, PPermCell, T_guess, ZRet, ZPerm, NCells)
            self._phi_ret = fug_ret / np.maximum(ZR * PR, 1e-300)
            self._phi_perm = fug_perm / np.maximum(ZP * PP, 1e-300)
            self._Z_ret_last = Z_ret        # for the (lagged) pressure drop
            self._Z_perm_last = Z_perm
            return fug_ret, fug_perm
        # Cheap path: reuse cached phi (and cached Z) against the current state.
        return self._phi_ret * ZR * PR, self._phi_perm * ZP * PP

    def _energy_bulk_props(self):
        """Bulk properties the ENERGY path must have evaluated.

        The property class only evaluates the full transport set for
        `eos == "HEOS"`; under "PR" -- which every scenario uses -- it defaults to
        `hmolar` alone. That silently broke two things:

          * `UCalculation` needs conductivity, viscosity, cpmass, molar_mass and
            rhomass, so activating it (`U = None`) raised
            `KeyError: 'conductivity'` immediately;
          * the energy Jacobian reads `.get("cpmolar", 30.0)`, so with cpmolar
            absent it always fell back to a hardcoded 30 J/mol.K despite the
            comment claiming an exact Cp.

        So the energy path now states its requirements explicitly instead of
        depending on the EOS default.
        """
        props = ["hmolar", "cpmolar"]
        if not self.heat_transfer_coef:      # U computed -> UCalculation active
            props += ["conductivity", "viscosity", "cpmass", "molar_mass",
                      "rhomass"]
        return props

    def _thermo_reuse(self, attr, components, P, T, Z, force_gas, NCells):
        """Reuse a cached CoolProp property object across the outer iterations
        of one candidate (updating P/T/Z in place via set_conditions) instead of
        rebuilding the NStates AbstractState objects every iteration. Rebuilt
        only if the node count, component set, or phase flag changes."""
        want = self._energy_bulk_props()
        obj = getattr(self, attr, None)
        if (obj is None or obj.NStates != NCells + 1
                or list(getattr(obj, "components", [])) != list(components)
                or bool(obj.force_gas_phase) != bool(force_gas)
                or set(want) - set(getattr(obj, "bulk_props", []))):
            obj = MixPropertiesCoolPropHEOS(
                components=components, P=P, T=T, Z=Z,
                force_gas_phase=force_gas, eos=self.eospackage,
                bulk_props=want)
            setattr(self, attr, obj)
        else:
            obj.set_conditions(P=P, T=T, Z=Z)
        return obj

    # ---------------------------------------
    # Main Simulation Runner
    # ---------------------------------------
    def run(self) -> SimulatorResultsHFM:
        """
        Public entry point. Runs the simulation and returns a results object.

        On a physically infeasible pressure drop (frictional drop exceeding the
        available driving pressure), run() does NOT raise: it returns a results
        object flagged as infeasible so the enumeration checks the flag and
        moves on:

            results = sim.run()
            if not results.feasible:
                ...  # skip / trim candidate (results.infeasible_reason)

        When infeasible, all physical fields remain None.
        """
        # -----------------------------------------------------------------
        # Solver ladder: LU -> Marching -> Least-squares. Each stage is tried
        # and, on non-convergence, control passes to the next (cheap -> robust).
        #   LU            : frozen-fugacity linear solve; fast, handles normal
        #                   (low module-Courant) candidates.
        #   Marching      : implicit forward march; makes the outer fugacity loop
        #                   contract on high module-Courant (oversized /
        #                   high-permeance) candidates where LU does not.
        #   Least-squares : trust-region solve with permeance homotopy; the final,
        #                   most robust resort.
        # -----------------------------------------------------------------
        def _pressure_infeasible_result():
            results = SimulatorResultsHFM()
            results.feasible = False
            results.infeasible_reason = (
                "Inviabilidade de pressão: o laço externo não converge porque a "
                "pressão do retentado permanece presa no limite inferior (nível do "
                "permeado). A queda de pressão excede a pressão disponível."
            )
            return results

        solver_ladder = (
            ("LU",            dict(prefer_marching=False, force_least_squares=False)),
            ("marching",      dict(prefer_marching=True,  force_least_squares=False)),
            ("least_squares", dict(prefer_marching=False, force_least_squares=True)),
        )
        def _run_ladder():
            last_exc = None
            _cold_retry_done = False
            for _name, _flags in solver_ladder:
                self._prefer_marching = _flags["prefer_marching"]
                self._force_least_squares = _flags["force_least_squares"]
                try:
                    return self._run_impl()
                except PressureDropInfeasible as e:
                    results = SimulatorResultsHFM()
                    results.feasible = False
                    results.infeasible_reason = str(e)
                    return results
                except SimulationNotConverged as e:
                    # NON-CONVERGENCE IS NOT PROOF OF INFEASIBILITY. This handler
                    # used to short-circuit the whole ladder whenever the pressure
                    # clamp happened to be active at the moment the loop ran out of
                    # iterations, on the argument that the flag "refers to the
                    # converged evaluation". It does not: if the loop did not
                    # converge, the flag describes the last (arbitrary) iterate.
                    #
                    # Measured consequence: a candidate that converges cleanly from
                    # a cold start (S0, L=1.3, D=0.2, 300/100 um, eps=0.40, PI) was
                    # declared pressure-infeasible when it inherited the warm start
                    # of a different candidate -- the LU rung failed to converge,
                    # the clamp was momentarily active, and marching and
                    # least_squares were never tried. The verdict depended on which
                    # candidate ran before it, and a viable design was rejected.
                    #
                    # So the clamp is only consulted after EVERY rung has failed
                    # (below) -- with one cheap disambiguation first.
                    #
                    # A clamp active at exhaustion is ambiguous between exactly two
                    # causes: a genuinely infeasible pressure profile, or a bad
                    # warm start inherited from the previous candidate. They are
                    # told apart directly by discarding the warm start and
                    # retrying: a viable candidate converges from the cold guess,
                    # a genuinely infeasible one fails again with the clamp still
                    # active and is rejected immediately, without paying for the
                    # remaining rungs.
                    last_exc = e
                    if (self.PRESSURE_INFEASIBLE_SHORTCUT
                            and self.pressure_drop
                            and getattr(self, "_pressure_violated", False)
                            and getattr(self, "_warm_start", None) is None):
                        # UNSOUND -- disabled by default. See the constant.
                        return _pressure_infeasible_result()
                    if (self.pressure_drop
                            and getattr(self, "_pressure_violated", False)
                            and not _cold_retry_done
                            and getattr(self, "_warm_start", None) is not None):
                        _cold_retry_done = True
                        _saved_ws = self._warm_start
                        self._warm_start = None
                        try:
                            return self._run_impl()
                        except PressureDropInfeasible as e2:
                            results = SimulatorResultsHFM()
                            results.feasible = False
                            results.infeasible_reason = str(e2)
                            return results
                        except SimulationNotConverged as e2:
                            last_exc = e2
                            if (self.PRESSURE_INFEASIBLE_SHORTCUT
                                    and getattr(self, "_pressure_violated", False)):
                                return _pressure_infeasible_result()
                        finally:
                            self._warm_start = _saved_ws
                    continue
            # Every rung failed to converge. Only now, with no solver able to
            # resolve the candidate, is a still-active clamp taken as evidence of
            # pressure infeasibility rather than of a solver limitation.
            if self.pressure_drop and getattr(self, "_pressure_violated", False):
                return _pressure_infeasible_result()
            raise last_exc

        _phi0 = int(getattr(self, "phi_refresh_every", 1))
        # Per-candidate wall-clock budget. Checked cooperatively inside the hot
        # loops (see Simulation_Deadline). A candidate that runs out is returned
        # as UNRESOLVED (`timed_out = True`), never silently as infeasible: it
        # was not proven infeasible, it was simply not finished.
        _deadline.arm(getattr(self, "time_budget_s", None))
        try:
            # The timeout guard must be the OUTERMOST handler. It previously sat
            # as a sibling of the phi-fallback clause below, so a timeout raised
            # during the fallback RETRY was not caught and escaped from run(),
            # killing the whole scenario in the batch runner. The budget is a
            # property of the candidate, not of the attempt, so every attempt
            # must be covered.
            try:
                try:
                    return _run_ladder()
                except (PressureDropInfeasible, SimulationNotConverged,
                        SimulationTimeout):
                    raise
                except Exception:
                    # The phi-refresh cadence (phi_refresh_every > 1) can destabilize
                    # the pressure/fugacity coupling on some high-stage-cut candidates
                    # (phi stops being "weak" when the composition changes sharply).
                    # Recover EXACTLY by retrying with phi recomputed every iteration.
                    if _phi0 > 1:
                        self.phi_refresh_every = 1
                        return _run_ladder()
                    raise
            except SimulationTimeout:
                results = SimulatorResultsHFM()
                results.feasible = False
                results.timed_out = True
                results.infeasible_reason = (
                    f"NOT RESOLVED: exceeded the {self.time_budget_s:g} s "
                    f"simulation time budget. This candidate was skipped for "
                    f"cost and is NOT proven infeasible -- re-run it with a "
                    f"larger budget before relying on the enumeration.")
                return results
        finally:
            _deadline.clear()   # must never leak into the next candidate
            self.phi_refresh_every = _phi0
            self._prefer_marching = False
            self._force_least_squares = False

    def _run_impl(self) -> SimulatorResultsHFM:
        """
        Executes the HFM simulation, coupling mass and energy balances.
        Returns: SimulatorResultsHFM object containing all simulation outputs.
        """
        # ---------------------------------------------------------
        # 1. Setup & Initial Conditions
        # ---------------------------------------------------------
        # Reset caches
        self._solver_paths = set()
        self._fug_call_count = 0
        self._phi_ret = None
        self._Z_ret_last = None
        self._Z_perm_last = None

        feed = self.feed
        if feed is None:
            raise RuntimeError("Feed stream not set")

        # Extract feed state
        components = feed.components
        FFeed_total = feed.molar_flow / self.geometry.NumberOfTubesInParallel
        ZFeed = np.array(feed.mole_fractions)
        FFeed = FFeed_total * ZFeed
        PFeed = feed.P
        TFeed = feed.T
        Permeance = self.permeance
        n_comp = len(components)
        PPerm = self.PPerm
        R = self.GAS_CONSTANT_R
        NCells = self.geometry.NCells

        # Some components lack transport models in CoolProp HEOS (e.g. H2S, COS).
        # Replace NaN with a default gas viscosity so the HZ correlation does not
        # propagate NaN and poison the whole simulation.
        _mu_pure = self.feed.component_viscosities.copy()
        _mu_pure[~np.isfinite(_mu_pure)] = 1e-5  # default gas viscosity [Pa·s]

        self.properties = MixtureProperties(
            components=components,
            MU=_mu_pure,
            M=self.feed.component_molar_masses,
            method=self.VISCOSITY_METHOD
        )

        props = self.properties

        # Reset the phi-refresh and Z caches for this run (fresh per ladder stage).
        # Which ladder rungs actually produced solutions in this run. The fast
        # paths fail silently and fall through, so this is the only way to see
        # from a result that it came from the last-resort solver.
        self._solver_paths = set()
        self._fug_call_count = 0
        self._phi_ret = None
        self._Z_ret_last = None
        self._Z_perm_last = None

        feed = self.feed
        # self.feed.flow = self.feed.flow / self.geometry.NumberOfTubesInParallel

        if feed is None:
            raise RuntimeError("Feed stream not set")

        components = feed.components
        # FFeed_total = feed.flow
        FFeed_total = feed.molar_flow / self.geometry.NumberOfTubesInParallel

        ZFeed = np.array(feed.mole_fractions)
        FFeed = FFeed_total * ZFeed
        
        PFeed = feed.P
        TFeed = feed.T
        props = self.properties
        Permeance = self.permeance
        n_comp = len(components)
        PPerm = self.PPerm
        R = self.GAS_CONSTANT_R
        NCells = self.geometry.NCells

        # ---------------------------------------------------------
        # 1b. Mesh: cell COUNT (Courant sizing) + cell SPACING (mesh_type)
        # ---------------------------------------------------------
        # N_Partitions is treated as a MINIMUM; the Courant criterion may ask for
        # more cells on high-permeance candidates. The cell SPACING is then set by
        # self.mesh_type ("uniform" default; "fixed" = geometric mesh fine at the
        # inlet, ~3-4x fewer cells at equal accuracy for low-stage-cut candidates,
        # see mesh_study/).
        N_partitions_min = NCells
        try:
            _courant_sizes = build_courant_adaptive_mesh(
                L=self.geometry.LHidraulic,
                AREA_PER_L=self.geometry.AREA_PER_L,
                PFeed=PFeed,
                FFeed_total_per_tube=FFeed_total,
                Q=np.asarray(Permeance, dtype=float),
                co_target=0.8,
                N_abs_max=1000,
                max_frac=0.1,
            )
            N_exp = len(_courant_sizes)
        except Exception:
            N_exp = 0

        NCells = N_exp if N_exp > N_partitions_min else N_partitions_min

        mesh_type = getattr(self, "mesh_type", "uniform")
        if mesh_type == "fixed":
            _cs = fixed_ratio_mesh(self.geometry.LHidraulic, NCells,
                                   getattr(self, "mesh_ratio", 40.0))
        else:  # "uniform"
            _cs = None
        if _cs is not None or NCells != self.geometry.NCells:
            self.geometry = self._rebuild_geometry(NCells, _cs)
        self._N_adapt = NCells

        # ---------------------------------------------------------
        # 2. Initial Fast Mass Balance (No Pressure Drop)
        # ---------------------------------------------------------
        ws = getattr(self, "_warm_start", None)
        ws_ok = False
        if ws is not None:
            try:
                ws = self._interpolate_warm_start(ws, NCells, n_comp)
                ws_ok = ws is not None
            except Exception:
                ws_ok = False

        if ws_ok:
            PRetCell_guess = ws["PRet"].copy()
            PPermCell_guess = ws["PPerm"].copy()
        else:
            PRetCell_guess = np.linspace(PFeed, PFeed, NCells + 1)
            PPermCell_guess = np.linspace(PPerm, PPerm + 0, NCells + 1)

        module = MassBalanceWithoutPressureDropHFM(
            geometry=self.geometry, properties=props, R=R, T=TFeed, Permeance=Permeance,
            n_comp=n_comp, FFeed=FFeed, PFeed=PFeed, PPerm=PPerm,
            PRetCell=PRetCell_guess, PPermCell=PPermCell_guess
        )
        module.prefer_marching = getattr(self, "_prefer_marching", False)
        module.force_least_squares = getattr(self, "_force_least_squares", False)

        # Mass-balance tolerances all derive from `iteration_tolerance` -- it is
        # the one convergence knob for the mass side (energy has its own,
        # ENERGY_CONVERGENCE_TOL). The inner fixed point inside
        # solve_partial_pressure_fast measures an ABSOLUTE error on component
        # flows [mol/s], so the tolerance is scaled by the total feed flow to
        # keep it dimensionally meaningful across candidates.
        _f_scale = max(float(np.sum(FFeed)), 1.0)
        self._f_scale = _f_scale
        # Standalone use (mass-only, no outer loop): the inner solve IS the
        # simulation, so it must meet `iteration_tolerance` itself. INNER_TOL_
        # FLOOR_FACTOR keeps it safely inside that criterion rather than exactly
        # on it.
        module.inner_tol = self.INNER_TOL_FLOOR_FACTOR * self.iteration_tolerance * _f_scale
        # Tolerance for the marching solver's Anderson phase. This one measures
        # |G - u| on the permeate COMPOSITION, which is dimensionless, so it is
        # derived from `iteration_tolerance` DIRECTLY and must NOT be scaled by
        # _f_scale the way `inner_tol` is -- `inner_tol` is an absolute flow in
        # mol/s and the two are not interchangeable.
        #
        # `solve_marching_fast` was previously called with no arguments at both
        # of its call sites, so it always ran on its hardcoded default of 1e-11
        # regardless of what the user asked for: with the scenarios'
        # iteration_tolerance of 1e-6 the marching phase was chasing a tolerance
        # 100 000x tighter than the loop consuming its result, which is why its
        # Anderson phase routinely exhausted all 400 iterations on a plateau it
        # had no reason to leave.
        module.march_tol = self.MARCH_TOL_FRACTION * self.iteration_tolerance

        if ws_ok:
            FRetCell_guess = ws["FRet"].copy()
            FPermCell_guess = ws["FPerm"].copy()
            # Enforce the feed boundary condition exactly on the warm-started flow.
            FRetCell_guess[0, :] = FFeed
        else:
            FRetCell_guess = np.zeros((NCells + 1, n_comp))
            FPermCell_guess = np.zeros((NCells + 1, n_comp))
            for i in range(n_comp):
                FRetCell_guess[:, i] = np.linspace(FFeed[i], FFeed[i] * 0.9, NCells + 1)
                FPermCell_guess[:, i] = np.linspace(FFeed[i] * 0.5, 1e-12, NCells + 1)

        solver = MassBalanceSolverHFM(module)

        # Whether the initial mass-only balance must run here:
        #  - cold start (no warm start): always, it produces the starting guess.
        #  - MASS-ONLY config (no fugacity, no pressure drop): ALWAYS, because
        #    there is no outer branch below to re-solve the candidate -- this
        #    solve IS the simulation and it is what populates module.last_FMemb.
        #  - warm-started fugacity/pressure config: skip it. The branch below
        #    re-solves the current candidate from the (better) warm-start profile;
        #    running the mass-only solve would only waste a solve and overwrite
        #    that good guess with an over-permeated mass-only one.
        mass_only = (not self.use_fugacity) and (not self.pressure_drop)
        if (not ws_ok) or mass_only:
            x0 = module.initial_guess(FRetCell_guess, FPermCell_guess)
            sol, FRetCell_guess, FPermCell_guess, info = solver.solve(
                x0, tol=self.solver_tolerance, verbose=self.verbose_least_squares)
            self._solver_paths.add(info.get('path', '?'))
            if info.get('march_exit'):
                self._march_exit = info['march_exit']

        if ws_ok:
            T_guess = ws["T"].copy()
        else:
            T_guess = np.zeros(2 * (NCells + 1))
            T_guess[:NCells + 1] = np.linspace(TFeed, TFeed - 1, NCells + 1)
            T_guess[NCells + 1:] = np.full(NCells + 1, TFeed - 1.0)

        FugacityRet = np.zeros((NCells+1, n_comp))
        FugacityPerm = np.zeros((NCells+1, n_comp))

        if not self.use_fugacity and not self.pressure_drop:
            FRetCell_fin = FRetCell_guess
            FPermCell_fin = FPermCell_guess
            PRetCell_fin = PRetCell_guess
            PPermCell_fin = PPermCell_guess

        # ---------------------------------------------------------
        # 3. OUTER LOOP: Mass and Energy Balance Coupling
        # ---------------------------------------------------------
        # --- ADAPTATIVE INITIALIZATION (OUTSIDE FOR) ---
        alpha = 0.30  # first aprox
        alpha_min = 0.01  # min step
        alpha_max = 1.00  # allow full step when convergence is monotone
        error_prev = np.inf
        # Error trajectory of whichever outer branch runs. Fed to
        # _classify_outer so a non-converged candidate reports HOW it failed
        # (oscillating / stalled / descending) instead of just "não convergiu".
        _hist = []
        self._outer_diag = None

        alpha_energy = 0.3  # damping da atualização de temperatura (adaptativo)
        error_prev_energy = np.inf

        for itermain in range(self.max_num_iterations):
            _deadline.check()   # per-candidate wall-clock budget
            
            # -----------------------------------------------------
            # BRANCH 1: Fugacity ONLY
            # -----------------------------------------------------
            if self.use_fugacity and not self.pressure_drop:
                for iter_fugacity in range(self.max_num_iterations):
                    _deadline.check()   # per-candidate wall-clock budget
                    FRet, FPerm, ZRet, ZPerm = self._get_stream_compositions(FRetCell_guess, FPermCell_guess)
                    fug_ret_array, fug_perm_array = self._fugacities(components, PRetCell_guess, PPermCell_guess,
                                                                         T_guess, ZRet, ZPerm, NCells)

                    module = MassBalanceWithFugacityHFM(
                        geometry=self.geometry, properties=props, R=R, T=T_guess, Permeance=Permeance,
                        n_comp=n_comp, FFeed=FFeed, PFeed=PFeed, PPerm=PPerm,
                        FugacityRetentate=fug_ret_array, FugacityPermeate=fug_perm_array,
                        ZRet=ZRet, ZPerm=ZPerm,
                        PRetCell=PRetCell_guess, PPermCell=PPermCell_guess
                    )
                    module.prefer_marching = getattr(self, "_prefer_marching", False)
                    module.force_least_squares = getattr(self, "_force_least_squares", False)

                    x0 = module.initial_guess(FRetCell_guess, FPermCell_guess)
                    # print("Running Mass Balance with fugacity...")
                    solver = MassBalanceSolverHFM(module)
                    sol, FRetCell_fin, FPermCell_fin, info = solver.solve(x0, tol=self.solver_tolerance,
                                                                          verbose=self.verbose_least_squares)
                    self._solver_paths.add(info.get('path', '?'))
                    if info.get('march_exit'):
                        self._march_exit = info['march_exit']

                    # Error Calculation
                    error_fugacity = max(
                        np.max(np.abs(FRetCell_guess - FRetCell_fin)), 
                        np.max(np.abs(FPermCell_guess[:-1, :] - FPermCell_fin[:-1, :]))
                    )
                    # print(f"Pressure + Fugacity iter {iter_fugacity}: Error = {error_fugacity:.3e} | Alpha = {alpha:.3f}")

                    # Simple damping
                    if error_fugacity < error_prev:
                        # acelerate if error improves
                        alpha = min(alpha * 1.25, alpha_max)
                    else:
                        # decelerate if error worsens
                        alpha = max(alpha * 0.5, alpha_min)
                    
                    error_prev = error_fugacity

                    # Relaxed update values
                    FRetCell_guess = (1.0 - alpha) * FRetCell_guess + alpha * FRetCell_fin
                    FPermCell_guess = (1.0 - alpha) * FPermCell_guess + alpha * FPermCell_fin

                    FRetCell_guess = np.maximum(FRetCell_guess, 0.0)
                    FPermCell_guess = np.maximum(FPermCell_guess, 0.0)

                    # Output variables actualization
                    FugacityRet = module.last_FugacityRet
                    FugacityPerm = module.last_FugacityPerm
                    PRetCell_fin = PRetCell_guess.copy()
                    PPermCell_fin = PPermCell_guess.copy()

                    # Verify convergence
                    _hist.append(float(error_fugacity))
                    if error_fugacity < self.iteration_tolerance:
                        # print("✅ Mass balance with pressure drop + fugacity CONVERGED.")
                        self._outer_diag = {"branch": 1, "exit": "converged",
                                            "iters": len(_hist)}
                        break
                else:
                    _lab, _st = self._classify_outer(_hist)
                    self._outer_diag = {"branch": 1, "exit": _lab, **_st}
                    raise SimulationNotConverged(
                        f"Branch 1 (fugacity) não convergiu [{_lab}]: "
                        f"erro={error_fugacity:.3e} >= tol={self.iteration_tolerance:.3e} "
                        f"após {self.max_num_iterations} iterações."
                    )


            # -----------------------------------------------------
            # BRANCH 2: Pressure Drop ONLY
            # -----------------------------------------------------
            elif self.pressure_drop and not self.use_fugacity:
                error_prev_p = np.inf
                alpha = 0.30  # reset por passada externa
                # Inexact inner solve: the inner partial-pressure fixed point is
                # only converged to a fraction of the CURRENT outer error, since
                # the outer loop damps its result by alpha and re-solves anyway.
                # Both bounds are multiples of `iteration_tolerance` (scaled by
                # the feed, as the inner error is absolute on flows). The floor
                # keeps the inner solve inside the outer criterion, making the
                # scheme asymptotically exact.
                _tol_unit = self.iteration_tolerance * self._f_scale
                _inner_floor = self.INNER_TOL_FLOOR_FACTOR * _tol_unit
                _inner_cap = self.INNER_TOL_RELAX_FACTOR * _tol_unit
                module.inner_tol = _inner_cap
                # The inexact inner solve does not bias the answer beyond the
                # outer tolerance, but it does change WHICH point inside the
                # outer tolerance ball is reached. So once the outer loop meets
                # its criterion, do one extra pass with an exact inner solve and
                # require the criterion again -- this "polish" costs ~1 inner
                # solve out of hundreds and removes the discrepancy.
                _polished = False
                # Anderson acceleration of the OUTER pressure<->flow fixed point.
                # The state is the PRESSURE profile (all O(1e5-1e6) Pa, i.e. well
                # scaled), never the flows. Anderson only supplies a better target
                # for the existing relaxation: with no history it returns the plain
                # Picard image, so the damping schedule below is unchanged and the
                # scheme cannot do worse than before by construction.
                _aa = {"F": [], "G": []}
                _n_nodes = NCells + 1
                # Anderson is a bet that the map is locally linear. On candidates
                # whose cost sits in the inner solve that bet keeps losing, and
                # the repeated restarts cost more than the extrapolation saves
                # (measured: one candidate 1.4x SLOWER). So count the restarts and
                # give up on the acceleration for the rest of this candidate once
                # it has proved unhelpful -- reverting to plain damped Picard.
                _aa_restarts = 0
                _aa_on = self.OUTER_ANDERSON_DEPTH > 0
                for iter_pressure in range(self.max_num_iterations):
                    _deadline.check()   # per-candidate wall-clock budget
                    FRet, FPerm, ZRet, ZPerm = self._get_stream_compositions(FRetCell_guess, FPermCell_guess)

                    # Damped pressure update: relax newly computed pressures
                    # toward the previous ones (the raw Picard update with no
                    # relaxation produces a limit cycle on the P<->F coupling).
                    PRet_old = PRetCell_guess.copy()
                    PPerm_old = PPermCell_guess.copy()
                    PRet_new, PPerm_new = self._update_pressures(PRetCell_guess.copy(), PPermCell_guess.copy(), FRet,
                                                                 FPerm, ZRet, ZPerm, T_guess, NCells, props, R)

                    # Anderson-accelerated relaxation target (falls back to the
                    # plain Picard image PRet_new/PPerm_new when there is no
                    # usable history). Pressures are floored at 1 Pa so an
                    # extrapolation can never hand a nonphysical profile to
                    # _update_pressures on the next pass.
                    # A pressure clamp active in _update_pressures makes the
                    # fixed-point map NON-SMOOTH (the retentate is pinned at the
                    # permeate level), so Anderson's local linear model is
                    # invalid: extrapolating there delays the infeasibility
                    # verdict badly (measured: 5.6 s -> >37 s on a
                    # pressure-infeasible candidate). Fall back to plain damped
                    # Picard for the rest of this candidate.
                    # The suppression is TEMPORARY, not permanent: the clamp often
                    # activates only transiently on candidates that end up
                    # perfectly feasible, and disabling the acceleration for good
                    # there throws away the largest win (measured: 3.8x -> 1.0x).
                    # A genuinely infeasible candidate stays clamped, so it simply
                    # never gets to use Anderson.
                    _clamped = getattr(self, "_pressure_violated", False)
                    if _clamped and _aa["F"]:
                        _aa["F"].clear()
                        _aa["G"].clear()

                    if _aa_on and not _clamped and iter_pressure >= self.OUTER_ANDERSON_WARMUP:
                        _un = self._anderson_extrapolate(
                            _aa,
                            np.concatenate([PRet_old, PPerm_old]),
                            np.concatenate([PRet_new, PPerm_new]),
                            m=self.OUTER_ANDERSON_DEPTH)
                        PRet_tgt = np.maximum(_un[:_n_nodes], 1.0)
                        PPerm_tgt = np.maximum(_un[_n_nodes:], 1.0)
                    else:
                        PRet_tgt, PPerm_tgt = PRet_new, PPerm_new

                    PRetCell_guess = (1.0 - alpha) * PRet_old + alpha * PRet_tgt
                    PPermCell_guess = (1.0 - alpha) * PPerm_old + alpha * PPerm_tgt

                    FRetCell_guess = np.maximum(FRetCell_guess, 0.0)
                    FPermCell_guess = np.maximum(FPermCell_guess, 0.0)

                    module.PRetCell = PRetCell_guess
                    module.PPermCell = PPermCell_guess

                    x0 = module.initial_guess(FRetCell_guess, FPermCell_guess)
                    # print("Running Basic Mass Balance plus pressure drop...")
                    solver = MassBalanceSolverHFM(module)
                    sol, FRetCell_fin, FPermCell_fin, info = solver.solve(x0, tol=self.solver_tolerance,
                                                                          verbose=self.verbose_least_squares)
                    self._solver_paths.add(info.get('path', '?'))
                    if info.get('march_exit'):
                        self._march_exit = info['march_exit']

                    error_pressure = max(np.max(np.abs(FRetCell_guess - FRetCell_fin)),
                                         np.max(np.abs(FPermCell_guess[:-1, :] - FPermCell_fin[:-1, :])))

                    # Tighten the inner tolerance as the outer error falls. Once
                    # the polishing pass has switched the inner solve to exact,
                    # it stays exact (degrades gracefully to the old scheme).
                    if not _polished:
                        module.inner_tol = float(np.clip(
                            self.INNER_TOL_FRACTION * error_pressure,
                            _inner_floor, _inner_cap))
                    # print( f"Pressure iteration {iter_pressure}: Error pressure = {error_pressure:.3e} | Alpha = {alpha:.3f}")

                    # Adaptive damping (same schedule as the fugacity branches)
                    if error_pressure < error_prev_p:
                        alpha = min(alpha * 1.25, alpha_max)
                    else:
                        alpha = max(alpha * 0.5, alpha_min)
                        # The error rose: the Anderson history is stale (or the
                        # linear model behind the extrapolation is no longer
                        # valid). Restart it, so the next step is plain damped
                        # Picard rather than an extrapolation off a bad secant.
                        _aa["F"].clear()
                        _aa["G"].clear()
                        if _aa_on:
                            _aa_restarts += 1
                            if _aa_restarts > self.OUTER_ANDERSON_MAX_RESTARTS:
                                _aa_on = False
                    error_prev_p = error_pressure
                    # print(error_pressure)

                    # Relaxed flow update
                    FRetCell_guess = (1.0 - alpha) * FRetCell_guess + alpha * FRetCell_fin
                    FPermCell_guess = (1.0 - alpha) * FPermCell_guess + alpha * FPermCell_fin

                    FRetCell_guess = np.maximum(FRetCell_guess, 0.0)
                    FPermCell_guess = np.maximum(FPermCell_guess, 0.0)

                    PRetCell_fin = PRetCell_guess
                    PPermCell_fin = PPermCell_guess

                    _hist.append(float(error_pressure))
                    if error_pressure < self.iteration_tolerance:
                        if _polished:
                            self._outer_diag = {"branch": 2, "exit": "converged",
                                                "iters": len(_hist)}
                            break
                        # Converged under the inexact inner solve: switch the
                        # inner solve to exact and demand the criterion once more.
                        _polished = True
                        module.inner_tol = _inner_floor
                        # Tightening the inner tolerance changes the fixed-point
                        # map, so the accumulated history no longer describes it.
                        _aa["F"].clear()
                        _aa["G"].clear()
                else:
                    _lab, _st = self._classify_outer(_hist)
                    self._outer_diag = {"branch": 2, "exit": _lab, **_st}
                    raise SimulationNotConverged(
                        f"Branch 2 (pressure drop) não convergiu [{_lab}]: "
                        f"erro={error_pressure:.3e} >= tol={self.iteration_tolerance:.3e} "
                        f"após {self.max_num_iterations} iterações."
                    )

            # -----------------------------------------------------
            # BRANCH 3: BOTH Fugacity AND Pressure Drop
            # -----------------------------------------------------
            elif self.use_fugacity and self.pressure_drop:
                for iter_fugacity in range(self.max_num_iterations):
                    _deadline.check()   # per-candidate wall-clock budget
                    FRet, FPerm, ZRet, ZPerm = self._get_stream_compositions(FRetCell_guess, FPermCell_guess)
                    # Relax the pressure with the SAME alpha as the flows.
                    #
                    # This branch used to take a FULL Picard step on the
                    # pressure (plain assignment) while damping only the flows
                    # below. Pressure and flow are strongly coupled here -- the
                    # bore pressure drop is roughly quadratic in the permeate
                    # flow -- so mixing a full step on one with a damped step on
                    # the other drives a period-2 limit cycle on narrow-bore
                    # candidates: the outer error oscillates (0.77, 0.18, 0.71,
                    # 0.18, ...) forever without a trend, the adaptive alpha
                    # ratchets down to its floor and stays there, and the
                    # candidate exhausts max_num_iterations. Those candidates
                    # were previously believed to be infeasible; they are not.
                    # Measured (S5/8428, S5/18063, S3/29007, all of which
                    # NEVER converged before): 18 s / no convergence ->
                    # 0.10-0.11 s converged to 1e-06, via LU + fixed point.
                    # Well-behaved candidates also improve (37 -> 22 outer
                    # iterations) and land on the SAME fixed point: the
                    # relaxation changes only the path, not the solution, and
                    # the two agree to 5e-07 / 1.0e-06, i.e. to the loop
                    # tolerance itself.
                    #
                    # Iteration 0 takes the full step: there is no previous
                    # pressure iterate worth averaging with, the incoming guess
                    # being merely the feed-pressure seed.
                    # Set BRANCH3_RELAX_PRESSURE = False to restore the
                    # undamped update (A/B measurement only).
                    _P_ret_prev = PRetCell_guess.copy()
                    _P_perm_prev = PPermCell_guess.copy()
                    _P_ret_new, _P_perm_new = self._update_pressures(
                        PRetCell_guess, PPermCell_guess, FRet,
                        FPerm, ZRet, ZPerm, T_guess, NCells, props, R)
                    if self.BRANCH3_RELAX_PRESSURE and iter_fugacity > 0:
                        PRetCell_guess = (1.0 - alpha) * _P_ret_prev + alpha * _P_ret_new
                        PPermCell_guess = (1.0 - alpha) * _P_perm_prev + alpha * _P_perm_new
                    else:
                        PRetCell_guess, PPermCell_guess = _P_ret_new, _P_perm_new
                    fug_ret_array, fug_perm_array = self._fugacities(components, PRetCell_guess, PPermCell_guess,
                                                                         T_guess, ZRet, ZPerm, NCells)

                    module = MassBalanceWithFugacityHFM(
                        geometry=self.geometry, properties=props, R=R, T=T_guess, Permeance=Permeance,
                        n_comp=n_comp, FFeed=FFeed, PFeed=PFeed, PPerm=PPerm,
                        FugacityRetentate=fug_ret_array, FugacityPermeate=fug_perm_array,
                        ZRet=ZRet, ZPerm=ZPerm,
                        PRetCell=PRetCell_guess, PPermCell=PPermCell_guess
                    )
                    module.prefer_marching = getattr(self, "_prefer_marching", False)
                    module.force_least_squares = getattr(self, "_force_least_squares", False)

                    x0 = module.initial_guess(FRetCell_guess, FPermCell_guess)
                    # print("Running mass balance with pressure drop plus fugacity...")
                    solver = MassBalanceSolverHFM(module)
                    
                    # Original tolerance for this specific coupled branch preserved
                    sol, FRetCell_fin, FPermCell_fin, info = solver.solve(x0, tol=self.solver_tolerance,
                                                                          verbose=self.verbose_least_squares)
                    self._solver_paths.add(info.get('path', '?'))
                    if info.get('march_exit'):
                        self._march_exit = info['march_exit']

                    # Error Calculation
                    error_fugacity = max(
                        np.max(np.abs(FRetCell_guess - FRetCell_fin)), 
                        np.max(np.abs(FPermCell_guess[:-1, :] - FPermCell_fin[:-1, :]))
                    )
                    # print(f"Pressure + Fugacity iter {iter_fugacity}: Error = {error_fugacity:.3e} | Alpha = {alpha:.3f}")

                    # Simple damping
                    if error_fugacity < error_prev:
                        # acelerate if error improves
                        alpha = min(alpha * 1.25, alpha_max)
                    else:
                        # decelerate if error worsens
                        alpha = max(alpha * 0.5, alpha_min)
                    
                    error_prev = error_fugacity

                    # Relaxed update values
                    FRetCell_guess = (1.0 - alpha) * FRetCell_guess + alpha * FRetCell_fin
                    FPermCell_guess = (1.0 - alpha) * FPermCell_guess + alpha * FPermCell_fin

                    FRetCell_guess = np.maximum(FRetCell_guess, 0.0)
                    FPermCell_guess = np.maximum(FPermCell_guess, 0.0)

                    # Output variables actualization
                    FugacityRet = module.last_FugacityRet
                    FugacityPerm = module.last_FugacityPerm
                    PRetCell_fin = PRetCell_guess.copy()
                    PPermCell_fin = PPermCell_guess.copy()

                    # Verify convergence
                    _hist.append(float(error_fugacity))
                    if error_fugacity < self.iteration_tolerance:
                        # print("✅ Mass balance with pressure drop + fugacity CONVERGED.")
                        self._outer_diag = {"branch": 3, "exit": "converged",
                                            "iters": len(_hist)}
                        break
                else:
                    _lab, _st = self._classify_outer(_hist)
                    self._outer_diag = {"branch": 3, "exit": _lab, **_st}
                    raise SimulationNotConverged(
                        f"Branch 3 (fugacity + pressure drop) não convergiu [{_lab}]: "
                        f"erro={error_fugacity:.3e} >= tol={self.iteration_tolerance:.3e} "
                        f"após {self.max_num_iterations} iterações."
                    )

            # ---------------------------------------------------------
            # 4. POST-MASS BALANCE: Fluxes & Results Object Setup
            # ---------------------------------------------------------
            FRet, FPerm, ZRet, ZPerm = self._get_stream_compositions(FRetCell_fin, FPermCell_fin)

            FMemb_comp = np.maximum(module.last_FMemb, 0)  # Limpiar posibles ruidos numéricos
            FMemb = FMemb_comp.sum(axis=1)

            ZMemb = np.zeros((NCells+1, n_comp))
            for k in range(1, NCells+1):
                ZMemb[k] = FMemb_comp[k] / FMemb[k]

            # -------------------------------------------------------------
            # Pressure feasibility on the CONVERGED profile
            # -------------------------------------------------------------
            # Only now are the flows trustworthy, so only now is the pressure
            # drop they imply trustworthy. During the iteration the pressure was
            # merely CLAMPED (never used to reject), because early iterates carry
            # near-feed flows and therefore the largest pressure drop of the whole
            # history -- rejecting there would trim viable high-stage-cut
            # candidates.
            #
            # `_pressure_violated` is reset at the top of every _update_pressures
            # call, so its value now refers to the CONVERGED evaluation: if the
            # clamp was still active there, the retentate genuinely cannot stay
            # above the permeate and the candidate is infeasible.
            if self.pressure_drop and getattr(self, "_pressure_violated", False):
                PRf = np.asarray(PRetCell_fin, dtype=float)
                PPf = np.asarray(PPermCell_fin, dtype=float)
                kbad = int(np.argmin(PRf - PPf))
                raise PressureDropInfeasible(
                    f"Queda de pressão excede a pressão disponível na solução CONVERGIDA: "
                    f"no nó {kbad}/{NCells} o retentado não consegue permanecer acima do "
                    f"permeado (PFeed={PRf[0]/1e5:.1f} bar, PPerm={PPf[kbad]/1e5:.2f} bar). "
                    f"A resistência viscosa é maior que a pressão disponível."
                )

            results = SimulatorResultsHFM()
            results.T_feed = TFeed
            results.NCells = NCells
            results.z = np.linspace(0, self.geometry.LHidraulic, NCells+1)
            results.components = components
            results.case_name = ("simulation", "case")

            results.FRet = FRet * self.geometry.NumberOfTubesInParallel
            results.FPerm = FPerm * self.geometry.NumberOfTubesInParallel
            results.ZRet = ZRet
            results.ZPerm = ZPerm
            results.PRetCell = PRetCell_fin
            results.PPermCell = PPermCell_fin

            results.FMemb = FMemb
            results.FMemb_comp = FMemb_comp
            results.ZMemb = ZMemb

            results.Permeance = self.permeance
            results.viscosity = feed.viscosity
            results.molecularweight = feed.molar_mass
            results.FugacityRet = FugacityRet
            results.FugacityPerm = FugacityPerm

            # ---------------------------------------------------------
            # 5. ENERGY MODEL
            # ---------------------------------------------------------
            if self.energy:
                # Reuse the CoolProp property objects across outer iterations
                # (updating P/T/Z in place) instead of rebuilding them each pass.
                _fg = bool(self.force_phase)
                thermo_retentate = self._thermo_reuse("_thermo_ret_cache", components, PRetCell_fin, T_guess[:NCells+1], ZRet, _fg, NCells)
                thermo_permeate = self._thermo_reuse("_thermo_perm_cache", components, PPermCell_fin, T_guess[NCells+1:], ZPerm, _fg, NCells)
                thermo_membrane = self._thermo_reuse("_thermo_memb_cache", components, PRetCell_fin, T_guess[:NCells+1], ZMemb, _fg, NCells)

                Ucalculated = UCalculation(geom=self.geometry, support_porosity=self.SUPPORT_POROSITY,
                                           k_polymer=self.K_POLYMER)

                if self.heat_transfer_coef:
                    # AREA_SEG is per-segment (length NCells); UA is per-node
                    # (length NCells+1). Map segment areas to nodes by repeating
                    # the last segment for the closed end. In the uniform-mesh
                    # case this reproduces the previous scalar behaviour exactly.
                    _area_seg = np.asarray(self.geometry.AREA_SEG, dtype=float)
                    _area_node = np.concatenate([_area_seg, _area_seg[-1:]])
                    UA = _area_node * self.heat_transfer_coef
                else:
                    UA = None

                energy_module = EnergyBalanceHFM(
                    FRet=FRet, FPer=FPerm, PRet=PRetCell_fin, PPerm=PPermCell_fin,
                    ZRet=ZRet, ZPerm=ZPerm, thermo_retentate=thermo_retentate,
                    thermo_permeate=thermo_permeate, thermo_membrane=thermo_membrane,
                    T_ret_in=TFeed, UA=UA, UCalculation=Ucalculated, FMemb=FMemb, ZMemb=ZMemb, geom=self.geometry
                )

                # print("Running Energy Balance...")
                energy_solver = EnergyBalanceSolverHFM(energy_module)
                T_guess = T_guess.copy()
                energy_results = energy_solver.solve(T_guess, tol=self.solver_tolerance,
                                                     verbose=self.verbose_least_squares)

                T_ret_per_new = np.concatenate((energy_results["T_ret"], energy_results["T_per"]))
                error = np.max(np.abs(T_ret_per_new[:-1] - T_guess[:-1]))

                # print(f"Outer Iteration {itermain}: error_T = {error:.3e}")
                if error < error_prev_energy:
                    alpha_energy = min(alpha_energy * 1.25, 1.0)
                else:
                    alpha_energy = max(alpha_energy * 0.5, 0.05)
                error_prev_energy = error
                T_guess = (1 - alpha_energy) * T_guess + alpha_energy * T_ret_per_new.copy()

                results.T_ret = energy_results["T_ret"]
                results.T_per = energy_results["T_per"]

                hRet = np.zeros(NCells+1)
                hPerm = np.zeros(NCells+1)
                hMemb = np.zeros(NCells+1)

                thermo_retentate.T[:] = results.T_ret
                thermo_permeate.T[:] = results.T_per
                thermo_membrane.T[:] = results.T_ret
                thermo_retentate.update_all()
                thermo_permeate.update_all()
                thermo_membrane.update_all()
                
                for k in range(NCells+1):
                    hRet[k] = thermo_retentate.props[k]["bulk"]["hmolar"]
                    hPerm[k] = thermo_permeate.props[k]["bulk"]["hmolar"]
                    hMemb[k] = thermo_membrane.props[k]["bulk"]["hmolar"]

                results.hRet = hRet
                results.hPerm = hPerm
                results.hMemb = hMemb

                # if self.calculate_dew_temperature:
                #     results.Tdew_ret = thermo_retentate.dew_temperature()
                #     results.Tdew_per = thermo_permeate.dew_temperature()
                #     results.Tdew_mem = thermo_membrane.dew_temperature()
                # else:
                #     results.Tdew_ret = hRet * 0
                #     results.Tdew_per = hRet * 0
                #     results.Tdew_mem = hRet * 0

                results.UA = energy_module.UA
                _area_seg = np.asarray(self.geometry.AREA_SEG, dtype=float)
                _area_node = np.concatenate([_area_seg, _area_seg[-1:]])
                results.U = results.UA / _area_node

                if error < self.ENERGY_CONVERGENCE_TOL:
                    break
            else:
                break
        else:
            raise SimulationNotConverged(
                f"Acoplamento energia<->massa não convergiu: |dT|={error:.3e} K "
                f">= tol={self.ENERGY_CONVERGENCE_TOL:.3e} após {self.max_num_iterations} iterações."
            )

        # ---------------------------------------------------------
        # 6. DEW-POINT CONDITION (phase stability at T - approach)
        # ---------------------------------------------------------
        # `dew_ok` is what the enumeration constraint reads. The Tdew_* arrays
        # are kept for reporting only -- they come from the PQ root-find, which
        # is unreliable near the boundary and must NOT be used to decide
        # feasibility (see MixPropertiesCoolPropHEOS.dew_temperature).
        results.dew_ok = True
        results.dew_bad_node = None
        results.dew_bad_side = None

        if self.energy:
            ok_r, bad_r = self._dew_stability(
                thermo_retentate, results.T_ret, self.dew_approach_K)
            if not ok_r:
                results.dew_ok = False
                results.dew_bad_node = bad_r
                results.dew_bad_side = "retentate"
            elif self.check_dew_permeate:
                ok_p, bad_p = self._dew_stability(
                    thermo_permeate, results.T_per, self.dew_approach_K)
                if not ok_p:
                    results.dew_ok = False
                    results.dew_bad_node = bad_p
                    results.dew_bad_side = "permeate"

        if self.calculate_dew_temperature and self.energy:
            results.Tdew_ret = thermo_retentate.dew_temperature()
            results.Tdew_per = thermo_permeate.dew_temperature()
            results.Tdew_mem = thermo_membrane.dew_temperature()
        else:
            results.Tdew_ret = T_guess[:NCells+1] * 0
            results.Tdew_per = T_guess[:NCells+1] * 0
            results.Tdew_mem = T_guess[:NCells+1] * 0



        try:
            _FRetc = FRet[:, None] * ZRet
            _FPermc = FPerm[:, None] * ZPerm
            if self.energy and results.T_ret is not None and results.T_per is not None:
                _Tws = np.concatenate((np.asarray(results.T_ret, float),
                                       np.asarray(results.T_per, float)))
            else:
                _Tws = T_guess.copy()
            results.warm_start = {
                "FRet": np.ascontiguousarray(_FRetc),
                "FPerm": np.ascontiguousarray(_FPermc),
                "PRet": np.ascontiguousarray(PRetCell_fin),
                "PPerm": np.ascontiguousarray(PPermCell_fin),
                "T": np.ascontiguousarray(_Tws),
                # Normalized node positions of THIS candidate's mesh, so a later
                # candidate with a different (possibly adaptive) mesh can
                # interpolate these profiles correctly.
                "zeta": np.ascontiguousarray(
                    self.geometry.z_nodes / self.geometry.LHidraulic),
            }
            results.N_adapt = getattr(self, "_N_adapt", NCells)
            results.solver_paths = sorted(getattr(self, "_solver_paths", set()))
            # How the outer loop terminated, and how each marching phase did.
            # These are the two things that were invisible while a period-2
            # limit cycle and a fixed-length inner loop both went unnoticed.
            results.outer_diag = getattr(self, "_outer_diag", None)
            results.march_exit = getattr(self, "_march_exit", None)
        except Exception:
            results.warm_start = None




        return results
