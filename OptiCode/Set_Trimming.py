#################################################################################################################
# region Nature: Optimization
# # Nature: Trimming by Constraints
# Methodology: Set Trimming
#################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.2        30-Oct-24        Diego Oliva                Taken from Set_Triming_Engine.py developed by A. Costa
#   0.3        31-Oct-2024      Diego Oliva                Output variable inside a library is homogenized
#                                                                                 (library_output)
#   0.4        10-Nov-2024      Miguel Bagajewicz          Comments revised- Changed output when a constraint
#                                                                                  produces an empty set
#                                                          Change name of output variable
#                                                                                  library_output-->survivor_set
#   0.9        20-Nov-2024      Miguel Bagajewicz          Changes in other functions names
#                                                          Some variable names also changed
#   0.10       10-Dec-2024      Mariana Mello              Add the type of equipment
#   0.11       08-Jan-2024      Mariana Mello              Modify output when set of candidate is empty
#   0.12       27-Apr-2025      Mariana Mello              Add .txt file with Results of Examples
#   0.13       13-May-2025      Mariana Mello              Update .txt file with Examples Results
#################################################################################################################
# INPUT:
#################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete Set_Trimming_Engine.py file !!!!!
#################################################################################################################
# endregion
#################################################################################################################

#################################################################################################################
# region Initialization
from OptiCode import Trimming
import os
#import sys

# endregion
#################################################################################################################

#################################################################################################################
# region  Call this function to perform a Set trimming
def Set_Trimming(trimming_list, candidates, problem_data, Type_Equipment, Active_Models_Constraints, Selected_Model,
                 Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    ### Main routine ###
    card_trim = []
    card_trim.append(candidates[0].size)
    # trimming process- It is a "for" loop applying the trimming to each constraint "const"
    #                                                            in the "trimming_list" at a time
    for const in trimming_list:
        candidates = Trimming.Trimming(const, candidates, problem_data, Type_Equipment, Active_Models_Constraints)
        card_trim.append(candidates[0].size)
        if candidates[0].size == 0:
            infeasible_constraint = const
            save_result("Set Trimming produced an empty set using constraint:", infeasible_constraint)
            save_result("The problem has no solution")
            #sys.exit()
            survivor_set = {'trimmed_candidates': [], 'candidate_set_cardinality_after_each_trimming': card_trim}
            return survivor_set
    #
    # "candidates" contains the matrix of feasible candidates after all trimmings have been performed
    # "card_trim" contains the initial number of combinations and the surviving candidates after each "trimming"
    #
    save_result("Set Trimming successful - The candidates solution set is not empty")
    survivor_set = {'trimmed_candidates': candidates, 'candidate_set_cardinality_after_each_trimming': card_trim}
    #
    return survivor_set

# endregion
#################################################################################################################
