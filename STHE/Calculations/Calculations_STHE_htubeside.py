#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          04-Dec-2024     Mariana Mello               Original
#   0.2          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_Nusselt_tubeside
#endregion

#region Calculations

def STHE_h_tubeside(mt, rot, Cpt, mit, kt, thk, yfluid, Ds, dte, Npt, rp, lay, L, m_p):
    Nut = Calculations_STHE_Nusselt_tubeside.STHE_Nusselt_tubeside(mt, rot, Cpt, mit, kt, thk, yfluid, Ds, dte, Npt, rp,
                                                                   lay, L, m_p)
    dti = dte - 2 * thk
    ht = Nut * kt / dti
    #print('ht',ht)
    return ht

#endregion