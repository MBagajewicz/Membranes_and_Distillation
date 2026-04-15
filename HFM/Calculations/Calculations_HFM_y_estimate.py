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
    A_t: float,
    Pf: float,
    Pp: float,
    F_f: float,
    x_feed : np.ndarray,
    Key_Comp_index: int,
    tol: float = 1e-10,
    max_iter: int = 2000,
):

    Q = np.asarray(Q, dtype=float).copy()

    # 1) Consistency check para permeancias e chute
    if np.any(Q < 0):
        raise ValueError("Q deve ser não-negativo.")


    # 2) inicialização

    y = Q/sum(Q) * x_feed

    delta = Pp/Pf

    for _ in range(max_iter):
        # "fluxos" relativos na parte fechada da fibra oca
        # 1) calcula x_r_end_min
        denom = (F_f*x_feed - sum(Q*A_t[:, None] * (Pf*x_feed-Pp*y)))
        denom[denom == 0] = 1e-16
        x_r_min = (F_f*x_feed - Q*A_t[:, None] * (Pf*x_feed-Pp*y))/denom

        x_r_min[x_r_min <= 0] = 0
        sx = x_r_min.sum(axis=1, keepdims=True)
        x_r_min /= np.maximum(sx, 1e-16)  # normaliza

        #2) calcula y_end
        driving = x_r_min - delta * y
        J = Q * np.maximum(driving, 1e-16)
        sJ = J.sum(axis=1, keepdims=True)
        y_new = J / sJ

        y_next = np.maximum(y_new, 1e-16) # evita divisão por zero
        sy = y_next.sum(axis=1, keepdims=True)
        y_next = y_next / sy

        if np.max(np.abs(y_next - y)) < tol: # se o valor de y não mudar por uma tolerância, retornar.
            return y_next

        y = y_next

    return y  # Retornar o melhor encontrado ao fim das iterações
