##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.2         28-Feb-2025     Alice Peccini              Relocating folders
#   0.3         26-Mar-2025     Mariana Mello              Update STHE examples
#   0.4         23-Apr-2025     Mariana Mello              Update STHE Model Parameters
#   0.5         30-Jun-2025     Mariana Mello              Add examples with larger search space
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add Examples of STHE in this file
'''
This is a STHE Model Examples File, Set Trimming is applied.

The main structure of the dictionary is:

ExampleX = {

    'Number_of_Equipment': N,

    'Equipment1': {}

    'Equipment2': {}

         ...

    'EquipmentN': {}

}

For each 'STHE' Type_Equipment the following data are required:

'EquipmentN': {

    'Model_Declarations': {

        'Type_Equipment': 'STHE',

        'Discrete_Values_of_Variables': [
                [],  # Ds

                [],  # dte

                [],  # Npt

                [],  # rp

                [],  # lay    (1  = 90° ;  2 = 30° ; 3 = 45°)

                [],  # L

                [],  # Nb

                []  # Bc
    },

    'Model_Parameters': {

           # Hot stream
            'mh': ,         # Flow rate (kg*s**-1)
            'roh': ,        # Density (kg*m**-3)
            'Cph': ,        # Heat capacity (J*(kg*K)**-1)
            'mih': ,        # Viscosity (Pa*s)
            'kh': ,         # Thermal conductivity (W*(m*K)**-1)
            'Rfh': ,        # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': ,    # Available pressure drop (Pa)

            # Cold stream
            'mc': ,        # Flow rate (kg*s**-1)
            'roc': ,       # Density (kg*m**-3)
            'Cpc': ,       # Heat capacity (J*(kg*K)**-1)
            'mic': ,       # Viscosity (Pa*s)
            'kc': ,        # Thermal conductivity (W*(m*K)**-1)
            'Rfc': ,       # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': ,   # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': ,            # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': ,              # Tube thickness
            'yfluid': ,           # Allocation of tube side: 'hot_stream' or 'cold_stream'. Entry is optional.
                                  # If entry is given as '' or if entry is completly skipped, both options will be evaluated

            # Correlations Tube and Shell Methods
            'Shell_Method': '',      # Kern or Bell
            'Tube_Method': '',       # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate

            # Problem
            'Objective_Function': '',    # Objective Functions: 'TAC' or 'Area' or 'CAPEX'
            'Aexc': ,                    # Area excess (%)
            'Tci': ,                     # Inlet temperature of the cold stream (oC)
            'Tco': ,                     # Outlet temperature of the cold stream (oC)
            'Thi': ,                     # Inlet temperature of the hot stream (oC)
            'Tho': ,                     # Outlet temperature of the hot stream (oC)
            'vsmax': ,                   # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': ,                   # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': ,                   # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': ,                   # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': ,                  # Lower bound on the tube-side Reynolds number
            'Resmin': ,                  # Lower bound on the shell-side Reynolds number
            'Retmax': ,                  # Upper bound on the tube-side Reynolds number
            'Resmax': ,                  # Upper bound on the shell-side Reynolds number
            'LBLD': ,                    # Lower bound on L/D
            'UBLD': ,                    # Upper bound on L/D

            # Required parameters for Bell Method
            'Nss': ,                   # Number of sealing strips
            'plbmax1': ,               # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': ,               # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys


            # Economic data
            'par_a': ,           # Cost model parameter
            'par_b': ,           # Cost model parameter
            'pc': ,              # Energy price ($)
            'int_rate': ,        # Interest rate
            'n': ,               # Project horizon (years)
            'eta': ,             # Pump efficiency
            'Nop':               # Number of hours of operation per year (h/y)

    }
}
'''

##################################################################################################################

# region Import Library
import numpy as np
import copy
# endregion

####################################################################################################################
####################################################################################################################

# region INPUT EXAMPLE 1 - STHE

