import numpy as np
from Common_Equations_Properties.Calculations_Prop_Viscosity_gas_mix import Mean_Viscosity_Mix
from HFM.Calculations.Calculations_HFM_dP_Bore import dP_Bore
from HFM.Calculations.Calculations_HFM_dP_Shell import dP_Shell
def membrane_system_3d(x, N, nc, Q, Ph, Pl_out, AREA_SEG, U_Target, V_Target,R,T,D_o,D_i,D,Dz):
    """
    Estrutura do vetor x (achatado) -> reshape para Matrix 2D (Nó, Variáveis)
    Colunas da Matriz:
    [0..nc-1] -> Fluxos U (nc colunas)
    [nc..2nc-1] -> Fluxos V (nc colunas)
    [2nc] -> Pressão Retentado (P)
    [2nc+1] -> Pressão Permeado (p)
    """

    # (2 * nc) fluxos + 2 pressões
    width = 2 * nc + 2
    all_vars = x.reshape((N + 1, width))

    U = all_vars[:, 0:nc]
    V = all_vars[:, nc:2 * nc]
    P_Ret = all_vars[:, 2 * nc]
    p_Perm = all_vars[:, 2 * nc + 1]

    residuals = []

    # --- CONDIÇÕES DE CONTORNO (BCs) ---

    # j = 0: Entrada do Sweep
    residuals.extend(V[0, :] - V_Target)

    # j = N: Entrada do Feed
    residuals.extend(U[N, :] - U_Target)

    # j = N: Pressão do Feed
    residuals.append(P_Ret[N] - Ph)

    # j = N: Pressão do Permeado
    residuals.append(p_Perm[N] - Pl_out)

    # --- LOOP NOS SEGMENTOS (1 até N) ---
    for k in range(1, N + 1):
        prev = k - 1
        curr = k

        # Propriedades Locais (Calculadas no nó 'curr')
        SumU = np.sum(U[curr, :])
        SumV = np.sum(V[curr, :])

        x_mol = U[curr, :] / SumU
        y_mol = V[curr, :] / SumV

        # --- 1. BALANÇO DE MASSA ---
        # Força Motriz
        DrivingForce = Q * AREA_SEG * (P_Ret[curr] * x_mol - p_Perm[curr] * y_mol)

        # V: Co-corrente com índice k (0->N) | V_curr - V_prev = +Transf
        eq_V = V[curr, :] - V[prev, :] - DrivingForce

        # U: Contra-corrente com índice k (N->0) | U_curr - U_prev = +Transf
        eq_U = U[curr, :] - U[prev, :] - DrivingForce

        residuals.extend(eq_V)
        residuals.extend(eq_U)

        # --- 2. BALANÇO DE QUANTIDADE DE MOVIMENTO (PRESSÃO) ---

        dP_shell = dP_Shell(R, T, D_o, SumU, x_mol, N, P_Ret[curr], D) * Dz
        eq_P = P_Ret[curr] - P_Ret[prev] - dP_shell
        residuals.append(eq_P)

        dp_bore = dP_Bore(R, T, D_i, SumV, y_mol, N, p_Perm[curr]) * Dz
        eq_p = p_Perm[curr] - p_Perm[prev] + dp_bore
        residuals.append(eq_p)

    return np.array(residuals).flatten()