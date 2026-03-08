#################################################################################################################
# region Nature: Optimization
# # Nature: Trimming by Constraints
# Methodology: Set Trimming Incremental
#################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.1        14-Ago-25        Diego Oliva                Taken from Set_Triming.py V 0.13
#   0.1        25-Sep-25        Diego Oliva                Allows incremental without primordial
#################################################################################################################
# INPUT:
#################################################################################################################
# INSTRUCTIONS
# !!!!! Do not touch, modify or delete Set_Trimming_Incremental.py file !!!!!
#################################################################################################################
# endregion
#################################################################################################################

#################################################################################################################
# region Initialization
from OptiCode import (Trimming_Incremental, Prep_Space, Prep_Space_Incremental)
import os
import numpy as np
import time
#import sys

# endregion
#################################################################################################################

#################################################################################################################
# region  Call this function to perform a Set trimming
def Set_Trimming(trimming_Info, Discretized_Variables, candidates, problem_data, Type_Equipment, Active_Models_Constraints, Selected_Model,
                 Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Creation of dictionary of the name of discrete variable with their values (discrete values)
    # {Ds: [1,4,2,3], ..., Dte: [3,43,2,1,3,56,6]}
    all_variables = dict(zip(trimming_Info['All_Variables_In_The_Problem'], Discretized_Variables))
    ### Main routine ###
    card_trim = []
    card_trim.append(candidates[0].size)
    # trimming process- It is a "for" loop applying the trimming to each constraint "const"
    #                                                            in the "trimming_list" at a time
    previous_variables_of_const = trimming_Info['Variables_used_in_primordial'] # Final variables from primordial
    if trimming_Info['Empty_primordial_set']:   # Ask if Prmordial Set has elements
        save_result(f'Empty Primordial Set!!!!')
        save_result(f'Initial size without primordial set: {card_trim[-1]}')
    else:
        save_result(f'Space from Primordial has the variables: {previous_variables_of_const}')
        save_result(f'Size of Space from Primordial: {card_trim[-1]}')
    for i, (const, variables_of_const) in enumerate(zip(trimming_Info['Set_Trimming_Constraints_List'], trimming_Info['Variables_Used_In_Incremental_For_Each_Set_Trimming_Constraint']), start=1):
        # compare "previous set of variables_of_const" with the new ones (variables_of_const).  
        # Those not repeated are taken to construct a new sapce.
        resulting_set = [elem for elem in variables_of_const if elem not in previous_variables_of_const] # eliminate variables from variables_of_const if exists in previous_variables_of_const 
        # Creation of matrix with discretized values refered by resulting_set
        # i.e. [[1,4,2,3],[3,43,2,1,3,56,6]] is the python structure created for 2 variables, the first one with 4 discrtized values the second one with 7
        if not resulting_set: # if reulting_set si empty
            save_result(f'Set Trimming {const} - Space Preparation is not needed. The set {list(set(previous_variables_of_const))} remains without changes.')
        else: # if resulting set is not empty means that it is necessary to construct a new space with candidates and the news variables od constraints
            save_result(f'Set Trimming {const} - Space Preparation adding following variables: {list(set(resulting_set))} to the previous set {list(set(previous_variables_of_const))}')
            discretized_variables_of_const = [all_variables[name] for name in resulting_set] # Construct set of discretized variables from resulting_set
            start_prepspace_sett = time.time()
            candidates = Prep_Space_Incremental.Prep_Space(candidates,discretized_variables_of_const) # Prepare space from candidates and discretized_variables_of_const
            end_prepspace_sett = time.time()
            elapsed_prepspace_sett = end_prepspace_sett - start_prepspace_sett
            card_trim.append(candidates[0].size)
            save_result(f'Set Trimming {const} - Space Size After Adding the variables {list(set(resulting_set))}: {card_trim[-1]}')
            save_result(f'Set Trimming - Adding variables time:  {elapsed_prepspace_sett:.5f} seconds\n')

        previous_variables_of_const = previous_variables_of_const + variables_of_const # Save the trimmed variables 
        start_trimming_sett = time.time()
        candidates = Trimming_Incremental.Trimming(const, candidates, previous_variables_of_const, problem_data, Type_Equipment, Active_Models_Constraints,trimming_Info)
        end_trimming_sett = time.time()
        elapsed_trimming_sett = end_trimming_sett - start_trimming_sett
        card_trim.append(candidates[0].size)
        save_result(f'Set Trimming {const} - Space Size After Trimming: {card_trim[-1]}')
        save_result(f'Set Trimming - Trimming time:  {elapsed_trimming_sett:.5f} seconds\n')


        if candidates[0].size == 0:
            infeasible_constraint = const
            save_result("Set Trimming Incremental produced an empty set using constraint:", infeasible_constraint)
            save_result("The problem has no solution after incremental trimming")
            #sys.exit()
            survivor_set = {'trimmed_candidates': [], 'candidate_set_cardinality_after_each_trimming': card_trim}
            return survivor_set
    # "candidates" contains the matrix of feasible candidates after all trimmings have been performed
    # "card_trim" contains the initial number of combinations and the surviving candidates after each "trimming"
    #

    resulting_set = [elem for elem in trimming_Info['All_Variables_In_The_Problem'] if elem not in previous_variables_of_const] # eliminate variables from Discretized_Variables if exists in previous_variables_of_const 
    print(resulting_set)
    discretized_variables_of_const = [all_variables[name] for name in resulting_set] # Construct set of discretized variables from resulting_set
    if discretized_variables_of_const:
        candidates = Prep_Space_Incremental.Prep_Space(candidates,discretized_variables_of_const) # Prepare space from candidates and discretized_variables_of_const
    else:
        print('Final candidates after Incremental Set Trimming explore all variables of the problem')

    #reordering candidates matrix to have the same ordered variables as used in constraints
    variables_of_const_no_duplicates =list(dict.fromkeys(previous_variables_of_const)) # eliminates variables repited from left to rigth and ordered
    labels_of_final_candidates = variables_of_const_no_duplicates + resulting_set
    labels_of_final_candidates = variables_of_const_no_duplicates
    candidatesnp = np.array(candidates)
    # print(candidatesnp)
    labels = np.array(labels_of_final_candidates)
    # print(labels)
    position = {etq: i for i, etq in enumerate(trimming_Info['All_Variables_In_The_Problem'])}
    # print(position)
    idx = np.argsort([position[l] for l in labels])
    # print(idx)
    mat_ordenada = candidatesnp[idx]
    candidates = mat_ordenada
     # candidates = mat_ordenada[idx].tolist()

    card_trim.append(candidates[0].size)
    save_result("Set Trimming successful - The candidates solution set is not empty")
    survivor_set = {'trimmed_candidates': candidates, 
                    'candidate_set_cardinality_after_each_trimming': card_trim,
                    'variables_survivor_names': variables_of_const_no_duplicates}


    return survivor_set



# endregion
#################################################################################################################