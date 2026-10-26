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
  
def Set_Up_HFM_DC_2FEEDS(Separation, Limit_other_comp_Perm, m_p_dict):

    # ========================================= Parameters update =========================================
 
    m_p1 = m_p_dict['m_p1']
    m_p2 = m_p_dict['m_p2']

    m_p1['MAX_COMP_RET AND MAX_REC_PERM' '] = np.array([Separation, Limit_other_comp_Perm])


 # there are no changes needed in the spec of DC2FEEDS   m_p2['xx']  ...
    
   
        feasibility = True

 
    return m_p_dict, feasibility
# endregion
##################################################################################################################

