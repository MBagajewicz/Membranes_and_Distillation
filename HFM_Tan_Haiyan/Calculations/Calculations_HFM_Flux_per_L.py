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
# from HF_Membrane.Calculations.Calculations_HFM_Area_per_L import HFM_area_per_L
#endregion

#region Calculations

def Flux_per_L(u,v, p, P, Ntf, dfo, Q):
    u_total = np.sum(u, axis=0)
    v_total = np.sum(v, axis=0)

    # --- Safeguards for numerical stability ---
    u_total_safe = np.maximum(u_total, 1e-12)
    v_total_safe = np.maximum(v_total, 1e-12)

    u_frac = u / u_total_safe
    v_frac = v / v_total_safe

    AREA_PER_L = Ntf * np.pi * dfo

    Q_col = Q[:, np.newaxis]

    partial_pressure_shell = P * u_frac
    partial_pressure_tube = p * v_frac
    driving_force = partial_pressure_shell - partial_pressure_tube
    flux_per_length = AREA_PER_L * Q_col * driving_force
    return flux_per_length