##################################################################################################################
# region Titles and Header
# Nature: Examples Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0       17-Feb-2025       Diego Oliva                Distillation Examples Repository
#   0.1       11-Mar-2025       Alice Peccini              Separation of Model_Def and Examples files
#   0.2       12-May-2025       Mariana Mello              Changed name from 'Discretized_Values_of_Variables' to
#                                                          'Discrete_Values_of_Variables'
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add Examples for DC model in this file
##################################################################################################################

##################################################################################################################
############################################## DISTILLATION COLUMN ###############################################
##################################################################################################################

##################################################################################################################
#region Import Library
import copy
#endregion
##################################################################################################################

##################################################################################################################
#region Example Instructions

''' 
This is a DC Model Examples File, Set Trimming and Enumeration are applied. 

The main structure of the dictionary is:

ExampleX = {

    'Number_of_Equipment': N,   

    'Equipment1': {}

    'Equipment2': {}

         ...

    'EquipmentN': {}

}
    
For each 'DC' Type_Equipment the following data are required:

'EquipmentN': {

    'Model_Declarations': {

        'Type_Equipment': 'DC',
                                
        'Discrete_Values_of_Variables': [
            [],     # Nf
            []      # Ns       
    
        'Type_Enumeration': 'Smart' (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')

        # Segmentation parameters - to be used when Segmental Smart Enumeration is true --> Leave it empty otherwise []
        'Segmentation_Parameters' : ['', , ], 
                                # Segmentation_Parameters[0]: The name of the discrete variable needs to mach one of the variables 
                                #                             given in 'List_of_Variables'
                                # Segmentation_Parameters[1]: Increment (n° of values in each segment) 
                                #                             -> If too small --> Excessive n° of intervals
                                #                             -> If too large --> Candidates cutting may not be as effective
                                # Segmentation_Parameters[2]: Correction factor to avoid small interval at the last segment 

        ]
    },

    'Model_Parameters': {

        'Nc' : ,                    # Number of components
        'Nsmin' : ,                 # Minimum number of stages (Condenser + stages within the column + Reboiler)
        'Nfmin' : ,                 # Minimum feed tray
        'Pcol' : ,                  # Column Pressure (Pa) - constant throughout the column --> Pendência: consider some pressure drop
        'z_f' : [ , , ],            # Feed molar composition [COMPONENT1, COMPONENT2, COMPONENT3]
        'F_f' :  ,                  # Feed flow (kmol/h)
        'T_f' :  ,                  # Feed temperature (K)
        'xB_TOP' : ,                # Top benzene purity
        'xB_BOTTOM' : ,             # Bottom benzene purity       
        'Comp_name' : ['', '', ''], # Componentes names (the same as given in Aspen Plus - Case Sensitive), in the same order as componentes feed molar composition     

        'Ur' : ,                    # Reboiler
        'Uc' : ,                    # Condenser
        'Tlpst' : ,                 # Low pressure steam 
        'Tcwin' : ,                 # Cooling water inlet 
        'Tcwout' : ,                # Cooling water outlet 

        'Ccw' : ,                   # Utilities costs ($/kJ) from Turton -> page 245 5ed 
        'Clpst' : ,                 # Utilities costs ($/kJ) from Turton -> page 245 5ed 
        'hours' : ,                 # Number of operation hours in a year (considering 7% of idle capacity)
        'Pb' : ,                    # Payback period (years)
        'lt' : ,                    # Tray spacing
        'roshell' : ,               # roshell (kg/m³)

        'L_D': ,                    #L/D ratio
        'TRL_min': 10,              # Reflux Drum residence time (min)

        'file_name' : ['.bkp'],
        'block_name' : [''],
        'stream_names': ['FEED', 'D-TOP', 'B-BOTTOM'],
        'reflux_ratio_bounds': [,],             # Reflux ratio 
        'distillate_rate_bounds': [,]           # Distillate rate 
                
    }
}

'''
# endregion
###################################################################################################################


###################################################################################################################
# region INPUT EXAMPLE 1 - BTX DISTILLATION COLUMN WITH SEGMENTAL SMART ENUMERATION

