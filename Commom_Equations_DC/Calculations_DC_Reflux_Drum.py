###################################################################################################################
#region Titles and Header
# Nature: Reflux Drum
# Methodology: Set trimming + Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          20-Mai-2025     Alice Peccini             Proposed 
##################################################################################################################
# INPUT: Reflux Drum related functions
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
from math import pi
#endregion
##################################################################################################################

##################################################################################################################
#region Calculations


def fun_RD_Vol(m_L, rho_L, TRL_min):

    # Volumetric flow rate in m³/s from m_L in kg/h
    vol_L = m_L/3600/rho_L

    # Liquid control volume (m³)
    vol_LVC = vol_L*TRL_min*60

    # 20% for vapor phase (Walas) plus 10% for dead space at the bottom 
    vol_RD = vol_LVC/0.7

    return vol_RD

def fun_L_D(volume, L_D):

    # Diameter (m):
    D_RD = (4*volume/(pi*L_D))**(1/3)

    # Length (m):
    L_RD = L_D*D_RD

    return D_RD, L_RD
#endregion
##################################################################################################################
