#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Proposed
#   0.2          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_Reynolds_shellside
#endregion

#region Calculations
def STHE_Nusselt_shellside(ms, ros, Cps, mis, ks, Ds, dte, rp, lay, L, Nb, m_p):
    # Shell-side Nusselt number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)
    Prs = Cps * mis / ks
    Nus = 0.36 * Res**0.55 * Prs**(1/3)
    return Nus

#endregion
