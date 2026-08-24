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
from scipy.sparse import lil_matrix, coo_matrix
from scipy.sparse.linalg import splu

from .Mass_Balance_Without_Pressure_Drop_HFM import (
    implicit_permeation_cell,
    # Early-exit guards for the two-phase marching solver. Defined once, in the
    # partial-pressure module, so the two twins cannot drift apart; see the
    # measurements documented alongside them there.
    _MARCH_EARLY_EXIT,
    _MARCH_P1_MIN_IT,
    _MARCH_P1_DX_TOL,
    _MARCH_P1_KSTAG_STABLE,
    _MARCH_P1_STALL_RUN,
    _MARCH_P2_STALL_RUN,
    _MARCH_STALL_FACTOR,
)

# ------------------------------------------------------------------
# Cache of LU factorizations for the (constant) linear mass-balance
# operator. The matrix A only contains +-1 entries determined purely
# by (NCells, nc) -> identical for every candidate with the same
# discretization, so one factorization serves the whole enumeration.
# ------------------------------------------------------------------
_LU_CACHE = {}


def _build_linear_operator(NCells, nc):
    """Assemble the constant linear operator A for the fugacity mass
    balance (FMemb frozen). Returns a CSC matrix. Row ordering:
      [BC feed] [BC permeate end] [retentate interior] [permeate interior]
    Variable layout matches residuals(): x.reshape(NCells+1, 2*nc),
    columns [0:nc]=FRet, [nc:2nc]=FPerm per cell.
    """
    width = 2 * nc
    nvar = (NCells + 1) * width
    rows = []
    cols = []
    vals = []
    r = 0
    # BC 1: FRet[0,i] = FFeed[i]
    for i in range(nc):
        rows.append(r); cols.append(i); vals.append(1.0); r += 1
    # BC 2: FPerm[NCells,i] = 0
    baseN = NCells * width
    for i in range(nc):
        rows.append(r); cols.append(baseN + nc + i); vals.append(1.0); r += 1
    # Retentate interior: FRet[k,i] - FRet[k-1,i] = -FMemb[k,i]
    for k in range(1, NCells + 1):
        for i in range(nc):
            rows.append(r); cols.append(k * width + i); vals.append(1.0)
            rows.append(r); cols.append((k - 1) * width + i); vals.append(-1.0)
            r += 1
    # Permeate interior: FPerm[k-1,i] - FPerm[k,i] = +FMemb[k,i]  (k<NCells)
    #                    FPerm[k-1,i]             = +FMemb[k,i]  (k==NCells)
    for k in range(1, NCells + 1):
        for i in range(nc):
            rows.append(r); cols.append((k - 1) * width + nc + i); vals.append(1.0)
            if k < NCells:
                rows.append(r); cols.append(k * width + nc + i); vals.append(-1.0)
            r += 1
    A = coo_matrix((vals, (rows, cols)), shape=(nvar, nvar)).tocsc()
    return A


