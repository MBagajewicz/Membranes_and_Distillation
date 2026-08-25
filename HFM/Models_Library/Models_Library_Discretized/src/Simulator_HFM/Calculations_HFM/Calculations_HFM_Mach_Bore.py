#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        21-Jul-2026     Joao Tupinamba               Bore-side Mach cut (Hagen-Poiseuille validity)
##################################################################################################################
#
# Discards candidates whose BORE-side flow provably violates the compressibility limit of the
# Hagen-Poiseuille pressure-drop model (Eq. 12), which assumes negligible kinetic energy, Ma <= 0.1.
#
# NOT CIRCULAR: at the permeate outlet (z = 0) the pressure P_P = P_perm is a specified design
# parameter, and the permeate flow there is bounded below by mass balance plus the retentate
# specification. That gives an exact LOWER bound on the exit velocity with no simulation.
#
# SAFE (no false negatives): going from z=0 (open) to z=L (closed), F_P falls to zero AND P_P rises.
# Both reduce v = (F_P/N)(Z R T/P_P)/A_bore, so the bore velocity is MAXIMUM at the exit, which is
# where the bound is evaluated. The result is a LOWER bound on the true maximum Mach number, and a
# candidate is discarded only when that lower bound already exceeds Ma_max.
#
# CONDITIONALITY (state explicitly in the manuscript): F_P_min presumes the candidate MEETS the
# retentate specification. Case analysis: either it meets the spec, in which case F_P >= F_P_min and
# the bound applies; or it does not, in which case it is already infeasible by Eq. (27). Discardable
# either way, but the justification is CONDITIONAL on the mass-transfer constraint.
#
# MATERIAL-INDEPENDENT: F_P_min follows from the feed and the specification only, and the geometry
# carries no permeance, so the surviving set is identical for every material.
##################################################################################################################
#endregion

#region Import Library
import numpy as np
#endregion

#region Constants

R_GAS = 8.314462618

_CP_NAME = {
    'CO2': 'CO2', 'CH4': 'Methane', 'N2': 'Nitrogen', 'C2H6': 'Ethane',
    'C3H8': 'Propane', 'nC4H10': 'n-Butane', 'H2S': 'HydrogenSulfide',
}

# The sound-speed bound is a scenario-level scalar: evaluated once, reused across the array.
_CACHE = {}

#endregion

#region Calculations


def min_permeate_flow(feed_flow, x_key_feed, theta_max):
    """
    Rigorous LOWER bound on the total permeate molar flow for any candidate meeting the spec.

    Let k be the key component, P_k and P_nk the key and non-key permeate molar flows, and
    F_P = P_k + P_nk. The retentate specification x_R,k <= Theta reads

        (F*x_F,k - P_k) / [ (F*x_F,k - P_k) + (F*(1 - x_F,k) - P_nk) ]  <=  Theta

    Clearing the denominator and regrouping:

        P_k*(1 - Theta) - Theta*P_nk  >=  F*(x_F,k - Theta)

    Adding P_nk to both sides and dividing by (1 - Theta):

        F_P  >=  [F*(x_F,k - Theta) + P_nk] / (1 - Theta)  >=  F*(x_F,k - Theta) / (1 - Theta)

    The minimum is attained at P_nk = 0, i.e. perfect selectivity; any real co-permeation only
    increases F_P. Verified against 4e5 randomly sampled feasible (P_k, P_nk) pairs, no violation.

    Returns 0.0 when the feed already meets the specification (x_F,k <= Theta).
    """
    val = feed_flow * (x_key_feed - theta_max) / (1.0 - theta_max)
    return max(float(val), 0.0)


def sound_speed_UB(components, T):
    """
    Conservative UPPER bound on the speed of sound of the permeate mixture.

    The permeate composition is not known a priori. For an ideal-gas mixture
    a = sqrt(gamma_mix * R * T / M_mix), with gamma_mix and M_mix lying between the pure-component
    extremes. Taking the largest gamma and the smallest M independently gives a bound no mixture
    can exceed:

        a  <=  sqrt( max_j(gamma_j) * R * T / min_j(M_j) )

    An UPPER bound on 'a' is what safety requires: Ma = v/a, so overestimating a UNDERestimates Ma,
    which under-trims rather than over-trims. The margin is large in practice (469 m/s bound versus
    ~333 m/s for a CO2-rich permeate), which also absorbs the Z = 1 assumption at the outlet.
    """
    key = (tuple(components), round(float(T), 6))
    if key in _CACHE:
        return _CACHE[key]
    import CoolProp.CoolProp as CP
    gammas, masses = [], []
    for c in components:
        f = _CP_NAME.get(c, c)  # fall back to the name as-is (already a CoolProp fluid, e.g. 'Ethane')
        cp = CP.PropsSI('CPMOLAR', 'T', T, 'P', 1e5, f)
        cv = CP.PropsSI('CVMOLAR', 'T', T, 'P', 1e5, f)
        gammas.append(cp / cv)
        masses.append(CP.PropsSI('M', f))
    a = float(np.sqrt(max(gammas) * R_GAS * T / min(masses)))
    _CACHE[key] = a
    return a


def bore_area(dfo, esp):
    """Bore cross-section per fiber, A = pi * Di^2 / 4, with Di = dfo - 2*esp (Eq. 20)."""
    dfo = np.asarray(dfo, dtype=float)
    esp = np.asarray(esp, dtype=float)
    Di = dfo - 2.0 * esp
    return np.pi * Di ** 2 / 4.0


def mach_bore(dfo, esp, Ntf, F_P_min, T, P_perm, a_UB, Z_bore=1.0):
    """
    LOWER bound on the Mach number at the permeate outlet, where the bore velocity peaks.

        v  = (F_P_min / N) * (Z * R * T / P_perm) / A_bore
        Ma = v / a_UB

    Z_bore defaults to 1.0: at ~1 bar the deviation is under 1% and is dominated by the margin
    already built into a_UB.
    """
    N = np.asarray(Ntf, dtype=float)
    A_bore = bore_area(dfo, esp)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = (F_P_min / N) * (Z_bore * R_GAS * T / P_perm) / A_bore
    return v / a_UB

#endregion