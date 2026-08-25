#region Title: SimulatorGeometryHFM
# Nature: Geometry definition
# Methodology: Define geometry given by the user
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

import numpy as np


class SimulatorGeometryHFM:
    """
    Geometry of the hollow fiber module.

    PASSIVE Class:
    - only stores geometric data
    - calculates derived quantities
    - does not know physics, solver or properties
    """
    """
    Geometria do módulo de fibras ocas.

    Classe PASSIVA:
    - apenas armazena dados geométricos
    - calcula grandezas derivadas
    - não conhece física, solver ou propriedades
    """

    def __init__(
        self,
        LSingleMembrane,
        DiamShell,
        DiamFiber_o,
        DiamFiber_i,
        NFibers,
        Void_Frac,
        NCells,
        NumberOfMembranesInSerie=1,
        NumberOfTubesInParallel=1,
        cell_sizes=None,

    ):
        """
        Parameters
        ----------
        LSingleMembrane: float
            Length of single membrane [m]
            Comprimento do membrana [m]
        NumberOfMembranesInSerie: float
            Number of membranes in one module
            Número de membranas em um módulo
        LHidraulic : float
            Module length [m]
            Comprimento do módulo [m]
        DiamShell : float
            Shell diameter [m]
            Diâmetro do casco [m]
        DiamFiber_o : float
            Fiber outer diameter [m]
            Diâmetro externo da fibra [m]
        DiamFiber_i : float
            Fiber inner diameter [m]
            Diâmetro interno da fibra [m]
        NFibers : int
            Number of fibers
            Número de fibras
        NCells : int
            Number of FDM segments
            Número de segmentos FDM
        """
        self.LSingleMembrane = LSingleMembrane
        self.NumberOfMembranesInSerie = NumberOfMembranesInSerie
        self.DiamShell = DiamShell
        self.DiamFiber_o = DiamFiber_o
        self.DiamFiber_i = DiamFiber_i
        self.NFibers = NFibers
        self.NCells = NCells
        self.NumberOfMembranesInSerie = NumberOfMembranesInSerie
        self.Void_Frac = Void_Frac
        self.NumberOfTubesInParallel = NumberOfTubesInParallel
        # ===============================
        # Derived quantities
        # Grandezas derivadas
        # ===============================
        self.LHidraulic = self.LSingleMembrane * self.NumberOfMembranesInSerie


        # Axial cell sizes. Uniform by default; a non-uniform vector may be
        # supplied (e.g. a Courant-adaptive mesh with fine cells near the inlet).
        # dz becomes an array of length NCells; dz[i] is the length of segment i
        # (which connects node i to node i+1). AREA_SEG follows per segment.
        if cell_sizes is None:
            self.dz = np.full(self.NCells, self.LHidraulic / self.NCells)
        else:
            cs = np.asarray(cell_sizes, dtype=float)
            if cs.ndim != 1 or cs.size != self.NCells:
                raise ValueError(
                    f"cell_sizes must have length NCells={self.NCells}, got {cs.size}.")
            # Rescale defensively so the mesh closes exactly at LHidraulic.
            self.dz = cs * (self.LHidraulic / np.sum(cs))
        # Scalar fallback (mean cell size) for any legacy consumer.
        # self.dz_scalar = float(self.LHidraulic / self.NCells)##### PROBLEM WITH NEW VERSIONS OF NUMPY #### New versions do not accept this.
            self.dz_scalar = np.asarray(
                self.LHidraulic / self.NCells
            ).item()


        # Node axial positions z_k = sum of dz up to node k (length NCells+1).
        self.z_nodes = np.concatenate([[0.0], np.cumsum(self.dz)])

        if not self.NFibers:
            self.NFibers = (1-self.Void_Frac)*(self.DiamShell*self.DiamShell)/(self.DiamFiber_o*self.DiamFiber_o)

        # Membrane area per unit length
        # Área de membrana por unidade de comprimento
        self.AREA_PER_L = np.pi * self.DiamFiber_o * self.NFibers

        # Membrane area per segment (vector of length NCells)
        # Área de membrana por segmento (vetor de comprimento NCells)
        self.AREA_SEG = self.AREA_PER_L * self.dz


    

