##################################################################################################################
#region Titles and Header
# Nature: Optimal solution obtained by sorting
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.2        30-Oct2024       Diego Oliva                Taken from Set_Triming_Engine.py developed by A. Costa
#   0.3        31-Oct-2024      Diego Oliva                Output variable inside a library is homogenized (library_output)
#   0.4        02-Nov-2024      Diego Oliva                New arguments OF_function,OF_variable to made more generic
#                                                          this library
#   0.5        06-Nov-2024      Diego Oliva                Name gen_sol.py of this file was changed by sorting.py
#   0.6        10-Nov-2024      Miguel Bagajewicz          Comments were revised
#   0.9        20-Nov-2024      Miguel Bagajewicz          Minor changes
#   0.10       10-Dec-2024      Mariana Mello              Add the type of equipment
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
from OptiCode import Constraint_Eval
import numpy as np
#endregion
##################################################################################################################

##################################################################################################################
#region Call this function to Obtain Optimal solution
def Sorting(candidates, problem_data, var_list, OF_function, OF_variable, Type_Equipment, Active_Models_Constraints):
    
    library_output = {}

    for Objective_Function, Objective_Variable in zip(OF_function, OF_variable):
      
        # The objective equation ("OF_function") is calculated for all combinations of candidates
        func = Constraint_Eval.Constraint_Eval(Objective_Function, candidates, problem_data, Type_Equipment, Active_Models_Constraints)
        
        # The minimum value of array "func" above is created
        func_min = np.amin(func)

        # Identify candidates with the min OF_Value
        indices = np.where(func == func_min)[0] 

        # Store the result: all best candidate indices for this variable value
        candidates = candidates[:, indices]

        # Number of candidates with fun = fun_min
        num_candidates = candidates.shape[1]

        library_output[Objective_Function] = {Objective_Variable: func_min, 'Number_of_solutions': num_candidates}

    # Populate the dictionary with the discrete variable values corresponding to the best candidate
    for j, var in enumerate(var_list):
        library_output[var] = candidates[j, 0]

    return library_output
#endregion
##################################################################################################################