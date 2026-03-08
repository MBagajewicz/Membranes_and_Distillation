#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          12-Dec-2024     Mariana Mello             Original - Apply direct loop
#   0.2          17-Jan-2025     Mariana Mello             Change the name
#   0.3          24-Jan-2025     Mariana Mello             Changes for solve flowsheet with recycle or not
#   0.4          03-Fev-2025     Alice Peccini             Changes for different enumeration type selection
#   0.5          25-Fev-2025     Alice Peccini             Changes in Equipment_Within structure
#   0.6          27-Fev-2025     Alice Peccini             Candidate_set initialization option
#   0.7          28-Fev-2025     Alice Peccini             OptiProcess Code Structure Update
#   0.8          26-Apr-2025     Mariana Mello             Add .txt file with Results of Examples
#   0.9          13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.10         25-Jun-2025     Mariana Mello             Minor changes
#   0.11         31-Ago-2025     Diego Oliva               Calculations_Execute_Solver.Execute_Solver modified
#   0.11         31-Ago-2025     Diego Oliva               sending all equipment_def['Set_Trimming_Info']
#   0.11         31-Ago-2025     Diego Oliva               unstead equipment_def['Set_Trimming_Info']['Set_Trimming_Constraints_List']
#   0.11         31-Ago-2025     Diego Oliva               in all calls
#   0.12         01-Sep-2025     Diego Oliva               Adding data to be send in Calculations_Execute_Solver.Execute_Solver,
#   0.12         01-Sep-2025     Diego Oliva               this data is used by Incremental routine;
#   0.12         01-Sep-2025     Diego Oliva               it is sending after "equipment_dt['Model_Declarations']['Type_Enumeration']"
##################################################################################################################
##################################################################################################################
#endregion

#region Import Library
from OptiCode import (
    Calculations_Execute_Solver,
    Trimming_Obj_Function
)
import time

import os
import numpy as np
import copy

#endregion

####################################################################################################################
#region Calculations_Organizer