Example1 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay  (1 = 90° ;  2 = 30° ; 3 = 45°)

                [1.2195, 1.8293, 2.4390, 3.0488, 3.6585, 4.8768, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.25] # Bc

            ],

            'Selected_OF': ['TAC_OF'],  #Options:   'TAC_OF', 'CAPEX_OF', 'AREA_OF'

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 20,           # Flow rate (kg*s**-1)
            'roh': 750,         # Density (kg*m**-3)
            'Cph': 2840,        # Heat capacity (J*(kg*K)**-1)
            'mih': 0.002,       # Viscosity (Pa*s)
            'kh': 0.19,         # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.0002,      # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 100e3,   # Available pressure drop (Pa)

            # Cold stream
            'mc': 60,           # Flow rate (kg*s**-1)
            'roc': 995,         # Density (kg*m**-3)
            'Cpc': 4187,        # Heat capacity (J*(kg*K)**-1)
            'mic': 0.0005,      # Viscosity (Pa*s)
            'kc': 0.6,          # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.0007,      # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': 100e3,   # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': 50,                  # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,               # Tube thickness
            'yfluid': 'hot_stream',       # Allocation of tube side: 'hot_stream' or 'cold_stream'

            # Correlations Tube and Shell Methods
            'Tube_Method': 'Dittus_Boelter',  # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate
            'Shell_Method': 'Kern',           # Kern or Bell

            # Problem
            'Aexc': 11,                   # Area excess (%)
            'Tci': 47,                    # Inlet temperature of the cold stream (oC)
            'Tco': 56,                    # Outlet temperature of the cold stream (oC)
            'Thi': 120,                   # Inlet temperature of the hot stream (oC)
            'Tho': 80,                    # Outlet temperature of the hot stream (oC)
            'vsmax': 2,                   # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,                 # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,                   # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,                   # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,                # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,                # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,                # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,                # Upper bound on the shell-side Reynolds number
            'LBLD': 3,                    # Lower bound on L/D
            'UBLD': 15,                   # Upper bound on L/D
            'Xp': 0.9,                    # Parameter Xp (Smith, 2005)
            'F_min': 0.75,                # Minimum LMTD Correction Factor


            # Data Economic
            'par_a': 635.14,    # Cost model parameter
            'par_b': 0.778,     # Cost model parameter
            'pc': 0.15,         # Energy price ($)
            'int_rate': 0.1,    # Interest rate
            'n': 10,            # Project horizon (years)
            'eta': 0.6,         # Pump efficiency
            'Nop': 7500         # Number of hours of operation per year (h/y)

        }
    },
}

# endregion

####################################################################################################################

# region INPUT EXAMPLE 2 - STHE

Example2 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay  (1  = 90° ;  2 = 30° ; 3 = 45°)

                [1.2195, 1.8293, 2.4390, 3.0488, 3.6585, 4.8768, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.25]  # Bc

            ],

            'Selected_OF': ['TAC_OF'],
            
        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 60,           # Flow rate (kg*s**-1)
            'roh': 995,         # Density (kg*m**-3)
            'Cph': 4187,        # Heat capacity (J*(kg*K)**-1)
            'mih': 0.0005,      # Viscosity (Pa*s)
            'kh': 0.6,          # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.0007,      # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 100e3,   # Available pressure drop (Pa)

            # Cold stream
            'mc': 80,           # Flow rate (kg*s**-1)
            'roc': 985,         # Density (kg*m**-3)
            'Cpc': 4183,        # Heat capacity (J*(kg*K)**-1)
            'mic': 0.005,       # Viscosity (Pa*s)
            'kc': 0.6,          # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.0006,      # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': 100e3,   # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': 50,                    # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,                 # Tube thickness
            'yfluid': 'cold_stream',        # Allocation, 1 = Cold stream in the tube side - 2 = Hot stream in the tube side

            # Correlations Tube and Shell Methods
            'Tube_Method': 'Dittus_Boelter',  # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate
            'Shell_Method': 'Kern',           # Kern or Bell

            # Problem
            'Aexc': 11,                   # Area excess (%)
            'Tci': 25,                    # Inlet temperature of the cold stream (oC)
            'Tco': 31.8,                  # Outlet temperature of the cold stream (oC)
            'Thi': 56,                    # Inlet temperature of the hot stream (oC)
            'Tho': 47,                    # Outlet temperature of the hot stream (oC)
            'vsmax': 2,                   # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,                 # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,                   # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,                   # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,                # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,                # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,                # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,                # Upper bound on the shell-side Reynolds number
            'LBLD': 3,                    # Lower bound on L/D
            'UBLD': 15,                   # Upper bound on L/D
            'Xp': 0.9,                    # Parameter Xp (Smith, 2005)
            'F_min': 0.75,                # Minimum LMTD Correction Factor

            # Economic
            'par_a': 635.14,    # Cost model parameter
            'par_b': 0.778,     # Cost model parameter
            'pc': 0.15,         # Energy price ($)
            'int_rate': 0.1,    # Interest rate
            'n': 10,            # Project horizon (years)
            'eta': 0.6,         # Pump efficiency
            'Nop': 7500         # Number of hours of operation per year (h/y)
        }
    }
}

