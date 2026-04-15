##################################################################################################################
# region Titles and Header
# Nature: 'Parameters_Calculations_List' and 'Example_Within_Set_Up' functions
# Methodology: Set trimming and Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          28-Fev-2025     Alice Peccini             Original
#   0.2          29-Apr-2025     Mariana Mello             Update to fix error
#   0.3          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
# INPUT: Define Functions for 'Parameters_Calculations_List' and 'Example_Within_Set_Up'
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def)
# For 'Parameters_Calculations_List':
#   def fun(model_parameters)
#       return model_parameters
# For 'Example_Within_Set_Up':
#   def fun(results,model_parameters)
#       return model_parameters
# endregion
##################################################################################################################

##################################################################################################################
# region Import Library
from Common_Equations_HEX import (
    Calculations_HEX_heatload, 
    Calculations_HEX_LMTD
    )
#from STHE.Calculations import Calculations_STHE_correction_factor
# endregion
##################################################################################################################


##################################################################################################################
# region Parameters Calculation functions
  
def Set_Up_HFM_DC(Tci_n, m_recirc_n, m_p_dict):

    # ========================================= Parameters update =========================================
    # Tci_n - Inlet temperature of the cold stream of Equipment 1 (°C)
    # m_recirc_n - Mass flow rate of the recirculation stream (kg/s)
    # m_cs_n - Mass flow rate of cold stream (kg/s)
    m_p1 = m_p_dict['m_p1']
    m_p2 = m_p_dict['m_p2']

    # Calculate the heat load
    Q = Calculations_HEX_heatload.HEX_heat_load(m_p1['mh'], m_p1['Cph'], m_p1['Thi'], m_p1['Tho'])
    m_p1['Tci'] = Tci_n
    m_p2['Tho'] = Tci_n
    m_p1['mc'] = m_recirc_n
    m_p1['ms'] = m_recirc_n
    m_p2['mh'] = m_recirc_n
    m_p2['ms'] = m_recirc_n
    #m_p2['mc'] = m_cs_n
    #m_p2['mt'] = m_cs_n

    # Calculate Tco of Equipment 1
    Tco_Eq1 = Q/(m_recirc_n * m_p1['Cpc']) + Tci_n
    m_p1['Tco'] = Tco_Eq1
    m_p2['Thi'] = Tco_Eq1
    # Calculate Tco of Equipment 2
    #Tco_Eq2 = (Q/(m_cs_n*m_p2['Cpc']) + m_p2['Tci'])
    #Tco_Eq2 = (Q / (m_p2['m_water'] * m_p2['Cpc']) + m_p2['Tci'])
    #m_p2['Tco'] = Tco_Eq2

    # ==================================== Check LMTD feasibility ====================================
    try:
        # LMTD of Equipment1
        lmtd1 = Calculations_HEX_LMTD.HEX_lmtd(m_p1['Thi'], m_p1['Tho'], m_p1['Tci'], m_p1['Tco'])

        # LMTD of Equipment2
        lmtd2 = Calculations_HEX_LMTD.HEX_lmtd(m_p2['Thi'], m_p2['Tho'], m_p2['Tci'], m_p2['Tco'])

        feasibility = True

    except (ValueError, ZeroDivisionError):

        feasibility = False

    return m_p_dict, feasibility

# endregion
##################################################################################################################