def Solver_Organizer(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Initialization
    total_solution = 0  # Stores summation of Equipments Objective Functions
    Sol_Dict = {}       # Stores Equipments individual solutions (OF and discrete variables)

    # Solve each piece of equipment sequentially
    for i in range(1, Active_Example['Number_of_Equipment'] + 1):

        equip_start_time = time.time()

        # Identify Problem to solve and its data
        equipment_key = f'Equipment{i}'                                         # Identify Equipment to solve
        equipment_dt = Active_Example[equipment_key]                            # Retrieve Equipment Data
        Type_Equipment = equipment_dt['Model_Declarations']['Type_Equipment']   # Identify Equipment Type
        equipment_def = Active_Models['Models_Def'][Type_Equipment]             # Retrivieng Model_definitions
        Sequential_Set_Up = equipment_def['Model_Info'].get('Set_Up_Sequential',{}).get(equipment_key,[])
        Initial_Set = equipment_dt['Model_Declarations']['Initial_Set']
        Candidates_Set = Initial_Set.copy()

        # Equipment sequential set up
        Parameters_Update_Module = Active_Models['Parameters_Update'][Type_Equipment]
        for function in Sequential_Set_Up:
            getattr(Parameters_Update_Module, function)(Sol_Dict, equipment_dt['Model_Parameters'])
        
        # Checks to see if recursive Trimming is applied for selected equipment
        if equipment_def['Set_Trimming_Info'].get('Recursive_Set_Trimming'):

            # Identifies Objective Function and decision variables
            OF_Function = equipment_dt['Model_Declarations']['Objective_Function']['Equation_Name'][0]
            OF_Variable = equipment_dt['Model_Declarations']['Objective_Function']['Optimization_Variables_Names'][0] 
            OF_Unit = equipment_dt['Model_Declarations']['Objective_Function']['Unit_OF'][0] # Retrive objective function measurement unit
            OF_Sol = 1e+20
            Solution = {}

            # Identify recursive trimming variable and its options:
            Recursive_Trimming_Info = equipment_def['Set_Trimming_Info'].get('Recursive_Set_Trimming')

            Variable_Name = Recursive_Trimming_Info.get('Variable_Name', [])
            Variable_Options = Recursive_Trimming_Info.get('Variable_Options', [])
            ST_Exclusion_Functions = Recursive_Trimming_Info.get('ST_Exclusion_Functions', [])

            # Checks if Recursive variable exists within Model Parameters:
            if Variable_Name in equipment_dt['Model_Parameters']:

                # Retrieves user selection for Recursive Variable
                Selected_Options = [equipment_dt['Model_Parameters'][Variable_Name]]

                # Checks if Selected Option for recursive variable is not valid:
                if Selected_Options[0] not in Variable_Options:

                    save_result(f'Options selected for {Variable_Name}: {Variable_Options}')
                    save_result(f"If only one option is desired example input for Model_Parameters['{Variable_Name}'] must be changed")
                    # Updates selected Options for Valid Recursive Trimming Options
                    Selected_Options = Variable_Options               
            else:
                save_result(f'Options selected for {Variable_Name}: {Variable_Options}')
                save_result(f"If only one option is desired example input for Model_Parameters['{Variable_Name}'] must be included with one of given options\n")
                # Updates selected Options for Valid Recursive Trimming Options

                Selected_Options = Variable_Options 

            # Calls Solver Organizer for each option of recursive trimming variable
            for index, option in enumerate(Selected_Options):
                # Generate missing parameters
                equipment_dt['Model_Parameters'][Variable_Name] = option
                for par_calc in equipment_def['Model_Info']['Parameters_Calculations_List']:
                    try:    # Try to generate parameters 
                        getattr(Parameters_Update_Module, par_calc)(equipment_dt['Model_Parameters'])
                    except:
                        pass

                # Call Calculation organizer for Equipment Design

                save_result(f'\nThe solution of {equipment_key} "{Type_Equipment}" with {Variable_Name} = {option} is presented below:')

                sol_eq = Calculations_Execute_Solver.Execute_Solver(Type_Equipment,
                                                        equipment_def['Next_Level'],
                                                        equipment_def['Set_Trimming_Mode'],
                                                        equipment_def['Sorting_Mode'],
                                                        equipment_def['Enumeration_Mode'],
                                                        equipment_def['Model_Info']['List_of_Variables'],
                                                        equipment_def['Set_Trimming_Info'],
                                                        equipment_def['Enumeration_Info']['Enumeration_Constraint_List'],
                                                        equipment_def['Enumeration_Info']['Lower_Bound_Equation'],
                                                        equipment_def['Enumeration_Info']['Fobj_within_LB'],
                                                        equipment_dt['Model_Declarations']['Sorting_by_Variable'],
                                                        equipment_dt['Model_Declarations']['Objective_Function']['Equation_Name'],
                                                        equipment_dt['Model_Declarations']['Objective_Function']['Optimization_Variables_Names'],
                                                        equipment_dt['Model_Declarations']['Type_Enumeration'],
                                                        equipment_dt['Model_Declarations']['Discrete_Values_of_Variables'], #added to be used in Incremental
                                                        Candidates_Set,
                                                        equipment_dt['Model_Declarations']['Segmentation_Parameters'],
                                                        equipment_dt['Model_Declarations']['Incumbent_Initialization']['Incumbent_Obj_Value'],
                                                        equipment_dt['Model_Declarations']['Incumbent_Initialization']['Incumbent_Variables'],
                                                        equipment_dt['Model_Parameters'],
                                                        Active_Example['Next_Level_Equipments'],
                                                        Active_Models['Constraints_and_OF'],
                                                        Active_Models['Parameters_Update'],
                                                        Active_Models['Models_Def'],
                                                        Selected_Model, Selected_Example, save_result)

                # Save obtained results
                OF_Sol_new = sol_eq[OF_Function][OF_Variable]
                if OF_Sol_new < OF_Sol:
                    OF_Sol = OF_Sol_new
                    Solution = copy.deepcopy(sol_eq)
                    Solution[Variable_Name] = option

                    # Checks to see if there is another option for recursive trimming variable:
                    if index < len(Selected_Options) - 1:
                        # Checks to see if objective function allows for objective function trimming
                        if OF_Function in ST_Exclusion_Functions:

                            save_result(f'Since Selected Objective Function {OF_Function} does not allow for recursive trimming, initial set will be used for next {Variable_Name} option.\n')
                        else:
                            Candidates_Set = Trimming_Obj_Function.Fobj_Trim(OF_Function, Initial_Set, equipment_dt['Model_Parameters'],
                                                                             Type_Equipment, Active_Models['Constraints_and_OF'], OF_Sol)
                            save_result(f'Previous solution used for trimming, candidates reduced from {Initial_Set.shape[1]} to {Candidates_Set.shape[1]}\n')

        # No recursive trimming applied:
        else:
            # Call Calculation organizer for Equipment Design
            save_result(f'The solution of {equipment_key} "{Type_Equipment}" is presented below:')
            sol_eq = Calculations_Execute_Solver.Execute_Solver(Type_Equipment,
                                                    equipment_def['Next_Level'],
                                                    equipment_def['Set_Trimming_Mode'],
                                                    equipment_def['Sorting_Mode'],
                                                    equipment_def['Enumeration_Mode'],                                                    
                                                    equipment_def['Model_Info']['List_of_Variables'],
                                                    equipment_def['Set_Trimming_Info'],  
                                                    equipment_def['Enumeration_Info']['Enumeration_Constraint_List'],  
                                                    equipment_def['Enumeration_Info']['Lower_Bound_Equation'],
                                                    equipment_def['Enumeration_Info']['Fobj_within_LB'],
                                                    equipment_dt['Model_Declarations']['Sorting_by_Variable'],
                                                    equipment_dt['Model_Declarations']['Objective_Function']['Equation_Name'],
                                                    equipment_dt['Model_Declarations']['Objective_Function']['Optimization_Variables_Names'],
                                                    equipment_dt['Model_Declarations']['Type_Enumeration'],
                                                    equipment_dt['Model_Declarations']['Discrete_Values_of_Variables'], #added to be used in Incremental
                                                    Candidates_Set,
                                                    equipment_dt['Model_Declarations']['Segmentation_Parameters'],        
                                                    equipment_dt['Model_Declarations']['Incumbent_Initialization']['Incumbent_Obj_Value'],
                                                    equipment_dt['Model_Declarations']['Incumbent_Initialization']['Incumbent_Variables'],
                                                    equipment_dt['Model_Parameters'],
                                                    Active_Example['Next_Level_Equipments'],
                                                    Active_Models['Constraints_and_OF'],
                                                    Active_Models['Parameters_Update'],
                                                    Active_Models['Models_Def'],
                                                    Selected_Model, Selected_Example, save_result)
    
            # Save obtained results
            OF_Function = equipment_dt['Model_Declarations']['Objective_Function']['Equation_Name'][0]
            OF_Variable = equipment_dt['Model_Declarations']['Objective_Function']['Optimization_Variables_Names'][0] 
            OF_Unit = equipment_dt['Model_Declarations']['Objective_Function']['Unit_OF'][0] # Retrive objective function measurement unit
            OF_Sol = sol_eq[OF_Function][OF_Variable]
            Solution = sol_eq

        total_solution += OF_Sol   # Summation of obtained objective function

        equip_end_time = time.time()
        equip_elapsed_time = equip_end_time - equip_start_time
        Sol_Dict[equipment_key] = Solution                    # Stores complete individual Equipment Solution
        save_result(f'Elapsed time for {equipment_key} "{Type_Equipment}": {equip_elapsed_time:.2f} seconds', '\n')

    Sol_Dict['total_solution'] = total_solution             # Stores summation of Equipments Objective Functions
    save_result(f'OF Solution total ({OF_Unit})', total_solution)

    return Sol_Dict

#endregion
####################################################################################################################