# endregion

######################################################################################################################

# region INPUT EXAMPLE 3 - STHE with Bell or Kern Method: Example 1 from Lemos et al (2020)

Example3 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay    (1  = 90° ;  2 = 30° ; 3 = 45°)

                [1.2195, 1.8293, 2.4390, 3.0488, 3.6585, 4.8768, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.25]  # Bc
            ],

            'Selected_OF': ['TAC_OF'],
            
        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 110,          # Flow rate (kg*s**-1)
            'roh': 786,         # Density (kg*m**-3)
            'Cph': 2177,        # Heat capacity (J*(kg*K)**-1)
            'mih': 0.00189,     # Viscosity (Pa*s)
            'kh': 0.12,         # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.0002,      # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 100e3,   # Available pressure drop (Pa)

            # Cold stream
            'mc': 228.8,        # Flow rate (kg*s**-1)
            'roc': 995,         # Density (kg*m**-3)
            'Cpc': 4187,        # Heat capacity (J*(kg*K)**-1)
            'mic': 0.00072,     # Viscosity (Pa*s)
            'kc': 0.59,         # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.0004,      # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': 100e3,   # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': 50,              # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 0.001225,          # Tube thickness
            'yfluid': 'cold_stream',  # Allocation of tube side: 'hot_stream' or 'cold_stream'

            # Correlations Tube and Shell Methods
            'Shell_Method': 'Bell',             # Kern or Bell
            'Tube_Method': 'Dewiit_Saunders',   # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate

            # Problem
            'Aexc': 11,                    # Area excess (%)
            'Tci': 30,                     # Inlet temperature of the cold stream (oC)
            'Tco': 40,                     # Outlet temperature of the cold stream (oC)
            'Thi': 90,                     # Inlet temperature of the hot stream (oC)
            'Tho': 50,                     # Outlet temperature of the hot stream (oC)
            'vsmax': 2,                    # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,                  # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,                    # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,                    # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,                 # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,                 # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,                 # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,                 # Upper bound on the shell-side Reynolds number
            'LBLD': 3,                     # Lower bound on L/D
            'UBLD': 15,                    # Upper bound on L/D
            'Xp': 0.9,                     # Parameter Xp (Smith, 2005)
            'F_min': 0.75,                 # Minimum LMTD Correction Factor

            # Required parameters for Bell Method
            'Nss': 0,                      # Number of sealing strips
            'plbmax1': 52,                 # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,              # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

            # Data Economic
            'par_a': 755.781,    # Cost model parameter
            'par_b': 0.59,       # Cost model parameter
            'pc': 0.1048,        # Energy price ($)
            'int_rate': 0.1,     # Interest rate
            'n': 10,             # Project horizon (years)
            'eta': 0.6,          # Pump efficiency
            'Nop': 7500          # Number of hours of operation per year (h/y)
        }
    }
}

# endregion

######################################################################################################################

# region Example 4 - Example 1 with AREA_OF

Example4 = copy.deepcopy(Example1)
Example4['Equipment1']['Model_Declarations']['Selected_OF'] = ['AREA_OF']

# endregion

#####################################################################################################################

# region Example 5 - Example 2 with AREA_OF

