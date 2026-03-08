##################################################################################################################
# region Titles and Header
# Nature: Smart Enumeration
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0        07-Nov-2024      Diego Oliva                Taken from Set_Triming_Engine.py developed A. Nahes
#   0.2        10-Nov-2024      Miguel Bagajewicz          Review of comments
#   0.9        20-Nov-2024      Miguel Bagajewicz          Routine name Change
#                                                          Changes in other functions names
#                                                          Some variable names also changed
#   0.10       10-Dec-2024      Mariana Mello              Add the type of equipment
#   0.11       03-Fev-2024      Alice Peccini              Minor changes required for enumeration where no 
#                                                          feasibility constraints are applied   
#   0.12       28-Fev-2025      Alice Peccini              OptiProcess Code Structure Update    
#   0.13       19-Mar-2025      Alice Peccini              Correction on Feasibility check
#   0.14       27-Apr-2025      Mariana Mello              Add .txt file with Results of Examples
#   0.15       13-May-2025      Mariana Mello              Update .txt file with Examples Results
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
import os
from OptiCode import Constraint_Eval


# endregion
##################################################################################################################

def Smart_Enumeration(OF_NAME, LB_NAME, Fobj_within_LB, INC_OBJ, INC_VAR, constraint_lists, var_list, OF_VAR, 
                      candidates, problem_data, Type_Equipment, Active_Models_Constraints, Selected_Model,
                      Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Initializing variable sol_data
    sol_data = {}

    # ---------------------------------------- Lower Bound Generation ---------------------------------------- #
    # If candidate's objective function are evaluated within LB Generation function:
    if Fobj_within_LB:
        # The variable which stores the minimum values of the objective functions of all candidates is created
        # and best solution found within LB generation function is retrieved 
        [LB_VAL, LB_Fobj_Best, LB_Args_Best] = Constraint_Eval.Constraint_Eval(LB_NAME[0], candidates, 
                                                        problem_data, Type_Equipment, Active_Models_Constraints)
        # If an incumbent solution value is provided, then it is used.   
        if not INC_OBJ or LB_Fobj_Best < INC_OBJ:
            INC_OBJ = LB_Fobj_Best
            INC_VAR = LB_Args_Best
    else:
        # The variable which stores the minimum values of the objective functions of all candidates is created
        LB_VAL = Constraint_Eval.Constraint_Eval(LB_NAME[0], candidates, problem_data, Type_Equipment, 
                                                 Active_Models_Constraints)
    save_result("Lower bound values", LB_VAL)
    save_result('Incumbent value:', INC_OBJ)

    # --------------------------------------- Incumbent Initialization --------------------------------------- #
    # If an incumbent solution value is provided or was found during LB generation, then it is used.   
    if not INC_OBJ:
        Incumbent_Value = 1e20
    else: 
        Incumbent_Value = INC_OBJ
        sol_data[OF_NAME[0]] = {OF_VAR[0]: INC_OBJ}
        for cont, value in zip(var_list, INC_VAR):
            sol_data[cont] = value


    # ------------------------------------- Organizing Smart Enumeration ------------------------------------- #
    # Total number of candidates
    number_of_candidates = candidates.shape[1]
    # Evaluating the maximum value among the objective function lower bounds
    Max_LB = np.max(LB_VAL)
    # Obtaining the position of elements in asceding order of lower bound
    Ranking_position = np.argsort(LB_VAL)
    # Traveling through the candidates
    COND = True
    k = 0
    iicount = 0

    # ------------------------------------- Executing Smart Enumeration ------------------------------------- #
    while COND:
        # print("===============Candidate_Tested====================")
        # Creating a multidimensional array containing just the candidate for simulation
        i = Ranking_position[k]
        candidate_tested = candidates[:, i].reshape(np.size(candidates[:, i]), 1)
        # print (candidate_tested)
        # Evaluating the candidate

        Candidate_evaluation = Constraint_Eval.Constraint_Eval(OF_NAME[0], candidate_tested, problem_data, 
                                                               Type_Equipment, Active_Models_Constraints)

        # Obtaining the current candidate rigorous objective function (first element of the candidate_evaluation)
        OF_VAL = Candidate_evaluation[0]

        # Checking for feasibility constraints
        Feasibility = True
        for constraints in constraint_lists:
            constraint_evaluation = Constraint_Eval.Constraint_Eval(constraints, candidate_tested, problem_data,
                                                                    Type_Equipment, Active_Models_Constraints)
            if constraint_evaluation[0] > 0:
                Feasibility = False
                break

        # Evaluating the minimum lower bound
        MIN_LB_VAL = np.min(LB_VAL)
        iicount = iicount + 1

        # If the objective function of the candidate is smaller than the current one the incumbent is updated
        if Feasibility and OF_VAL < Incumbent_Value:
            # Storing the candidate objective function at the variable sol_data
            OF_Min_sol = np.copy(OF_VAL)
            sol_data[OF_NAME[0]] = {OF_VAR[0]: OF_Min_sol}

            # Storing the candidate design variables at the variable sol_data
            for cont, value in zip(var_list, candidate_tested):
                sol_data[cont] = value

            save_result("**********************************")
            save_result("Updating incumbent")
            save_result("Lower Bound:", MIN_LB_VAL, "Candidate:", k)

            Incumbent_Value = OF_VAL
            save_result("New Incumbent:", Incumbent_Value)

        # Checking the convergence criterion
        if Incumbent_Value <= MIN_LB_VAL:
            save_result("##################################")
            save_result("Exit at candidate:", k)
            save_result("Lower Bound:", MIN_LB_VAL, "Candidate:", k)

            COND = False
        #
        LB_VAL[i] = Max_LB
        k = k + 1
        if k > (number_of_candidates - 1):
            save_result("#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            save_result("All", k, "candidates were evaluated - Smart Enumeration became exhaustive")
            save_result("#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            COND = False

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
