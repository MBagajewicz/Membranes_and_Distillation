#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR              DESCRIPTION OF CHANGES MADE
#   0.0        25-Fev-2025      Alice Peccini        Original - Updates Internal Problem Parameters and Execute it
#   0.1        28-Fev-2025      Alice Peccini        OptiProcess Code Structure Update 
##################################################################################################################
##################################################################################################################
# INSTRUCTIONS
# Do not modify this file
# endregion
##################################################################################################################

##################################################################################################################
#region Import Library
from OptiCode import Calculations_Solver_Organizer
#endregion
##################################################################################################################

##################################################################################################################
#region Solver ST/SE of Equipment

def Next_Level(results, Model_Parameters):

    # Dictionary to save Equipments_within solutions
    Solution_Next_Level = {}

    # Organizes problems to be solved
    Type_Equipment = Model_Parameters['Main_Type']                      # Type_equipment of main problem
    Next_Level_Example = Model_Parameters['Next_Level_Data']            # Retrieves Nexte_Level_Equipments Dictionary
    Next_Level_Example.setdefault('Next_Level_Equipments', [])
    Active_Models_Update = Model_Parameters['Active_Models']['Parameters_Update']     # Retrieves Parameters_and_Update Modules
    Active_Models_Def = Model_Parameters['Active_Models']['Models_Def']           # Retrieves Models Definitions
    Set_Up_Module = Active_Models_Update[Type_Equipment]
    Set_Up_Dic = Active_Models_Def[Type_Equipment]['Next_Level_Info']['Set_Up_Next_Level'] 

    # For each internal problem to solve, problem_data is updated with main problem results 
    for equipment_key, Set_Up_fun in Set_Up_Dic.items():
        
        equipment_NL = Next_Level_Example[equipment_key]                   # Identify internal problem (IP)
        Example_Mod_Par_NL = equipment_NL['Model_Parameters']              # IP model_parameters
       
        try:
            getattr(Set_Up_Module, Set_Up_fun)(results,Example_Mod_Par_NL)
        except ModuleNotFoundError:
            raise ValueError(f"Module '{Set_Up_Module}' not found. Ensure it exists in your project.")
        except AttributeError:
            raise ValueError(f"Constraint '{Set_Up_fun}' not found in module '{Set_Up_Module}'. Ensure the function exists.")
     
    # Execute Solver for Internal Problem
    Solution_Next_Level = Calculations_Solver_Organizer.Solver_Organizer(Next_Level_Example,Model_Parameters['Active_Models'],Type_Equipment,Model_Parameters['Selected_Example'], Model_Parameters['Save_Results']) 

    return Solution_Next_Level

#endregion
####################################################################################################################

