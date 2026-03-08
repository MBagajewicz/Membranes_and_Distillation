##################################################################################################################
# region Titles and Header
# Nature: Constraint evaluations
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.1      15-Ago-2025      Diego Oliva                Based on Constraint_Eval.py V0.12
##################################################################################################################
# INPUT: No inputs allowed
##################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete this file !!!!!
# endregion
##################################################################################################################


##################################################################################################################
# region Call this function to Evaluate Constraints
def Constraint_Eval(fun, candidates, variables_of_const, problem_data, Type_Equipment, Active_Models_Constraints,trimming_Info):
    # Preliminary processing 
    # This generated a list of arguments where candidates[i] go from row 0 to the last row n in the candidates matrix
    #                                 (i.e. it enumerates the discretized variables of the problem from i to n)
    args = [] 
    for i in range(candidates.shape[0]): args.append(candidates[i]) 
    args.append(problem_data) 

    names_to_kwargs = variables_of_const + ['m_p']

    for elem in trimming_Info['All_Variables_In_The_Problem']:
        if elem not in variables_of_const:
            names_to_kwargs.append(elem)

    # kwargs = {names_to_kwargs[i]: args[i] for i in range(len(args))}

    kwargs = {
    names_to_kwargs[i]: args[i] if i < len(args) else []
    for i in range(len(names_to_kwargs))
    }


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
    library_output = getattr(module_name, fun)(**kwargs)

    # DO Comments
    # The output of this function are results of the functions in Constraints_and_OF depending on the required input
    # "fun" that needs to be evaluated
    return library_output

# endregion
##################################################################################################################