Example5 = copy.deepcopy(Example2)
Example5['Equipment1']['Model_Declarations']['Selected_OF'] = ['AREA_OF']

# endregion

#####################################################################################################################

# region Example 6 - Example 1 with AREA_OF and allocation of tube side 'hot_stream' and 'cold_stream'

Example6 = copy.deepcopy(Example1)
Example6['Equipment1']['Model_Declarations']['Selected_OF'] = ['AREA_OF']
Example6['Equipment1']['Model_Parameters']['yfluid'] = ''

# endregion

######################################################################################################################

# region Example 7 - Example 1 with larger space search

Example7 = copy.deepcopy(Example1)
Example7['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
                [0.2032, 0.254, 0.3048, 0.33655, 0.38735, 0.43815, 0.48895, 0.53975, 0.59055, 0.635, 0.6858, 0.7366,
                 0.7874, 0.8382, 0.8890, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 1.6764, 1.8288, 1.9812,
                 2.1336, 2.286, 2.4384, 2.7432, 3.048],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2, 3],  # lay  -->  1  = 90° and 2 = 30° and 3 = 45°

                [1.2195, 1.524, 1.8288, 2.1336, 2.4384, 2.7432, 3.048, 3.3528, 3.6576, 3.9624, 4.2672, 4.572, 4.8768,
                 5.1816, 5.4864, 5.7912, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]  # Bc
                ]
# endregion

######################################################################################################################

# region Example 8 - Example 2 with larger space search

Example8 = copy.deepcopy(Example2)
Example8['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
                [0.2032, 0.254, 0.3048, 0.33655, 0.38735, 0.43815, 0.48895, 0.53975, 0.59055, 0.635, 0.6858, 0.7366,
                 0.7874, 0.8382, 0.8890, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 1.6764, 1.8288, 1.9812,
                 2.1336, 2.286, 2.4384, 2.7432, 3.048],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2, 3],  # lay  -->  1  = 90° and 2 = 30° and 3 = 45°

                [1.2195, 1.524, 1.8288, 2.1336, 2.4384, 2.7432, 3.048, 3.3528, 3.6576, 3.9624, 4.2672, 4.572, 4.8768,
                 5.1816, 5.4864, 5.7912, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]  # Bc
                ]
# endregion

######################################################################################################################

# region INPUT EXAMPLE 9 - STHE with Bell Method: Example 2 from Lemos et al (2020)

Example9 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay    (1  = 90° ;  2 = 30° ; 3 = 45°)

                [1.2195, 1.8293, 2.4390, 3.0488, 3.6585, 4.8768, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.25]  # Bc

            ],

            'Selected_OF': ['TAC_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 50,  # Flow rate (kg*s**-1)
            'roh': 786,  # Density (kg*m**-3)
            'Cph': 2177,  # Heat capacity (J*(kg*K)**-1)
            'mih': 0.00189,  # Viscosity (Pa*s)
            'kh': 0.12,  # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.00018,  # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 60e3,  # Available pressure drop (Pa)

            # Cold stream
            'mc': 130,  # Flow rate (kg*s**-1)
            'roc': 995,  # Density (kg*m**-3)
            'Cpc': 4187,  # Heat capacity (J*(kg*K)**-1)
            'mic': 0.00072,  # Viscosity (Pa*s)
            'kc': 0.59,  # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.00026,  # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': 50e3,  # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': 50,  # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 0.001225,  # Tube thickness
            'yfluid': 'cold_stream',  # Allocation of tube side: 'hot_stream' or 'cold_stream'

            # Correlations Tube and Shell Methods
            'Shell_Method': 'Bell',  # Kern or Bell
            'Tube_Method': 'Dewiit_Saunders',
            # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate

            # Problem
            'Aexc': 11,  # Area excess (%)
            'Tci': 30,  # Inlet temperature of the cold stream (oC)
            'Tco': 40,  # Outlet temperature of the cold stream (oC)
            'Thi': 100,  # Inlet temperature of the hot stream (oC)
            'Tho': 50,  # Outlet temperature of the hot stream (oC)
            'vsmax': 2,  # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,  # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,  # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,  # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,  # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,  # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,  # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,  # Upper bound on the shell-side Reynolds number
            'LBLD': 3,  # Lower bound on L/D
            'UBLD': 15,  # Upper bound on L/D
            'Xp': 0.9,  # Parameter Xp (Smith, 2005)
            'F_min': 0.75,  # Minimum LMTD Correction Factor

            # Required parameters for Bell Method
            'Nss': 0,  # Number of sealing strips
            'plbmax1': 52,
            # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,
            # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

            # Data Economic
            'par_a': 755.781,  # Cost model parameter
            'par_b': 0.59,  # Cost model parameter
            'pc': 0.1048,  # Energy price ($)
            'int_rate': 0.1,  # Interest rate
            'n': 10,  # Project horizon (years)
            'eta': 0.6,  # Pump efficiency
            'Nop': 7500  # Number of hours of operation per year (h/y)
        }
    }
}

