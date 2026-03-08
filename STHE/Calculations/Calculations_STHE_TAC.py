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
from STHE.Calculations import Calculations_STHE_DeltaPtubeside, Calculations_STHE_DeltaPshellside, Calculations_STHE_area
#endregion

#region Calculations

def STHE_TAC(int_rate, n, par_a, par_b, Nop, pc, eta, Ds, dte, Npt, rp, lay, L, ms, mt, ros, rot, mis, mit, thk, Nb, Bc, m_p):
    r = ((int_rate*(1+int_rate)**n))/(((1+int_rate)**n) - 1)
    Atot = Calculations_STHE_area.STHE_area(Ds, dte, Npt, rp, lay, L, m_p)
    Cap = par_a*Atot**par_b                             # Capital cost
    deltaPs = Calculations_STHE_DeltaPshellside.STHE_shellside_DeltaP(ms, ros, mis, Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)
    deltaPt = Calculations_STHE_DeltaPtubeside.STHE_tubeside_DeltaP(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, L, m_p)
    #print('DPt', deltaPt)
    Cop_s = Nop*(pc/1000)*((deltaPs*ms)/(eta*ros))      # Operating cost on a yearly fot the shell side stream
    Cop_t = Nop*(pc/1000)*((deltaPt*mt)/(eta*rot))      # Operating cost on a yearly fot the tube side stream
    TAC = r*Cap + Cop_s + Cop_t
    return TAC

#endregion