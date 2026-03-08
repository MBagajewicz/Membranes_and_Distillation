##################################################################################################################
#region Titles and Header
# Nature: Segmental Smart Enumeration
# Methodology: Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0        29-Jan-2025       Alice Peccini              Proposed
#   0.2        28-Fev-2025       Alice Peccini              OptiProcess Code Structure Update
#   0.3        27-Apr-2025       Mariana Mello              Add .txt file with Results of Examples
#   0.4        13-May-2025       Mariana Mello              Update .txt file with Examples Results
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
import copy
import os
from OptiCode import (
    Constraint_Eval,
    Next_Level_Enum_Smart,
    Prep_Segmented_Space
)

#endregion
##################################################################################################################

def Seg_Smart_Enum_Next_Level(OF_NAME, LB_NAME, Fobj_within_LB, SEG_PAR, INC_OBJ, INC_VAR, constraint_lists, var_list, 
                              OF_VAR, candidates, problem_data, Type_Equipment, Active_Models_Constraints,
                              Selected_Model, Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    INC_NEXT_LEVEL = 1e20

    # ---------------------------------------- Lower Bound Generation ---------------------------------------- #
    # If candidate's objective function are evaluated within LB Generation function:
    if Fobj_within_LB:
        # The variable which stores the minimum values of the objective functions of all candidates is created
        # and best solution found within LB generation function is retrieved 
        [LB_VAL, LB_Fobj_Best, LB_Args_Best, LB_Solution_Next_Level_Best] = Constraint_Eval.Constraint_Eval(LB_NAME[0], 
                                                        candidates, problem_data, Type_Equipment,Active_Models_Constraints)
    
        # If an incumbent solution value is provided, then it is used.   
        if not INC_OBJ or LB_Fobj_Best < INC_OBJ:
            INC_OBJ = LB_Fobj_Best
            INC_VAR = LB_Args_Best
            INC_NEXT_LEVEL = LB_Solution_Next_Level_Best
    else:
        LB_VAL = Constraint_Eval.Constraint_Eval(LB_NAME[0], 
                                              candidates, problem_data, Type_Equipment,Active_Models_Constraints)

    save_result("Lower bound values", LB_VAL)
    save_result('Incumbent value:', INC_OBJ)
    # --------------------------------------- Incumbent Initialization --------------------------------------- #
    # Initializing Incumbent: if an incumbent solution value is provided, then it is used, if it is not:  
    Incumbent_Value = INC_OBJ

    # -------------------------------- Organizing Segmental Smart Enumeration -------------------------------- #
    # Total number of candidates
    number_of_candidates = candidates.shape[1]

    # Segmentation of problem space
    segmented_candidates = Prep_Segmented_Space.Segment_Space(candidates, var_list, SEG_PAR[0], SEG_PAR[1], SEG_PAR[2])
    save_result(f"Search space of {number_of_candidates} candidates divided in {len(segmented_candidates)} segments")

    # -------------------------------- Executing Segmental Smart Enumeration -------------------------------- #
    # Traveling through space segments
    for i, interval_candidates in enumerate(segmented_candidates):

        # Filter the LB_VAL values corresponding to the candidates in the interval
        mask = np.any(np.all(candidates[:, :, None] == interval_candidates[:, None, :], axis=0), axis=1)
        LB_min = np.min(LB_VAL[mask])   # Select minimum value between selected values

        # If the smallest LB of the interval is already greater than the incumbent, we skip the interval
        if LB_min >= Incumbent_Value:
            save_result("##################################")
            save_result(f"Skipping Segment {i + 1} (LB_min = {LB_min:.2f}, Incumbent = {Incumbent_Value:.2f})")
            continue

        save_result("********************************************")
        save_result(f"Performing Smart Enumeration on Segment {i + 1} (total of {segmented_candidates[i].shape[1]} candidates)")
        save_result(f"LB_min = {LB_min:.2f}, Incumbent = {Incumbent_Value:.2f}")
        save_result("********************************************")

        sol_interval = Next_Level_Enum_Smart.Smart_Enumeration_Next_Level(OF_NAME, [LB_NAME[1]], Fobj_within_LB, 
                                    Incumbent_Value, INC_VAR, constraint_lists, var_list, OF_VAR, 
                                    interval_candidates, problem_data, Type_Equipment, Active_Models_Constraints,
                                    Selected_Model, Selected_Example, save_result, INC_NEXT_LEVEL)

        # If OF_VAR exists, it means a better solution than Incumbent_Value was found and incumbent is updated:
        if OF_NAME[0] in sol_interval:
            Incumbent_Value = np.copy(sol_interval[OF_NAME[0]][OF_VAR[0]])
            INC_VAR = [sol_interval[cont] for cont in var_list]
            INC_NEXT_LEVEL = np.copy(sol_interval['Next_Level'])
            Incumbent_Dictionary = copy.deepcopy(sol_interval)

    # Storing the incumbent at sol_segmental variable
    sol_segmental = Incumbent_Dictionary

    return sol_segmental
