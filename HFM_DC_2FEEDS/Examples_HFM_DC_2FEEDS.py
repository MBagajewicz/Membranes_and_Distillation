##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.2         28-Feb-2025     Alice Peccini              Relocating folders
#   0.3         29-Apr-2025     Mariana Mello              Update Model Parameters of STHE
#   0.4         12-May-2025     Mariana Mello              Changed name from 'Discretized_Values_of_Variables' to
#                                                          'Discrete_Values_of_Variables'
#   0.5         25-May-2025     Mariana Mello              Minor changes and add examples to update
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add Examples of Thermal_Loop in this file
##################################################################################################################

# region Import Library
import numpy as np
import copy
# endregion

####################################################################################################################
####################################################################################################################

# region INPUT EXAMPLE 1 - STHE + STHE

Example1 = {

    'Number_of_Equipment': 2,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'HFM',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay

                [1.2195, 1.8293, 2.4390, 3.0488, 3.6585, 4.8768, 6.0976],  # L

                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Nb

                [0.25] # Bc
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

            'ktube': 50,             # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,          # Tube thickness
            'yfluid': 'hot_stream',  # Allocation of tube side: 'hot_stream' or 'cold_stream'


            # Correlations Tube and Shell Methods
            'Tube_Method': 'Dittus_Boelter',  # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate
            'Shell_Method': 'Kern',           # Kern or Bell

            # Problem
            'Aexc': 11,         # Area excess (%)
            'Tci': 47,          # Inlet temperature of the cold stream (oC)
            'Tco': 56,          # Outlet temperature of the cold stream (oC)
            'Thi': 120,         # Inlet temperature of the hot stream (oC)
            'Tho': 80,          # Outlet temperature of the hot stream (oC)
            'vsmax': 2,         # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,       # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,         # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,         # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,      # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,      # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,      # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,      # Upper bound on the shell-side Reynolds number

            'LBLD': 3,          # Lower bound on L/D
            'UBLD': 15,         # Upper bound on L/D
            'Xp': 0.9,          # Parameter Xp (Smith, 2005)
            'F_min': 0.75,      # Minimum LMTD Correction Factor

            # Required parameters for Bell Method
            'Nss': 0,          # Number of sealing strips
            'plbmax1': 52,     # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,  # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

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

########################################################################

    'Equipment2': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'DC',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Npt

                [1.25, 1.33, 1.50],  # rp

                [1, 2],  # lay

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

            'ktube': 50,        # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,     # Tube thickness
            'yfluid': 'cold_stream',        # Allocation, 1 = Cold stream in the tube side - 2 = Hot stream in the tube side


            # Correlations Tube and Shell Methods
            'Tube_Method': 'Dittus_Boelter',  # Dittus_Boelter or Dewiit_Saunders or Gnielinski or Hausen or Sieder_Tate
            'Shell_Method': 'Kern',           # Kern or Bell

            # Problem
            'Aexc': 11,         # Area excess (%)
            'Tci': 25,          # Inlet temperature of the cold stream (oC)
            'Tco': 31.8,        # Outlet temperature of the cold stream (oC)
            'Thi': 56,          # Inlet temperature of the hot stream (oC)
            'Tho': 47,          # Outlet temperature of the hot stream (oC)
            'vsmax': 2,         # Upper bound on the shell-side velocity (m*s**(-1))
            'vsmin': 0.5,       # Lower bound on the shell-side velocity (m*s**(-1))
            'vtmax': 3,         # Upper bound on the tube-side velocity (m*s**(-1))
            'vtmin': 1,         # Lower bound on the tube-side velocity (m*s**(-1))
            'Retmin': 1e4,      # Lower bound on the tube-side Reynolds number
            'Resmin': 2e3,      # Lower bound on the shell-side Reynolds number
            'Retmax': 5e6,      # Upper bound on the tube-side Reynolds number
            'Resmax': 1e5,      # Upper bound on the shell-side Reynolds number
            'LBLD': 3,          # Lower bound on L/D
            'UBLD': 15,         # Upper bound on L/D
            'Xp': 0.9,          # Parameter Xp (Smith, 2005)
            'F_min': 0.75,      # Minimum LMTD Correction Factor

            # Required parameters for Bell Method
            'Nss': 0,          # Number of sealing strips
            'plbmax1': 52,     # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,  # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

            # Economic
            'par_a': 635.14,    # Cost model parameter
            'par_b': 0.778,     # Cost model parameter
            'pc': 0.15,         # Energy price ($)
            'int_rate': 0.1,    # Interest rate
            'n': 10,            # Project horizon (years)
            'eta': 0.6,         # Pump efficiency
            'Nop': 7500         # Number of hours of operation per year (h/y)
        }
},

# endregion

######################################################################################################################

