#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello              Proposed
#   0.2          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_countingtable
from math import pi
#endregion

#region Calculations

def STHE_area(Ds, dte, Npt, rp, lay, L, m_p):
    # Heat exchanger area
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(Ds, dte, Npt, rp, lay, m_p)
    A = Ntt * pi * dte * L
    return A

