#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          24-Mar-2024     Mariana Mello             Proposed
#   0.2          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_area
#endregion

#region Calculations

def STHE_CAPEX(par_a, par_b, Ds, dte, Npt, rp, lay, L, m_p):
    # Area
    Atot = Calculations_STHE_area.STHE_area(Ds, dte, Npt, rp, lay, L, m_p)
    # Capital cost
    Cap = par_a*(Atot**par_b)
    return Cap

#endregion