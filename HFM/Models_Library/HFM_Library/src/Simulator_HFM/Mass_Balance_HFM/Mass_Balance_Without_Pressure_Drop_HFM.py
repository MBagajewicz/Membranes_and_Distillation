#region Title: MassBalanceWithoutPressureDropHFM
# Nature: Residual of mass balance without pressure drop equation plus jacobian for HFM
# Methodology: Prepare scaled residual and jacobian to be used in MassBalanceSolverHFM Class 
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2025    Diego Gabriel Oliva            Commented
#  0.1       07-Jun-2026    Qwen3.7 and Diego Oliva        Fixed scaling consistency (1e-12) between residual and jacobian
##################################################################################################################
#endregion

import numpy as np
from ..Simulation_Deadline import check as _deadline_check
from scipy.sparse import lil_matrix
from scipy.optimize import brentq

# --- inner damping schedule (solve_partial_pressure_fast) -------------------
# Length of the unbroken run of improving sweeps required before the damping
# ceiling is allowed to rise again. See the discussion in
# solve_partial_pressure_fast. Set to a huge value to recover the one-way
# ratchet (only useful for reproducing the pre-fix behaviour).
_DAMP_CEILING_RECOVERY_RUN = 50
# Set False to restore the ORIGINAL schedule (no ceiling ratchet: x1.1 up to a
# fixed 0.7, x0.5 down to a floor of 0.05). For A/B measurement only.
_DAMP_RATCHET = True

# ------------------------------------------------------------------
# Early-exit guards for the two-phase marching solver
# (solve_marching_fast, both here and in the fugacity twin).
#
# Both phases were written as FIXED-length loops: phase 1 always ran
# it_phase1 = 120 damped-Picard sweeps with no convergence test at all, and
# phase 2 only stopped on |G - u|_inf < tol with tol hardcoded at 1e-11.
# Instrumenting a converging candidate (S1, L = 0.6 m, D = 0.17 m,
# d_o/d_i = 130/30 um) over its 54 solver calls showed what that costs:
#
#   * phase 1 reaches machine precision (dx ~ 1e-16) by sweep 40-80 and then
#     grinds out the remaining sweeps at full price -- 83 % of all marches;
#   * phase 2 consequently performs exactly ONE march and breaks, so the
#     Anderson acceleration it exists for is never actually exercised.
#
# On a badly-behaved narrow-bore candidate (S5, d_i = 20 um) the failure is
# the mirror image: phase 1 does not contract at all (dx pinned at 5.3e-01
# for all 120 sweeps) while phase 2's Anderson does the real work, but stalls
# at |f| ~ 4e-08 and therefore burns all 400 iterations chasing 1e-11.
#
# The guards below stop each phase once it is either converged or provably
# not progressing. They cannot compromise the answer: the returned solution
# is certified independently, downstream, by the flux-residual acceptance
# test (res_act > res_accept raises), so an exit that were too early can only
# make the solver fall through to the next rung of the ladder -- never return
# a silently wrong result. Measured on the candidate above: 8130 -> 2570
# marches, 10.8 s -> 4.1 s, with the converged state agreeing to 2.8e-14
# relative.
#
# Set _MARCH_EARLY_EXIT = False to restore the original fixed-length loops.
_MARCH_EARLY_EXIT = True
# Minimum phase-1 sweeps before any exit is considered.
_MARCH_P1_MIN_IT = 10
# Phase 1 is considered converged when the permeate-composition update falls
# below this AND the stagnation index has been unchanged for
# _MARCH_P1_KSTAG_STABLE consecutive sweeps (phase 2 freezes kstag, so it must
# have settled before the hand-off).
_MARCH_P1_DX_TOL = 1e-6
_MARCH_P1_KSTAG_STABLE = 5
# Consecutive non-improving sweeps that declare a phase stalled.
_MARCH_P1_STALL_RUN = 12
_MARCH_P2_STALL_RUN = 25
# A sweep counts as an improvement only if it cuts the residual by at least
# this factor; plain "smaller than before" would never trigger on a slowly
# creeping iterate.
_MARCH_STALL_FACTOR = 0.98