# endregion

######################################################################################################################

# region Example 10 - Example 3 with larger space search

Example10 = copy.deepcopy(Example3)
Example10['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
                [0.2032, 0.254, 0.3048, 0.33655, 0.38735, 0.43815, 0.48895, 0.53975, 0.59055, 0.635, 0.6858, 0.7366,
                 0.7874, 0.8382, 0.8890, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 1.6764, 1.8288, 1.9812,
                 2.1336, 2.286, 2.4384, 2.7432, 3.048],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2, 3],  # lay  -->  1  = 90° and 2 = 30° and 3 = 45°

                [1.2195, 1.524, 1.8288, 2.1336, 2.4384, 2.7432, 3.048, 3.3528, 3.6576, 3.9624, 4.2672, 4.572, 4.8768,
                 5.1816, 5.4864, 5.7912, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]  # Bc
                ]
# endregion

######################################################################################################################

# region Example 11 - Example 9 with larger space search

Example11 = copy.deepcopy(Example9)
Example11['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
                [0.2032, 0.254, 0.3048, 0.33655, 0.38735, 0.43815, 0.48895, 0.53975, 0.59055, 0.635, 0.6858, 0.7366,
                 0.7874, 0.8382, 0.8890, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 1.6764, 1.8288, 1.9812,
                 2.1336, 2.286, 2.4384, 2.7432, 3.048],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2, 3],  # lay  -->  1  = 90° and 2 = 30° and 3 = 45°

                [1.2195, 1.524, 1.8288, 2.1336, 2.4384, 2.7432, 3.048, 3.3528, 3.6576, 3.9624, 4.2672, 4.572, 4.8768,
                 5.1816, 5.4864, 5.7912, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]  # Bc
                ]
# endregion

######################################################################################################################

# region INPUT EXAMPLE 12 (EXAMPLE 1 with big data set) - STHE

