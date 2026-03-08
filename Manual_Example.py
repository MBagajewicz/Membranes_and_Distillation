##################################################################################################################
# region Titles and Header
# Nature: Manual for Examples Repository Files
# Methodology: Dictionary
##################################################################################################################
# VERSION       DATE            AUTHOR                  DESCRIPTION OF CHANGES MADE
#   0.0         20-Mar-2025     Alice Peccini           Proposed  
##################################################################################################################
# INSTRUCTIONS: 
# Do not modify this file!
# This file is not used by Opticode; it serves solely as a manual guide for programmers.
##################################################################################################################
'''

Examples_(MODEL).py files

Location: 
Each model should have its own Examples_(MODEL).py file, located inside the corresponding model's main folder.

Content: 
These files contain example dictionaries with user-input example data. The required content may vary from model 
to model, depending on the model definitions.

This document provides a general overview of the possible inputs. However, more specific instructions — such as 
the allowed objective functions (for models where multiple options exist) and the default selection — must be 
provided at the beginning of each Examples_(MODEL).py file as an instruction for user.

'''
##################################################################################################################

##################################################################################################################
##################################################################################################################
# region INPUT Example Dictionary Default

# All examples must have at least two main keys (Number_of_Equipment and Equipment1), but additional keys may 
# be required depending on the example or model:
ExampleX = {

    'Number_of_Equipment': 1,       # Mandatory: Defines the number of equipment in the first optimization level.

    'Equipment1': {},               # Mandatory: At least one equipment key must be present.
    
    # Additional keys (optional, depending on the model):
    
    'Equipment2': {},               # If the first (or only) optimization level has more than one equipment

    'Equipment3': {},               # If the first (or only) optimization level has more than one equipment

    'Global_Optimizer': {},         # If it uses an external global optimizer

    'Next_Level_Equipments': {},    # If it is a two-level problem

}

# With the exception of 'Number_of_Equipment', each of these keys are dictionaries of their own, where:

# Each equipment dictionary constains two dictionaries within (Model_Declarations and Model_Parameters)
ExampleX['Equipment1'] = {

        'Model_Declarations': {     

            'Type_Equipment': 'STHE',   
            # Mandatory: This is the type of equipment, given as a string. 
            # 'STHE' is an example, must be a valid model (Case Sensitive)

            'Discrete_Values_of_Variables': [ [], [], ...],
            # Mandatory: This is a list of lists with the values of equipment's discrete design variables
            # They must be given in a predefined order, this information must be at the detailed instructions
            # for the user at the beggining of the Example file

            'Selected_OF': ['Cost_OF',''],
            # Optional: Specifies the selected objective function(s) for the problem. It must be a list of strings (case sensitive).
            # Some models may offer multiple objective function options — these, along with the default, should be
            # clearly documented in the user instructions at the beginning of the example file.
            # The first item in the list will be used as the primary criterion for minimization.
            # Additional items, if provided, will be used for display purposes only — unless the first criterion results
            # in multiple optimal solutions, in which case the next one(s) will be used as tie-breakers.
            # For a practical example, refer to the STRAY model.

            'Type_Enumeration': 'Exhaustive',
            # Optional: This entry gives the user the possibility to choose the type of enumeration to run
            # if the model required enumeration to be solved. 
            # 'Exhaustive', 'Smart' and 'Segmental_Smart' are the possibilities
            # If none is given, or this key is not initialized Smart Enumeration is used as default. 
            # To see an example go to DC model

            'Segmentation_Parameters' : ['Ns', 6, 0.5], 
            # This is required if 'Segmental_Smart' Enumeration is chosen, otherwise user do not need to enter this info
            # Segmentation_Parameters[0]: The name of the discrete variable needs to mach one of the variables 
            #                             given in 'List_of_Variables'
            # Segmentation_Parameters[1]: Increment (n° of values in each segment) 
            #                             -> If too small --> Excessive n° of intervals
            #                             -> If too large --> Candidates cutting may not be as effective
            # Segmentation_Parameters[2]: Correction factor to avoid small interval at the last segment
            # To see an example go to DC model)

            'Sorting_by_Variable': '',
            # Optional: This entry gives the name of the variable to be used when Sorting_by_Variable is active
            # If none is given, standard sorting will be performed

        },

        'Model_Parameters': {}
        # Mandatory: This dictionary contains all Problem_Parameters that user must enter for the computation of 
        # Constraint and Objective function values in "Constraints_and_OF_(Model).py" 
        # Required entries vary from model to model, and clear instructions must be given for user at the beggining of 
        # the Example file

}

# Global Optimizer dictionary is to be entrerd when a global external solver is required for a given model
ExampleX['Global_Optimizer'] = {

    'Lower_Bounds': [],
    'Upper_Bounds': [],
    # Mandatory: This are the upper and lower bounds for continuous design optimization variables of the
    # global optimizer. They must be given in a predefined order, this information must be at the detailed instructions
    # for the user at the beggining of the Example file. (to see an example go to Thermal_Loop model)

    'Selected_Optimizer': 'Direct',   
    # Optional: Default Optimizer is Direct Solver (and so far the only programmed option)

    },

# Next Level Equipment follows the same pattern as the first level problem, the number od equipments and equipment data 
# must be entered. To see an example go to DC_ST_HE 
ExampleX['Next_Level_Equipments'] = {

    'Number_of_Equipment': 2,

    'Equipment1': {},

    'Equipment2': {},

}


# endregion
###################################################################################################################
###################################################################################################################






