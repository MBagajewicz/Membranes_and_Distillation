##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION       DATE            AUTHOR                  DESCRIPTION OF CHANGES MADE
#   0.0         28-Feb-2025     Alice Peccini           Standard Model for Examples File
#   0.1         17-Mar-2025     Alice Peccini           Separation of Examples Files in Model_Def and Example
#   0.2         12-May-2025     Mariana Mello           Add data consistency
##################################################################################################################
# INPUT: Do not Modify this file!
##################################################################################################################
# INSTRUCTIONS
'''
Model_Def_(MODEL).py file contains a dictionary with Model Definitions that do not change from Example to Example
This file shows the standard format for this Dictionary
'''
##################################################################################################################

##################################################################################################################
##################################################################################################################
# region INPUT Model_MODEL Dictionary Default

Model_MODEL = {

    # =========================================== General Information ============================================
    # The first entries are General (True or False) Information regarding the Model Operation Mode.
    # These entries are required for all models

    'Global_Optimizer': False,      # Set to True if model requires an external global solver. False otherwise

    'Next_Level': False,            # Set to True if model involves a bilevel optimization. False otherwise

    'Set_Trimming_Mode': False,     # Set to True Set Trimming Mode is selected. False otherwise

    'Sorting_Mode': False,          # Set to True if Sorting is required after Trimming. False otherwise

    'Enumeration_Mode': False,      # Set to True if an Enumeration Mode is to be activated (Enumeration type will 
                                    # be selected by user within Example Data if this is set to True)

    # ============================================= Model Information ============================================
    # This entry is required for all models

    'Model_Info': {

        'Parameters_Calculations_List': [],
        # This is a list of functions used to generated model calculated parameters and they must be defined 
        # in Model.Parameters_Update_(Model).py file 
        # These parameters are generated before Intial Set generation by Calculations_Initial_Set_Up.py
        # For bilevel optimization models (e.g. Kettle Model used in next_level of DC_ST_HE model), some of the 
        # functions of the list may be skipped and should be called by model programmer inside Next_Level_Set_Up function

        'List_of_Variables': ['' , '' , ''],
        # List of discrete design variables. User will give discrete options in example file in the same order as 
        # defined here, and this is also the same order that must be used in Constraints_and_OF.py functions

        'Objective_Function': {'Equation_Name': [''], 'Optimization_Variables_Names': [''], 'Unit_OF': ['']},
        # Objetive Function to be minimized and its corresponding variable and measurement unit
        # More than one option can be defined as possible. The order in which they are defined are the default order
        # in which they will be applied. 
        # The first item in the list will be used as the primary criterion for minimization.
        # Additional items, if provided, will be used for display purposes only — unless the first criterion results
        # in multiple optimal solutions, in which case the next one(s) will be used as tie-breakers.
        # User may choose a different order with 'Selected_OF' entry in the Example file
        # Equation_Name must be a function defined in "Constraints_and_FO.py" where Optimization_Variables_Names is 
        # its return variable. 
        # For a practical example, refer to the STRAY model.

        'Set_Up_Sequential': {'EquipmentX': ''},
        # This is a dictionary with functions used to generated model calculated parameters that depend on the
        # result of a previous Equipment. Which means that the order in which example data are given in the example 
        # data would be predefined by model programmer and must be on the instructions for example file user. 
        # To see an example go to STRAY_2D

        'Consistency_Check_Functions' : [''],
        'Standard_Variables_Values': {
            '': [],
            '': [],
            '': []
        ...
        }
        # Functions that checks if Example Data provided by user has any consistency problems (e.g. negative flows or compositions)
        # These functions msut be provided on Parameters_Update_{Model}.py file

    },

    # ========================================= Set Trimming Information =========================================
    # Set Trimming Information section only needs to be filled if Set_Trimming_Mode is set to True. If not, 
    # model programmer may either leave an empty dictionary or completly skip the entry definition

    'Set_Trimming_Info': {

        'Primordial_Set_Trimming_Constraints_List': ['', '' ],
        # These are the Set_Trimming functions used for Initial Set Generation (they are applied to Primordial Set before
        # solver is called (e.g. Geometric Constraints, that do not depend on problem data)
        # Listed functions must be defined in Constraints_and_OF.py file
        # This entry is optional, if the list is empty, or if the entry is completly skipped, the Initial Set 
        # will be the same as the Primordial Set

        'Set_Trimming_Constraints_List': ['', ''],
        # These are the Set Set Trimming Constraints to be applied to Initial Set when Solver is called
        # They also must be defined in Constraints_and_OF.py file

        'Recursive_Set_Trimming': {
            'Variable_Name': '',
            'Variable_Options': [],
            'ST_Exclusion_Functions': []
            },
        # Recursive Set Trimming Option. It is Optional. If user defines the parameter with the same name, 
        # only one option would be evaluated. If user does not enter a valid option, Varible_Options will be used.
        # ST Exclusion Functions are the Objective Function that can not be applied for recursive trimming
        # To see an example go to STHE
    },

    # ========================================= Enumeration Information =========================================
    # Enumeration Information section only needs to be filled if Enumeration_Mode is set to True. If not, 
    # model programmer may either leave an empty dictionary or completly skip the entry definition
    # To see an example go to DC model

    'Enumeration_Info': {

        'Enumeration_Constraint_List': [],
        # These are feasibility constraints that may be required to check candidate feasibility during enumeration 
        # Listed functions must be defined in Constraints_and_OF.py file
        # This entry is optional, if the list is empty, or if the entry is completly skipped, feasibility 
        # wont be checked by Enumeration routine, it will be assumed as true

        'Lower_Bound_Equation': [],
        # This are the lower bound generation functions required for smart and segmental enumerations
        # If two different functions are to be used for each type of enumeration, the list must have two positions
        # ['fun_LB_Smart','fun_LB_Segmental']. If the same funtion is to be used programmer may either leave it 
        # with a single position, or repeat the function name 

        'Fobj_within_LB' : False, 
        # This must be set to True if candidate's Objective Function are evaluated within LB generation function
    },

    # ========================================= Global Optimizer Information =======================================
    # Equipment Loop Information section only needs to be filled if Global_Optimizer is set to True
    # To see an example go to Thermal Loop

    'Global_Optimizer_Info': {

        'Optimization_Variables': ['', '', ''],
        # List of continuous global optimizer design variables. User will give lower and upper bounds in example file
        # for each variable in the same order as defined here, and this is also the same order that must be used in 
        # Parameters_Update_Model.py function from next entry

        'Set_Up_Global_Optimizer': ''
        # This function will be used inside global optimizer to generate Equipments problem parameters during the 
        # search that may depend on the external variable of global optimizer search 

    },

    # ========================================= Next Level Equipment =========================================
    # Next Level Information section only needs to be filled if Next_Level is set to True
    'Next_Level_Info': {

        'Set_Up_Next_Level': {
            'Model1': '',
            'Model2': '',
        }
    },

}

# endregion
###################################################################################################################
###################################################################################################################

