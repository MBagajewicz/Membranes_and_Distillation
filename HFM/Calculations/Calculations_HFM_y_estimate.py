#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        10-Jan-2026     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
#endregion

#region Calculations
def estimate_y_pc_multicomponent(
    Q: np.ndarray,
    A_t: np.ndarray,
    Pf: float,
    Pp: float,
    F_f: float,
    x_feed: np.ndarray,
    Key_Comp_index: int,
    tol: float = 1e-5,
    max_iter: int = 2000,
):
    Q = np.asarray(Q, dtype=float).copy()

    # garante shape (nc, n_cases)
    if Q.ndim == 1:
        Q = Q[:, None]

    A_t = np.asarray(A_t, dtype=float)
    if A_t.ndim == 0:
        A_t = np.array([A_t], dtype=float)

    x_feed = np.asarray(x_feed, dtype=float).reshape(-1, 1)  # (nc, 1)

    nc, n_cases = Q.shape

    if x_feed.shape[0] != nc:
        raise ValueError("x_feed e Q têm números de componentes incompatíveis.")

    if A_t.size != n_cases:
        raise ValueError("A_t e Q têm números de candidatos incompatíveis.")

    if np.any(Q < 0):
        raise ValueError("Q deve ser não-negativo.")

    delta = Pp / Pf

    # chute inicial: composição do permeado puxada por Q
    y = Q / np.maximum(np.sum(Q, axis=0, keepdims=True), 1e-16)   # (nc, n_cases)
    y = y * x_feed
    y = y / np.maximum(np.sum(y, axis=0, keepdims=True), 1e-16)

    for _ in range(max_iter):
        # transferência máxima por componente/candidato
        driving_pf = np.maximum(Pf * x_feed - Pp * y, 0.0)        # (nc, n_cases)
        transfer = Q * A_t[None, :] * driving_pf                  # (nc, n_cases)

        # fluxo total remanescente no retentado
        denom = F_f - np.sum(transfer, axis=0, keepdims=True)     # (1, n_cases)
        denom = np.maximum(denom, 1e-16)

        # composição mínima do retentado na extremidade fechada
        x_r_min = (F_f * x_feed - transfer) / denom               # (nc, n_cases)
        x_r_min = np.maximum(x_r_min, 1e-16)
        x_r_min = x_r_min / np.maximum(np.sum(x_r_min, axis=0, keepdims=True), 1e-16)

        # composição local do permeado que atravessa
        driving = np.maximum(x_r_min - delta * y, 1e-16)
        J = Q * driving
        y_next = J / np.maximum(np.sum(J, axis=0, keepdims=True), 1e-16)

        if np.max(np.abs(y_next - y)) < tol:
            driving_pf = np.maximum(Pf * x_feed - Pp * y_next, 0.0)  # (nc, n_cases)
            transfer = Q * A_t[None, :] * driving_pf  # (nc, n_cases)
            # fluxo total remanescente no retentado
            denom = F_f - np.sum(transfer, axis=0, keepdims=True)  # (1, n_cases)
            denom = np.maximum(denom, 1e-16)
            # composição mínima do retentado na extremidade fechada
            x_r_min = (F_f * x_feed - transfer) / denom  # (nc, n_cases)
            x_r_min = np.maximum(x_r_min, 1e-16)
            x_r_min = x_r_min / np.maximum(np.sum(x_r_min, axis=0, keepdims=True), 1e-16)
            return y_next.T, x_r_min  # (n_cases, nc)

        y = y_next

    return y.T, x_r_min
