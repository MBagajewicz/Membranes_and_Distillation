#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Proposed
#   0.2          27-Feb-2025     Mariana Mello             Add options of Shell Method
#   0.3          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_velocity_shellside
from math import pi
import numpy as np
#endregion

#region Calculations

def STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p):
    # Shell-side Reynolds number
    if m_p['Shell_Method'] == "Bell":
        # Shell velocity
        vs = Calculations_STHE_velocity_shellside.STHE_shellside_velocity(ms, ros, Ds, rp, L, Nb, dte, lay, m_p)

        # Reynolds number with the fouling layer
        #Res = (dte + 2 * fts_thk) * vs * m_p['ros'] / m_p['mis']

        # Reynolds number without the fouling layer
        Res = (dte*vs*ros) / mis

        #print('Res',Res)

    elif m_p['Shell_Method'] == "Kern":
        vs = Calculations_STHE_velocity_shellside.STHE_shellside_velocity(ms, ros, Ds, rp, L, Nb, dte, lay, m_p)
        K_Deq = 4 * np.ones(lay.shape)
        if isinstance(lay, float) or isinstance(lay, int):
            if lay == 2: K_Deq = 3.46
        else:
            K_Deq[lay == 2] = 3.46
        ltp = rp * dte
        Deq = (K_Deq * ltp**2) / (pi * dte) - dte
        Res = (Deq * vs * ros) / mis

    else:
        raise ValueError(f"Invalid Shell Method: {m_p['Shell_Method']}.")

    return Res

#endregion
