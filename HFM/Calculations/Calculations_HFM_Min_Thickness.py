#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        10-Nov-2025     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
#endregion

#region Calculations

def Min_Thickness(P, p, dfo, E, nu, degradation_factor, safety_factor):
    """
    Calculate the minimum membrane thickness required to resist collapse.

    Args:
        P: Shell pressure (Pa)
        p: Bore pressure (Pa)
        dfo: fiber outer diameter (m)
        E: Young Modulus (Pa),
        nu: Poisson's Coefficient

        degradation_factor: Assume a 30% loss of strength due to CO2 plasticization.
        safety_factor: Safety factor (assumed to be 3.0 to cover eccentricity and creep)

    Returns:
        t_min (m): Recommended minimum thickness
    """

    P_diff = (P - p) # Pa

    # Apply CO2 degradation factor (Plasticization)
    # CO2 softens the polymer matrix, reducing E.
    E_deg = E * degradation_factor

    # --- CRITERION B: Elastic Instability (Buckling/Collapse) ---
    # Classic formula for long pipe collapse under external pressure
    # P_cr = [2E / (1-nu^2)] * (t / 2Ro)^3
    # Isolando t:
    term_1 = (P_diff * safety_factor * (1 - nu ** 2)) / (2 * E_deg)
    t_buckling = dfo * (term_1) ** (1 / 3)

    return t_buckling
