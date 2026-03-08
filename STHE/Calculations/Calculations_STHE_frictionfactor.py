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


#region Import Library
from STHE.Calculations import Calculations_STHE_Reynolds_tubeside
#endregion

#region Calculations

def STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p):
    # Tube-side friction factor
    # Reynold number
    Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)

    ft = 64 / Ret
    ft[Ret > 1311] = 0.048
    ft[Ret > 3380] = 0.014 + 1.056/(Ret[Ret > 3380]**0.42)

    return ft

# endregion

