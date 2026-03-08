##################################################################################################################
#region Titles and Header
# Nature: Cost functions
# Methodology: Set trimming + Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          27-Nov-2024     Alice Peccini             Proposed 
##################################################################################################################
# INPUT: Cost calculation related functions
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
from Commom_Equations_DC import Calculations_DC_Column_Sizing
#endregion
##################################################################################################################

##################################################################################################################
#region Calculations=

def Towler_and_Sinnot_Cost_Function(a,b,n,S):

    CAPEX = a + b*S**n

    return CAPEX

def CAPEX_Shell_and_Tube(Area): # Area must me in m²

    CAPEX_STHE = Towler_and_Sinnot_Cost_Function(28000, 54, 1.2, Area)

    return CAPEX_STHE

def CAPEX_Kettle(Area): # Area must me in m²

    CAPEX_Kettle = Towler_and_Sinnot_Cost_Function(29000, 400, 0.9, Area)

    return CAPEX_Kettle

def fun_CAPEX_Col(Wshell,Dc,Nt): # Wshell must be in kg and Dc in m

    CAPEX_trays = Towler_and_Sinnot_Cost_Function(130, 440, 1.8, Dc)*Nt
    CAPEX_shell = Towler_and_Sinnot_Cost_Function(11600, 34, 0.85, Wshell)
    # print('CAPEX_trays',CAPEX_trays)
    # print('CAPEX_shell',CAPEX_shell)
    CAPEX_Col = CAPEX_trays + CAPEX_shell

    return CAPEX_Col

def fun_CAPEX_Reflux_Drum(L,D,roshell):

    twall = Calculations_DC_Column_Sizing.f_twall(D)
    W_RD = pi*roshell*D*L*twall
    CAPEX_RD = Towler_and_Sinnot_Cost_Function(10200, 31, 0.85, W_RD)

    return CAPEX_RD

def fun_Utility_Costs(Util_cost, Duty, hours): 
    # Util_cost in $/kJ, Duty in W, and hours in h/year --> Util_Costs in $/year
    Duty_kJ_hr = Duty*3600/1000 # convert from W to kJ/h
    Util_Costs = Util_cost*Duty_kJ_hr*hours

    return Util_Costs

#endregion
##################################################################################################################
