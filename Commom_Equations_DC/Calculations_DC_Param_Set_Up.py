###################################################################################################################
# region Titles and Header
# Nature: Parameter Update and Set Up Functions for DC models
# Methodology: Set trimming + Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          10-jun-2025     Alice Peccini             Proposed
##################################################################################################################
# INPUT: Functions to initialize, run and get results from Aspen Plus
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def), input parameters and variables are defined in the "Examples_Repository.py" dictionary
#                          named Model_Declarations['Discretized_Values_of_Variables'] or in the one
#                          named Model_Parameters
# endregion
##################################################################################################################

##################################################################################################################
# region Import Library
from Commom_Equations_DC import Calculations_DC_2FEEDS_Aspen


# endregion
##################################################################################################################

##################################################################################################################
# region Calculations

# Call Aspen Initialization (used for DC, DC_ST, DC_ST_HE, DC_ST_HE_RD and DC_ST_HE_RD_2D)

def call_initial_Aspen_2feeds(m_p):
    file_name = m_p['file_name'][0]
    stream_name1 = m_p['stream_names'][0]
    stream_name2 = m_p['stream_names'][1]
    block_name = m_p['block_name'][0]
    comp_name = m_p['Comp_name']
#FEED1
    z_feed1 = m_p['z_f'][0]  # Feed molar fractions
    F_feed1 = m_p['F_f'][0]  # Feed molar flow for each component
    T_feed1 = m_p['T_f'][0]  # Feed temperature
#FEED2
    z_feed2 = m_p['z_f'][1]  # Feed molar fractions
    F_feed2 = m_p['F_f'][1]  # Feed molar flow for each component
    T_feed2 = m_p['T_f'][1]  # Feed temperature

    P_col = m_p['Pcol']  # Column pressure
    x_TOP = m_p['xB_TOP']  # Top product purity
    x_BOTTOM = m_p['xB_BOTTOM']  # Bottom product purity
    D_LB = m_p['distillate_rate_bounds'][0]
    D_UB = m_p['distillate_rate_bounds'][1]
    RR_LB = m_p['reflux_ratio_bounds'][0]
    RR_UB = m_p['reflux_ratio_bounds'][1]

    m_p['Aspen_engine'] = Calculations_DC_2FEEDS_Aspen.fun_initial_Aspen(
        file_name, stream_name1,stream_name2, block_name, comp_name,
    z_feed1, F_feed1, T_feed1,z_feed2, F_feed2, T_feed2, P_col, x_TOP, x_BOTTOM,
        D_LB, D_UB, RR_LB, RR_UB)

    return m_p
