##################################################################################################################
#region Titles and Header
# Nature: Exhaustive Enumeration
# Methodology: Enumeration
##################################################################################################################
# VERSION        DATE             AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0       28-Jan-2025        Alice Peccini              Proposed
#   0.2       28-Fev-2025        Alice Peccini              OptiProcess Code Structure Update
#   0.3       27-Apr-2025        Mariana Mello              Add .txt file with Results of Examples
#   0.4       13-May-2025        Mariana Mello              Update .txt file with Examples Results
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
from OptiCode import Constraint_Eval
import os
#endregion
##################################################################################################################

def Exhaustive_Enumeration(OF_NAME, constraint_lists, var_list, OF_VAR, candidates , problem_data, 
                           Type_Equipment, Active_Models_Constraints, Selected_Model, Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Total number of candidates
    number_of_candidates = candidates.shape[1]

    # Results keeping lists
    OF_SOL = []
    sol_data = {}

    for i in range(0, number_of_candidates):

        # Evaluating the candidate
        candidate_tested = candidates[:,i].reshape(np.size(candidates[:,i]),1)
        Candidate_evaluation = Constraint_Eval.Constraint_Eval(OF_NAME[0], candidate_tested, problem_data, 
                                                               Type_Equipment, Active_Models_Constraints)

        # Obtaining the current candidate rigorous objective function (first element of the candidate_evaluation output)
        OF_VAL = Candidate_evaluation[0]

        # Checking for feasibility constraints:
        if not constraint_lists:
            OF_SOL.append(np.copy(OF_VAL))
        else:
            Feasibility = False
            # Obtaining the candidate constraint values - If the constraint value is negative, feasibility is "True"      
            for constraints in constraint_lists:
                constraint_evaluation = Constraint_Eval.Constraint_Eval(constraints, candidate_tested, problem_data,
                                                                        Type_Equipment, Active_Models_Constraints)
                if constraint_evaluation[0] < 0:
                    Feasibility = True
            if Feasibility:
                # Storing the candidate objective function at the variable sol_data
                OF_SOL.append(np.copy(OF_VAL))
            else:
                OF_SOL.append(None)

    # Selecting best solution
    OF_SOL_array = np.array(OF_SOL, dtype = float)

    # Checking for feasible results
    if np.all(np.isnan(OF_SOL_array)):
        save_result('No feasible candidates found in exhaustive enumeration')

        sol_data[OF_NAME[0]] = {OF_VAR[0]: None}
    else:
        min_index = np.nanargmin(OF_SOL_array)
        min_value = OF_SOL_array[min_index]
    
    # Saving best result
    sol_data[OF_NAME[0]] = {OF_VAR[0]: min_value}
    for cont, value in zip(var_list, candidates[:, min_index]):
        sol_data[cont] = value
         
    save_result("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    save_result("All", number_of_candidates, "candidates were evaluated")
    save_result("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    # If there is more than one Objective Function, evaluate others
    if len(OF_NAME) > 1:
        # Recriate candidate
        best_candidate = np.array([sol_data[var] for var in var_list]).reshape(-1, 1)
        # Calculate value for other Objective functions selected
        for i in range(1, len(OF_NAME)):
            Candidate_evaluation = Constraint_Eval.Constraint_Eval(
                OF_NAME[i], best_candidate, problem_data, Type_Equipment, Active_Models_Constraints
            )
            sol_data[OF_NAME[i]] = {OF_VAR[i]: Candidate_evaluation[0]}
            
    return sol_data
