#region Title: MassBalanceSolverHFM
# Nature: Solver of equations
# Methodology: Uses least_squares library to minimize mass balance residuals of HFM models 
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2025    Diego Gabriel Oliva            Commented
#  0.0       13-May-2025    Diego Gabriel Oliva            Only one mass balance
##################################################################################################################
#endregion



# Import NumPy for numerical operations
# Importa NumPy para operações numéricas
import numpy as np
from ..Simulation_Deadline import SimulationTimeout

# Import nonlinear least squares solver from SciPy
# Importa o solver de mínimos quadrados não lineares do SciPy
from scipy.optimize import least_squares

# Import time module to measure computation time
# Importa o módulo time para medir o tempo de computação
import time

class MassBalanceSolverHFM:
    """
    Numerical solver for the HFM model.

    SINGLE RESPONSIBILITY:
    - assemble the initial vector
    - call least_squares
    - return the solution
    """
    """
    Solver numérico para o modelo HFM.

    RESPONSABILIDADE ÚNICA:
    - montar o vetor inicial
    - chamar least_squares
    - retornar a solução
    """

    def __init__(self, MassBalance):
        """
        Numerical solver for the HFM model.

        Parameters
        ----------
        MassBalance : Hollow Fiber Mass Balance
            Physical model (defines residuals)
        """
        """
        Solver numérico para o modelo HFM.

        Parameters
        ----------
        MassBalance : Hollow Fiber Module Mass Balance
            Modelo físico (define os resíduos)
        """

        # Store reference to the physical module model
        # Armazena a referência ao modelo físico do módulo
        self.MassBalance = MassBalance



    def _bounds(self):
        """Physical bounds for component molar flows.
        A component flow in either side of a single module cannot be negative and
        cannot exceed the corresponding component feed flow. The previous version
        used total feed as the upper bound for every component, which allowed, for
        example, CH4 permeate > CH4 feed in high-permeance cases.
        """

        mb = self.MassBalance
        N = mb.geom.NCells
        nc = mb.nc
        ub_node = np.concatenate([mb.FFeed, mb.FFeed])
        lb_node = np.zeros(2 * nc)
        lower = np.tile(lb_node, N + 1)
        upper = np.tile(ub_node, N + 1)
        # Avoid zero-width bounds if a trace component is exactly zero in the feed.
        upper = np.maximum(upper, 1e-300) * (1.0 + 1e-9)

        return lower, upper
    def _estimate_membrane_courant(self):
        """A-priori estimate of the maximum membrane Courant number, computed
        WITHOUT simulating. It is the ratio, per component, between the molar
        flow that can permeate through a single axial segment (at the strongest
        driving force: retentate at feed pressure, permeate at rho = 0) and the
        axial molar flow of that component entering the module.

            Co_i = Q_i * A_seg * (P_R * x_feed,i) / F_feed,i

        Co << 1 means each cell removes only a small fraction of the local axial
        flow -> the first-order upwind mesh resolves the profile well. Co >> 1
        means a single cell would remove more than the axial flow carries, so the
        discretization is too coarse and the fixed-point / direct solve become
        ill-conditioned. Returns max_i Co_i (the worst component, normally the
        most permeable one). Returns 0.0 if the estimate cannot be formed.
        """
        try:
            mb = self.MassBalance
            Q = np.asarray(mb.Permeance, dtype=float)
            FFeed = np.asarray(mb.FFeed, dtype=float)
            PR = float(np.asarray(mb.PRetCell)[0]) if np.size(mb.PRetCell) else float(mb.PFeed)
            A_seg = float(mb.geom.AREA_SEG)
            # Per-component permeation capacity of one segment vs axial feed flow.
            # x_feed,i is embedded in FFeed already (F_feed,i = F_total * x_feed,i),
            # and the driving partial pressure uses that same mole fraction:
            # P_R * x_feed,i = P_R * F_feed,i / sum(F_feed).
            Ftot = max(float(np.sum(FFeed)), 1e-300)
            xfeed = FFeed / Ftot
            perm_seg = Q * A_seg * (PR * xfeed)          # mol/s permeating in one segment
            axial = np.maximum(FFeed, 1e-300)            # mol/s entering axially
            return float(np.max(perm_seg / axial))
        except Exception:
            return 0.0

    def _mass_balance_imbalance(self, x):
        """Return the maximum per-component relative global mass imbalance of a
        candidate solution: max_i |FFeed_i - FRet[N,i] - FPerm[0,i]| / |FFeed_i|.

        A high-Courant candidate can make least_squares report success at a point
        where the scaled permeation residuals are small but the global component
        balance is badly violated. This scalar is used both to trigger the
        homotopy fallback and to decide which solution (direct vs homotopy)
        conserves mass better.
        """
        nc = self.MassBalance.nc
        NCells = self.MassBalance.geom.NCells
        sol = np.asarray(x, dtype=float).reshape((NCells + 1, 2 * nc))
        FRet = sol[:, :nc]
        FPerm = sol[:, nc:2 * nc]
        FFeed = np.asarray(self.MassBalance.FFeed, dtype=float)
        imbalance = FFeed - FRet[NCells, :] - FPerm[0, :]
        scale = np.maximum(np.abs(FFeed), 1e-30)
        return float(np.max(np.abs(imbalance) / scale))

    def _run_least_squares(self, x0, Jac_fun, Spa_Mat, lower_bounds, upper_bounds,
                           tol, maxfev, verbose):
        """Single trust-region least-squares solve on the current model state
        (whatever self.MassBalance.Permeance is set to). Returns the raw
        OptimizeResult; the caller inspects result.success."""
        return least_squares(
            fun=self.MassBalance.residuals,
            x0=x0,
            jac=Jac_fun,
            bounds=(lower_bounds, upper_bounds),
            jac_sparsity=Spa_Mat,
            method='trf',
            tr_solver='lsmr',
            ftol=tol,
            xtol=tol,
            gtol=tol,
            max_nfev=maxfev,
            x_scale='jac',
            verbose=verbose,
        )

    def _solve_with_permeance_homotopy(self, x0, Jac_fun, Spa_Mat,
                                       lower_bounds, upper_bounds, tol, maxfev, verbose,
                                       lambdas=(0.05, 0.1, 0.2, 0.4, 0.7, 1.0)):
        """Permeance continuation for badly-conditioned (high-Courant) candidates.

        Solves a sequence of problems with permeance lambda*Q for increasing
        lambda, warm-starting each from the previous solution. Small lambda means
        a weakly-permeating membrane (low effective Courant number), which is
        easy to solve; increasing lambda gradually walks the solution to the true
        problem. The permeance is scaled on the model in place and always
        restored, so there is no lasting side effect.

        Returns the OptimizeResult of the final (lambda = 1) solve, or None if any
        continuation step fails (caller then reports non-convergence).
        """
        Q_original = self.MassBalance.Permeance
        x_prev = np.array(x0, dtype=float)
        final_result = None
        try:
            for lam in lambdas:
                self.MassBalance.Permeance = lam * Q_original
                result = self._run_least_squares(
                    x_prev, Jac_fun, Spa_Mat, lower_bounds, upper_bounds,
                    tol, maxfev, verbose=0)
                if not result.success:
                    # A continuation step failed: abandon homotopy. The caller
                    # will surface non-convergence for this candidate.
                    return None
                x_prev = result.x
                final_result = result
        finally:
            # Always restore the true permeance, even if a step raised.
            self.MassBalance.Permeance = Q_original

        if verbose and final_result is not None:
            print(f"Mass balance converged via permeance homotopy "
                  f"({len(lambdas)} continuation steps).")
        return final_result

    def solve(self, x0, tol=1e-8, maxfev=20000, verbose=2):
        """
        Solves the nonlinear system using least squares
        with positivity constraints.

        Returns
        -------
        sol : ndarray
            Solution vector
        info : dict
            Convergence information
        """
        """
        Resolve o sistema não linear usando mínimos quadrados.

        Returns
        -------
        sol : ndarray
            Vetor solução
        info : dict
            Informações de convergência
        """

        # Record start time of the solver
        # Registra o tempo inicial do solver
        t00 = time.time()

        # ------------------------------------------------------------------
        # FAST PATH: if the model exposes a direct linear solve (constant
        # Jacobian, e.g. frozen-fugacity mass balance), use a single cached
        # LU back-substitution instead of nonlinear least squares.
        # ------------------------------------------------------------------
        if hasattr(self.MassBalance, "solve_linear_fast") and \
                not getattr(self.MassBalance, "force_least_squares", False):
            # Fugacity model. The linear (LU) path freezes the WHOLE fugacity
            # f = phi * x * P, i.e. it freezes the retentate composition x too --
            # which is the strong coupling that makes the OUTER fugacity loop
            # lose contraction on oversized / high-permeance modules. The
            # marching path freezes only phi (weak coupling) and resolves x
            # implicitly inside each cell.
            #
            # The LU path is far cheaper, so it stays the default and normal
            # candidates are untouched. The marching path is used only when the
            # runner has already seen the outer loop fail and re-runs with
            # prefer_marching set. Both share the same fixed point, so a
            # converged result is the same either way.
            if getattr(self.MassBalance, "prefer_marching", False) and \
                    hasattr(self.MassBalance, "solve_marching_fast"):
                try:
                    x, FRet_results, FPerm_results = self.MassBalance.solve_marching_fast()
                    elapsed = time.time() - t00
                    if verbose:
                        print(f"Computation time mass balance (marching, fugacity): {elapsed:.4f} s")
                    return x, FRet_results, FPerm_results, {
                        "iterations": 1,
                        "time": elapsed,
                        "cost": 0.0,
                        "optimality": 0.0,
                    "path": "marching_fugacity",
                    }
                except SimulationTimeout:
                    raise   # control-flow signal: never swallow it
                except Exception:
                    pass  # fall back to the frozen-fugacity linear solve

            x, FRet_results, FPerm_results = self.MassBalance.solve_linear_fast()
            elapsed = time.time() - t00
            if verbose:
                print(f"Computation time mass balance (direct): {elapsed:.4f} s")
            return x, FRet_results, FPerm_results, {
                "iterations": 1,
                "time": elapsed,
                "cost": 0.0,
                "optimality": 0.0,
                    "path": "LU",
            }

        # Fixed-point fast path for the (composition-nonlinear) partial-pressure
        # model. Falls through to least_squares if it fails to converge.
        if hasattr(self.MassBalance, "solve_partial_pressure_fast") and \
                not getattr(self.MassBalance, "prefer_marching", False) and \
                not getattr(self.MassBalance, "force_least_squares", False):
            # 1st fast path: damped successive substitution (LU-cached linear
            # operator). Converges quickly for normal candidates; loses
            # contraction at extreme permeance (module-level Courant number is
            # mesh-independent), in which case it raises and we fall through.
            # Skipped entirely when the runner already knows the Courant number
            # is large (prefer_marching), since it would only waste iterations.
            try:
                x, FRet_results, FPerm_results = self.MassBalance.solve_partial_pressure_fast(x0)
                elapsed = time.time() - t00
                if verbose:
                    print(f"Computation time mass balance (fixed-point): {elapsed:.4f} s")
                return x, FRet_results, FPerm_results, {
                    "iterations": 1,
                    "time": elapsed,
                    "cost": 0.0,
                    "optimality": 0.0,
                    "path": "fixed_point",
                }
            except SimulationTimeout:
                raise   # control-flow signal: never swallow it
            except Exception:
                pass  # fall through to the marching fast path

        if hasattr(self.MassBalance, "solve_marching_fast") and \
                not getattr(self.MassBalance, "force_least_squares", False):
            # 2nd fast path: outer iteration on the permeate composition with an
            # unconditionally stable implicit forward march. Robust at extreme
            # permeance (oversized modules), mass-exact by construction, allows
            # counter-permeation, and handles the permeate dead zone by
            # complementarity. Raises if its active-zone residual is not met.
            try:
                x, FRet_results, FPerm_results = self.MassBalance.solve_marching_fast()
                elapsed = time.time() - t00
                if verbose:
                    print(f"Computation time mass balance (marching): {elapsed:.4f} s")
                return x, FRet_results, FPerm_results, {
                    "iterations": 1,
                    "time": elapsed,
                    "cost": 0.0,
                    "optimality": 0.0,
                    "path": "marching",
                    # How each marching phase actually terminated (converged /
                    # stalled / exhausted). Without this the rung is opaque and
                    # a phase silently burning its whole iteration budget looks
                    # exactly like one that converged on the first sweep.
                    "march_exit": getattr(self.MassBalance, "last_march_exit", None),
                }
            except SimulationTimeout:
                raise   # control-flow signal: never swallow it
            except Exception:
                pass  # fall back to least squares below

        # Build sparsity pattern of the Jacobian matrix
        # Constrói a estrutura esparsa do Jacobiano
        Spa_Mat = self.MassBalance.build_jac_sparsity()
        Jac_fun = self.MassBalance.jacobian if hasattr(self.MassBalance, "jacobian") else '2-point'


        # Define physics limits.
        # Per-component upper bound: a component molar flow in either side of a
        # single module cannot exceed its own feed flow. The previous version
        # used total feed as the bound for every component, allowing e.g.
        # CH4 permeate > CH4 feed in high-permeance cases.
        #
        # A tiny headroom (1 + 1e-9) is added so that an initial guess sitting
        # exactly at FFeed[i] -- which is how the retentate feed node is seeded --
        # stays STRICTLY inside the bounds. Without it, least_squares raises
        # "Initial guess is outside of provided bounds" when x0[i] == ub[i] due
        # to floating-point rounding. The headroom is physically negligible.
        lower_bounds, upper_bounds = self._bounds()
        # Clamp the initial guess strictly inside the bounds. Guesses seeded at
        # FFeed[i] (retentate feed node) or warm-started from a previous
        # candidate can land on or just outside a bound; least_squares requires
        # lb <= x0 <= ub. This is a projection onto the feasible box and does not
        # change the physics -- the solver moves x freely from there.
        x0 = np.clip(np.asarray(x0, dtype=float), lower_bounds, upper_bounds)

        # A-priori Courant estimate decides the strategy WITHOUT simulating.
        # High Courant => the direct solve is expected to be ill-conditioned
        # (fixed-point diverges, least_squares lands on a mass-violating point),
        # so we go STRAIGHT to permeance homotopy and skip the wasted direct
        # attempt. Low Courant => the direct solve is reliable and cheap, so we
        # try it first and only fall back to homotopy if the balance does not
        # close. The threshold is conservative: continuation is only worth its
        # ~6 solves when the single direct solve is genuinely at risk.
        COURANT_HOMOTOPY_THRESHOLD = 1.0
        courant = self._estimate_membrane_courant()

        if courant >= COURANT_HOMOTOPY_THRESHOLD:
            # Go directly to homotopy for this ill-conditioned candidate.
            result = self._solve_with_permeance_homotopy(
                x0, Jac_fun, Spa_Mat, lower_bounds, upper_bounds, tol, maxfev, verbose)
            if result is None:
                # Homotopy could not complete; fall back to a direct attempt so
                # the candidate still gets a result (or a clean failure below).
                result = self._run_least_squares(
                    x0, Jac_fun, Spa_Mat, lower_bounds, upper_bounds, tol, maxfev, verbose)
        else:
            # Low-Courant candidate: direct least squares is reliable here and
            # this path behaves exactly as before (no homotopy overhead).
            result = self._run_least_squares(
                x0, Jac_fun, Spa_Mat, lower_bounds, upper_bounds, tol, maxfev, verbose)

            # Safety net: if the direct solve nonetheless fails to close the
            # global mass balance, attempt homotopy and keep whichever solution
            # conserves mass better.
            direct_imb = self._mass_balance_imbalance(result.x)
            if not result.success or direct_imb > 1e-6:
                homotopy = self._solve_with_permeance_homotopy(
                    x0, Jac_fun, Spa_Mat, lower_bounds, upper_bounds, tol, maxfev, verbose)
                if homotopy is not None:
                    if self._mass_balance_imbalance(homotopy.x) < direct_imb:
                        result = homotopy

        # Compute total elapsed computation time
        # Calcula o tempo total de computação
        elapsed = time.time() - t00

        # Optionally print computation time
        # Opcionalmente imprime o tempo de computação
        if verbose:
            print(f"Computation time mass balance: {elapsed:.2f} s")

        # Check solver convergence
        # Verifica se o solver convergiu
        if not result.success:

            # Raise an error if solver failed
            # Lança erro caso o solver falhe
            raise RuntimeError(
                f"Convergence failure:\n{result.message}"
            )

        # ------------------------------------------------
        # Results depending if has pressure drop
        # ------------------------------------------------
        self.MassBalance.nc
        sol_mat = result.x.reshape((self.MassBalance.geom.NCells+1, self.MassBalance.nc*2))
        # ------------------------------------------------
        # Extract results
        # Extrair resultados
        # ------------------------------------------------
        FRet_results = sol_mat[:, :self.MassBalance.nc]
        FPerm_results = sol_mat[:, self.MassBalance.nc:2*self.MassBalance.nc]

        # Return solution vector and diagnostic information
        # Retorna vetor solução e informações diagnósticas
        return result.x, FRet_results, FPerm_results, {

            # Number of function evaluations
            # Número de avaliações da função
            "iterations": result.nfev,

            # Total computation time
            # Tempo total de computação
            "time": elapsed,

            # Final least squares cost
            # Valor final da função de custo
            "cost": result.cost,

            # Optimality measure (gradient norm)
            # Medida de otimalidade (norma do gradiente)
            "optimality": result.optimality,

            # Which rung of the ladder produced this solution. The fast paths
            # above fail SILENTLY (except: pass) and fall through to here, so
            # without this label there is no way to tell from a result that it
            # came from the expensive last-resort solver -- which is how a
            # wrong-but-plausible answer once propagated into a certified
            # optimum. The simulator copies it to results.solver_paths.
            "path": "least_squares"
        }