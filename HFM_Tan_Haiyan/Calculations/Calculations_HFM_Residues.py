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
from HFM.Calculations.Calculations_HFM_dP_Bore import dP_Bore
from HFM.Calculations.Calculations_HFM_dP_Shell import dP_Shell
from HFM.Calculations.Calculations_HFM_Area_per_L import HFM_area_per_L
#endregion

#region Calculations

def membrane_system_residuals(x, N, nc, Q, P_Feed, P_Permeate, U_Target, V_Target, T, dfi, dfo, Ntf, D, MU, M, Dz):
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
    residuals.append(P_Ret[N] - P_Feed)

    # j = N: Pressão do Permeado
    residuals.append(p_Perm[N] - P_Permeate)

    # --- LOOP NOS SEGMENTOS (1 até N) ---
    for k in range(1, N + 1):
        prev = k - 1
        curr = k

        # Propriedades Locais (Calculadas no nó 'curr')
        SumU = np.sum(U[curr, :])
        SumV = np.sum(V[curr, :])

        u_frac = U[curr, :] / SumU
        v_frac = V[curr, :] / SumV

        # Viscosidades
        # mu_u = Mean_Viscosity_Mix(u_frac)
        # mu_v = Mean_Viscosity_Mix(v_frac)
        
        #Segmental area
        AREA_SEG = HFM_area_per_L(dfo, Ntf) * Dz

        # --- 1. BALANÇO DE MASSA ---
        # Força Motriz
        DrivingForce = Q * AREA_SEG * (P_Ret[curr] * u_frac - p_Perm[curr] * v_frac)

        # V: Co-corrente com índice k (0->N) | V_curr - V_prev = +Transf
        eq_V = V[curr, :] - V[prev, :] - DrivingForce

        # U: Contra-corrente com índice k (N->0) | U_curr - U_prev = +Transf
        eq_U = U[curr, :] - U[prev, :] - DrivingForce

        residuals.extend(eq_V)
        residuals.extend(eq_U)

        # --- 2. BALANÇO DE QUANTIDADE DE MOVIMENTO (PRESSÃO) ---

        # Perda de carga no segmento (dP total = dP/dz * Dz)
        # Nota: Usamos SumU/P_curr como aproximação local

        # Retentado (Shell): Flui N->0 (curr -> prev)
        # Pressão cai de curr para prev. Logo P_curr > P_prev.
        # Eq: P_curr - P_prev = Perda
        # dP_shell = (K_shell * mu_u * R * T * SumU) / P_Ret[curr] * Dz
        dP_shell = dP_Shell(T, dfo, SumU, u_frac, Ntf, P_Ret[curr], D, MU, M) * Dz
        eq_P = P_Ret[curr] - P_Ret[prev] - dP_shell
        residuals.append(float(eq_P))

        # Permeado (Bore): Flui 0->N (prev -> curr)
        # Pressão cai de prev para curr. Logo p_prev > p_curr.
        # Eq: p_prev - p_curr = Perda  =>  p_curr - p_prev + Perda = 0
        # dp_bore = (K_bore * mu_v * R * T * SumV) / p_Perm[curr] * Dz
        dp_bore = dP_Bore(T, dfi, SumV, v_frac, Ntf, p_Perm[curr], MU, M) * Dz
        eq_p = p_Perm[curr] - p_Perm[prev] + dp_bore
        residuals.append(float(eq_p))

    return np.array(residuals).flatten()
