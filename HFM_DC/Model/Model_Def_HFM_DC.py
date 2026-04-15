##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.1         28-Feb-2025     Alice Peccini              Relocating folders 
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

Model_HFM_DC = {

    # =========================================== General Information ============================================
    # The first entries are General (True or False) Information regarding the Model Operation Mode.
    # These entries are required for all models

    'Global_Optimizer': True,       # Set to True if model requires an external global solver. False otherwise

    'Next_Level': False,            # Set to True if model involves a bilevel optimization. False otherwise

    'Set_Trimming_Mode': False,     # Set to True Set Trimming Mode is selected. False otherwise

    'Sorting_Mode': False,          # Set to True if Sorting is required after Trimming. False otherwise

    'Enumeration_Mode': False,      # Set to True if an Enumeration Mode is to be activated (Enumeration type will 
                                    # be selected by user within Example Data if this is set to True)

    # ============================================= Model Information ============================================
    # This entry is required for all models

    # 'Model_Info': {

    #     'Parameters_Calculations_List': [],
    #     # This is a list of functions used to generated model calculated parameters and they must be defined 
    #     # in Model.Parameters_Update_(Model).py file 
    #     # These parameters are generated before Initial Set generation by Calculations_Initial_Set_Up.py
    #     # For bilevel optimization models (e.g. Kettle Model used in next_level of DC_ST_HE model), some of the 
    #     # functions of the list may be skipped and should be called by model programmer inside Next_Level_Set_Up function

    #     'List_of_Variables': [],
    #     # List of discrete design variables. User will give discrete options in example file in the same order as 
    #     # defined here, and this is also the same order that must be used in Constraints_and_OF.py functions

    #     'Objective_Function': {},
    #     # Objetive Function to be minimized and its corresponding variable and measurement unit
    #     # Equation_Name must be a function defined in "Constraints_and_FO.py" where Optimization_Variables_Names is 
    #     # its return variable. 

    #     'Alternative_Objective_Functions': {
    #         'Equation_Name': [],
    #         'Optimization_Variables_Names': [],
    #         'Unit_OF': []
    #     },
    #     # This entry is OPTIONAL. If only one objective function is possible for a given model, programmer may either
    #     # leave it empty, or completely skip it. This is for models where alternative objective functions are possible
    #     # User will select the desired function in Examples file 
    #     # Objective_Function entry is used as DEFAULT
        
    # },

    # ========================================= Equipment Loop Information =======================================

    # Equipment Loop Information section only needs to be filled if Model['Set_Trimming'] is set to True
    'Global_Optimizer_Info': {

        'Unit_OF': '$/year',

        'Optimization_Variables': ['Sep'],

        'Set_Up_Global_Optimizer': 'Set_Up_HFM_DC'

    }

}
