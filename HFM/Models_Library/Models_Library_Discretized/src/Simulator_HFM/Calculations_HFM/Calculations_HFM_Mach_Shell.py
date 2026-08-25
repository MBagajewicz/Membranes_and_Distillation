#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        21-Jul-2026     Joao Tupinamba               Shell-side Mach cut (Hagen-Poiseuille validity)
##################################################################################################################
#
# Discards candidates whose SHELL-side flow provably violates the compressibility limit of the
# Hagen-Poiseuille pressure-drop model (Eq. 11), which assumes negligible kinetic energy, Ma <= 0.1.
#
# NOT CIRCULAR: at the feed inlet (z = 0) nothing has permeated yet, so F_R = F_feed, P_R = P_feed,
# T and x = x_feed are ALL specified. The inlet velocity is computed EXACTLY, no bound needed.
#
# SAFE (no false negatives): the true maximum shell velocity is >= its inlet value, so the inlet
# Mach number is a LOWER bound on the true maximum. A candidate is discarded only when that lower
# bound already exceeds Ma_max, i.e. only when the violation is certain.
#
# REAL GAS MATTERS: the molar volume comes from the real-fluid backend. At 60 bar Z ~ 0.90, and the
# ideal-gas value would overestimate the velocity by ~11%, trimming admissible candidates.
#
# MATERIAL-INDEPENDENT: the inlet state is fixed by the feed and the free flow area is pure
# geometry, so the surviving set is identical for every material.
#
# PRACTICAL NOTE: for the natural-gas scenarios of this work the shell Mach number peaks around
# 0.017 over the whole grid, so this cut trims nothing. Retained for completeness, and because it
# can bind at lower feed pressures or larger feed flows.
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

# The inlet state is a scenario-level scalar: evaluated once, reused across the candidate array.
_CACHE = {}

#endregion

#region Calculations


def feed_state(components, x_feed, T, P_feed):
    """
    Speed of sound and molar volume at the feed inlet.

    EXACT: composition, temperature and pressure are all specified there, so the real-fluid
    backend is used directly. No bound is involved.

    Returns:
        (a_feed [m/s], v_molar_feed [m3/mol])
    """
    key = (tuple(components), tuple(np.round(np.asarray(x_feed, float), 10)),
           round(float(T), 6), round(float(P_feed), 3))
    if key in _CACHE:
        return _CACHE[key]
    import CoolProp.CoolProp as CP
    st = CP.AbstractState('HEOS', '&'.join(_CP_NAME.get(c, c) for c in components))
    st.set_mole_fractions([float(v) for v in np.asarray(x_feed, dtype=float)])
    st.update(CP.PT_INPUTS, float(P_feed), float(T))
    out = (float(st.speed_sound()), 1.0 / float(st.rhomolar()))
    _CACHE[key] = out
    return out


def free_flow_area(D, Void_Frac):
    """Shell-side free flow area, A = eps * pi * D^2 / 4, with eps the void fraction (Eq. 19)."""
    D = np.asarray(D, dtype=float)
    eps = np.asarray(Void_Frac, dtype=float)
    return eps * np.pi * D ** 2 / 4.0


def mach_shell(D, Void_Frac, feed_flow, v_molar_feed, a_feed):
    """
    Mach number at the feed inlet (exact).

        v  = F_feed * v_molar_feed / A_free
        Ma = v / a_feed
    """
    A_free = free_flow_area(D, Void_Frac)
    with np.errstate(divide='ignore', invalid='ignore'):
        v = feed_flow * v_molar_feed / A_free
    return v / a_feed

#endregion