##################################################################################################################
# region Titles and Header
# Nature: Constraint evaluations
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.2        30-Oct2024       Diego Oliva                Taken from Set_Triming_Engine.py developed A. Costa
#   0.3        31-Oct-2024      Diego Oliva                Output variable inside a library is homogenized (library_output)
#   0.4        10-Nov-2024      Miguel Bagajewicz          Review comments
#   0.9        20-Nov-2024      Miguel Bagajewicz          Routine name Change from 'constr.py"
#                                                          Changes in other functions names
#                                                          Some variable names also changed
#   0.10       10-Dec-2024      Mariana Mello              Add the type of equipment
#   0.11       03-Fev-2024      Alice Peccini              Include Dist_Column as Type_Equipment
#   0.12       28-Fev-2025      Alice Peccini              OptiProcess Code Structure Update 
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
# endregion
##################################################################################################################


##################################################################################################################
# region Call this function to Evaluate Constraints
def Constraint_Eval(fun, candidates, problem_data, Type_Equipment, Active_Models_Constraints):
    # Preliminary processing 
    # This generated a list of arguments where candidates[i] go from row 0 to the last row n in the candidates matrix
    #                                 (i.e. it enumerates the discretized variables of the problem from i to n)
    args = []
    for i in range(candidates.shape[0]): args.append(candidates[i])
    args.append(problem_data)
    # Evaluation of the constraint
    #
    # The python library "eval" function is used to evaluate a function written as a string
    #                                          (the string has a concatenated text with parts above detailed)
    # Here we are passing rows of candidates (or sets of discretized variables ordered in combinatorial candidates
    # matrix) to be evaluated by functions in Constraints_and_OF
    # Functions in Constraints_and_OF will use or not some of the rows
    # In Constraints_and_OF input discretized variables need to be ordered as the rows in candidates matrix

    # Construct the module name dynamically
    module_name = Active_Models_Constraints[Type_Equipment]

    # Call the function dynamically using getattr()
    library_output = getattr(module_name, fun)(*args)

    # DO Comments
    # The output of this function are results of the functions in Constraints_and_OF depending on the required input
    # "fun" that needs to be evaluated
    return library_output

# endregion
##################################################################################################################