#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          20-Mar-2025     Alice Peccini             Proposed 
##################################################################################################################
##################################################################################################################
#endregion

#region Import Library
import numpy as np
from OptiCode import Constraint_Eval
#endregion

####################################################################################################################
#region Create Set Trimming Function

def Fobj_Trim(fun, candidates, problem_data, Type_Equipment, Active_Models_Constraints, Best_Sol):

    FOBJ = Constraint_Eval.Constraint_Eval(fun, candidates, problem_data, Type_Equipment, Active_Models_Constraints)
    
    fun_val = FOBJ - Best_Sol

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


#endregion
####################################################################################################################

