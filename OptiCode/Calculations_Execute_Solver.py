##################################################################################################################
# region Titles and Header
# Nature: Organize Calculations
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.7       12-Nov-2024       Diego Oliva                Only calculations
#   0.9       20-Nov-2024       Miguel Bagajewicz          Routine name Change from 'calculations.py"
#                                                          Changes in other functions names
#                                                          Some variable names also changed
#   0.10      08-Jan-2025       Mariana Mello              Change by adding an if for when the candidate set is empty
#   0.11      29-Jan-2025       Mariana Mello              Add Parameters_Calculations
#   0.12      03-Fev-2025       Alice Peccini              Add different enumeration types
#   0.13      27-Fev-2025       Alice Peccini              OptiProcess Code Structure Update
#   0.14      26-Apr-2025       Mariana Mello              Add .txt file with Results of Examples
#   0.15      13-May-2025       Mariana Mello              Update .txt file with Examples Results
#   0.16      31-Ago-2025       Diego Oliva                In Set_Trimming.Set_Trimming call the first argument is changed
#   0.16      31-Ago-2025       Diego Oliva                with the new name Set_Trimming_Constraints_List['Set_Trimming_Constraints_List']
#   0.17      31-Ago-2025       Diego Oliva                Set_Trimming_Constraints_List is changed to Set_Trimming_Info
#   0.17      31-Ago-2025       Diego Oliva                New variable (Discretized_Variables) comes from Calculations_Solver_Organizer.py
#   0.17      31-Ago-2025       Diego Oliva                New import Set_Trimming_Incremental
##################################################################################################################
# INPUT: go to region INPUT MODEL DETAILS
##################################################################################################################
# INSTRUCTIONS
# Do not modify this file
# endregion
##################################################################################################################

##################################################################################################################
# region Import Library

from OptiCode import (
    Next_Level_Enum_Exhaustive,
    Next_Level_Enum_Seg_Smart,
    Next_Level_Enum_Smart,
    Set_Trimming,
    Sorting,
    Enumeration_Exhaustive,
    Enumeration_Smart,
    Enumeration_Seg_Smart,
    Sorting_by_Variable,
    Set_Trimming_Incremental,
    Set_Trimming_Incremental_2
)
import os
import time

# endregion
##################################################################################################################

##################################################################################################################
# region Calculations

