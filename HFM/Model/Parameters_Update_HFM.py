##################################################################################################################
# region Titles and Header
# Nature: 'Parameters_Calculations_List' and 'Example_Within_Set_Up' functions
# Methodology: Set trimming and Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          28-Fev-2025     Alice Peccini             Original
#   0.2          21-Mar-2025     Mariana Mello             Allocation as a parameter
#   0.3          12-May-2025     Mariana Mello             Update data consistency
#   0.4          06-Jun-2025     Mariana Mello             Update to fix error
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
import sys
from Common_Equations_MEM import Calculations_MEM_Consistency
from HFM.Model.Model_Def_HFM import Model_HFM
# endregion
##################################################################################################################


##################################################################################################################
# region Parameters Calculation functions
#
# Adjustment of the data

# def allocation(m_p):
#     if m_p['yfluid'] == 'cold_stream':
#         m_p['mt'] = m_p['mc']
#         m_p['rot'] = m_p['roc']
#         m_p['Cpt'] = m_p['Cpc']
#         m_p['mit'] = m_p['mic']
#         m_p['kt'] = m_p['kc']
#         m_p['Rft'] = m_p['Rfc']
#         m_p['DPtdisp'] = m_p['DPcdisp']

#         m_p['ms'] = m_p['mh']
#         m_p['ros'] = m_p['roh']
#         m_p['Cps'] = m_p['Cph']
#         m_p['mis'] = m_p['mih']
#         m_p['ks'] = m_p['kh']
#         m_p['Rfs'] = m_p['Rfh']
#         m_p['DPsdisp'] = m_p['DPhdisp']

#     elif m_p['yfluid'] == 'hot_stream':
#         m_p['mt'] = m_p['mh']
#         m_p['rot'] = m_p['roh']
#         m_p['Cpt'] = m_p['Cph']
#         m_p['mit'] = m_p['mih']
#         m_p['kt'] = m_p['kh']
#         m_p['Rft'] = m_p['Rfh']
#         m_p['DPtdisp'] = m_p['DPhdisp']

#         m_p['ms'] = m_p['mc']
#         m_p['ros'] = m_p['roc']
#         m_p['Cps'] = m_p['Cpc']
#         m_p['mis'] = m_p['mic']
#         m_p['ks'] = m_p['kc']
#         m_p['Rfs'] = m_p['Rfc']
#         m_p['DPsdisp'] = m_p['DPcdisp']
    
#     return m_p

# endregion
######################################################################################################################

# region Consistency

def consistency(m_d, m_p, save_result):
    save_result('\n******* Testing consistency *******\n')

    def variables_bounds(m_d):
        m_i = Model_HFM['Model_Info']
        variables = m_i['List_of_Variables']

        discrete_values = m_d['Discrete_Values_of_Variables']
        standard_values = m_i['Standard_Variables_Values']
        tol = 0.001

        out_of_limit = {}

        for name, values in zip(variables, discrete_values):
            standard_values_verif = standard_values.get(name, [])
            if not standard_values_verif:
                continue
            min_val = min(standard_values_verif)
            max_val = max(standard_values_verif)
            for v in values:
                if v < (min_val-tol) or v > (max_val+tol):
                    if name not in out_of_limit:
                        out_of_limit[name] = []
                    out_of_limit[name].append(v)

        if out_of_limit:
            save_result("WARNING: Variables out of range:")
            for var, vals in out_of_limit.items():
                save_result(f" - {var}: Invalid values {vals}\n")
        else:
            pass
        return m_d

    def variables_standard_values(m_d):
        m_i = Model_HFM['Model_Info']
        variables = m_i['List_of_Variables']

        discrete_values = m_d['Discrete_Values_of_Variables']
        standard_values = m_i['Standard_Variables_Values']
        tol = 0.001
        out = {}
        for name, values in zip(variables, discrete_values):
            standard_values_verif = standard_values.get(name, [])
            for v in values:
                value_c = False
                for std_val in standard_values_verif:
                    if abs(v - std_val) <= tol:
                        value_c = True
                if not value_c:
                    if name not in out:
                        out[name] = []
                    out[name].append(v)
        if out:
            save_result("WARNING: Variables do not match standard values")
            for var, vals in out.items():
                save_result(f" - {var}: Invalid values {vals}\n")
        else:
            pass
        return m_d



    verif1 = Calculations_MEM_Consistency.verification_positive_variables(m_p, save_result)
    verif2 = Calculations_MEM_Consistency.verification_Pfeed_Pperm(m_p, save_result)
    # verif4 = variables_bounds(m_d)
    # verif5 = variables_standard_values(m_d)
    return m_d, m_p


# endregion
##################################################################################################################
