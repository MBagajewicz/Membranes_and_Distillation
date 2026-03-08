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

# region Import Library
from math import sqrt, pi
import numpy as np
#endregion


#region Calculations
def STHE_counting_table(Ds, dte, Npt, rp, lay, m_p):
    # Counting table
    if m_p['Shell_Method'] == "Bell":
        # Counting table
        ppDs = [0.2050, 0.3048, 0.3874, 0.4890, 0.5906, 0.6858, 0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 2]
        pppsi_1 = [0,       0,       0,       0,       0,       0,       0,     0,     0,     0,    0,     0,     0,     0,      0,    0,    0]
        pppsi_2 = [0.18, 0.09, 0.06, 0.046, 0.042, 0.036, 0.034, 0.033, 0.032, 0.03, 0.028, 0.025, 0.024, 0.0235, 0.02, 0.018, 0.018]
        pppsi_4 = [0.3, 0.2, 0.16, 0.125, 0.118, 0.11, 0.095, 0.090, 0.085, 0.08, 0.075, 0.073, 0.071, 0.0650, 0.06, 0.050, 0.05]
        pppsi_6 = [0.4, 0.22, 0.18, 0.168, 0.158, 0.148, 0.122, 0.118, 0.11, 0.105, 0.098, 0.090, 0.088, 0.0870, 0.08, 0.074, 0.074]

        # Shell - bundle leakage // Folga casco - matriz tubular
        Lbb = 0.0048*Ds + 0.0128

        C1 = np.ones(lay.shape)
        C1[lay == 2] = 0.866

        Ntt1 = (0.78 * (Ds - Lbb - dte)**2) / (C1*(rp*dte)**2)

        psi = np.zeros(Ds.shape)
        for i in range(0, len(pppsi_1)):
            CondDs = Ds > 10e10
            CondNpt = Ds > 10e10
            CondInter = Ds > 10e10

            CondDs[Ds == ppDs[i]] = True

            CondNpt[Npt == 1] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_1[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 2] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_2[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 4] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_4[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 6] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_6[i]

        #psi = 0.074
        Ntt = np.round(Ntt1 * (1 - psi))


    elif m_p['Shell_Method'] == "Kern":

        KNPt = sqrt(0.9) * np.ones(Npt.shape)
        if isinstance(Npt, float) or isinstance(Npt, int):
            if Npt == 1: KNPt = sqrt(0.93)
        else:
            KNPt[Npt == 1] = sqrt(0.93)
        Db = Ds * KNPt
        ltp = rp * dte
        Klay = np.ones(lay.shape)
        Klay[lay == 2] = 0.866
        Ntt = np.round((pi * Db ** 2) / (4 * ltp ** 2 * Klay))

    else:
        raise ValueError(f"Invalid Shell Method: {m_p['Shell_Method']}.")

    #print('Ntt', Ntt)
    return Ntt

#endregion
