#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Proposed
#   0.2          28-Feb-2025     Mariana Mello             Add options of Shell Method
#   0.3          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion

# region Import Library
from STHE.Calculations import Calculations_STHE_Auxiliary_Bell_Method
# endregion



#region Calculations
def STHE_shellside_velocity(ms, ros, Ds, rp, L, Nb, dte, lay, m_p):
    # Shell-side velocity
    if m_p['Shell_Method'] == "Bell":
        Sm = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)
        vs = ms / Sm / ros
        #print('vs',vs)

    elif m_p['Shell_Method'] == "Kern":
        qs = ms / ros
        FAR = 1 - 1 / rp
        lbc = (L / (Nb + 1))
        Ar = Ds * FAR * lbc
        vs = qs / Ar

    else:
        raise ValueError(f"Invalid Shell Method: {m_p['Shell_Method']}.")

    return vs

#endregion