def implicit_permeation_cell(F, qa, pr, c):
    """Implicit local permeation step for ONE cell (shared by the partial-pressure
    and fugacity marching solvers).

    Solves, for the cell's membrane transfer M (per component):

        M_i = qa_i * ( pr_i * (F_i - M_i)/S  -  c_i ),    S = sum_j (F_j - M_j)

    where the flux is written at the DOWNSTREAM retentate composition
    x_R,i = (F_i - M_i)/S, exactly as in `residuals`. F is the retentate entering
    the cell.

    Parameters
    ----------
    F  : (nc,) retentate molar flow entering the cell [mol/s]
    qa : (nc,) permeance * segment area, Q_i * A_k
    pr : scalar OR (nc,) retentate-side driving coefficient.
         - partial-pressure model : pr = P_R,k            (scalar, phi = 1)
         - fugacity model         : pr_i = phi_R,k,i * P_R,k   (per component)
    c  : (nc,) frozen permeate-side term.
         - partial-pressure model : c_i = P_P,k-1 * x_P,k-1,i
         - fugacity model         : c_i = phi_P,k-1,i * P_P,k-1 * x_P,k-1,i
         (i.e. c is simply the permeate-side fugacity/partial pressure.)

    Given S, each component has the closed form

        M_i(S) = qa_i * (pr_i*F_i - c_i*S) / (S + qa_i*pr_i)

    and S solves the scalar equation  S + sum_i M_i(S) = sum_i F_i, found
    robustly by bracketing + brentq. Solving the cell implicitly is what makes
    the march unconditionally stable: the large gain Q*A*P_R is absorbed inside
    the cell instead of being propagated by the outer iteration.

    Structural properties (no projections, no sign constraints):
      - M_i < F_i strictly  -> the downstream retentate stays positive;
      - M_i may be negative -> counter-permeation is allowed naturally.
    """
    SF = F.sum()
    if SF < 1e-30:
        return np.zeros_like(F)

    # NOTE: a safeguarded Newton with the closed-form derivative
    #   g'(S) = -1 + sum_i qa_i*pr_i*(F_i + qa_i*c_i) / (S + qa_i*pr_i)^2
    # was tried here on the assumption that brentq needs ~50 evaluations per
    # cell. It does not -- Brent's method is superlinear and converges in far
    # fewer, and Newton costs two Python/NumPy callbacks per iteration instead of
    # one. Measured consistently SLOWER (5.5 s -> 7.9 s on a marching-dominated
    # candidate). Do not re-add it without measuring.
    def g(S):
        return SF - S - (qa * (pr * F - c * S) / (S + qa * pr)).sum()

    lo, hi = max(1e-14 * SF, 1e-290), SF
    glo, ghi = g(lo), g(hi)
    if glo > 0 and ghi <= 0:
        S = brentq(g, lo, hi, xtol=1e-300, rtol=8.9e-16)
    elif glo <= 0 and ghi <= 0:
        Ss = np.geomspace(lo, hi, 80)
        gs = [g(S) for S in Ss]
        idx = [i for i in range(len(Ss) - 1) if gs[i] * gs[i + 1] < 0]
        S = brentq(g, Ss[idx[0]], Ss[idx[0] + 1], xtol=1e-300, rtol=8.9e-16) if idx else lo
    else:
        S = hi
    return qa * (pr * F - c * S) / (S + qa * pr)


