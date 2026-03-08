##################################################################################################################
#region Titles and Header
# Nature: Optimal solution obtained by sorting
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0        19-Mar-2025       Alice Peccini             Original - Proposed
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
from OptiCode import Sorting
import numpy as np
#endregion
##################################################################################################################

##################################################################################################################
#region Call this function to Obtain Optimal solution
def Sorting_by_Variable(candidates, problem_data, var_list, OF_function, OF_variable, Type_Equipment, 
                        Active_Models_Constraints, SO_Variable):

    # Identify SO_Variable and its corresponding values:
    index_var = var_list.index(SO_Variable)     # Index for variable
    values_var = candidates[index_var, :]       # Candidates values for SO_Variable
    unique_values = np.unique(values_var)       # Distinct values for SO_Variable
 
    library_output = {}

    # For each SO_Variable:
    for j, val in enumerate(unique_values):

        # Create a string for results storage
        name = f'{SO_Variable}{j+1}'

        # Get the indices of candidates that match this variable value
        indices = np.where(values_var == val)[0]  

        # Get candidates with this variable value
        candidates_by_variable = candidates[:, indices]

        # Perform Sorting for this set of candidates:
        library_output[name] = Sorting.Sorting(candidates_by_variable, problem_data, var_list, OF_function, OF_variable,
                                               Type_Equipment, Active_Models_Constraints)
            
    # Selects the best solution found among all values of SO_Variable
    keys = [key for key in library_output if key.startswith(SO_Variable)]                   # Detecting name keys
    best_key = min(keys, key=lambda k: library_output[k][OF_function[0]][OF_variable[0]])   # Detects best solution
    # Updates upper level of library output with internal keys of library_output[best_key]
    for subkey, value in library_output[best_key].items():
        library_output[subkey] = value

    # The library_output dictionary contains the combination of discrete variables and OF_variables at the Optimum
    return library_output

#endregion
##################################################################################################################