Example12 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.7957, 0.804, 0.8122, 0.8128, 0.8205, 0.8288, 0.8371, 0.8382, 
                0.8453, 0.8536, 0.8619, 0.8636, 0.8702, 0.8784, 0.8867, 0.889, 0.895, 
                0.9033, 0.9115, 0.9144, 0.9198, 0.9281, 0.9364, 0.9398, 0.9447, 0.9529, 
                0.9612, 0.9652, 0.9695, 0.9778, 0.986, 0.9906, 0.9943, 1.0026, 1.0109, 
                1.016, 1.0191, 1.0274, 1.0357, 1.0414, 1.044, 1.0522, 1.0605, 1.0668, 
                1.0688, 1.0771, 1.0854, 1.0922, 1.0936, 1.1019, 1.1102, 1.1176, 1.1185, 
                1.1267, 1.135, 1.143, 1.1433, 1.1516, 1.1598, 1.1681, 1.1684, 1.1764, 
                1.1847, 1.1929, 1.1938, 1.2012, 1.2095, 1.2178, 1.2192, 1.226, 1.2343, 
                1.2426, 1.2446, 1.2509, 1.2592, 1.2674, 1.27, 1.2757, 1.284, 1.2923, 
                1.2954, 1.3005, 1.3088, 1.3171, 1.3208, 1.3254, 1.3336, 1.3419, 1.3462, 
                1.3502, 1.3585, 1.3667, 1.3716, 1.375, 1.3833, 1.3916, 1.397, 1.3999, 
                1.4081, 1.4164, 1.4224, 1.4247, 1.433, 1.4412, 1.4478, 1.4495, 1.4578, 
                1.4661, 1.4732, 1.4743, 1.4826, 1.4909, 1.4986, 1.4992, 1.5074, 1.5157, 
                1.524],  # Ds

                [0.01905, 0.02132, 0.02359, 0.0254, 0.02585, 0.02812, 0.03039, 0.03175, 
                 0.03266, 0.03492, 0.03719, 0.0381, 0.03946, 0.04173, 0.044, 0.04626, 0.04853, 0.0508],  # dte

                [1, 2, 4, 6, 8],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay  (1 = 90° ;  2 = 30° ; 3 = 45°)

                [1.2195, 1.4835, 1.7476, 1.8293, 2.0116, 2.2756, 2.439, 
                2.5396, 2.8036, 3.0488, 3.0677, 3.3317, 3.5957, 3.6585, 
                3.8598, 4.1238, 4.3878, 4.6519, 4.8768, 4.9159, 5.1799, 
                5.4439, 5.7079, 5.9719, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.20, 0.25, 0.3, 0.35, 0.4] # Bc

            ],

            'Selected_OF': ['TAC_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 20,           # Flow rate (kg*s**-1)
            'roh': 750,         # Density (kg*m**-3)
            'Cph': 2840,        # Heat capacity (J*(kg*K)**-1)
            'mih': 0.002,       # Viscosity (Pa*s)
            'kh': 0.19,         # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.0002,      # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 100e3,   # Available pressure drop (Pa)

            # Cold stream
            'mc': 60,           # Flow rate (kg*s**-1)
            'roc': 995,         # Density (kg*m**-3)
            'Cpc': 4187,        # Heat capacity (J*(kg*K)**-1)
            'mic': 0.0005,      # Viscosity (Pa*s)
            'kc': 0.6,          # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.0007,      # Fouling factor (m**2*oC*W**-1)
            'DPcdisp': 100e3,   # Available pressure drop (Pa)

            # Heat exchanger
            'ktube': 50,                  # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,               # Tube thickness
            'yfluid': 'hot_stream',       # Allocation of tube side: 'hot_stream' or 'cold_stream'

            # Correlations Tube and Shell Methods
            'Tube_Method': 'Dittus_Boelter',  # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate
            'Shell_Method': 'Kern',           # Kern or Bell

            # Required parameters for Bell Method
            'Nss': 0,                      # Number of sealing strips
            'plbmax1': 52,                 # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,              # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

            # Problem
            'Aexc': 11,                   # Area excess (%)
            'Tci': 47,                    # Inlet temperature of the cold stream (oC)
            'Tco': 56,                    # Outlet temperature of the cold stream (oC)
            'Thi': 120,                   # Inlet temperature of the hot stream (oC)
            'Tho': 80,                    # Outlet temperature of the hot stream (oC)
            'vsmax': 2,                   # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,                 # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,                   # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,                   # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,                # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,                # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,                # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,                # Upper bound on the shell-side Reynolds number
            'LBLD': 3,                    # Lower bound on L/D
            'UBLD': 15,                   # Upper bound on L/D
            'Xp': 0.9,                    # Parameter Xp (Smith, 2005)
            'F_min': 0.75,                # Minimum LMTD Correction Factor


            # Data Economic
            'par_a': 635.14,    # Cost model parameter
            'par_b': 0.778,     # Cost model parameter
            'pc': 0.15,         # Energy price ($)
            'int_rate': 0.1,    # Interest rate
            'n': 10,            # Project horizon (years)
            'eta': 0.6,         # Pump efficiency
            'Nop': 7500         # Number of hours of operation per year (h/y)

        }
    },
}

# endregion

######################################################################################################################

# region INPUT EXAMPLE 13 (EXAMPLE 1 Bell with big data set) - STHE

Example13 = copy.deepcopy(Example12)
Example13['Equipment1']['Model_Parameters']['Shell_Method'] = 'Bell'

# endregion

######################################################################################################################