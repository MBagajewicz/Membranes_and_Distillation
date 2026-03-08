#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello              Proposed
#   0.2          27-Feb-2025     Mariana Mello             Add options of Shell Method
#   0.3          07-May-2025     Mariana Mello             Update to fix error in Ntcc/Jr
#   0.4          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_Nusselt_shellside, Calculations_STHE_Auxiliary_Bell_Method
from math import pi
import numpy as np
#endregion

#region Calculations

def STHE_h_shellside(ms, ros, Cps, mis, ks, Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    if m_p['Shell_Method'] == "Bell":
        phi = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Idealcrossflowh(Ds, dte, rp, lay, L, Nb, ms, ros, mis, Cps, ks, m_p)
        #print('phi', phi)
        Jc = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jc(Ds, dte, Bc, m_p)
        #print('jc', Jc)
        Jl = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)
        #print('Jl', Jl)
        Jb1 = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jb1(Ds, dte, Npt, rp, lay, ms, ros, mis, L, Nb, Bc, m_p)
        #print('Jb', Jb1)
        Jr = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jr(Ds, dte, Npt, rp, lay, L, Nb, ms, ros, mis, Bc, m_p)
        #print('Jr', Jr)

        Jtot = Jc * Jl * Jb1 * Jr
        #print('Jtot',Jtot)

        hs = phi * Jc * Jl * Jb1 * Jr
        #print('hs', hs)

    elif m_p['Shell_Method'] == "Kern":
        Nus = Calculations_STHE_Nusselt_shellside.STHE_Nusselt_shellside(ms, ros, Cps, mis, ks, Ds, dte, rp, lay, L, Nb, m_p)
        K_Deq = 4 * np.ones(lay.shape)
        K_Deq[lay == 2] = 3.46
        ltp = rp * dte
        Deq = (K_Deq * ltp**2) / (pi * dte) - dte
        hs = Nus * ks / Deq

    else:
        raise ValueError(f"Invalid Shell Method: {m_p['Shell_Method']}.")

    return hs

#endregion