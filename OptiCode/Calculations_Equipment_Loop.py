#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          03-Jan-2024     Mariana Mello             Original - Function of Equipment Loop
#   0.2          03-Fev-2025     Alice Peccini             Minor change to avoid SyntaxError: f-string: unmatched '['
#   0.3          05-Feb-2025     Mariana Mello             Changes in arguments to fix error
#   0.4          28-Fev-2025     Alice Peccini             OptiProcess Code Structure Update
#   0.5          17-Apr-2025     Mariana Mello             Update Error Correction
#   0.6          26-Apr-2025     Mariana Mello             Add .txt file with Results of Examples
#   0.7          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
#   0.8          13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.9          25-Jun-2025     Mariana Mello             Minor changes
#   0.10         04-Aug-2025     Alice Peccini             Include Next Level m_p dictionaries for set_up functions
##################################################################################################################
##################################################################################################################
#endregion

#region Import Library
from OptiCode import Calculations_Solver_Organizer
import os
#endregion

####################################################################################################################
#region Calculations

def ST_SE_Equipment_Loop(x, Active_Example, Active_Models, Selected_Model, Selected_Example, save_result):

    # Identify path for results text file
    f_path = f"{Selected_Model}"
    file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
    file_path = os.path.join(f_path, file_name)

    # Retrieve General Information
    Model_Definitions = Active_Models['Models_Def'][Selected_Model] # Model_Def dictionary for Selected_Model
    Number_of_Equipments = Active_Example['Number_of_Equipment']    # Number of Equipments for Selected_Example

    # Retrieve the Setup Function Name and the corresponding module where it is implemented
    Set_Up_Global_Optimizer = Model_Definitions['Global_Optimizer_Info']['Set_Up_Global_Optimizer']
    Module_name = Active_Models['Parameters_Update'][Selected_Model]
    
    # Generate the Model_Parameters dictionary, which includes model parameters and equipment types 
    Model_Parameters = {
        f'm_p{i+1}': {
            **Active_Example[f'Equipment{i+1}']['Model_Parameters'], 
            'Type_Equipment': Active_Example[f'Equipment{i+1}']['Model_Declarations']['Type_Equipment']
        } 
        for i in range(Number_of_Equipments)
    }

    # Generate the Model_Parameters dictionary for next level equipments, if they exist
    NL_Number_of_Equipments = Active_Example['Next_Level_Equipments'].get('Number_of_Equipment', 0)
    for i in range(NL_Number_of_Equipments):
        Model_Parameters[f'NL_m_p{i+1}'] = {
            **Active_Example['Next_Level_Equipments'][f'Equipment{i+1}']['Model_Parameters'], 
            'Type_Equipment': Active_Example['Next_Level_Equipments'][f'Equipment{i+1}']['Model_Declarations']['Type_Equipment']
        } 

    # Get the list of optimization variables and dynamically create variable mappings from x values using Optimization_Variables
    Optimization_Variables = Model_Definitions['Global_Optimizer_Info']['Optimization_Variables']
    var_dict = dict(zip(Optimization_Variables, x))

    # Call the setup function dynamically, passing unpacked variable values and Model_Parameters
    m_p_dict, feasibility = getattr(Module_name, Set_Up_Global_Optimizer)(*var_dict.values(), Model_Parameters)

    # Temporário: Talvez para tirar esse if de dentro do direct, lá na função de set up pode ser inserido um 
    # parâmetro a ser usado como penalidade na função objetivo e aí pode tirar esse feasibility dos argumentos de saída 
    if not feasibility:
        return 1e20

    for i in range(Number_of_Equipments):
        equipment_key = f'Equipment{i + 1}'
        pd_key = f'm_p{i + 1}'
        Active_Example[equipment_key]['Model_Parameters'].update(m_p_dict[pd_key])

    try:
        Sol_Dict = Calculations_Solver_Organizer.Solver_Organizer(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result)
        
        # Sum of the objective function of each equipment
        solution = Sol_Dict['total_solution']
        unit_OF = Model_Definitions['Global_Optimizer_Info']['Unit_OF']

        #print(f'TAC total ({unit_OF})', solution)
        #save_result(f'TAC total ({unit_OF})', solution)

        return solution

    except UnboundLocalError:
        save_result('There is no feasible solution')

        return 1e20


###################################################################################################################