class MassBalanceWithFugacityHFM:
    """
    Mass balance without pressure drop of the hollow fiber module.
    """

    def __init__(self, geometry, properties, R, T, Permeance, n_comp, FFeed, PFeed, PPerm,
                 FugacityRetentate, FugacityPermeate,
                 ZRet=None, ZPerm=None, PRetCell=None, PPermCell=None):
        self.geom = geometry
        self.props = properties
        self.R = R
        self.T = T
        self.Permeance = Permeance
        self.nc = n_comp
        self.FFeed = FFeed
        self.PFeed = PFeed
        self.PPerm = PPerm
        self.FugacityRetentate = FugacityRetentate
        self.FugacityPermeate = FugacityPermeate
        # Compositions and pressures that were used to evaluate the fugacities
        # above. They are optional (the linear fast path and the residuals do not
        # need them), but when supplied they let solve_marching_fast recover the
        # fugacity COEFFICIENTS phi = f / (x * P) and thus update the retentate
        # composition implicitly instead of freezing the whole fugacity.
        self.ZRet = ZRet
        self.ZPerm = ZPerm
        self.PRetCell = PRetCell
        self.PPermCell = PPermCell
        # When True, MassBalanceSolverHFM uses solve_marching_fast instead of the
        # (cheaper) frozen-fugacity LU solve. The runner sets this only after the
        # outer fugacity loop has failed to converge, so normal candidates keep
        # the fast LU path with no overhead.
        self.prefer_marching = False
        self.eps = 1e-8
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

        FugacityRet_saved = np.zeros((NCells + 1, nc))

        FugacityPerm_saved = np.zeros((NCells + 1, nc))

        # ===============================
        # Axial discretization loop
        # ===============================
        for k in range(1, NCells + 1):
            km = k - 1

            # Fuerza motriz 
            FMemb = self.Permeance * AREA[km] * (self.FugacityRetentate[k] - self.FugacityPermeate[km])

            # Retentate mass balance
            Res_Vec[i:i+nc] = (FRet_Comp[k] - FRet_Comp[km] + FMemb) / scale_comp
            i += nc
            FMemb_saved[k, :] = FMemb
            FugacityRet_saved[k] = self.FugacityRetentate[k]
            FugacityPerm_saved[km] = self.FugacityPermeate[km]

            # Permeate mass balance
            if k < NCells:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FPerm_Comp[k] - FMemb) / scale_comp
            else:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FMemb) / scale_comp
            i += nc

        self.last_FMemb = FMemb_saved
        self.last_FugacityRet = FugacityRet_saved
        self.last_FugacityPerm = FugacityPerm_saved
        return Res_Vec

    def build_jac_sparsity(self):
        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc
        nvar = (NCells + 1) * width
        neq = nc + nc + NCells * (2 * nc)
        
        Spa_Mat = lil_matrix((neq, nvar), dtype=int)
        row = 0
        
        # BC 1: Feed (Depende solo de FRet[0])
        for j in range(nc):
            Spa_Mat[row, j] = 1
            row += 1
        
        # BC 2: Permeate end (Depende solo de FPerm[NCells])
        baseN = NCells * width
        for j in range(nc):
            Spa_Mat[row, baseN + nc + j] = 1
            row += 1
        
        # Interior
        for k in range(1, NCells + 1):
            km = k - 1
            base_k = k * width
            base_km = km * width
            
            # Ecuación de balance del Retentado
            # CAMBIO: Ya NO depende de FPerm[km] porque FMemb es constante respecto a x
            Spa_Mat[row, base_k:base_k + nc] = 1      # dRes/dFRet[k]
            Spa_Mat[row, base_km:base_km + nc] = 1    # dRes/dFRet[km]
            row += 1
        
            # Ecuación de balance del Permeado
            # CAMBIO: Ya NO depende de FRet[k] porque FMemb es constante respecto a x
            Spa_Mat[row, base_km + nc:base_km + 2*nc] = 1  # dRes/dFPerm[km]
            if k < NCells:
                Spa_Mat[row, base_k + nc:base_k + 2*nc] = 1  # dRes/dFPerm[k]
            row += 1
            
        return Spa_Mat.tocsr()

    def jacobian(self, x):
        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc

        X = x.reshape((NCells + 1, width))
        # Nota: FRet_Comp y FPerm_Comp solo se usan para las derivadas de las identidades,
        # ya no se usan para calcular composiciones (zR, zP) porque la fugacidad es externa.
        
        scale_comp = self.scale_comp
        neq = nc + nc + NCells * (2 * nc)
        nvar = (NCells + 1) * width
        
        J = lil_matrix((neq, nvar), dtype=float)
        I_nc = np.eye(nc)
        row = 0

        # ===============================
        # Boundary conditions
        # ===============================
        # BC 1: Feed
        for j in range(nc):
            J[row + j, j] = 1.0 / scale_comp[j]
        row += nc
        
        # BC 2: Permeate end
        baseN = NCells * width
        for j in range(nc):
            J[row + j, baseN + nc + j] = 1.0 / scale_comp[j]
        row += nc

        # ===============================
        # Axial discretization loop
        # ===============================
        for k in range(1, NCells + 1):
            km = k - 1
            base_k = k * width
            base_km = km * width

            # CAMBIO RADICAL: Las derivadas de FMemb son CERO.
            # El Jacobiano se reduce a simples identidades escaladas.

            # Retentate mass balance
            rows = slice(row, row + nc)
            J[rows, base_k:base_k + nc] = I_nc / scale_comp[:, None]       # dRes/dFRet[k]
            J[rows, base_km:base_km + nc] = -I_nc / scale_comp[:, None]    # dRes/dFRet[km]
            # dRes/dFPerm[km] es 0
            row += nc

            # Permeate mass balance
            rows = slice(row, row + nc)
            # dRes/dFRet[k] es 0
            J[rows, base_km + nc:base_km + 2*nc] = I_nc / scale_comp[:, None]  # dRes/dFPerm[km]
            
            if k < NCells:
                J[rows, base_k + nc:base_k + 2*nc] = -I_nc / scale_comp[:, None] # dRes/dFPerm[k]
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
        return True

    # ------------------------------------------------------------------
    # FAST PATH: direct linear solve (FMemb is frozen -> system is linear)
    # ------------------------------------------------------------------
    def solve_linear_fast(self):
        """Solve the (linear) fugacity mass balance with a single cached
        LU back-substitution instead of nonlinear least squares.

        Returns
        -------
        x : ndarray              flat solution vector
        FRet_results : ndarray   (NCells+1, nc)
        FPerm_results : ndarray  (NCells+1, nc)
        """
        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc
        AREA = self.geom.AREA_SEG

        # Frozen membrane molar flow per segment (k = 1..NCells), per component
        # FMemb[k] = Q * (w*dz) * (f_R,k - f_P,k-1)
        FMemb = (self.Permeance * AREA[:, None]
                 * (self.FugacityRetentate[1:NCells + 1]
                    - self.FugacityPermeate[0:NCells]))  # shape (NCells, nc)

        # Build RHS b in the same row order as _build_linear_operator
        nvar = (NCells + 1) * width
        b = np.zeros(nvar)
        r = 0
        b[r:r + nc] = self.FFeed; r += nc          # BC feed
        b[r:r + nc] = 0.0; r += nc                  # BC permeate end
        # retentate interior rows: RHS = -FMemb
        for k in range(NCells):
            b[r:r + nc] = -FMemb[k]; r += nc
        # permeate interior rows: RHS = +FMemb
        for k in range(NCells):
            b[r:r + nc] = FMemb[k]; r += nc

        # Cached LU factorization (constant operator for given NCells, nc)
        key = (NCells, nc)
        lu = _LU_CACHE.get(key)
        if lu is None:
            lu = splu(_build_linear_operator(NCells, nc))
            _LU_CACHE[key] = lu

        x = lu.solve(b)

        sol_mat = x.reshape((NCells + 1, width))
        FRet_results = sol_mat[:, :nc]
        FPerm_results = sol_mat[:, nc:2 * nc]

        # Recover diagnostics consumed downstream by the runner
        FMemb_saved = np.zeros((NCells + 1, nc))
        FMemb_saved[1:NCells + 1, :] = FMemb
        self.last_FMemb = FMemb_saved
        self.last_FugacityRet = self.FugacityRetentate
        self.last_FugacityPerm = self.FugacityPermeate

        return x, FRet_results, FPerm_results

    # ------------------------------------------------------------------
    # Marching fast path (robust for extreme permeance / oversized modules)
    # ------------------------------------------------------------------
    def _fugacity_coefficients(self):
        """Recover the fugacity COEFFICIENTS phi = f / (x * P) from the frozen
        fugacity arrays and the compositions/pressures they were evaluated at.

        Rationale: the fugacity f = phi * x * P mixes a STRONGLY composition-
        dependent factor (x, which the march must resolve implicitly) with a
        WEAKLY composition-dependent one (phi, safe to freeze across an outer
        iteration). Freezing f wholesale -- as solve_linear_fast does -- freezes
        x too, which is exactly what makes the outer loop diverge at extreme
        permeance. Freezing only phi keeps the nonideality while letting the
        march update x.

        Where a component is essentially absent (x -> 0) phi is ill-conditioned;
        we fall back to phi = 1 there, which is harmless because that component
        carries no flow.

        Returns (phi_ret, phi_perm) with shapes (NCells+1, nc), or None if the
        compositions/pressures were not supplied to the constructor.
        """
        if (self.ZRet is None or self.ZPerm is None
                or self.PRetCell is None or self.PPermCell is None):
            return None
        ZR = np.asarray(self.ZRet, dtype=float)
        ZP = np.asarray(self.ZPerm, dtype=float)
        PR = np.asarray(self.PRetCell, dtype=float)
        PP = np.asarray(self.PPermCell, dtype=float)
        fR = np.asarray(self.FugacityRetentate, dtype=float)
        fP = np.asarray(self.FugacityPermeate, dtype=float)

        x_floor = 1e-12
        denR = ZR * PR[:, None]
        denP = ZP * PP[:, None]
        phiR = np.where(ZR > x_floor, fR / np.maximum(denR, 1e-300), 1.0)
        phiP = np.where(ZP > x_floor, fP / np.maximum(denP, 1e-300), 1.0)
        # Guard against non-physical values from a bad outer guess.
        phiR = np.clip(np.nan_to_num(phiR, nan=1.0, posinf=1.0, neginf=1.0), 1e-6, 10.0)
        phiP = np.clip(np.nan_to_num(phiP, nan=1.0, posinf=1.0, neginf=1.0), 1e-6, 10.0)
        return phiR, phiP

    def solve_marching_fast(self, x0=None, tol=None, it_phase1=120, it_phase2=400,
                            res_accept=1e-6):
        """Countercurrent solve by outer iteration on the PERMEATE COMPOSITION
        profile with an unconditionally stable implicit forward march --
        fugacity version.

        Identical in structure to the partial-pressure marching solver; the only
        change is the driving force. With phi frozen (weak coupling) the cell
        equation is

            M_i = Q_i*A_k * ( phi_R,k,i * P_R,k * x_R,k,i  -  f_P,k-1,i )

        so the shared implicit cell solver is called with a PER-COMPONENT
        retentate coefficient  pr_i = phi_R,k,i * P_R,k  and the permeate term
        c_i = phi_P,k-1,i * P_P,k-1 * x_P,k-1,i  (i.e. the permeate fugacity
        evaluated at the current outer permeate composition).

        Mass closes exactly by construction; counter-permeation stays free (no
        sign constraints); the permeate dead zone of oversized modules is handled
        by complementarity (FP = 0 -> flux equation released).

        Raises RuntimeError if the active-zone residual is not met, or if the
        fugacity coefficients are unavailable (constructor called without
        ZRet/ZPerm/PRetCell/PPermCell), so the caller falls back to
        solve_linear_fast / least squares.
        """
        phis = self._fugacity_coefficients()
        if phis is None:
            raise RuntimeError(
                "marching fast path needs ZRet/ZPerm/PRetCell/PPermCell to recover phi")
        phiR, phiP = phis

        # Tolerance on |G - u| for the Anderson phase -- a COMPOSITION residual
        # (dimensionless), so it comes from `march_tol`, derived by the
        # simulator straight from `iteration_tolerance`. NOT `inner_tol`, which
        # is an absolute flow in mol/s. 1e-11 is the historical default, kept
        # for standalone use with no simulator to supply a tolerance.
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
                # Retentate coefficient is per component: phi_R * P_R.
                pr_vec = phiR[k + 1] * PR[k + 1]
                # Permeate fugacity at the current outer permeate composition.
                c_vec = phiP[k] * PP[k] * xP[k]
                M[k] = implicit_permeation_cell(
                    F, self.Permeance * AREA[k], pr_vec, c_vec)
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

        # Phase 2: frozen kstag + Anderson acceleration on the active permeate xP
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
        # Exit diagnostics for this solve -- see the twin in the
        # partial-pressure module. The solver layer copies this into the
        # returned `info`, so it reaches `results.solver_paths`.
        self.last_march_exit = {
            "phase1": p1_exit, "phase1_iters": it1 + 1, "phase1_dx": best_dx,
            "phase2": p2_exit, "phase2_res": best_f, "tol": tol,
        }
        xP[:ka] = u.reshape(ka, nc)
        M, FP = march(xP, ka)

        # Reconstruct flows; check the flux residual on ACTIVE cells only.
        FR = np.empty((NCells + 1, nc))
        FR[0] = FFeed
        FR[1:] = FFeed - np.cumsum(M, axis=0)
        FRp = np.maximum(FR, 0.0)
        FPp = np.maximum(FP, 0.0)
        xR = FRp / np.maximum(FRp.sum(1), eps)[:, None]
        xPc = FPp / np.maximum(FPp.sum(1), eps)[:, None]
        Mm = self.Permeance * AREA[:, None] * (
            phiR[1:NCells + 1] * PR[1:NCells + 1, None] * xR[1:NCells + 1]
            - phiP[0:NCells] * PP[0:NCells, None] * xPc[0:NCells])
        res_act = 0.0
        if ka > 0:
            res_act = float(np.max(np.abs(M[:ka] - Mm[:ka])) / max(FFeed.max(), 1e-30))
        if not np.isfinite(res_act) or res_act > res_accept:
            raise RuntimeError(
                f"marching fast path (fugacity) residual {res_act:.2e} above "
                f"acceptance {res_accept:.0e}")

        sol = np.zeros((NCells + 1, width))
        sol[:, :nc] = FR
        sol[:, nc:2 * nc] = FP
        x = sol.reshape(-1)
        FMemb_saved = np.zeros((NCells + 1, nc))
        FMemb_saved[1:NCells + 1, :] = M
        self.last_FMemb = FMemb_saved
        # Fugacities consistent with the converged march (consumed downstream).
        self.last_FugacityRet = phiR * PR[:, None] * xR
        self.last_FugacityPerm = phiP * PP[:, None] * xPc
        return x, FR, FP