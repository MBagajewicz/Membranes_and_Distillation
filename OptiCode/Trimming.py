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
    trim = fun_val <= 0

    # Reduction of the set of candidates
    #
    # The number of columns of the candidates matrix is obtained

    Nvar = int(candidates.shape[0])

    # The matrix of candidates filled with a "True" or "False" attributes is created
    # Columns with a "False" are infeasible combinations because of the "fun" constraint violation)

    trimMat = np.tile(trim, (Nvar, 1))
    #
    # A boolean selection in the matrix candidates using boolean matrix trimMat is performed.
    #                   The result is a 1D vector with values of candidates of the matrix
    reduced_candidates_1D = candidates[trimMat]
    #
    # The number of columns is obtained using the length of 1D vector "reduced_candidates_1D"
    # The number of columns is needed to perform the transformation of the 1D vector "reduced_candidates_1D"
    #
    Ncand = int(reduced_candidates_1D.shape[0] / Nvar)

    # The 1D vector "reduced_candidates_1D" is transformed into a matrix
    #       (i.e. a matrix where infeasible problem combinations (columns with all False) were eliminated)

    library_output = np.reshape(reduced_candidates_1D, (Nvar, Ncand))

    # A matrix with feasible combinations in columns is returned.
    return library_output
# endregion
##################################################################################################################