###################################################################################################################
# region Titles and Header
# Nature: Here we put the constraints and Objective Function used in Set Trimming
# methodology
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          2024            Diego Oliva               Original
#   0.2          01-Dec-2024     Mariana Mello             Add constraints
#   0.3          03-Mar-2025     Mariana Mello             Changes after add options of tube and shell methods
#   0.4          23-Apr-2025     Mariana Mello             Update to fix error and add constraint Fmin
#   0.5          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
# INPUT: Define Constraints as def and return + or - values depending the > or < inequality
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def)  for each constraint defined in the "Examples_Repository.py" dictionary
#                          named Model_Declarations['Active_Constraints_List']
# Then add an Objective Function to be minimized before declared in:
#                            Model_Declarations['Standard_Objective_Function']['Equation_Name']
# Finally, add the Lower Bound x
# endregion
############################################################################################

##################################################################################################################
# region Import Library
from math import pi
from HFM.Calculations import (
Calculations_HFM_Area,
Calculations_HFM_Recovery,
Calculations_HFM_Nf,
Calculations_HFM_Min_Thickness,
Calculations_HFM_y_estimate
)
# from Common_Equations_HEX import Calculations_HEX_LMTD, Calculations_HEX_heatload
# endregion
##################################################################################################################

##################################################################################################################
# region Constraints
# Negatives survive

def dfo_dfi(L,D,dfo,dfi,Void_Frac,m_p):
    # dfi < dfo
    fun_val = dfi-dfo + 1e-6 # +1e-6 to remove equal diameters
    return fun_val

def LD_lb(L,D,dfo,dfi,Void_Frac,m_p):
    # Lower bound on L/Ds
    fun_val = m_p['LDLB'] - L / D
    return fun_val

def LD_ub(L,D,dfo,dfi,Void_Frac,m_p):
    # Upper bound on L/Ds
    fun_val = L/D -m_p['LDUB']
    return fun_val

# def HFM_shell_velocity(L,D,dfo,dfi,Void_Frac,m_p): #todo
#     Ntf = Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
#     vel_s = Calculations_HFM_Velocity_Shell(molar_flow_shell, comp_shell, M, rho, D, dfo, Ntf)
#     return vel_s

def max_recovery_proxy(L,D,dfo,dfi,Void_Frac,m_p):
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Area = Ntf * pi * dfo * L

    x_feed = (m_p['U_Feed_Target'][:, None] / sum(m_p['U_Feed_Target']))

    Key_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY'])
    y_end = Calculations_HFM_y_estimate.estimate_y_pc_multicomponent(Q=m_p['Q'],A_t=Area, Pf=m_p['P_Feed'],Pp=m_p['P_Permeate'],
                                                                     F_f=m_p['f_total'],x_feed=m_p['comp_f'],Key_Comp_index=Key_Comp_index)

    max_transfer = m_p['Q'][:, None] * Area * (m_p['P_Feed'] * x_feed - m_p['P_Permeate'] * y_end.reshape(3,-1))

    fun_val = m_p['REC_MIN_PROXY'] - (max_transfer/m_p['U_Feed_Target'][:, None])[Key_Comp_index,:]
    return fun_val

def esp_LB(L,D,dfo,dfi,Void_Frac,m_p):
    # Upper bound on L/Ds
    esp_min = Calculations_HFM_Min_Thickness.Min_Thickness(m_p['P_Feed'], m_p['P_Permeate'], dfo, m_p['E'], m_p['sigma_y'], m_p['nu'], m_p['degradation_factor'], m_p['safety_factor'])
    fun_val = esp_min - (dfo - dfi)
    return fun_val

def esp_UB(L,D,dfo,dfi,Void_Frac,m_p):
    # Upper bound on L/Ds
    esp_min = Calculations_HFM_Min_Thickness.Min_Thickness(m_p['P_Feed'], m_p['P_Permeate'], dfo, m_p['E'], m_p['sigma_y'], m_p['nu'], m_p['degradation_factor'], m_p['safety_factor'])
    fun_val = - 10e-6 - (esp_min - (dfo - dfi)) # a menor diferença entre uma espessura e a próxima é 10e-6
    # 0 <- (dfo - dfi - esp_min) <= 10e-6
    # print(esp_min)
    return fun_val
######################################################################################################################

# region LB function

# -------------------------------------------------------------------------------------------------------------------
# Lower Bound Function
# --------------------------------------------------------------------------------------------------------------------

def Recovery(L,D,dfo,dfi,Void_Frac,m_p):
    # Lower bound on recovery
    # N_partitions = m_p['N_Partitions']
    # Dz = L / N_partitions
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    # Key_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY'])
    recovery= Calculations_HFM_Recovery.model_HFM_Recovery(L,D,dfo,dfi,Void_Frac,m_p,Ntf)
    fun_val = m_p['REC_MIN'] - recovery
    return [fun_val]

def LB_HFM(L,D,dfo,dfi,Void_Frac,m_p):
    # Lower bound using the Area
    Ntf=Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    LB = Calculations_HFM_Area.HFM_area(dfo, L, Ntf)
    return LB

# endregion
######################################################################################################################

# region Objective Functions

def LB_Gen():
    # Lower bound -
    pass

def AREA_OF(L,D,dfo,dfi,Void_Frac,m_p):
    Ntf=Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    Area = Calculations_HFM_Area.HFM_area(dfo, L, Ntf)
    return Area

# endregion
##################################################################################################################