def build_courant_adaptive_mesh(L, AREA_PER_L, PFeed, FFeed_total_per_tube, Q,
                                co_target=0.8, N_abs_max=1000, max_frac=0.1):
    """Build a geometric (exponential) axial mesh anchored by two endpoints:

        - first cell  dz_1 = dz1_max   (so first-node Courant = co_target)
        - last cell   dz_N = max_frac * L   (default 10% of L)

    The growth ratio r is NOT a free parameter to be minimized: it is fixed by
    the requirement that the geometric progression carry dz_1 up to dz_N. For a
    geometric mesh dz_i = dz_1 * r**(i-1), the two anchors give

        r**(N-1) = dz_N / dz_1                                   (endpoint ratio)
        dz_1 * (r**N - 1) / (r - 1) = L                          (closure at L)

    which is two equations in (r, N). We sweep N (integer) upward; for each N the
    endpoint ratio fixes r, and we pick the smallest N whose closed length is >= L
    (then rescale to close exactly). N is capped at N_abs_max.

    Special cases:
      - dz1_max >= max_frac*L : the inlet cell is already at/above the cap, so a
        uniform mesh of ceil(1/max_frac) cells is used (no refinement needed).
      - degenerate permeance : a modest uniform mesh is returned.

    Returns cell_sizes (sums to L), length N.
    """
    Q = np.asarray(Q, dtype=float)
    Qmax = float(np.max(Q[np.isfinite(Q)])) if np.any(np.isfinite(Q)) else 0.0

    denom = Qmax * AREA_PER_L * PFeed
    if denom <= 0.0 or FFeed_total_per_tube <= 0.0:
        n = max(2, min(N_abs_max, 20))
        return np.full(n, L / n)

    dz1 = co_target * FFeed_total_per_tube / denom
    dzN = max_frac * L

    # Inlet cell already coarse enough: uniform mesh, no refinement.
    if dz1 >= dzN:
        n = max(2, int(np.ceil(1.0 / max_frac)))
        n = min(n, N_abs_max)
        return np.full(n, L / n)

    def closed_length(N):
        """For a given integer N, r is fixed by dz1*r**(N-1) = dzN. Return the
        geometric-sum length and the ratio r."""
        if N == 1:
            return dz1, 1.0
        r = (dzN / dz1) ** (1.0 / (N - 1))
        if abs(r - 1.0) < 1e-15:
            return dz1 * N, 1.0
        return dz1 * (r ** N - 1.0) / (r - 1.0), r

    # Sweep N upward: length grows with N. Find the smallest N with length >= L.
    # Lower bound: at least enough cells that the endpoint ratio is >= 1
    # (dzN >= dz1 guaranteed above, so r >= 1 for all N >= 2).
    N_sel, r_sel = None, None
    N_hi = min(N_abs_max, 200000)
    for N in range(2, N_hi + 1):
        length, r = closed_length(N)
        if length >= L - 1e-15:
            N_sel, r_sel = N, r
            break

    if N_sel is None:
        # Even at N_abs_max the geometric mesh cannot fill L (extreme case).
        # Do NOT reject a viable candidate for cost: fall back to a uniform mesh
        # of N_abs_max cells (relaxes Co_1 as little as possible).
        n = min(N_abs_max, max(2, int(np.ceil(L / dz1))))
        n = min(n, N_abs_max)
        return np.full(n, L / n)

    # Build the geometric mesh and rescale to close exactly at L.
    sizes = dz1 * r_sel ** np.arange(N_sel)
    sizes *= L / np.sum(sizes)
    return sizes


def fixed_ratio_mesh(L, N, ratio=40.0):
    """Geometric axial mesh, fine at the INLET (z=0). ratio = dz_last/dz_first.

    Concentrates cells where the CO2 permeation front is steepest. Reaches the
    same outlet-composition accuracy as a uniform mesh with ~3-4x fewer cells;
    the accuracy optimum is a broad plateau over ratio ~20-80 (see mesh_study/).
    """
    N = int(N)
    if N < 2:
        return np.array([float(L)])
    g = ratio ** (1.0 / (N - 1))
    dz1 = L * (g - 1.0) / (g ** N - 1.0)
    cs = dz1 * g ** np.arange(N)
    return cs * (L / cs.sum())
