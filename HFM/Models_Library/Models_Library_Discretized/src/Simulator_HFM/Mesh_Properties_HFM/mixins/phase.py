#region Title: MixPropertiesCoolPropHEOS – Phase Mixin
# Nature: Phase-stability tests and dew-point calculations
# Methodology: PT flashes for stability; PQ flashes for dew temperatures.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

import numpy as np
import CoolProp
from CoolProp.CoolProp import AbstractState, PropsSI


class PhaseMixin:
    """
    Mixin responsible for:
      - Phase-stability testing (single_phase_at)
      - Dew-point temperature calculation (dew_temperature)
      - Component bounds for dew-temperature plausibility checks
    """

    # ==============================================================
    # PHASE STABILITY
    # ==============================================================
    def single_phase_at(self, T_eval, nodes=None):
        """Phase-stability test: is the mixture single-phase at (T_eval, P, Z)?

        Returns (ok, Q) with one entry per evaluated node; entries for nodes that
        were not evaluated are True / NaN.

        WHY THIS AND NOT dew_temperature(). The design condition is
        T >= T_dew + approach, which is EXACTLY equivalent to "the mixture is
        still single-phase at T - approach". That is a stability question, not a
        root-finding one. `dew_temperature()` solves PQ with Q = 1, i.e. it
        searches for a root ON the phase boundary, where the flash is at its
        least reliable: on the CO2/CH4/N2 retentate compositions of scenario S0 it
        returns 476 K at one node and raises at two others, while the correct dew
        temperatures fall smoothly from 206 K to 196 K. A PT flash at those same
        states answers correctly every time.

        Cost is self-regulating: ~0.8 ms per node far from the phase boundary,
        ~9 ms close to it -- expensive only where the constraint can actually bind.

        Parameters
        ----------
        T_eval : scalar or (NStates,) array -- temperature at which to test.
        nodes  : optional iterable of node indices to evaluate (default: all).
        """
        T_eval = np.broadcast_to(np.asarray(T_eval, dtype=float),
                                 (self.NStates,))
        idx = range(self.NStates) if nodes is None else list(nodes)

        ok = np.ones(self.NStates, dtype=bool)
        Q = np.full(self.NStates, np.nan)
        fluid_string = "&".join(self.components)

        for k in idx:
            Zk = np.asarray(self.Z[k], dtype=float).copy()
            Zk[Zk < 1e-16] = 1e-16
            Zk = Zk / np.sum(Zk)
            st = AbstractState(self.eos, fluid_string)
            st.set_mole_fractions(list(Zk))
            try:
                st.update(CoolProp.PT_INPUTS, float(self.P[k]), float(T_eval[k]))
                q = st.Q()
            except Exception:
                # A PT flash that cannot be resolved is NOT evidence of
                # feasibility. Report it as a failure so the caller can decide,
                # instead of silently passing as the old NaN path did.
                ok[k] = False
                Q[k] = np.nan
                continue
            Q[k] = q
            # CoolProp returns Q = -1 for a single-phase state; 0 <= Q <= 1 is
            # two-phase (Q = 1 means exactly on the dew line, i.e. no margin).
            ok[k] = (q < 0.0) or (q > 1.0)

        return ok, Q

    # ==============================================================
    # DEW TEMPERATURES
    # ==============================================================
    def dew_temperature(self):
        """
        Dew point temperatures [K]

        DEPRECATED for constraint evaluation -- use single_phase_at(). This
        routine root-finds on the phase boundary (PQ with Q = 1) and accepts
        whatever the first non-raising attempt returns, with no plausibility
        check, so it can return values far above the mixture critical temperature
        or below every triple point. Retained only for reporting.
        """

        fluid_string = "&".join(self.components)
        Tdew = np.full(self.NStates, np.nan)
        n_failed = 0

        for k in range(self.NStates):

            # ==========================================================
            # Temporary state
            # ==========================================================
            st = AbstractState(self.eos, fluid_string)

            # ==========================================================
            # Safe composition
            # ==========================================================
            Zk = np.array(self.Z[k], dtype=float)
            Zk[Zk < 1e-16] = 1e-16
            Zk = Zk / np.sum(Zk)
            st.set_mole_fractions(Zk)

            # ==========================================================
            # Pressure
            # ==========================================================
            P = self.P[k]

            # ==========================================================
            # Robust dew calculation
            # ==========================================================
            attempts = [
                P,
                P * 0.999,
                P * 1.001,
                P * 0.99,
                P * 1.01,
                P * 0.97,
                P * 1.03,
            ]

            success = False

            for P_try in attempts:

                try:

                    st.update(
                        CoolProp.PQ_INPUTS,
                        P_try,
                        1.0
                    )

                    T_try = st.T()

                    # PLAUSIBILITY GATE. The flash can converge to a spurious
                    # root and report success: on the CO2/CH4/N2 retentate of
                    # scenario S0 it returned 476 K at one node (above the
                    # critical temperature of every component present) and values
                    # of 6 K and 21 K at others (below every triple point). A
                    # mixture dew temperature must lie between the lowest triple
                    # point and the highest critical temperature of its
                    # components -- a cheap and rigorous bound. Anything outside
                    # is a numerical artefact and is discarded as NaN rather than
                    # reported as a temperature.
                    if not (self._T_dew_lo <= T_try <= self._T_dew_hi):
                        continue

                    Tdew[k] = T_try

                    success = True

                    break

                except Exception:

                    pass

            if not success:
                n_failed += 1

        if n_failed:
            # One summary line, not one per node: on scenarios whose operating
            # pressure sits near or above the mixture cricondenbar the dew point
            # simply does not exist and every node "fails", which would print a
            # line per node per candidate and flood the run log.
            print(
                f"[INFO] Dew point unresolved at {n_failed}/{self.NStates} nodes "
                f"(P ~ {float(np.mean(self.P)):.4g} Pa) -> reported as NaN. "
                f"This is a REPORTING value only; feasibility is decided by the "
                f"phase-stability test, not by these numbers."
            )

        return Tdew

    # ==============================================================
    # DEW TEMPERATURE BOUNDS
    # ==============================================================
    @property
    def _T_dew_bounds(self):
        """(lowest triple point, highest critical temperature) of the components."""
        cached = getattr(self, "_Tdew_bounds_cache", None)
        if cached is not None:
            return cached
        lo, hi = [], []
        for c in self.components:
            try:
                lo.append(PropsSI("Ttriple", c))
            except Exception:
                pass
            try:
                hi.append(PropsSI("Tcrit", c))
            except Exception:
                pass
        bounds = (min(lo) if lo else 0.0, max(hi) if hi else float("inf"))
        self._Tdew_bounds_cache = bounds
        return bounds

    @property
    def _T_dew_lo(self):
        return self._T_dew_bounds[0]

    @property
    def _T_dew_hi(self):
        return self._T_dew_bounds[1]
