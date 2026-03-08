##################################################################################################################
#region Titles and Header
# Nature: Optimization
# Methodology: Set Trimming and/or Enumeration
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0        25-Fev-2025       Alice Peccini             Original
#   0.1        28-Fev-2025       Alice Peccini             OptiProcess Code Structure Update 
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

def Import_Example(Model,Prefix):

    file_name = f"{Prefix}{Model}"   # Construct the module name dynamically
    
    try:
        module = importlib.import_module(f'{Model}.{file_name}') 
 
        imported_object = module

    except ModuleNotFoundError:
        print(f"Module {Model} not found. Skipping...")
    except ImportError:
        print(f"Could not import {file_name} from {Model}. Skipping...")
    
    return imported_object

#endregion
##################################################################################################################
