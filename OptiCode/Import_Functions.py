##################################################################################################################
#region Titles and Header
# Nature: Optimization
# Methodology: Set Trimming and/or Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0        25-Fev-2025      Alice Peccini              Original
#   0.1        28-Fev-2025      Alice Peccini              OptiProcess Code Structure Update 
##################################################################################################################
#endregion
##################################################################################################################

##################################################################################################################
#region Import Library
import importlib

#endregion
##################################################################################################################

##################################################################################################################
#region Example Dynamic Importation


##################################################################################################################
#region Constraints_and_OF_LB or Parameters_Update Dynamic Importation

def Import_Functions(Models,Prefix):

    # Dictionary to store imported modules
    imported_objects = {}

    # Loop to dynamically create import statements and execute them
    for model in Models:

        file_name = f"{Prefix}{model}"      # Construct module name dynamically. Example: "Constraints_and_OF_STHE"
        module_path = f"{model}.Model.{file_name}"  # Construct module path. Example: STHE.Model.Constraints_and_OF_STHE

        try:
            module = importlib.import_module(module_path)    
            imported_objects[model] = module

        except ModuleNotFoundError:
            print(f"{file_name} not found. Skipping.")
            imported_objects[model] = []
        except ImportError:
            print(f"Could not import {file_name} from {model}. Skipping.")
            imported_objects[model] = []

    return imported_objects