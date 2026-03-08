##################################################################################################################
#region Titles and Header
# Nature: Matrix with all combinations of discrete variables Construction
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.2        30-Oct2024       Diego Oliva                Taken from Set_Triming_Engine.py developed by A. Costa
#   0.3        31-Oct-2024      Diego Oliva                Output variable inside a library was homogenized (library_output)
#   0.4        10-Nov-2024      Miguel Bagajewicz          Comments were revised
#   0.5        20-Nov-2024      Miguel Bagajewicz          No changes
#   0.6        12-May-2025      Mariana Mello              Changed name from 'Discretized_Values_of_Variables' to
#                                                         'Discrete_Values_of_Variables'
#   0.7        13-Ago-2025     Diego Oliva                 Prep Space faster version. Old version commented.
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
import numpy as np

#endregion
##################################################################################################################

##################################################################################################################
#region Call this function to create a Matrix with all posible combinations among your discrete variables

def Prep_Space(problem_space):
    Mat_candidates = np.meshgrid(*problem_space)

    # Organization of the search space
    # candidates = []
    candidates = [m.flatten() for m in Mat_candidates]

    # Conversion from list to array
    output = np.array(candidates)

    return output

# '''
# def Prep_Space(problem_space):

#     # Mesh creation (to mantain index)
#     new_spaces = np.meshgrid(*problem_space, indexing='ij')
#     # unpack combinations and put in a numpy.ndarray
#     candidates = np.vstack([new_space.ravel() for new_space in new_spaces])
#     return candidates

# #****************************************************************************************************************
#     # OLD VERSION COMMENTED
#     # # Creation of the command to generate the matrix of candidates
#     # var_par = ''
#     # for i in range(0,len(problem_space)):
#     #     var_par += 'problem_space[' + str(i) + ']'
#     #     if i != len(problem_space)-1:
#     #         var_par  += ', '

#     # # Combinatorial composition - Multidimensional
#     # Mat_candidates = eval('np.meshgrid(' + var_par + ')')

#     # # Organization of the search space
#     # candidates = []
#     # for i in range(0,len(Mat_candidates)):
#     #     candidates.append(Mat_candidates[i][Mat_candidates[i]>-1e10])


#     #
#     # The type of array is as follows:
#                                 #    cand1   cand2   cand3  ... cand(n-2) cand(n-1) candn
#     # discrete variable 1 --->  [[0.205   0.205   0.205   ... 1.524      1.524   1.524  ]
#     # discrete variable 2 --->  [0.01905 0.01905 0.01905 ... 0.0508     0.0508   0.0508 ]
#     # discrete variable 3 --->  [1.      1.      1.      ... 6.            6.      6.   ]
#     #...
#     #                           [0.25    0.25    0.25    ... 0.25         0.25    0.25  ]
#     #                           [1.      2.      3.      ... 1.            2.      3.   ]
#     # discrete variable n --->  [0.      0.      0.      ... 0.            0.      0.   ]]
#     #
#     # The matrix above has n columns and as many rows as variables.
#     #             Each Column is a possible combination of discrete variable values.
#     return output


# #endregion
# ##################################################################################################################