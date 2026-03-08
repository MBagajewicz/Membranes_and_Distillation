#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          04-Dec-2024     Mariana Mello             Proposed
#   0.2          23-Apr-2025     Mariana Mello             Update include Xp and Pmax
#   0.3          25-Apr-2025     Mariana Mello             Update include R = 1
##################################################################################################################
#endregion

# region Import Library
import numpy as np
#endregion


#region Calculations

def STHE_correction_factor(Thi, Tho, Tci, Tco, Npt, Xp):
    # LMTD correction factor
    F = np.ones(Npt.shape)
    #F = np.ones_like(Npt, dtype=float)

    R = (Thi - Tho) / (Tco - Tci)
    P = (Tco - Tci) / (Thi - Tci)

    Pmax = 2/(R+1+(R*R+1)**0.5)

    cond = (Pmax*Xp) > P

    try:
        if cond:
            if R == 1:
                try:
                    F_1N = (2**0.5*P) / ((1 - P) * np.log((2 - P*(2 - 2**0.5)) / (2 - P*(2 + 2**0.5))))
                except:
                    print("Unable to calculate LMTD correction factor, data inconsistency")
                F[Npt > 1] = F_1N

            else:
                try:
                    F_1N = (np.sqrt(R**2 + 1)*np.log((1-P)/(1-R*P)))/((R - 1)*np.log((2-P*(R+1-np.sqrt(R**2 + 1)))/(2-P*(R+1+np.sqrt(R**2 + 1)))))
                except:
                    print("Unable to calculate LMTD correction factor, data inconsistency")
                F[Npt > 1] = F_1N
        else:
            F[Npt > 1] = 1e-15

    except:
        if cond.all():
            if np.all(R) == 1:
                try:
                    F_1N = (2**0.5*P) / ((1 - P)*np.log((2 - P*(2 - 2**0.5)) / (2 - P*(2 + 2**0.5))))
                except:
                    F_1N = 1e-15
                F[Npt > 1] = F_1N[Npt > 1]

            else:
                try:
                    F_1N = (np.sqrt(R**2 + 1)*np.log((1-P)/(1-R*P)))/((R - 1)*np.log((2-P*(R+1-np.sqrt(R**2 + 1)))/(2-P*(R+1+np.sqrt(R**2 + 1)))))
                except:
                    F_1N = 1e-15
                F[Npt > 1] = F_1N[Npt > 1]
        else:
            F[Npt > 1] = 1e-15

    return F

#endregion
