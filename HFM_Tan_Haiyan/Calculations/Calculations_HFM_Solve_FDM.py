#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        06-Nov-2025     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
from scipy.optimize import fsolve
from HFM.Calculations.Calculations_HFM_Residues import membrane_system_residuals
#endregion

#region Calculations

def solve_HFM_model_FDM(N_parts, U_Feed_Target, V_Sweep_Target, Q, P_Feed, P_Permeate, T, dfi, dfo, Ntf, D, MU, M, Dz):
    # Dimensões
    n_comp = len(Q)
    width = 2 * n_comp + 2

    # --- CHUTE INICIAL (Interpolação Linear) ---
    # Criamos arrays [N+1, Variável] para depois achatar
    U_guess = np.zeros((N_parts + 1, n_comp))
    V_guess = np.zeros((N_parts + 1, n_comp))
    P_guess = np.linspace(P_Feed - 1e4, P_Feed, N_parts + 1)  # Leve queda N->0
    p_guess = np.linspace(P_Permeate + 1e4, P_Permeate, N_parts + 1)  # Leve queda 0->N

    for i in range(n_comp):
        U_guess[:, i] = np.linspace(U_Feed_Target[i] * 0.8, U_Feed_Target[i], N_parts + 1)
        V_guess[:, i] = np.linspace(V_Sweep_Target[i], U_Feed_Target[i] * 0.2, N_parts + 1)

    # Monta a matriz [N+1, width]
    # Colunas: [U... , V... , P, p]
    x_init_mat = np.hstack([U_guess, V_guess, P_guess.reshape(-1, 1), p_guess.reshape(-1, 1)])
    x_init = x_init_mat.flatten()

    # --- RESOLVE ---
    sol, infodict, ier, mesg = fsolve(
        membrane_system_residuals,
        x_init,
        args=(N_parts, n_comp, Q, P_Feed, P_Permeate, U_Feed_Target, V_Sweep_Target, T, dfi, dfo, Ntf, D, MU, M, Dz),
        full_output=True
    )

    if ier != 1:
        print(f"Falha: {mesg}")
        return 0,0,0,0

    # --- PÓS-PROCESSAMENTO ---
    # Recupera a estrutura 2D
    sol_mat = sol.reshape((N_parts + 1, width))
    U_fin = sol_mat[:, 0:n_comp]
    V_fin = sol_mat[:, n_comp:2 * n_comp]
    P_fin = sol_mat[:, 2 * n_comp]
    p_fin = sol_mat[:, 2 * n_comp + 1]

    return U_fin, V_fin, P_fin, p_fin
