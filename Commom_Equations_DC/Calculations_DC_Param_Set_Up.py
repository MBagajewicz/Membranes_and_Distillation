###################################################################################################################
#region Titles and Header
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
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
from Commom_Equations_DC import Calculations_DC_Aspen
from HSTC.Model import Parameters_Update_HSTC
from Kettle_2.Model import Parameters_Update_Kettle_2
from Reflux_Drum.Model import Parameters_Update_Reflux_Drum

#endregion
##################################################################################################################

##################################################################################################################
#region Calculations

# Call Aspen Initialization (used for DC, DC_ST, DC_ST_HE, DC_ST_HE_RD and DC_ST_HE_RD_2D)

def call_initial_Aspen(m_p):

    file_name = m_p['file_name'][0]
    stream_name = m_p['stream_names'][0]
    block_name = m_p['block_name'][0]
    comp_name = m_p['Comp_name']
    z_feed = m_p['z_f']         # Feed molar fractions
    F_feed = m_p['F_f']         # Feed molar flow for each component
    T_feed = m_p['T_f']         # Feed temperature 
    P_col = m_p['Pcol']         # Column pressure
    x_TOP = m_p['xB_TOP']       # Top product purity
    x_BOTTOM = m_p['xB_BOTTOM'] # Bottom product purity
    D_LB = m_p['distillate_rate_bounds'][0]   
    D_UB = m_p['distillate_rate_bounds'][1]
    RR_LB = m_p['reflux_ratio_bounds'][0]
    RR_UB = m_p['reflux_ratio_bounds'][1]

    m_p['Aspen_engine'] = Calculations_DC_Aspen.fun_initial_Aspen(file_name, stream_name, block_name, comp_name,  
                                        z_feed, F_feed, T_feed, P_col, x_TOP, x_BOTTOM, D_LB, D_UB, RR_LB, RR_UB)
    
    return m_p

# Sieve Tray (Problem Within) set up (used for DC_ST, DC_ST_HE and DC_ST_HE_RD)
def SU_Sieve_Tray(results, m_p):

    # Liquid and vapor flows (converted from kg/hr to kg/s)
    m_p['Lw'] = (results['liquid_mass_flows'][1:-1]/3600).tolist()
    m_p['Vw'] = (results['vapor_mass_flows'][1:-1]/3600).tolist()

    # Hydraulics:
    m_p['rol'] = results['hydraulics']['density_liquid'].tolist()       # kg/m³
    m_p['rov'] = results['hydraulics']['density_vapor'].tolist()        # kg/m³
    m_p['sig'] = results['hydraulics']['surface_tension'].tolist()      # N/m

    # Number of stages:
    m_p['Nt'] = len(m_p['Lw'])

    return m_p

def SU_HSTC(results, m_p):

    # Hot stream - shell side
    m_p['m_s'] = results['liquid_mass_flows'][0]/3600                       # Flow rate (kg/s)
    m_p['Tin_s'] = results['temperatures'][1]                               # Inlet temperature of the hot stream (K)
    m_p['Tout_s'] = results['temperatures'][0]                              # Outlet temperature of the hot stream (K)

    m_p['ro_s'] = results['condenser_hot_stream']['liquid_density']         # Liquid density (kg/m³)
    m_p['rov_s'] = results['condenser_hot_stream']['vapor_density']         # Vapor density (kg/m³)
    m_p['mi_s'] = results['condenser_hot_stream']['liquid_viscosity']       # Liquid viscosity (Pa.s)
    m_p['miv_s'] = results['condenser_hot_stream']['vapor_viscosity']       # Vapor viscosity (Pa.s)
    m_p['k_s'] = results['condenser_hot_stream']['thermal_conductivity']    # Thermal conductivity (W/(m.K))
    m_p['Hvap_s'] = results['condenser_duty']/m_p['m_s']                    # Vaporization enthalpy (J/kg)         

    Parameters_Update_HSTC.fun_LMTD(m_p)
    Parameters_Update_HSTC.fun_Prt(m_p)
    m_p['Q'] = results['condenser_duty']
    Parameters_Update_HSTC.fun_m_t(m_p)

    return m_p

def SU_Kettle(results, m_p):

    # Cold stream - Shell side  
    m_p['m_s'] = results['liquid_mass_flows'][-2]/3600                      # Flow rate (kg/s)
    m_p['Tin_s'] = results['temperatures'][-2]                              # Inlet temperature of the cold stream (K)
    m_p['Tout_s'] = results['temperatures'][-1]                             # Outlet temperature of the cold stream (K)
    m_p['P_s'] = results['Pcol']                                            # Pressure (Pa)
    m_p['Pc'] = results['reboiler_cold_stream']['critical_pressure']        # Critical pressure (Pa)
    m_p['Hvap_s'] = results['reboiler_duty']/m_p['m_s']                     # Vaporization enthalpy (J/kg) 

    m_p['Q'] = results['reboiler_duty']
    Parameters_Update_Kettle_2.fun_Pr(m_p)
    Parameters_Update_Kettle_2.fun_Fp(m_p)
    Parameters_Update_Kettle_2.fun_m_t(m_p)
    Parameters_Update_Kettle_2.fun_LMTD(m_p)
    Parameters_Update_Kettle_2.fun_q1_max(m_p)

    return m_p

def SU_Reflux_Drum(results, m_p):

    m_p['m_L'] = results['liquid_mass_flows'][0] + results['mass_distillate_rate']    # Flow rate (kg/h)
    m_p['rho_L'] = results['distillate_liquid_mass_density']                          # Liquid density (kg/m³)
    Parameters_Update_Reflux_Drum.fun_vL(m_p)

    return m_p