def Execute_Solver(Type_Equipment, Next_Level, ST_Mode, SO_Mode, Enum_Mode, List_of_Variables, 
                   Set_Trimming_Info, Enumeration_Constraints_List, LB_NAME, Fobj_within_LB,
                   SO_Variable, OF_NAME, OPT_VAR_NAMES, Enum_type, Discretized_Variables, candidates, SEG_PAR, INC_OBJ, INC_VAR, Model_Parameters,
                   Next_Level_Data, Active_Models_Constraints, Active_Models_Update, Active_Models_Def, Selected_Model,
                   Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # ---------------------------------------- Modes of Operation ---------------------------------------- #

    # 1 - No Set Trimming and no Enumeration                (ST_Mode = False,   Enum_Mode = False) => There is no problem to solve
    # 2 - No Set Trimming, only Exhaustive Enumeration      (ST_Mode = False,   Enum_Mode = True,   Enum_type = 'Exhaustive')
    # 3 - No Set Trimming, only Smart Enumeration           (ST_Mode = False,   Enum_Mode = True,   Enum_type = 'Smart')
    # 4 - No Set Trimming, only Segmental Samrt Enumeration (ST_Mode = False,   Enum_Mode = True,   Enum_type = 'Segmental_Smart')

    # 5 - Set Trimming only, no Enumeration                 (ST_Mode = True,    Enum_Mode = False)
        # 5.1: Sorting by variable after trimming               (SO_Mode = True and SO_Variable = True)
        # 5.2: Standard Sorting  after trimming                 (SO_Mode = True and SO_Variable = False)
        # 5.3: No Sorting after trimming                        (SO_Mode = False)
        # (the solution is the set of trimmed candidates)

    # 6 - Set Trimming and Exhaustive Enumeration           (ST_Mode = True,    Enum_Mode = True,   Enum_type = 'Exhaustive')
    # 7 - Set Trimming and Smart Enumeration                (ST_Mode = True,    Enum_Mode = True,   Enum_type = 'Smart')
    # 8 - Set Trimming and Segmental Samrt Enumeration      (ST_Mode = True,    Enum_Mode = True,   Enum_type = 'Segmental_Smart')

    # Operational mode selection
    COND_ST = ST_Mode       # Set Trimming Mode
    COND_SO = SO_Mode       # Sorting Mode
    COND_EN = Enum_Mode     # Enumeration Mode
    COND_NL = Next_Level    # Next Level Mode

    # OBSERVATION: For Next_Level problems, scenarios 2 to 8 appear as well. Since next_level enumeration
    # functions are different the operation mode selection and execution is done separately for One Level 
    # Optimization or Bilevel Optimization (COND_NL check).

    # ------------------------------------ One level Optimization ------------------------------------ #

    if not COND_NL:

        if not COND_ST:
            # Set Trimming was NOT activated. Scenarios 1 to 4:

            #### SCENARIO 1 - NO Set Trimming and NO Enumeration - There is no problem to solve!
            if not COND_ST and not COND_EN:
                save_result('NO execution mode (set trimming or enumeration) was activated! There is NO problem to solve')
                exit

            #### SCENARIO 2 - NO Set Trimming, ONLY Exhaustive Enumeration
            if COND_EN and Enum_type == 'Exhaustive':
                save_result("Set trimming mode was NOT activated. Performing Exhaustive Enumeration ONLY")

                Solution = Enumeration_Exhaustive.Exhaustive_Enumeration(OF_NAME, Enumeration_Constraints_List,
                                                                         List_of_Variables, OPT_VAR_NAMES, candidates,
                                                                         Model_Parameters, Type_Equipment,
                                                                         Active_Models_Constraints, Selected_Model,
                                                                         Selected_Example, save_result)
                save_result("Exhaustive Enumeration Solution", Solution)

            #### SCENARIO 3 - NO Set Trimming, ONLY Smart Enumeration
            if COND_EN and Enum_type == 'Smart':
                save_result("Set trimming mode was NOT activated. Performing Smart Enumeration ONLY")

                Solution = Enumeration_Smart.Smart_Enumeration(OF_NAME, LB_NAME, Fobj_within_LB, INC_OBJ,
                                                               INC_VAR, Enumeration_Constraints_List, List_of_Variables,
                                                               OPT_VAR_NAMES, candidates, Model_Parameters,
                                                               Type_Equipment, Active_Models_Constraints,
                                                               Selected_Model, Selected_Example, save_result)
                save_result("Smart Enumeration Solution", Solution)

            #### SCENARIO 4 - NO Set Trimming, ONLY Segmental Smart Enumeration
            if COND_EN and Enum_type == 'Segmental_Smart':
                save_result("Set trimming mode was NOT activated. Performing Smart Enumeration ONLY")

                Solution = Enumeration_Seg_Smart.Segmental_Smart_Enumeration(OF_NAME, LB_NAME, Fobj_within_LB,
                                                                             SEG_PAR, INC_OBJ, INC_VAR,
                                                                             Enumeration_Constraints_List,
                                                                             List_of_Variables, OPT_VAR_NAMES,
                                                                             candidates, Model_Parameters,
                                                                             Type_Equipment, Active_Models_Constraints,
                                                                             Selected_Model, Selected_Example, save_result)
                save_result("Smart Enumeration Solution", Solution)

        if COND_ST:
            # Set Trimming activated. Scenarios 5 to 8:
#SEGUIMOS AQUI ***********************************************************************************************

            #### SCENARIO 5 - Set Trimming ONLY, NO Enumeration
            if not COND_EN:
                save_result('NO Enumeration mode was activated. Performing Set Trimming ONLY')
                if Set_Trimming_Info['Incremental_Set_Trimming']:
                    solution_set_trimming = Set_Trimming_Incremental_2.Set_Trimming(Set_Trimming_Info,Discretized_Variables, candidates, 
                                                                    Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                                    Selected_Model, Selected_Example, save_result)
                    save_result('Candidate set cardinality after each incremental trimming',
                            solution_set_trimming['candidate_set_cardinality_after_each_trimming'])
                else:
                    solution_set_trimming = Set_Trimming.Set_Trimming(Set_Trimming_Info['Set_Trimming_Constraints_List'], candidates, 
                                                                   Model_Parameters, Type_Equipment,
                                                                   Active_Models_Constraints, Selected_Model,
                                                                   Selected_Example, save_result)
                    save_result('Candidate set cardinality after each trimming',
                            solution_set_trimming['candidate_set_cardinality_after_each_trimming'])

                if COND_SO:     # Sorting after Trimming Activated
                    if len(solution_set_trimming['trimmed_candidates']) == 0:
                        Solution = {OF_NAME[0]: {OPT_VAR_NAMES[0]: 1e20}}
                    else:
                        if SO_Variable: # SCENARIO 5.1 - Sorting by variable:
                            Solution = Sorting_by_Variable.Sorting_by_Variable(solution_set_trimming['trimmed_candidates'], 
                                                                               Model_Parameters, List_of_Variables,
                                                                               OF_NAME, OPT_VAR_NAMES, Type_Equipment,
                                                                               Active_Models_Constraints, SO_Variable)
                        else: # SCENARIO 5.2 - Standard sorting:
                            Solution = Sorting.Sorting(solution_set_trimming['trimmed_candidates'], Model_Parameters,
                                                       List_of_Variables, OF_NAME, OPT_VAR_NAMES, Type_Equipment,
                                                       Active_Models_Constraints)
                    save_result(Solution)

                else:           # SCENARIO 5.3 - No sorting, solution will be the set of trimmed candidates
                    Solution = solution_set_trimming['trimmed_candidates']
                    save_result(Solution)

            else:
                save_result("Set trimming and Enumeration activated. Performing Set Trimming First, followed by Selected Enumeration")

                if Set_Trimming_Info['Incremental_Set_Trimming']:
                    start_time = time.time()
                    solution_set_trimming = Set_Trimming_Incremental_2.Set_Trimming(Set_Trimming_Info,Discretized_Variables, candidates, 
                                                                    Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                                    Selected_Model, Selected_Example, save_result)
                    save_result("Set Trimming Incremental Solution", solution_set_trimming)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    save_result('Elapsed time Set Trimming Incremental:', elapsed_time)
                else:
                    start_time = time.time()
                    solution_set_trimming = Set_Trimming.Set_Trimming(Set_Trimming_Info['Set_Trimming_Constraints_List'], candidates, 
                                                                   Model_Parameters, Type_Equipment,
                                                                   Active_Models_Constraints, Selected_Model,
                                                                   Selected_Example, save_result)
                    save_result("Set Trimming Solution", solution_set_trimming)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    save_result('Elapsed time Set Trimming:', elapsed_time)

                #### SCENARIO 6 - Set Trimming AND Exhaustive Enumeration
                if Enum_type == 'Exhaustive':         
                    save_result("Performing Exhaustive Enumeration now")
                    Solution = Enumeration_Exhaustive.Exhaustive_Enumeration(OF_NAME, Enumeration_Constraints_List,
                                                                             List_of_Variables, OPT_VAR_NAMES,
                                                                             solution_set_trimming['trimmed_candidates'],
                                                                             Model_Parameters, Type_Equipment,
                                                                             Active_Models_Constraints, Selected_Model,
                                                                             Selected_Example, save_result)

                    save_result("Solution after Exhaustive Enumeration", Solution)

                if Enum_type == 'Smart':
                #### SCENARIO 7 - Set Trimming AND Smart Enumeration
                    save_result("Performing Smart Enumeration now")

                    Solution = Enumeration_Smart.Smart_Enumeration(OF_NAME, LB_NAME, Fobj_within_LB, INC_OBJ, INC_VAR,
                                                                   Enumeration_Constraints_List, List_of_Variables,
                                                                   OPT_VAR_NAMES,
                                                                   solution_set_trimming['trimmed_candidates'],
                                                                   Model_Parameters, Type_Equipment,
                                                                   Active_Models_Constraints, Selected_Model,
                                                                   Selected_Example, save_result)
                    save_result("Solution after Smart Enumeration", Solution)

                if Enum_type == 'Segmental_Smart':
                #### SCENARIO 8 - Set Trimming AND Segmental Smart Enumeration
                    save_result("Performing Segmental Smart Enumeration now")
                    Solution = Enumeration_Seg_Smart.Segmental_Smart_Enumeration(OF_NAME, LB_NAME, Fobj_within_LB,
                                                                                 SEG_PAR, INC_OBJ, INC_VAR,
                                                                                 Enumeration_Constraints_List,
                                                                                 List_of_Variables, OPT_VAR_NAMES,
                                                                                 solution_set_trimming['trimmed_candidates'],
                                                                                 Model_Parameters, Type_Equipment,
                                                                                 Active_Models_Constraints,
                                                                                 Selected_Model, Selected_Example,
                                                                                 save_result)
                    save_result("Solution after Segmental Smart Enumeration", Solution)


    # ------------------------------------- Bilevel Optimization ------------------------------------- #

    else:

        # Save required information to be accessed within main problem objective function
        Model_Parameters['Main_Type'] = Type_Equipment
        Model_Parameters['Next_Level_Data'] = Next_Level_Data
        Model_Parameters['Active_Models'] = {
            'Models_Def': Active_Models_Def, 
            'Constraints_and_OF': Active_Models_Constraints,
            'Parameters_Update': Active_Models_Update}
        Model_Parameters['Selected_Example'] = Selected_Example
        Model_Parameters['Save_Results'] = save_result

        if not COND_ST:
            # Set Trimming was NOT activated. Scenarios 2 to 4:

            #### SCENARIO 2 - NO Set Trimming, ONLY Exhaustive Enumeration
            if COND_EN and Enum_type == 'Exhaustive':
                save_result("Set trimming mode was NOT activated. Performing Exhaustive Enumeration ONLY")
                Solution = Next_Level_Enum_Exhaustive.Exhaustive_Enumeration_Next_Level(OF_NAME, Enumeration_Constraints_List, 
                                                                                        List_of_Variables, OPT_VAR_NAMES,
                                                                                        candidates, Model_Parameters,
                                                                                        Type_Equipment,
                                                                                        Active_Models_Constraints,
                                                                                        Selected_Model, Selected_Example,
                                                                                        save_result)
                save_result("Exhaustive Enumeration Solution", Solution)

            #### SCENARIO 3 - NO Set Trimming, ONLY Smart Enumeration
            if COND_EN and Enum_type == 'Smart':
                save_result("Set trimming mode was NOT activated. Performing Smart Enumeration ONLY")

                Solution = Next_Level_Enum_Smart.Smart_Enumeration_Next_Level(OF_NAME, LB_NAME, Fobj_within_LB, INC_OBJ, 
                                                                              INC_VAR, Enumeration_Constraints_List,
                                                                              List_of_Variables, OPT_VAR_NAMES,
                                                                              candidates, Model_Parameters,
                                                                              Type_Equipment, Active_Models_Constraints,
                                                                              Selected_Model, Selected_Example,
                                                                              save_result)
                save_result("Smart Enumeration Solution", Solution)

            #### SCENARIO 4 - NO Set Trimming, ONLY Segmental Smart Enumeration
            if COND_EN and Enum_type == 'Segmental_Smart':
                save_result("Set trimming mode was NOT activated. Performing Smart Enumeration ONLY")

                Solution = Next_Level_Enum_Seg_Smart.Seg_Smart_Enum_Next_Level(OF_NAME, LB_NAME, Fobj_within_LB, SEG_PAR, 
                                                                               INC_OBJ, INC_VAR,
                                                                               Enumeration_Constraints_List,
                                                                               List_of_Variables, OPT_VAR_NAMES,
                                                                               candidates, Model_Parameters,
                                                                               Type_Equipment, Active_Models_Constraints,
                                                                               Selected_Model, Selected_Example,
                                                                               save_result)
                save_result("Smart Enumeration Solution", Solution)

        if COND_ST:
            # Set Trimming activated. Scenarios 5 to 8:
            #### SCENARIO 5 - Set Trimming ONLY, NO Enumeration
            if not COND_EN:
                save_result('NO Enumeration mode was activated. Performing Set Trimming ONLY')
                if Set_Trimming_Info['Incremental_Set_Trimming']:
                    solution_set_trimming = Set_Trimming_Incremental_2.Set_Trimming(Set_Trimming_Info,Discretized_Variables, candidates, 
                                                                    Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                                    Selected_Model, Selected_Example, save_result)
                    save_result('Candidate set cardinality after each incremental trimming',
                            solution_set_trimming['candidate_set_cardinality_after_each_trimming'])
                else:
                    solution_set_trimming = Set_Trimming.Set_Trimming(Set_Trimming_Info['Set_Trimming_Constraints_List'], candidates, 
                                                                   Model_Parameters, Type_Equipment,
                                                                   Active_Models_Constraints, Selected_Model,
                                                                   Selected_Example, save_result)
                    save_result('Candidate set cardinality after each trimming',
                            solution_set_trimming['candidate_set_cardinality_after_each_trimming'])

                if COND_SO:     # Sorting after Trimming Activated
                    if len(solution_set_trimming['trimmed_candidates']) == 0:
                        Solution = {OF_NAME[0]: {OPT_VAR_NAMES[0]: 1e20}}
                    else:
                        if SO_Variable: # SCENARIO 5.1 - Sorting by variable:
                            Solution = Sorting_by_Variable.Sorting_by_Variable(solution_set_trimming['trimmed_candidates'], 
                                                                               Model_Parameters, List_of_Variables,
                                                                               OF_NAME, OPT_VAR_NAMES, Type_Equipment,
                                                                               Active_Models_Constraints, SO_Variable)
                        else: # SCENARIO 5.2 - Standard sorting:
                            Solution = Sorting.Sorting(solution_set_trimming['trimmed_candidates'], Model_Parameters,
                                                       List_of_Variables, OF_NAME, OPT_VAR_NAMES, Type_Equipment,
                                                       Active_Models_Constraints)
                    save_result(Solution)

                else:           # SCENARIO 5.3 - No sorting, solution will be the set of trimmed candidates
                    Solution = solution_set_trimming['trimmed_candidates']
                    save_result(Solution)

            else:
                save_result("Set trimming and Enumeration activated. Performing Set Trimming First, followed by Selected Enumeration")

                if Set_Trimming_Info['Incremental_Set_Trimming']:
                    start_time = time.time()
                    solution_set_trimming = Set_Trimming_Incremental_2.Set_Trimming(Set_Trimming_Info,Discretized_Variables, candidates,
                                                                    Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                                    Selected_Model, Selected_Example, save_result)
                    save_result("Set Trimming Incremental Solution", solution_set_trimming)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    save_result('Elapsed time Set Trimming Incremental:', elapsed_time)
                else:
                    start_time = time.time()
                    solution_set_trimming = Set_Trimming.Set_Trimming(Set_Trimming_Info['Set_Trimming_Constraints_List'], candidates, 
                                                                   Model_Parameters, Type_Equipment,
                                                                   Active_Models_Constraints, Selected_Model,
                                                                   Selected_Example, save_result)
                    save_result("Set Trimming Solution", solution_set_trimming)
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    save_result('Elapsed time Set Trimming:', elapsed_time)

                #### SCENARIO 6 - Set Trimming AND Exhaustive Enumeration
                if Enum_type == 'Exhaustive':              
                    save_result("Performing Exhaustive Enumeration now")
                    Solution = Next_Level_Enum_Exhaustive.Exhaustive_Enumeration_Next_Level(OF_NAME,Enumeration_Constraints_List, 
                                                                                            List_of_Variables, OPT_VAR_NAMES,
                                                                                            solution_set_trimming['trimmed_candidates'],
                                                                                            Model_Parameters, Type_Equipment,
                                                                                            Active_Models_Constraints,
                                                                                            Selected_Model, Selected_Example,
                                                                                            save_result)
                    save_result("Solution after Exhaustive Enumeration", Solution)

                if Enum_type == 'Smart':
                #### SCENARIO 7 - Set Trimming AND Smart Enumeration
                    save_result("Performing Smart Enumeration now")
                    Solution = Next_Level_Enum_Smart.Smart_Enumeration_Next_Level(OF_NAME, LB_NAME, Fobj_within_LB, INC_OBJ, 
                                                                                INC_VAR, Enumeration_Constraints_List,
                                                                                List_of_Variables, OPT_VAR_NAMES,
                                                                                solution_set_trimming['trimmed_candidates'],
                                                                                Model_Parameters, Type_Equipment,
                                                                                Active_Models_Constraints, Selected_Model,
                                                                                Selected_Example, save_result)
                    save_result("Solution after Smart Enumeration", Solution)

                if Enum_type == 'Segmental_Smart':
                #### SCENARIO 8 - Set Trimming AND Segmental Smart Enumeration
                    save_result("Performing Segmental Smart Enumeration now")

                    Solution = Next_Level_Enum_Seg_Smart.Seg_Smart_Enum_Next_Level(OF_NAME, LB_NAME, Fobj_within_LB, SEG_PAR,
                                                                                INC_OBJ, INC_VAR, Enumeration_Constraints_List,
                                                                                List_of_Variables, OPT_VAR_NAMES,
                                                                                solution_set_trimming['trimmed_candidates'],
                                                                                Model_Parameters, Type_Equipment,
                                                                                Active_Models_Constraints, Selected_Model,
                                                                                Selected_Example, save_result)
                    save_result("Solution after Segmental Smart Enumeration", Solution)

    return Solution

# endregion
#################################################################################################################################