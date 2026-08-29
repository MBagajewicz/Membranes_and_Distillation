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
from Common_Equations_Properties.Calculations_Prop_Viscosity_gas_mix import Mean_Viscosity_Mix

# endregion

# region Calculations

def dP_Shell(T, D_o, sum_u, u_frac, Ntf, P, D, MU, M):
    mu_u_mix = Mean_Viscosity_Mix(u_frac,MU,M)

    u_total_safe = np.maximum(sum_u, 1e-12)

    dP_dz = (192 * Ntf * D_o * (D + Ntf * D_o) * mu_u_mix * 8.314 * T * u_total_safe /
             (np.pi * (D ** 2 - Ntf * D_o ** 2) ** 3 * P))
    return dP_dz