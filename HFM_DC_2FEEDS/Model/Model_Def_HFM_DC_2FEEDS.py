##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.1         28-Feb-2025     Alice Peccini              Relocating folders
#   0.2         26-Oct-2026     Mariana Mello              Add 'Set_Up_Sequential' (HFM outlet feeds DC_2FEEDS) and
#                                                          syntax error correction
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add Examples of STHE in this file
##################################################################################################################

# region Import Library
# endregion

####################################################################################################################
####################################################################################################################

# region INPUT Model

Model_HFM_DC_2FEEDS = {

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
    
    #    'Model_Info': {
    
    #        'Parameters_Calculations_List': [],   #N_fiber is a routine that calculates the number of fibers given the 
            #                                               design variables values
            # This is a list of functions used to generated model calculated parameters and they must be defined 
            # in Model.Parameters_Update_(Model).py file 
            # These parameters are generated before Initial Set generation by Calculations_Initial_Set_Up.py
            # For bilevel optimization models (e.g. Kettle Model used in next_level of DC_ST_HE model), some of the 
            # functions of the list may be skipped and should be called by model programmer inside Next_Level_Set_Up
            # function
    
    #        'List_of_Variables': ['L','D','dfo_esp','Void_Frac'],  #length, shell diamter, fiber diameters, void fraction in the shell.
            
            # List of discrete design variables. User will give discrete options in example file in the same order as 
            # defined here, and this is also the same order that must be used in Constraints_and_OF.py functions
    
    #        'Objective_Function': {
    #            'Equation_Name': ['AREA_OF'],
    #            'Optimization_Variables_Names': ['Area'],
    #           'Unit_OF': ['m²']
    #       },
            # Objetive Function to be minimized and its corresponding variable and measurement unit
            # Equation_Name must be a function defined in "Constraints_and_FO.py" where Optimization_Variables_Names is 
            # its return variable. When more than one is given, user may select the desired objective function, but the
            # first one on the list will be the default if no selection is made
    
    
    
            # Functions that checks if Example Data provided by user has any consistency problems (e.g. negative flows or compositions)
            # These functions must be provided on Parameters_Update_{Model}.py file
            
#        },
    
        # ========================================= Set Trimming Information =========================================
        # Set Trimming Information section only needs to be filled if Set_Trimming_Mode is set to True. If not, 
        # model programmer may either leave an empty dictionary or completely skip the entry definition
    
    #   'Set_Trimming_Info': {
    
            # 'Primordial_Set_Trimming_Constraints_List': ['LD_lb', 'LD_ub', 'esp_LB', 'esp_UB', 'max_xret_proxy'],
#            'Primordial_Set_Trimming_Constraints_List': ['LD_LB_UB', 'esp_LB_UB'],
            # These are the Set_Trimming functions used for Initial Set Generation (they are applied to Primordial Set before
            # solver is called (e.g. Geometric Constraints, that do not depend on problem data)
            # Listed functions must be defined in Constraints_and_OF.py file
            # This entry is optional, if the list is empty, or if the entry is completely skipped, the Initial Set
            # will be the same as the Primordial Set
    
#            'Set_Trimming_Constraints_List': ['max_xret_proxy'],   # 'Dpr_max','Dpp_max'  these are proxy constraints
    
            #'Set_Trimming_Constraints_List': ['v_r_min','v_r_max','v_p_min','v_p_max','v_dti_min','v_dti_max','Re_r_min','Re_r_max','Re_p_min','Re_p_max','Dp_r_max','Dp_p_max'], 
            # Other constraints are proxy constraints
    
            # These are the Set Trimming Constraints to be applied to Initial Set when Solver is called
            # They also must be defined in Constraints_and_OF.py file
    
#            'Recursive_Set_Trimming': {
#                },
            # Recursive Set Trimming Option. It is Optional. If user defines the parameter with the same name, 
            # only one option would be evaluated. If user does not enter a valid option, Variable_Options will be used.
#        } ,
        # ========================================= Enumeration Information =========================================
    
#        'Enumeration_Info': {
    
#            'Enumeration_Constraint_List': ['Max_comp_ret_AND_Max_rec_perm'],
    
#            'Lower_Bound_Equation': ['LB_HFM'],
    
#            'Fobj_within_LB' : False
    
#       }
       # ========================================= Next Level Equipment =========================================

#         'Next_Level_Info': {

#           'Set_Up_Next_Level': {
#           'Equipment1': 'Set_Up_DC_2FEEDS'
#           }

#        },

       # ========================================= Sequential Set Up =========================================

        'Set_Up_Sequential': {
            'Equipment2': ['Set_Up_DC_2FEEDS']
        }
        # Functions (defined in Parameters_Update_HFM_DC_2FEEDS.py) that transfer the results of the previous
        # Equipment (HFM) to the Model_Parameters of the given Equipment (DC_2FEEDS). Only applied if 'update': True
        # is set in the Model_Parameters of the receiving Equipment in the example file

}

# endregion