Example1 = {

    'Number_of_Equipment': 1,
    # If there is only 1 piece of equipment, add the information as 'Equipment1'.

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'DC',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [
    
                            list(range(3, 41)), # Nf (Feed considered from stage 3 to 40, considering there are always a stripping 
                                                # and a rectifying section)
                                                # Nf is interpreted regarding stages and not trays (same as in Aspen Plus)
                            list(range(5, 43))  # Ns (Stages and not trays, as in Aspen Plus)
                                                # Ns = 5 means: condenser + 3 stages within the column + reboiler
                                                # Ns = 42 means: condenser + 40 stages within the column + reboiler                
                                    ],

            # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',  
            
            # Segmentation parameters - to be used when Segmental Smart Enumeration is true --> Leave it empty otherwise []
            'Segmentation_Parameters' : ['Ns', 6, 0.5], 
                                    # Segmentation_Parameters[0]: The name of the discrete variable needs to mach one of the variables 
                                    #                             given in 'List_of_Variables'
                                    # Segmentation_Parameters[1]: Increment (n° of values in each segment) 
                                    #                             -> If too small --> Excessive n° of intervals
                                    #                             -> If too large --> Candidates cutting may not be as effective
                                    # Segmentation_Parameters[2]: Correction factor to avoid small interval at the last segment


        },

         # These Problem_Parameters are used for the computation of Constraint and Objective function values
         #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {


            # --------------------------- 
            # Problem Data
            # ---------------------------
            # General Data
            'Nc' : 3,                   # Number of components
            'Nsmin' : 13,               # Minimum number of stages (Condenser + 11 stages within the column + Reboiler)
            'Nfmin' : 3,                # Minimum feed tray
            'Pcol' : 1e5,               # Column Pressure (Pa) - constant throughout the column --> Pendência: consider some pressure drop
            # Feed Data 
            'z_f' : [0.14, 0.39, 0.47], # Feed molar composition [Benzene, Toluene, m-Xylene]
            'F_f' :  100,               # Feed flow (kmol/h)
            'T_f' :  113.4 + 273.15,    # Feed temperature (K)
            # Separation Task Specification 
            'xB_TOP' : 0.99,                    # Top benzene purity
            'xB_BOTTOM' : 0.005,                # Bottom benzene purity       
            # Components - NAMES MUST BE THE SAME AS SET IN ASPEN PLUS (if Aspen is to be used)!! CASE SENSITIVE 
            'Comp_name' : ['BENZENE', 'TOLUENE', 'M-XYLENE'],      

            # --------------------------- 
            # Thermal Utilities Data
            # ---------------------------
            # Global heat exchange coefficient (W/m²K) - Cheng - 2009 and Douglas book
            'Ur' : 1050,                # Reboiler
            'Uc' : 850,                 # Condenser
            # Utilities temperatures (K)
            'Tlpst' : 160 + 273.15,     # Low pressure steam 
            'Tcwin' : 303.15,           # Cooling water inlet 
            'Tcwout' : 323.15,          # Cooling water outlet 

            # --------------------------- 
            # Costing Data
            # ---------------------------
            'Ccw' : 0.378e-6,                           # Utilities costs ($/kJ) from Turton -> page 245 5ed 
            'Clpst' : 2.78e-6,                          # Utilities costs ($/kJ) from Turton -> page 245 5ed 
            'hours' : 8150,                             # Number of operation hours in a year (considering 7% of idle capacity)
            'Pb' : 3,                                   # Payback period (years)
            'lt' : 0.6096,                              # Tray spacing
            'roshell' : 7900,                           # roshell (kg/m³)

            # --------------------------- 
            # Reflux Drum Data
            # ---------------------------
            'L_D': 4,                                   # L/D ratio
            'TRL_min': 5,                              # Reflux Drum residence time (min)

            # --------------------------- 
            # Aspen Related Data
            # ---------------------------
            # File, block and streams - ATTENTION: THIS NAMES ARE CASE SENSITIVE, MUST BE THE SAME AS IN ASPEN FILE
            'file_name' : ['BTX Column.bkp'],
            'block_name' : ['COLUMN1'],
            'stream_names': ['FEED', 'D-TOP', 'B-BOTTOM'],
            # Bounds for manipulated variables within Aspen Active Specs
            'reflux_ratio_bounds': [0,100],             # Reflux ratio 
            'distillate_rate_bounds': [0,100]           # Distillate rate 

        }
    },
    
}

# endregion
###################################################################################################################
###################################################################################################################

###################################################################################################################
# region INPUT EXAMPLE 1 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example1_Fix_1 = copy.deepcopy(Example1)

Example1_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example1_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[14],[33]]

# endregion
###################################################################################################################
###################################################################################################################


###################################################################################################################
# region INPUT EXAMPLE 1 WITH PAYBACK PERIOD OF 10 YEARS INSTEAD OF 3

Example2 = copy.deepcopy(Example1)

Example2['Equipment1']['Model_Parameters']['Pb'] = 10

# endregion
###################################################################################################################
###################################################################################################################


###################################################################################################################
# region INPUT EXAMPLE 2 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example2_Fix_1 = copy.deepcopy(Example2)

Example2_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example2_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[15],[38]]

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 3

Example3 = copy.deepcopy(Example1)
Example3['Equipment1']['Model_Parameters']['F_f'] = 25
Example3['Equipment1']['Model_Parameters']['z_f'] = [0.1, 0.25, 0.65]

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 3 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example3_Fix_1 = copy.deepcopy(Example3)

Example3_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example3_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[13],[29]]

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 4

Example4 = copy.deepcopy(Example3)
Example4['Equipment1']['Model_Parameters']['F_f'] = 100

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 3 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example4_Fix_1 = copy.deepcopy(Example4)

Example4_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example4_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[13],[31]]

# endregion
###################################################################################################################
###################################################################################################################


###################################################################################################################
# region INPUT EXAMPLE 4 WITH PAYBACK PERIOD OF 10 YEARS INSTEAD OF 3

Example5 = copy.deepcopy(Example4)
Example5['Equipment1']['Model_Parameters']['Pb'] = 10
Example5['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [list(range(3, 51)),list(range(5, 53))]

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 5 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example5_Fix_1 = copy.deepcopy(Example5)

Example5_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example5_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[15],[37]]

# endregion
###################################################################################################################
###################################################################################################################


###################################################################################################################
# region INPUT EXAMPLE 6

Example6 = copy.deepcopy(Example1)
Example6['Equipment1']['Model_Parameters']['z_f'] = [0.35, 0.25, 0.4]

# endregion
###################################################################################################################
###################################################################################################################



###################################################################################################################
# region INPUT EXAMPLE 6 WITH FIXED SOLUTION FOR PRINT RESULTS (uncomment prints on TAC_OF in file Model>Constraints_and_OF)

Example6_Fix_1 = copy.deepcopy(Example6)

Example6_Fix_1['Equipment1']['Model_Declarations']['Type_Enumeration'] = 'Exhaustive'
Example6_Fix_1['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [[13],[27]]

# endregion
###################################################################################################################
###################################################################################################################


