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
#   0.8          27-Apr-2025     Mariana Mello             Add .txt file with Results of Examples
#   0.9          13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.10         11-Jun-2025     Mariana Mello             Add Golden Section (Global Optimizer)
#   0.11         25-Jun-2025     Mariana Mello             Minor changes
#   0.12         26-Jun-2025     Mariana Mello             Add Parameter_Enumeration (Global Optimizer)

##################################################################################################################
##################################################################################################################
#endregion

#region Import Library
from OptiCode import (
    Calculations_Equipment_Loop,
    Calculations_Execute_Solver,
    Calculations_Solver_Organizer,
    Calculations_Golden_Section
)
from scipy.optimize import direct, golden
import numpy as np

import time
import os
#endregion

####################################################################################################################
#region Calculations_Organizer

def Solver_Selection(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result):

    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    Global_Optimizer = Active_Models['Models_Def'][Selected_Model]['Global_Optimizer']
    
    # =========================================== DIRECT SOLVER ===========================================
    if Global_Optimizer:

        # Identify Optimizer Solver. If none was given select Direct Solver as default
        Optimizer = Active_Example['Global_Optimizer'].get('Selected_Optimizer')
        if not Optimizer:
            Optimizer = 'Direct'


        # Retrieving Optimization Variables Bounds
        LB = Active_Example['Global_Optimizer']['Lower_Bounds']
        UB = Active_Example['Global_Optimizer']['Upper_Bounds']
        bounds = list(zip(LB, UB))

        if Optimizer == 'Direct':

            start_time = time.time()
            save_result('Applying the direct method to optimize')

            result = direct(Calculations_Equipment_Loop.ST_SE_Equipment_Loop, bounds, args=(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result))
            save_result("\nOptimized variables:", result.x)

            unit_OF = Active_Models['Models_Def'][Selected_Model]['Global_Optimizer_Info']['Unit_OF']
            save_result(f'OF_Solution total ({unit_OF}):', result.fun)
            end_time = time.time()
            elapsed_time = end_time - start_time
            save_result(f"Total elapsed time: {elapsed_time:.2f} seconds\n")


        elif Optimizer == 'Golden_Section':

            start_time = time.time()
            save_result('Applying the golden section method to optimize')

            result = Calculations_Golden_Section.golden_section(Calculations_Equipment_Loop.ST_SE_Equipment_Loop, float(LB[0]), float(UB[0]), tol=1e-4, max_iter=100, args=(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result))

            save_result("\nOptimized variable:", result[0])

            unit_OF = Active_Models['Models_Def'][Selected_Model]['Global_Optimizer_Info']['Unit_OF']
            save_result(f'OF_Solution total ({unit_OF}):', result[1])
            end_time = time.time()
            elapsed_time = end_time - start_time
            save_result(f"Total elapsed time: {elapsed_time:.2f} seconds\n")
        elif Optimizer == 'Parameter_Enumeration':

            step = Active_Example['Global_Optimizer'].get('Step')
            if not step:
                step = 5

            start_time = time.time()

            save_result(f'Applying the Parameter_Enumeration with step = {step}')

            x_values = np.arange(float(LB[0]), float(UB[0]), step)
            results = []

            for x in x_values:
                x_input = [x]
                result = Calculations_Equipment_Loop.ST_SE_Equipment_Loop(x_input, Active_Example, Active_Models,
                                                                          Selected_Model, Selected_Example, save_result)
                results.append((x, result))
            x_opt, sol_opt = min(results, key=lambda t: t[1])

            save_result(f"\nOptimized Variable: {x_opt}")
            save_result(f"OF_Solution: {sol_opt}")

            end_time = time.time()
            elapsed_time = end_time - start_time
            save_result(f"Total elapsed time: {elapsed_time:.2f} seconds\n")

        # HERE WE CAN ADD OTHER GLOBAL_OPTIMIZER SOLVERS

        return result

    # ========================================= SEQUENCIAL SOLVER =========================================
    else:

        Sol_Dict = Calculations_Solver_Organizer.Solver_Organizer(Active_Example, Active_Models, Selected_Model,
                                                                  Selected_Example, save_result)

    return Sol_Dict


#endregion
####################################################################################################################



