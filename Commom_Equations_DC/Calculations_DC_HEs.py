###################################################################################################################
#region Titles and Header
# Nature: Heat Exchanger 
# Methodology: Set trimming + Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          27-Nov-2024     Alice Peccini             Proposed 
##################################################################################################################
# INPUT: Heat exchanger related functions
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def), input parameters and variables are defined in the "Examples_Repository.py" dictionary
#                          named Model_Declarations['Discretized_Values_of_Variables'] or in the one
#                          named Model_Parameters
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
import numpy as np
#endregion
##################################################################################################################

##################################################################################################################
#region Calculations

# --------------------------------------- LOG MEAN TEMPERATURE DIFFERENCE --------------------------------------- #

def fun_LMTD(Thin, Thout, Tcin, Tcout):

    teta1 = Thout - Tcin
    teta2 = Thin - Tcout

    if abs(teta1 - teta2) <= 1e-3:
        dTc = (teta1 + teta2)/2
    else:
        dTc = (teta1 - teta2)/np.log(teta1/teta2) 

    return dTc


# -------------------------------------------- HEAT EXCHANGER AREAS -------------------------------------------- #

def fun_HE_areas(Thin, Thout, Tcin, Tcout, Duty, U):

    # Heat Exchanger Area (m²)
    dTr = fun_LMTD(Thin, Thout, Tcin, Tcout)
    # Duty in W, U in (W/m².K)
    Area = Duty/(U*dTr) 

    return Area



#endregion
##################################################################################################################
