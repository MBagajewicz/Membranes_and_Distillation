##################################################################################################################
# region Titles and Header
# Nature: Trimming by Constraints
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.2        30-Oct2024       Diego Oliva                Taken from Set_Triming_Engine.py developed by A. Costa
#   0.3        31-Oct-2024      Diego Oliva                Output variable inside a library is homogenized (library_output)
#   0.4        10-Nov-2024      Miguel Bagajewicz          Comments were revised
#   0.9        20-Nov-2024      Miguel Bagajewicz          Changes in other functions names
#   0.10       10-Dec-2024      Mariana Mello              Add the type of equipment
#   0.11       31-Mar-2026      João Tupinambá             Adapted for array of constraints + optimization
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
# endregion
##################################################################################################################

##################################################################################################################
# region Import Library
import numpy as np
from OptiCode import Constraint_Eval
# endregion
##################################################################################################################

##################################################################################################################
# region This function is used to trim a candidates set using a specific constraint

def Trimming(fun, candidates, problem_data, Type_Equipment, Active_Models_Constraints):
    # Evaluation of a constraint

    fun_val = Constraint_Eval.Constraint_Eval(fun, candidates, problem_data, Type_Equipment, Active_Models_Constraints)

    # The value "True" or "False" is assigned to a trimming constraint depending on (fun_val <= 0)
    #                                                    - (False for infeasible)
    # fv is the array of fun_val and has shape (N_candidates,N_constraints)
    fv = np.asarray(fun_val)

    # The array of candidates filled with a "True" or "False" attributes is created
    # Columns with a "False" are infeasible combinations because of the "fun" constraint violation)
    # trim is the array of boolean values, lines represent candidates, columns represents constraints
    if fv.ndim == 1: # One constraint for each candidate
        trim = fv <= 0
    else:
        trim = np.all(fv <= 0, axis=0) # multiple constraints (usually upper and lower bound) for each candidate

    # Reduction of the set of candidates

    # A boolean selection in the matrix candidates using boolean array trim is performed.
    reduced_candidates = candidates[:, trim]

    return reduced_candidates
# endregion
##################################################################################################################