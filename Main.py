##################################################################################################################
#region Titles and Header
# Nature: Optimization
# Methodology: Set Trimming and/or Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          12-Dec-2024     Mariana Mello             Original - Apply direct loop
#   0.2          17-Jan-2025     Mariana Mello             Change the name
#   0.3          24-Jan-2025     Mariana Mello             Changes for solve flowsheet with recycle or not
#   0.4          03-Fev-2025     Alice Peccini             Changes for different enumeration type selection
#   0.5          25-Fev-2025     Diego Oliva               Ubication of examples changed. Examples are in
#   0.5          25-Fev-2025     Diego Oliva               subfolders related with the unit type.
#   0.5          25-Fev-2025     Diego Oliva               Calling structure: Examples_unit.Example_name
#   0.5          25-Fev-2025     Diego Oliva               e.g. for STHE you should write:
#   0.5          25-Fev-2025     Diego Oliva               Active_Example = Examples_STHE.Example1
#   0.6          26-Fev-2025     Alice Peccini             Repository dynamic importation
#   0.7          27-Fev-2025     Alice Peccini             OptiProcess Code Structure Update
#   0.8          26-Apr-2025     Mariana Mello             Add .txt file with Results of Examples
#   0.9          13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.10         29-Ago-2025     Diego Oliva               New Set Trimming Incremental full developed
##################################################################################################################
#endregion

##################################################################################################################
##################################################################################################################
#region INPUT: !! Only Model and Example Selection and if you want to create a .txt file with the results!!
# !! Do not modify any other aspect of the file !!
##################################################################################################################


Selected_Model = 'HFM'          # The same as defined in Models_List (CASE SENSITIVE)
Selected_Example = 'Example2'   # The same as defined in Examples_{Model} in Model folder (CASE SENSITIVE)
Create_Results_txt = True       # True or False


##################################################################################################################
#endregion
##################################################################################################################
##################################################################################################################
#region Import Library
##################################################################################################################
from OptiCode import (
    Calculations_Prep_Organizer,
    Calculations_Solver_Selection,
    Calculations_Consistency_Check,
    Import_Example,
    Import_Functions,
    Import_Models)
import sys
import os
import time
##################################################################################################################
#endregion
##################################################################################################################
##################################################################################################################
#region Import Active Example Data and Models Declarations
##################################################################################################################

# Ensure the root directory is in sys.path so Python can locate modules
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

# ========================================= IMPORT SELECTED EXAMPLE DATA =========================================

# Dynamically select the active example based on user input
try:
    Active_Repository = Import_Example.Import_Example(Selected_Model,'Examples_')
except:
    print(f'**There is no Example Repository named Examples_{Selected_Model} in {Selected_Model} folder. Check and try again**')
    sys.exit()

Active_Example = getattr(Active_Repository, Selected_Example)

# ================================================================================================================

f_path = f"{Selected_Model}"
file_name = f"Results_{Selected_Model}_{Selected_Example}.txt"
file_path = os.path.join(f_path, file_name)

try:
    if Create_Results_txt:
        with open(file_path, "w", encoding="utf-8") as f:
            pass
except NameError or KeyError:
    print('\n@@@@@@@@ A .txt file with the results was automatically created @@@@@@@@')
    with open(file_path, "w", encoding="utf-8") as f:
        pass

def save_result(*texts):
    text_c = " ".join(str(t) for t in texts)
    try:
        if Create_Results_txt:
            print(text_c)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(text_c + "\n")
        else:
            print(text_c)
    except NameError or KeyError:
        print(text_c)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(text_c + "\n")

# ===================================== IMPORT REQUIRED MODELS DECLARATIONS =====================================

Active_Models_List = [Selected_Model]

# Identify which models are required for first optimization level
for i in range(1, Active_Example['Number_of_Equipment'] + 1):
    
    equipment_key = f'Equipment{i}'             
    Active_Models_List.append(Active_Example[equipment_key]['Model_Declarations']['Type_Equipment'])

# Identify which models are required for next level optimization (if it exists)
if Active_Example.get('Next_Level_Equipments'):

    for i in range(1, Active_Example['Next_Level_Equipments']['Number_of_Equipment'] + 1):
        equipment_key = f'Equipment{i}'
        Active_Models_List.append(Active_Example['Next_Level_Equipments'][equipment_key]['Model_Declarations']
                                  ['Type_Equipment'])

# Removes duplicates from the list
Active_Models_List = list(set(Active_Models_List))

Active_Models = {}
# Import Active_Models Definitions
Active_Models['Models_Def'] = Import_Models.Import_Models(Active_Models_List,'Model_Def_')
# Import Active_Models Constraints_and_OF
Active_Models['Constraints_and_OF'] = Import_Functions.Import_Functions(Active_Models_List,'Constraints_and_OF_')
# Import Active_Models Parameters_Update
Active_Models['Parameters_Update'] = Import_Functions.Import_Functions(Active_Models_List,'Parameters_Update_')

##################################################################################################################
#endregion
##################################################################################################################

##################################################################################################################
#region Run Optimization Code
##################################################################################################################

# Recording start time
start_time = time.time()

# Calls for Example Data Consistency Check 
Calculations_Consistency_Check.Consistency_Check(Active_Example, Active_Models, save_result)

# Active Example Initial Set Up (Parameters, Primordial and Initial Set Generation)
Calculations_Prep_Organizer.Prep_Organizer(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result)

save_result(f'\n******************** Starting Execution for {Selected_Model}_{Selected_Example} ********************\n')

# Call calculations
Solution = Calculations_Solver_Selection.Solver_Selection(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result)

# Record end time
end_time = time.time()


elapsed_total_time = end_time - start_time

save_result(f'Total time elapsed: {elapsed_total_time:.5f} seconds\n')


##################################################################################################################
#endregion
##################################################################################################################

