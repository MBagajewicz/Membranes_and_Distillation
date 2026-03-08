#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          12-Mar-2025     Alice Peccini             Original - Initial Set Generation
#   0.2          27-Apr-2025     Mariana Mello             Add .txt file with Results of Examples
#   0.3          13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.4          13-Ago-2025     Diego Oliva               Incremental option added (Discretized_Variables with 
#                                                          more information)
#   0.5          25-Sep-2025     Diego Oliva               Allows incremental without primordial
##################################################################################################################
##################################################################################################################
#endregion

#region Import Library
from OptiCode import (
    Set_Trimming,
    Set_Trimming_Incremental,
    Prep_Space)
import os
import time
#endregion

####################################################################################################################
#region Initial Set Up (Generation of Model Parameters, Primordial and Initial Sets)

def Calculations_Initial_Set_Up(Type_Equipment, Set_Trimming_Info, Discretized_Variables,
                Model_Parameters, Parameters_Update_Module, Parameters_Calculations_List, Active_Models_Constraints,
                Selected_Model, Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Generating Model Calculated Parameters
    for par_calc in Parameters_Calculations_List:

        try:  # Try to generate parameters (for Next Level Equipment some parameters may be skipped in the first stage)
            getattr(Parameters_Update_Module, par_calc)(Model_Parameters)
        except:
            save_result(f'{Type_Equipment} parameter from par_calc was not generated at this stage. Skipping')
            pass
    

    # Constructs Primordial Set Candidate Matrix
    # Verify the existence of a Primordial_Set_Constraints_List and Generate Initial Set
    if Set_Trimming_Info['Primordial_Set_Trimming_Constraints_List']:
        # Ask if Incremental or Normal mode will be used
        if Set_Trimming_Info['Incremental_Set_Trimming'] and Set_Trimming_Info['Primordial_Set_Trimming_Constraints_List']:
            Set_Trimming_Info['Empty_primordial_set'] = False
            Set_Trimming_Solution = Set_Trimming_Incremental.Set_Trimming(Set_Trimming_Info,Discretized_Variables, 
                                                            Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                            Selected_Model, Selected_Example, save_result)
            Initial_Set = Set_Trimming_Solution['trimmed_candidates']
            Set_Trimming_Info['Variables_used_in_primordial'] = Set_Trimming_Solution['variables_survivor_names']
            
            save_result('\n************ Initial Set generated from Primordial Set using Incremental Set Trimming************\n')
            save_result('Candidate set cardinality after each incremental trimming',
                         Set_Trimming_Solution['candidate_set_cardinality_after_each_trimming'],
                         '\n Variables used for trim',
                         Set_Trimming_Solution['variables_survivor_names'])
        else:
            Set_Trimming_Info['Empty_primordial_set'] = True
            start_prepspace_time = time.time() 
            Primordial_Set = Prep_Space.Prep_Space(Discretized_Variables)
            end_prepspace_time = time.time() 
            elapsed_time_prepspace = end_prepspace_time - start_prepspace_time


            start_settrimming_primordial = time.time()
            Set_Trimming_Solution = Set_Trimming.Set_Trimming(Set_Trimming_Info['Primordial_Set_Trimming_Constraints_List'], Primordial_Set, 
                                                            Model_Parameters, Type_Equipment, Active_Models_Constraints,
                                                            Selected_Model, Selected_Example, save_result)
            Initial_Set = Set_Trimming_Solution['trimmed_candidates']
            end_settrimming_primordial = time.time()
            elapsed_settrimming_primordial_time = end_settrimming_primordial - start_settrimming_primordial


            save_result(f'Building initial set time:  {elapsed_time_prepspace:.5f} seconds\n')
            save_result(f'Primordial Set Trimming time:  {elapsed_settrimming_primordial_time:.5f} seconds\n')

            save_result('\n************ Initial Set generated from Primordial Set ************\n')
            save_result('Candidate set cardinality after each trimming',
                        Set_Trimming_Solution['candidate_set_cardinality_after_each_trimming'])
    else:
        Primordial_Set = Prep_Space.Prep_Space(Discretized_Variables)
        Initial_Set = Primordial_Set
        save_result(f'\n************ Initial Set = Primordial Set with {Initial_Set.shape[1]} candidates ************\n')
        Set_Trimming_Info['Variables_used_in_primordial'] =  Set_Trimming_Info['All_Variables_In_The_Problem']
        if not Set_Trimming_Info['Primordial_Set_Trimming_Constraints_List']:
            Set_Trimming_Info['Empty_primordial_set'] = True
        


    return Initial_Set