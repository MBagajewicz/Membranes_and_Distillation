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
from STHE.Calculations import Calculations_STHE_Reynolds_shellside, Calculations_STHE_velocity_shellside, Calculations_STHE_Auxiliary_Bell_Method
from math import pi
import numpy as np
#endregion

#region Calculations

def STHE_shellside_DeltaP(ms, ros, mis, Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    # Shell-side pressure drop

    if m_p['Shell_Method'] == "Bell":
        DPc = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_crossflowDeltaP(ms, ros, mis, Ds, dte, Npt, rp,
                                                                                     lay, L, Nb, Bc, m_p)
        #print('DPc',DPc)
        DPw = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_BaffleWidownDeltaP(ms, ros, mis, Ds, dte, Npt, rp,
                                                                                        lay, L, Nb, Bc, m_p)
        #print('DPw', DPw)
        DPe = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_EndZonesDeltaP(ms, ros, mis, Ds, dte, rp, lay, L,
                                                                                    Nb, Bc, m_p)
        #print('DPe', DPe)
        DPs = DPc + DPw + DPe
        #print('DPs',DPs)

    elif m_p['Shell_Method'] == "Kern":

        K_Deq = 4 * np.ones(lay.shape)

        if isinstance(lay, float) or isinstance(lay, int):
            if lay == 2: K_Deq = 3.46
        else:
            K_Deq[lay == 2] = 3.46

        ltp = rp * dte
        Deq = (K_Deq * ltp**2) / (pi * dte) - dte
        vs = Calculations_STHE_velocity_shellside.STHE_shellside_velocity(ms, ros, Ds, rp, L, Nb, dte, lay, m_p)
        Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)
        fs = 1.728 / Res**0.188
        DPs = (ros * fs * Ds * (Nb + 1) * vs**2) / (2 * Deq)

    else:
        raise ValueError(f"Invalid Shell Method: {m_p['Shell_Method']}.")

    return DPs

#endregion