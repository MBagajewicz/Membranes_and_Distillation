#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        10-Nov-2025     João Tupinambá               Proposed
#  0.1        15-Jul-2026     João Tupinambá               E, nu, degradation_factor, safety_factor are now
#                                                          per-material dicts; Material is an array of 'PI'/'CA'.
#                                                          Returns a per-candidate array of minimum thickness.
##################################################################################################################
#endregion

#region Import Library
import numpy as np
#endregion

#region Calculations

def Min_Thickness(P, p, dfo, E, nu, degradation_factor, safety_factor, Material):
    """
    Minimum membrane wall thickness to resist elastic collapse (buckling) under external pressure.

    Now vectorized over the candidate set: the mechanical properties depend on the fiber MATERIAL,
    which varies candidate by candidate.

    Args:
        P:   Shell (retentate) pressure (Pa). Scalar or array broadcastable to Material.
        p:   Bore (permeate) pressure (Pa). Scalar or array broadcastable to Material.
        dfo: Fiber outer diameter (m). Array, one value per candidate (same length as Material).
        E:                  dict {'PI': Pa, 'CA': Pa}   -- fiber Young's modulus per material.
        nu:                 dict {'PI': -,  'CA': -}    -- Poisson's ratio per material.
        degradation_factor: dict {'PI': -,  'CA': -}    -- lambda_d (<1): E_eff = E * lambda_d.
        safety_factor:      dict {'PI': -,  'CA': -}    -- lambda_s.
        Material:           array of str, 'PI'/'CA', one entry per candidate.

    Returns:
        t_min (np.ndarray): minimum thickness (m), one value per candidate (same shape as Material).
    """

    # --- resolve the per-material scalars into per-candidate arrays --------------------------------
    Material = np.asarray(Material)
    dfo = np.asarray(dfo, dtype=float)

    def _by_material(prop_dict):
        # Map each candidate's material string to its property value.
        # (Building one boolean mask per material is faster than np.vectorize for large arrays.)
        out = np.empty(Material.shape, dtype=float)
        for mat, value in prop_dict.items():
            out[Material == mat] = value
        # guard: any candidate whose material is not in the dict would stay uninitialized
        unknown = ~np.isin(Material, list(prop_dict.keys()))
        if unknown.any():
            bad = np.unique(Material[unknown])
            raise KeyError(f"Material(s) {bad.tolist()} missing from property dict {list(prop_dict.keys())}")
        return out

    E_v   = _by_material(E)
    nu_v  = _by_material(nu)
    deg_v = _by_material(degradation_factor)
    saf_v = _by_material(safety_factor)

    P_diff = (P - p)  # Pa

    # Apply degradation factor (plasticization): CO2 softens the matrix, reducing E.
    E_deg = E_v * deg_v

    # --- CRITERION B: Elastic Instability (Buckling/Collapse) -------------------------------------
    # Long-pipe elastic collapse under external pressure:
    #     P_cr = [2E / (1 - nu^2)] * (t / Do)^3
    # Isolating t and applying the safety factor (lambda_s) inside the cube root:
    #     t = Do * [ lambda_s * (P_R_in - P_P_0) * (1 - nu^2) / (2 * E_deg) ]^(1/3)
    # NOTE: the (1 - nu^2) term carries NO factor 3. The sqrt(3(1-nu^2)) that appears in Eq. (31)
    # of the current manuscript draft is erroneous and must be corrected there to match this.
    term_1 = (saf_v * P_diff * (1 - nu_v ** 2)) / (2 * E_deg)
    t_buckling = dfo * (term_1) ** (1 / 3)

    return t_buckling

#endregion
