#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          08-May-2025     Mariana Mello              Proposed
#   0.1          26-Oct-2026     Mariana Mello              HFM outlet recalculated from optimal design variables;
#                                                           m_p_prev argument, kmol/h conversion and T_f from HFM

##################################################################################################################
#endregion

# region Import
import ast
import numpy as np
from HFM.Calculations import Calculations_HFM_Nf, Calculations_HFM_Recovery
# endregion

#region Calculations

def SU_DC_2FEEDS(results, m_p_prev, m_p):

    # results: HFM solution (optimal L, D, dfo_esp, Void_Frac)
    # m_p_prev: HFM Model_Parameters
    # m_p: DC_2FEEDS Model_Parameters (Feed 1 = permeate, Feed 2 = retentate)

    L = float(results['L'])
    D = float(results['D'])
    Void_Frac = float(results['Void_Frac'])
    dfo, esp = ast.literal_eval(results['dfo_esp'])
    dfi = dfo - 2*esp
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)

    outlet = Calculations_HFM_Recovery.model_HFM_Outlet(L, D, dfo, dfi, Void_Frac, m_p_prev, Ntf)

    # mol/s -> kmol/h
    perm_flow_kmolh = float(np.squeeze(outlet['perm_flow'])) * 3.6
    ret_flow_kmolh = float(np.squeeze(outlet['ret_flow'])) * 3.6

    # z_f, F_f and T_f are in a form of vectors for the two feeds.
    m_p['z_f'] = [np.squeeze(outlet['perm_comp']).tolist(), np.squeeze(outlet['ret_comp']).tolist()]
    m_p['F_f'] = [perm_flow_kmolh, ret_flow_kmolh]
    m_p['T_f'] = [m_p_prev['T'], m_p_prev['T']]

    return m_p

#endregion
