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
#   0.9          12-May-2025     Mariana Mello             Changed name from 'Discretized_Values_of_Variables' to
#                                                          'Discrete_Values_of_Variables'
#   0.10         13-May-2025     Mariana Mello             Update .txt file with Examples Results
#   0.11         13-Ago-2025     Diego Oliva               Option Incremental added
#   0.12         28-Ago-2025     Diego Oliva               Deleting developer message and 
#   0.12         28-Ago-2025     Diego Oliva               avoid conflicts with old versions (setdefault added)

##################################################################################################################
##################################################################################################################
#endregion

##################################################################################################################
#region Import Library
from OptiCode import Calculations_Initial_Set_Up
#endregion
##################################################################################################################

##################################################################################################################
#region Calculations organizer to call Initial Set Up

def Prep_Organizer(Active_Example, Active_Models, Selected_Model, Selected_Example, save_result):

    # Active_Example: If no next-level problem to solve, ensure 'Next_Level_Equipments' exists as an empty list
    if not Active_Models['Models_Def'][Selected_Model]['Next_Level']:
        Active_Example.setdefault('Next_Level_Equipments', {})

    # Model_Def Files: Iterate over all active models and ensure required data structures exist.
    # - Ensure required dictionaries and lists exist, allowing user-defined inputs when applicable.
    for Model_Name, Model_Def in Active_Models['Models_Def'].items():
        Fill_Model_Definitions(Model_Def)

    # First Level Optimization Equipment Data:
    for i in range(1, Active_Example['Number_of_Equipment'] + 1):

        # Detect Equipment Data and corresponding Model Definitions
        equipment_dt = Active_Example[f'Equipment{i}']
        Type_Equipment = equipment_dt['Model_Declarations']['Type_Equipment']   
        equipment_def = Active_Models['Models_Def'][Type_Equipment]             

        # Fill equipment data and Run Prep_Equipment
        Fill_Equipment_Data(equipment_def, equipment_dt)
        Prep_Equipment(equipment_def, equipment_dt, Active_Models, Selected_Model, Selected_Example, save_result)

    # Next Level Equipment Data:
    if Active_Example.get('Next_Level_Equipments'):
        
        for i in range(1, Active_Example['Next_Level_Equipments']['Number_of_Equipment'] + 1):
   
            # Detect Equipment Data and corresponding Model Definitions
            equipment_dt = Active_Example['Next_Level_Equipments'][f'Equipment{i}']
            Type_Equipment = equipment_dt['Model_Declarations']['Type_Equipment'] 
            equipment_def = Active_Models['Models_Def'][Type_Equipment]

            # Fill equipment data and Run Prep_Equipment
            Fill_Equipment_Data(equipment_def, equipment_dt)
            Prep_Equipment(equipment_def, equipment_dt, Active_Models, Selected_Model, Selected_Example, save_result)

#endregion
####################################################################################################################

##################################################################################################################
#region Auxiliary functions

def Fill_Model_Definitions(Model_Def):
    # Ensure 'Set_Trimming_Info' dictionary and its required keys exist
    Set_trimming_info = Model_Def.setdefault('Set_Trimming_Info', {})
    Set_trimming_info.setdefault('Set_Trimming_Constraints_List', [])
    Set_trimming_info.setdefault('Primordial_Set_Trimming_Constraints_List', None)
    
    # Ensure 'Enumeration_Info' dictionary and its required keys exist
    Enumeration_info = Model_Def.setdefault('Enumeration_Info', {})
    Enumeration_info.setdefault('Enumeration_Constraint_List', [])
    Enumeration_info.setdefault('Fobj_within_LB', False)
    LB_Name = Enumeration_info.setdefault('Lower_Bound_Equation', [])
    if len(LB_Name) == 1: LB_Name.append(LB_Name[0])


def Fill_Equipment_Data(equipment_def, equipment_dt):

    # Set Enumeration default and segmentation parameters
    equipment_dt['Model_Declarations'].setdefault('Type_Enumeration', 'Smart')
    equipment_dt['Model_Declarations'].setdefault('Segmentation_Parameters', [])

    # Fill Incumbent Initialization if none was given
    equipment_dt['Model_Declarations'].setdefault('Incumbent_Initialization', {}).setdefault('Incumbent_Obj_Value', [])
    equipment_dt['Model_Declarations']['Incumbent_Initialization'].setdefault('Incumbent_Variables', [])

    # Detect Model Default Objective Funtion
    Default_Equation_Name = equipment_def['Model_Info']['Objective_Function']['Equation_Name']
    Default_Optimization_Variables_Names = equipment_def['Model_Info']['Objective_Function']['Optimization_Variables_Names']
    Default_Unit = equipment_def['Model_Info']['Objective_Function']['Unit_OF']

    # Detect Selected Objective function(s) if more than one possibility is allowed for a given model
    Selected_OF = equipment_dt['Model_Declarations'].get('Selected_OF', [])
    equipment_dt['Model_Declarations']['Objective_Function'] = {}

    # If no objective section was selected by user, default is used
    if len(Selected_OF) == 0:
        OF_functions = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Equation_Name', Default_Equation_Name)
        OF_variables = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Optimization_Variables_Names', Default_Optimization_Variables_Names)
        OF_units = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Unit_OF', Default_Unit)
    else:
        OF_functions = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Equation_Name',Selected_OF)
        OF_variables = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Optimization_Variables_Names', [])
        OF_units = equipment_dt['Model_Declarations']['Objective_Function'].setdefault('Unit_OF', [])
        # Add selected OF and corresponding information to respective lists
        for Fobj in OF_functions:
            index = Default_Equation_Name.index(Fobj)
            OF_variables.append(Default_Optimization_Variables_Names[index])
            OF_units.append(Default_Unit[index])

    # Determine sorting type (by variable or not) and identifying sorting variable if applicable:
    Sorting_Variable = equipment_dt['Model_Declarations'].setdefault('Sorting_by_Variable', None)
    if Sorting_Variable not in equipment_def['Model_Info']['List_of_Variables']:
        Sorting_Variable = None

def Prep_Equipment(equipment_def, equipment_dt, Active_Models, Selected_Model, Selected_Example, save_result):

    Type_Equipment = equipment_dt['Model_Declarations']['Type_Equipment']  

    equipment_def['Set_Trimming_Info'].setdefault('Incremental_Set_Trimming', False)
    if equipment_def['Set_Trimming_Info']['Incremental_Set_Trimming']:
        save_result('********** Incremental Set Trimming running **********')
    else:
        save_result('********** Normal Set Trimming running **********')


    # Call Initial Set Up for Generation of Model Parameters, Primordial and Initial Sets
    Initial_Set = Calculations_Initial_Set_Up.Calculations_Initial_Set_Up(Type_Equipment,
                                            equipment_def['Set_Trimming_Info'],
                                            equipment_dt['Model_Declarations']['Discrete_Values_of_Variables'],
                                            equipment_dt['Model_Parameters'],
                                            Active_Models['Parameters_Update'][Type_Equipment],
                                            Active_Models['Models_Def'][Type_Equipment]['Model_Info']['Parameters_Calculations_List'],
                                            Active_Models['Constraints_and_OF'], Selected_Model, Selected_Example, save_result)
    # Update Model_Declarations with Initial Set
    equipment_dt['Model_Declarations']['Initial_Set'] = Initial_Set

#endregion
####################################################################################################################