class MassBalanceWithoutPressureDropHFM:
    """
    Mass balance without pressure drop of the hollow fiber module.
    """

    def __init__(self, geometry, properties, R, T, Permeance, n_comp, FFeed, PFeed, PPerm, PRetCell, PPermCell):
        self.geom = geometry
        self.props = properties
        self.R = R
        self.T = T
        self.Permeance = Permeance
        self.nc = n_comp
        self.FFeed = FFeed
        self.PFeed = PFeed
        self.PPerm = PPerm
        self.PRetCell = np.asarray(PRetCell)
        self.PPermCell = np.asarray(PPermCell)
        self.eps = 1e-12

        self.scale_comp = np.maximum(self.FFeed, self.eps)


    def residuals(self, x):
        # least_squares has no callback; the budget is enforced here,
        # which every trust-region step must pass through.
        _deadline_check()
        NCells = self.geom.NCells
        nc = self.nc
        dz = self.geom.dz
        AREA = self.geom.AREA_SEG
        width = 2 * nc

        X = x.reshape((NCells + 1, width))
        FRet_Comp = X[:, :nc]
        FPerm_Comp = X[:, nc:2 * nc]

        eps = self.eps
        scale_comp = self.scale_comp
        
        SumFRet_Comp = FRet_Comp.sum(axis=1)
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)

        invSumFRet_Comp = 1.0 / np.maximum(SumFRet_Comp, eps)
        invSumFPerm_Comp = 1.0 / np.maximum(SumFPerm_Comp, eps)

        nR = nc + nc + NCells * (2 * nc)
        Res_Vec = np.zeros(nR)
        FMemb_saved = np.zeros((NCells + 1, nc))

        i = 0

        # ===============================
        # Boundary conditions
        # ===============================
        Res_Vec[i:i+nc] = (FRet_Comp[0] - self.FFeed) / scale_comp
        i += nc

        Res_Vec[i:i+nc] = (FPerm_Comp[NCells]) / scale_comp
        i += nc

        # ===============================
        # Axial discretization loop
        # ===============================
        for k in range(1, NCells + 1):
            km = k - 1

            ZRet_k = FRet_Comp[k] * invSumFRet_Comp[k]
            ZRet_km = FRet_Comp[km] * invSumFRet_Comp[km]
            ZPerm_k = FPerm_Comp[k] * invSumFPerm_Comp[k]
            ZPerm_km = FPerm_Comp[km] * invSumFPerm_Comp[km]

            if k == NCells:
                ZPerm_k[:] = 0.0  

            # Fuerza motriz 
            FMemb = self.Permeance * AREA[km] * (self.PRetCell[k] * ZRet_k - self.PPermCell[km] * ZPerm_km)

            # Retentate mass balance
            Res_Vec[i:i+nc] = (FRet_Comp[k] - FRet_Comp[km] + FMemb) / scale_comp
            i += nc
            FMemb_saved[k, :] = FMemb

            # Permeate mass balance
            if k < NCells:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FPerm_Comp[k] - FMemb) / scale_comp
            else:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FMemb) / scale_comp
            i += nc

        self.last_FMemb = FMemb_saved
        return Res_Vec

    def build_jac_sparsity(self):
        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc
        nvar = (NCells + 1) * width
        neq = nc + nc + NCells * (2 * nc)
        
        Spa_Mat = lil_matrix((neq, nvar), dtype=int)
        row = 0
        
        # BC 1: Feed
        for j in range(nc):
            Spa_Mat[row, j] = 1
            row += 1
        
        # BC 2: Permeate end
        baseN = NCells * width
        for j in range(nc):
            Spa_Mat[row, baseN + nc + j] = 1
            row += 1
        
        # Interior
        for k in range(1, NCells + 1):
            km = k - 1
            base_k = k * width
            base_km = km * width
            
            for _ in range(nc):
                # Retentate balance dependencies
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_km:base_km + nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2*nc] = 1
                row += 1
            
                # Permeate balance dependencies
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2*nc] = 1
                if k < NCells:
                    Spa_Mat[row, base_k + nc:base_k + 2*nc] = 1
                row += 1
            
        return Spa_Mat.tocsr()

    def jacobian(self, x):
        NCells = self.geom.NCells
        nc = self.nc
        AREA = self.geom.AREA_SEG
        width = 2 * nc
        eps = 1e-12

        X = x.reshape((NCells + 1, width))
        FRet_Comp = X[:, :nc]
        FPerm_Comp = X[:, nc:2*nc]

        # CAMBIO 2 y 3: Usar escala constante y las presiones del objeto
        scale_comp = self.scale_comp
        PRetCell = self.PRetCell
        PPermCell = self.PPermCell

        SumFRet_Comp = FRet_Comp.sum(axis=1)
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)
        SumFRet_safe = np.maximum(SumFRet_Comp, eps)
        SumFPerm_safe = np.maximum(SumFPerm_Comp, eps)

        neq = nc + nc + NCells * (2 * nc)
        nvar = (NCells + 1) * width
        
        J = lil_matrix((neq, nvar), dtype=float)
        I_nc = np.eye(nc)
        row = 0

        # Boundary conditions
        for j in range(nc):
            J[row + j, j] = 1.0 / scale_comp[j]
        row += nc
        
        baseN = NCells * width
        for j in range(nc):
            J[row + j, baseN + nc + j] = 1.0 / scale_comp[j]
        row += nc

        # Axial discretization loop
        for k in range(1, NCells + 1):
            km = k - 1
            base_k = k * width
            base_km = km * width

            zR = FRet_Comp[k] / SumFRet_safe[k]
            zP = FPerm_Comp[km] / SumFPerm_safe[km]

            M = self.Permeance * AREA[km]

            dZRet_dFRet = (I_nc - zR[:, None]) / SumFRet_safe[k]
            dZPerm_dFPermPrev = (I_nc - zP[:, None]) / SumFPerm_safe[km]

            dFMemb_dFRet = (M[:, None] * PRetCell[k]) * dZRet_dFRet
            dFMemb_dFPermPrev = -(M[:, None] * PPermCell[km]) * dZPerm_dFPermPrev

            # Retentate mass balance
            rows = slice(row, row + nc)
            J[rows, base_k:base_k + nc] = (I_nc + dFMemb_dFRet) / scale_comp[:, None]
            J[rows, base_km:base_km + nc] = (-I_nc) / scale_comp[:, None]
            J[rows, base_km + nc:base_km + 2*nc] = dFMemb_dFPermPrev / scale_comp[:, None]
            row += nc

            # Permeate mass balance
            rows = slice(row, row + nc)
            J[rows, base_k:base_k + nc] = (-dFMemb_dFRet) / scale_comp[:, None]
            J[rows, base_km + nc:base_km + 2*nc] = (I_nc - dFMemb_dFPermPrev) / scale_comp[:, None]
            
            if k < NCells:
                J[rows, base_k + nc:base_k + 2*nc] = (-I_nc) / scale_comp[:, None]
            row += nc

        return J.tocsr()
    
    def initial_guess(self,F_guess_from_other_result,G_guess_from_other_result):
        # ------------------------------------------------
        # Initial guess
        # Chute inicial
        # ------------------------------------------------
        NCells = self.geom.NCells
        n_comp = self.nc

        F_guess = np.abs(F_guess_from_other_result)
        G_guess = np.abs(G_guess_from_other_result)

        width = 2 * n_comp
        x0 = np.zeros((NCells + 1) * width)
        for i in range(NCells + 1):
            idx = i * width
            x0[idx:idx+n_comp] = F_guess[i]           # FRet
            x0[idx+n_comp:idx+2*n_comp] = G_guess[i]      # FPerm 

        return x0

    def has_pressure_drop(self):
        return False

    def has_fugacity(self):
        return False

    # ------------------------------------------------------------------
    # FAST PATH: fixed-point (successive substitution) reusing the cached
    # linear operator from the fugacity model. The partial-pressure flux
    # is nonlinear only through composition; freezing composition makes
    # the balance linear (same operator A), so each sweep is one cached
    # LU back-substitution instead of a trust-region least-squares step.
    # ------------------------------------------------------------------
    def solve_partial_pressure_fast(self, x0, tol=None, maxit=400):
        from .Mass_Balance_With_Fugacity_HFM import _build_linear_operator, _LU_CACHE
        from scipy.sparse.linalg import splu

        # Convergence tolerance for this inner fixed point. It is an ABSOLUTE
        # error on component flows [mol/s], and it comes from the caller via
        # `inner_tol`, which the simulator derives from `iteration_tolerance`
        # (scaled by the total feed flow) -- there is no independent tolerance
        # for this solver.
        #
        # When this balance sits inside the Branch-2 outer Picard loop
        # (pressure <-> flow), the caller additionally RELAXES `inner_tol` while
        # the outer error is still large: converging the inner fixed point
        # tightly is wasted work there, because the outer loop damps the result
        # by alpha and re-solves anyway. `inner_tol` is tightened as the outer
        # error falls, so the scheme is asymptotically exact.
        if tol is None:
            tol = getattr(self, "inner_tol", None)
            if tol is None:
                # No caller-supplied tolerance (direct/standalone use).
                tol = 1e-8 * max(float(np.sum(self.FFeed)), 1.0)

        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc
        AREA = self.geom.AREA_SEG
        PR = np.asarray(self.PRetCell, dtype=float)
        PP = np.asarray(self.PPermCell, dtype=float)

        key = (NCells, nc)
        lu = _LU_CACHE.get(key)
        if lu is None:
            lu = splu(_build_linear_operator(NCells, nc))
            _LU_CACHE[key] = lu

        X = np.array(x0, dtype=float).reshape((NCells + 1, width))
        FR = np.maximum(X[:, :nc], 0.0).copy()
        FP = np.maximum(X[:, nc:2 * nc], 0.0).copy()

        nvar = (NCells + 1) * width
        eps = 1e-300
        FMemb = np.zeros((NCells, nc))

        # Adaptive damping (pure substitution diverges; mirror the proven
        # fugacity-loop strategy). Nonnegativity projection + NaN guard keep
        # transient overshoots from blowing up.
        # The damping is bounded above by a RATCHET (`damp_max`). The plain
        # up/down schedule (x1.1 on success, x0.5 on failure) limit-cycles on
        # candidates whose driving force reverses locally (narrow permeate bore
        # -> permeate pressure climbing toward the retentate pressure): the
        # nonnegativity projection fights the update, the error rises, damping is
        # cut, the error then falls steadily -- and the x1.1 growth immediately
        # breaks it again. Observed: err 1.09 -> 0.42 -> 0.24 -> 0.11 -> 0.75.
        # Every time the error rises, the ceiling itself is lowered, so damping
        # can never return to a value already known to diverge; recovery is also
        # slower (x1.05) than the cut (x0.5). This converts a solve that fell
        # back to least_squares (~36 s per call) into a normal inner solve.
        # Once the ratchet has pinned damping near its floor the contraction per
        # sweep is only ~0.98, so a solve that genuinely converges needs several
        # hundred sweeps instead of ~16, overruns maxit, and FAILS -- which is
        # expensive, because it drops the caller into the least_squares fallback
        # (~36 s) and kicks the outer loop out of convergence.
        #
        # So the ceiling is allowed to recover, but only on evidence that the
        # iteration is genuinely descending rather than cycling. The two regimes
        # are cleanly separated by the length of the improving run:
        #   * limit cycle (pressure-infeasible candidates): the error alternates
        #     up/down every 1-2 sweeps;
        #   * heavily damped but converging: runs of 100-250 improving sweeps.
        # Requiring a long unbroken run before lifting the ceiling therefore
        # helps the second case without reopening the first.
        # Simply lifting the ceiling after ~10 good sweeps is NOT enough
        # separation (it restarts the limit cycle: 5.6 s -> does not finish), and
        # neither is spending the budget in units of accumulated damping instead
        # of sweeps (29007 fixed, but the infeasible candidate went 5.6 -> 29 s).
        damping = 0.5
        damp_max = 0.7
        good = 0
        err_prev = np.inf
        converged = False
        for _it in range(maxit):
            _deadline_check()   # per-candidate wall-clock budget
            if not (np.all(np.isfinite(FR)) and np.all(np.isfinite(FP))):
                break  # diverged -> caller falls back to least squares
            sumR = np.maximum(FR.sum(axis=1), eps)
            sumP = np.maximum(FP.sum(axis=1), eps)
            xR = FR / sumR[:, None]
            xP = FP / sumP[:, None]
            FMemb = self.Permeance * AREA[:, None] * (
                PR[1:NCells + 1, None] * xR[1:NCells + 1]
                - PP[0:NCells, None] * xP[0:NCells]
            )

            b = np.zeros(nvar)
            b[:nc] = self.FFeed                              # node-0 retentate BC
            # b[nc:2nc] = 0                                    # node-0 permeate BC
            fm = FMemb.ravel()                               # (NCells*nc,)
            b[2 * nc:2 * nc + NCells * nc] = -fm             # retentate source terms
            b[2 * nc + NCells * nc:] = fm                    # permeate source terms

            xnew = lu.solve(b).reshape((NCells + 1, width))
            FRn = xnew[:, :nc]
            FPn = xnew[:, nc:2 * nc]
            if not (np.all(np.isfinite(FRn)) and np.all(np.isfinite(FPn))):
                break
            err = max(np.max(np.abs(FRn - FR)), np.max(np.abs(FPn - FP)))

            if not _DAMP_RATCHET:                    # original schedule (A/B only)
                damping = (min(damping * 1.1, 0.7) if err < err_prev
                           else max(damping * 0.5, 0.05))
            elif err < err_prev:
                damping = min(damping * 1.05, damp_max)
                good += 1
                if good >= _DAMP_CEILING_RECOVERY_RUN:  # unbroken descent -> lift
                    damp_max = min(damp_max * 1.2, 0.7)
                    good = 0
            else:
                damping = max(damping * 0.5, 0.02)
                damp_max = max(damping, 0.02)   # ratchet the ceiling down
                good = 0
            err_prev = err

            FR = np.maximum((1.0 - damping) * FR + damping * FRn, 0.0)
            FP = np.maximum((1.0 - damping) * FP + damping * FPn, 0.0)
            if err < tol:
                converged = True
                break

        if not converged:
            raise RuntimeError("partial-pressure fixed point did not converge")

        sol = np.zeros((NCells + 1, width))
        sol[:, :nc] = FR
        sol[:, nc:2 * nc] = FP
        x = sol.reshape(-1)

        FMemb_saved = np.zeros((NCells + 1, nc))
        FMemb_saved[1:NCells + 1, :] = FMemb
        self.last_FMemb = FMemb_saved
        return x, FR, FP

    # ------------------------------------------------------------------
    # Marching fast path (robust for extreme permeance / oversized modules)
    # ------------------------------------------------------------------
    @staticmethod
    def _implicit_permeation_cell(F, qa, pr, c):
        """Thin wrapper kept for backwards compatibility; see the module-level
        `implicit_permeation_cell`."""
        return implicit_permeation_cell(F, qa, pr, c)

    def solve_marching_fast(self, x0=None, tol=None, it_phase1=120, it_phase2=400,
                            res_accept=1e-6):
        """Countercurrent solve by outer iteration on the PERMEATE COMPOSITION
        profile with an unconditionally stable implicit forward march.

        Motivation: the damped substitution fast path loses contraction at
        extreme permeance regardless of mesh size, because the module-level
        Courant number (Q*A_total*P_R/F) is mesh-independent. Here the strong
        gain (Q*A*P_R*x_R) is absorbed INSIDE the implicit march (stable per
        cell), and the outer loop carries only the weak permeate-composition
        coupling, whose gain ~ P_P/P_R << 1 -- so it contracts regardless of
        permeance.

        Oversized modules develop a permeate DEAD ZONE near the closed end
        (everything permeable already transferred): there FP = 0 and the flux
        equation is released by complementarity (bound active), which is
        detected and enforced via the stagnation index kstag. Phase 1 iterates
        with kstag free; phase 2 freezes kstag and applies Anderson
        acceleration on the active-zone permeate composition.

        Mass balance closes EXACTLY by construction (flows reconstructed by
        cumulative sums of M). Counter-permeation is allowed (no sign
        constraints). Raises RuntimeError if the active-zone flux residual does
        not reach `res_accept` (caller falls back to least squares).
        """
        # Tolerance on |G - u| for the Anderson phase. This is a COMPOSITION
        # residual (dimensionless), so it comes from `march_tol`, which the
        # simulator derives straight from `iteration_tolerance`. It must NOT be
        # taken from `inner_tol`: that one is an absolute flow in mol/s.
        # The 1e-11 fallback is the historical default, for standalone use with
        # no simulator to supply a tolerance.
        if tol is None:
            tol = getattr(self, "march_tol", None)
            if tol is None:
                tol = 1e-11

        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc
        AREA = np.asarray(self.geom.AREA_SEG, dtype=float)
        PR = np.asarray(self.PRetCell, dtype=float)
        PP = np.asarray(self.PPermCell, dtype=float)
        FFeed = np.asarray(self.FFeed, dtype=float)
        eps = 1e-300

        def march(xP, kstag):
            M = np.zeros((NCells, nc))
            F = FFeed.copy()
            for k in range(kstag):
                M[k] = self._implicit_permeation_cell(
                    F, self.Permeance * AREA[k], PR[k + 1], PP[k] * xP[k])
                F = F - M[k]
            FP = np.empty((NCells + 1, nc))
            FP[NCells] = 0.0
            FP[:-1] = np.cumsum(M[::-1], axis=0)[::-1]
            return M, FP

        # Phase 1: free stagnation index
        xP = np.tile(FFeed / max(FFeed.sum(), eps), (NCells, 1))
        kstag = NCells
        alpha = 0.6
        best_dx = np.inf     # smallest update seen so far
        stall_p1 = 0         # consecutive sweeps without a real improvement
        kstag_run = 0        # consecutive sweeps with an unchanged kstag
        kstag_prev = -1
        for it1 in range(it_phase1):
            _deadline_check()   # per-candidate wall-clock budget
            M, FP = march(xP, kstag)
            FPt = FP.sum(1)
            neg = np.where(FPt[:NCells] <= eps)[0]
            kstag = int(neg.min()) if len(neg) > 0 else NCells
            FPp = np.maximum(FP, 0.0)
            xPn = xP.copy()
            if kstag > 0:
                xPn[:kstag] = FPp[0:kstag] / np.maximum(FPp[0:kstag].sum(1), eps)[:, None]
            if kstag < NCells:
                xPn[kstag:] = xPn[max(kstag - 1, 0)]
            dx = float(np.max(np.abs(xPn - xP)))
            kstag_run = kstag_run + 1 if kstag == kstag_prev else 0
            kstag_prev = kstag
            if dx < _MARCH_STALL_FACTOR * best_dx:
                best_dx = dx
                stall_p1 = 0
            else:
                stall_p1 += 1
            xP = (1.0 - alpha) * xP + alpha * xPn
            # Leave as soon as the sweep is either converged (with a settled
            # stagnation index, which phase 2 is about to freeze) or provably
            # not contracting -- in the latter case Anderson, not Picard, is
            # the tool that will move this iterate.
            if (_MARCH_EARLY_EXIT and it1 + 1 >= _MARCH_P1_MIN_IT
                    and ((kstag_run >= _MARCH_P1_KSTAG_STABLE
                          and dx < _MARCH_P1_DX_TOL)
                         or stall_p1 >= _MARCH_P1_STALL_RUN)):
                p1_exit = ("converged" if dx < _MARCH_P1_DX_TOL else "stalled")
                break
        else:
            p1_exit = "exhausted"

        # Phase 2: frozen kstag + Anderson acceleration on active xP
        ka = max(kstag, 1)
        u = xP[:ka].ravel().copy()
        Fs, Gs = [], []
        m_and, reg = 8, 1e-12
        best_f = np.inf      # smallest residual seen so far
        best_u = u.copy()    # and the iterate that produced it
        stall_p2 = 0
        for _ in range(it_phase2):
            _deadline_check()   # per-candidate wall-clock budget
            xPfull = xP.copy()
            xPfull[:ka] = u.reshape(ka, nc)
            M, FP = march(xPfull, ka)
            FPp = np.maximum(FP, 0.0)
            G = (FPp[0:ka] / np.maximum(FPp[0:ka].sum(1), eps)[:, None]).ravel()
            f = G - u
            fn = float(np.max(np.abs(f)))
            if fn < best_f:
                best_u = G.copy()
            if fn < _MARCH_STALL_FACTOR * best_f:
                best_f = fn
                stall_p2 = 0
            else:
                stall_p2 += 1
            if fn < tol:
                u = G
                p2_exit = "converged"
                break
            # Anderson can plateau above tol. Once it has stopped improving,
            # further sweeps only cost time: return the best iterate found and
            # let the residual acceptance test below decide whether it is good
            # enough.
            if _MARCH_EARLY_EXIT and stall_p2 >= _MARCH_P2_STALL_RUN:
                u = best_u
                p2_exit = "stalled"
                break
            Fs.append(f.copy()); Gs.append(G.copy())
            if len(Fs) > m_and:
                Fs.pop(0); Gs.pop(0)
            kk = len(Fs)
            if kk >= 2:
                dF = np.column_stack([Fs[i + 1] - Fs[i] for i in range(kk - 1)])
                dG = np.column_stack([Gs[i + 1] - Gs[i] for i in range(kk - 1)])
                try:
                    gam = np.linalg.solve(dF.T @ dF + reg * np.eye(kk - 1), dF.T @ f)
                    un = G - dG @ gam
                except np.linalg.LinAlgError:
                    un = G
            else:
                un = G
            u = np.clip(0.3 * u + 0.7 * un, 0.0, None)
        else:
            p2_exit = "exhausted"
        # Exit diagnostics for this solve. The marching solver used to be
        # completely opaque: nobody could tell whether a phase had converged,
        # plateaued or simply run out of iterations, which is precisely how a
        # phase-1 loop with no convergence test at all, and a phase-2 loop
        # exhausting 400 iterations on a plateau, both survived several reviews.
        # The solver layer copies this into the returned `info`, so it reaches
        # `results.solver_paths`.
        self.last_march_exit = {
            "phase1": p1_exit, "phase1_iters": it1 + 1, "phase1_dx": best_dx,
            "phase2": p2_exit, "phase2_res": best_f, "tol": tol,
        }
        xP[:ka] = u.reshape(ka, nc)
        M, FP = march(xP, ka)

        # Reconstruct flows and check the flux residual on ACTIVE cells only
        # (dead-zone cells have the equation released by complementarity).
        FR = np.empty((NCells + 1, nc))
        FR[0] = FFeed
        FR[1:] = FFeed - np.cumsum(M, axis=0)
        FRp = np.maximum(FR, 0.0)
        FPp = np.maximum(FP, 0.0)
        xR = FRp / np.maximum(FRp.sum(1), eps)[:, None]
        xPc = FPp / np.maximum(FPp.sum(1), eps)[:, None]
        Mm = self.Permeance * AREA[:, None] * (
            PR[1:NCells + 1, None] * xR[1:NCells + 1]
            - PP[0:NCells, None] * xPc[0:NCells])
        res_act = 0.0
        if ka > 0:
            res_act = float(np.max(np.abs(M[:ka] - Mm[:ka])) / max(FFeed.max(), 1e-30))
        if not np.isfinite(res_act) or res_act > res_accept:
            raise RuntimeError(
                f"marching fast path residual {res_act:.2e} above acceptance "
                f"{res_accept:.0e}")

        sol = np.zeros((NCells + 1, width))
        sol[:, :nc] = FR
        sol[:, nc:2 * nc] = FP
        x = sol.reshape(-1)
        FMemb_saved = np.zeros((NCells + 1, nc))
        FMemb_saved[1:NCells + 1, :] = M
        self.last_FMemb = FMemb_saved
        return x, FR, FP