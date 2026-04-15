##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.2         28-Feb-2025     Alice Peccini              Relocating folders
#   0.3         08-May-2025     Mariana Mello              Add consistency check
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add STHE Model info in this file
####################################################################################################################
####################################################################################################################
import numpy as np
# region

Model_HFM = {

    # =========================================== General Information ============================================
    # The first entries are General (True or False) Information regarding the Model Operation Mode.
    # These entries are required for all models

    'Global_Optimizer': False,      # Set to True if model requires an external global solver. False otherwise

    'Next_Level': False,            # Set to True if model involves a bilevel optimization. False otherwise

    'Set_Trimming_Mode': True,      # Set to True Set Trimming Mode is selected. False otherwise

    'Sorting_Mode': True,           # Set to True if Sorting is required after Trimming. False otherwise

    'Enumeration_Mode': True,      # Set to True if an Enumeration Mode is to be activated (Enumeration type will
                                    # be selected by user within Example Data if this is set to True)

    # ============================================= Model Information ============================================
    # This entry is required for all models

    'Model_Info': {

        'Parameters_Calculations_List': [],   #N_fiber is a routine that calculates the number of fibers given the 
        #                                               design variables values
        # This is a list of functions used to generated model calculated parameters and they must be defined 
        # in Model.Parameters_Update_(Model).py file 
        # These parameters are generated before Initial Set generation by Calculations_Initial_Set_Up.py
        # For bilevel optimization models (e.g. Kettle Model used in next_level of DC_ST_HE model), some of the 
        # functions of the list may be skipped and should be called by model programmer inside Next_Level_Set_Up
        # function

        'List_of_Variables': ['L','D','dfo_esp','Void_Frac'],  #length, shell diamter, fiber diameters, void fraction in the shell.
        
        # List of discrete design variables. User will give discrete options in example file in the same order as 
        # defined here, and this is also the same order that must be used in Constraints_and_OF.py functions

        'Objective_Function': {
            'Equation_Name': ['AREA_OF'],
            'Optimization_Variables_Names': ['Area'],
            'Unit_OF': ['m²']
        },
        # Objetive Function to be minimized and its corresponding variable and measurement unit
        # Equation_Name must be a function defined in "Constraints_and_FO.py" where Optimization_Variables_Names is 
        # its return variable. When more than one is given, user may select the desired objective function, but the
        # first one on the list will be the default if no selection is made

        'Consistency_Check_Functions': ['consistency'],
        'Standard_Variables_Values': {
            'L': list(np.round(np.linspace(0.5,2,16),2)),
            'D': list(np.linspace(50,200,16)*1e-3),
            # 'dfo': list(np.linspace(50,200,16)*1e-6), # 50,60,70... | Richard W. Baker(auth.) - Membrane Technology and Applications pg 148
            'dfo_esp': ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
            'Void_Frac': list(np.round(np.linspace(0.2,0.6,41),2)) # 0.30,0.31,0.32...
        }

        # Functions that checks if Example Data provided by user has any consistency problems (e.g. negative flows or compositions)
        # These functions must be provided on Parameters_Update_{Model}.py file
        
    },

    # ========================================= Set Trimming Information =========================================
    # Set Trimming Information section only needs to be filled if Set_Trimming_Mode is set to True. If not, 
    # model programmer may either leave an empty dictionary or completely skip the entry definition

    'Set_Trimming_Info': {

        'Primordial_Set_Trimming_Constraints_List': ['LD_lb', 'LD_ub', 'esp_LB', 'esp_UB', 'max_recovery_proxy'],
        # These are the Set_Trimming functions used for Initial Set Generation (they are applied to Primordial Set before
        # solver is called (e.g. Geometric Constraints, that do not depend on problem data)
        # Listed functions must be defined in Constraints_and_OF.py file
        # This entry is optional, if the list is empty, or if the entry is completely skipped, the Initial Set
        # will be the same as the Primordial Set

        'Set_Trimming_Constraints_List': [],   # 'Dpr_max','Dpp_max'  these are proxy constraints

        #'Set_Trimming_Constraints_List': ['v_r_min','v_r_max','v_p_min','v_p_max','v_dti_min','v_dti_max','Re_r_min','Re_r_max','Re_p_min','Re_p_max','Dp_r_max','Dp_p_max'], 
        # Other constraints are proxy constraints

        # These are the Set Trimming Constraints to be applied to Initial Set when Solver is called
        # They also must be defined in Constraints_and_OF.py file

        'Recursive_Set_Trimming': {
            },
        # Recursive Set Trimming Option. It is Optional. If user defines the parameter with the same name, 
        # only one option would be evaluated. If user does not enter a valid option, Variable_Options will be used.
    } ,
    # ========================================= Enumeration Information =========================================

    'Enumeration_Info': {

        'Enumeration_Constraint_List': ['Recovery'],

        'Lower_Bound_Equation': ['LB_HFM'],

        'Fobj_within_LB' : False

    }
}

if __name__ == '__main__':
    import numpy as np
    from itertools import product

    diametros = np.round(np.linspace(50, 300, 26) * 1e-6, 6)
    espessuras = np.round(np.linspace(20, 150, 14) * 1e-6, 6)

    lista_strings = [
        f"({a},{b})"
        for a, b in product(diametros, espessuras)
        if b < a / 2
    ]

    print(lista_strings[:10])
    print(len(lista_strings))