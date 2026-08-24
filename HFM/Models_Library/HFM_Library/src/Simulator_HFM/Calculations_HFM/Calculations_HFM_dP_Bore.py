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
from Common.Physical_Properties.Viscosity.Mixture_Properties import MixtureProperties
#endregion

#region Calculations

def dP_Bore(T, D_i, sum_v, v_frac, N, p, MU, M):

    mu_v_mix = MixtureProperties(v_frac, MU, M, method="HZ")

    v_total_safe = np.maximum(sum_v, 1e-12)

    dp_dz = (128 * 8.314 * T * mu_v_mix * v_total_safe) / (np.pi * D_i ** 4 * N * p)
    return dp_dz