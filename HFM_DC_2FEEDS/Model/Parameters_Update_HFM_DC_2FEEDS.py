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
from Common_Equations_MEM import (
     Calculations_HFM_Results_Transfer_to_other_models
    )
 
# endregion
##################################################################################################################


##################################################################################################################
# region Parameters Calculation functions
  
 


def Set_Up_DC_2FEEDS(results, m_p):

    m_p = Calculations_HFM_Results_Transfer_to_other_models.SU_DC_2FEEDS(results, m_p)

    return m_p





    
# endregion
##################################################################################################################

