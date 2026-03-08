#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Proposed
#   0.2          28-Feb-2025     Mariana Mello             Add options of Tube Method
#   0.3          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_Reynolds_tubeside, Calculations_STHE_velocity_tubeside, Calculations_STHE_frictionfactor
import numpy as np
#endregion

#region Calculations

def STHE_tubeside_DeltaP(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, L, m_p):
    # Tube-side pressure drop
    if m_p['Tube_Method'] == 'Dewiit_Saunders':
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(mt, rot, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9
        dti = dte - 2 * thk
        DPt = (rot * ft * Npt * L * vt ** 2) / (2 * dti) + rot * K * Npt * vt ** 2 / 2

    elif m_p['Tube_Method'] == 'Gnieliski':
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(mt, rot, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9
        dti = dte - 2 * thk
        DPt = (rot * ft * Npt * L * vt ** 2) / (2 * dti) + rot * K * Npt * vt ** 2 / 2

    elif m_p['Tube_Method'] == 'Hausen':
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(mt, rot, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9
        dti = dte - 2 * thk
        DPt = (rot * ft * Npt * L * vt ** 2) / (2 * dti) + rot * K * Npt * vt ** 2 / 2

    elif m_p['Tube_Method'] == 'Sieder_Tate':
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(mt, rot, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9
        dti = dte - 2 * thk
        DPt = (rot * ft * Npt * L * vt ** 2) / (2 * dti) + rot * K * Npt * vt ** 2 / 2

    elif m_p['Tube_Method'] == "Dittus_Boelter":
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(mt, rot, thk, Ds, dte, Npt, rp, lay, m_p)
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = 0.014 + 1.056 / (Ret**0.42)
        #print('ft',ft)
        K = 1.6 * np.ones(Npt.shape)
        # if isinstance(Npt, float) or isinstance(Npt, int):
        #     if Npt == 1: K = 0.9
        # else:
        #       K[Npt == 1] = 0.9
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9
        dti = dte - 2 * thk
        DPt = (rot * ft * Npt * L * vt**2) / (2 * dti) + rot * K * Npt * (vt**2) / 2

    else:
        raise ValueError(f"Invalid Tube Method: {m_p['Tube_Method']}.")

    return DPt

#endregion
