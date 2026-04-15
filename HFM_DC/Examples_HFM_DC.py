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

#######################################################################

    'Global_Optimizer': {

        'Selected_Optimizer': 'Direct',
        # Bounds must be given in the same order as model optimization variables ['Tci_n', 'mrecirc_n', 'm_cs_n']
        #'Lower_Bounds': [50, 50, 48],
        'Lower_Bounds': [0.5],
        #'Upper_Bounds': [51, 52, 50]
        'Upper_Bounds': [0.98]
    },
}
# endregion

######################################################################################################################

# region INPUT EXAMPLE 2 - STHE + GPHE

Example2 = {

    'Number_of_Equipment': 2,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'STHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0.7874, 0.8382, 0.889, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524],  # Ds

                [0.01905, 0.02540, 0.03175, 0.03810, 0.05080],  # dte

                [1, 2, 4, 6],  # Ntp

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
            'ktube': 50,        # Tube wall thermal conductivity (W*(m*K)**-1)
            'thk': 1.65e-3,     # Tube thickness
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
            'Nss': 0,           # Number of sealing strips
            'plbmax1': 52,      # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,   # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

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

###########################################################################

    'Equipment2': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'GPHE',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                list(range(10, 800 + 1)),  # Ntp - total number of plates
                # (minimum number of plates -> maximum number of plates)
                # NumbPlatesMin = 10
                # NumbPlatesMax = 800

                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # Pl - Plate size (options of Lp, Lw, Dp)

                [30, 45, 50, 60, 65],  # Sa - Chevron angle

                [1, 2],  # Nph - Number of passes of hot stream

                [1, 2]  # Npc - number of passes of cold stream

            ],

            'Selected_OF': ['TAC_OF'],  # TAC_OF or AREA_OF or CAPEX_OF

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        # in "Constraints_and_OF.py"
        'Model_Parameters': {

            # Hot stream
            'mh': 60,               # Flow rate (kg*s**-1)
            'roh': 995,             # Density (kg*m**-3)
            'Cph': 4187,            # Heat capacity (J*(kg*K)**-1)
            'mih': 0.0005,          # Viscosity (Pa*s)
            'kh': 0.6,              # Thermal conductivity (W*(m*K)**-1)
            'Rfh': 0.0007,          # Fouling factor (m**2*oC*W**-1)
            'DPhdisp': 0.7,         # Available pressure drop (Pa)

            # Cold stream
            'mc': 80,               # Flow rate (kg*s**-1)
            'roc': 985,             # Density (kg*m**-3)
            'Cpc': 4183,            # Heat capacity (J*(kg*K)**-1)
            'mic': 0.005,           # Viscosity (Pa*s)
            'kc': 0.6,              # Thermal conductivity (W*(m*K)**-1)
            'Rfc': 0.0006,          # Fouling Factor (m**2*oC*W**-1)
            'DPcdisp': 0.7,         # Available pressure drop (Pa)

            # Data of heat exchanger
            'kplate': 16.2,         # Thermal conductivity of plate (W*(m*K)**-1)
            'thk': 0.0008,          # Thickness
            'phi': 1.15,            # The surface enlargement factor
            'bp': 0.003,            # Plate gap

            # Problem data
            'Aexc': 11,             # Area excess (%)
            'Tci': 25,              # Inlet temperature of the cold stream (oC)
            'Tco': 31.8,            # Outlet temperature of the cold stream (oC)
            'Thi': 56,              # Inlet temperature of the hot stream (oC)
            'Tho': 47,              # Outlet temperature of the hot stream (oC)
            'vhmax': 0.9,           # Upper bound on the hot stream velocity (m*s**(-1))
            'vhmin': 0.3,           # Lower bound on the hot stream velocity (m*s**(-1))
            'vcmax': 0.9,           # Upper bound on the cold stream velocity (m*s**(-1))
            'vcmin': 0.3,           # Lower bound on the cold stream velocity (m*s**(-1))

            'ppLp': np.array([0.743, 0.978, 1.281, 1.50, 1.835, 2.092, 1.551, 0.400, 1.845, 1.543]),
            # Plate length (m)
            'ppLw': np.array([0.845, 0.812, 1.200, 1.22, 0.945, 1.200, 0.909, 0.125, 0.450, 0.812]),
            # Plate width (m)
            'ppDp': np.array([0.3, 0.288, 0.4, 0.35, 0.3, 0.4, 0.285, 0.03, 0.155, 0.283]),
            # Port diameter (m)

            # Economic data
            'par_a': 635.14,        # Cost model parameter
            'par_b': 0.778,         # Cost model parameter
            'pc': 0.15,             # Energy price ($)
            'int_rate': 0.1,        # Interest rate
            'n': 10,                # Project horizon (years)
            'eta': 0.6,             # Pump efficiency
            'Nop': 7500             # Number of hours of operation per year (h/y)
        }
    },

#######################################################################

    'Global_Optimizer': {

        'Selected_Optimizer': 'Direct',
        # Bounds must be given in the same order as model optimization variables ['Tci_n', 'mrecirc_n', 'm_cs_n']
        #'Lower_Bounds': [40, 40, 40],
        'Lower_Bounds': [40, 40],
#        'Upper_Bounds': [65, 53, 80]
        'Upper_Bounds': [65, 53]

    },
}

# endregion

###################################################################################################################

# region INPUT EXAMPLE 3 - STHE + STHE Bell Method

Example3 = copy.deepcopy(Example1)
Example3['Equipment1']['Model_Parameters']['Shell_Method'] = 'Bell'
Example3['Equipment1']['Model_Parameters']['Tube_Method'] = 'Dewiit_Saunders'
Example3['Equipment2']['Model_Parameters']['Shell_Method'] = 'Bell'
Example3['Equipment2']['Model_Parameters']['Tube_Method'] = 'Dewiit_Saunders'

# endregion

###################################################################################################################

# region INPUT EXAMPLE 4 - STHE + GPHE Bell Method

Example4 = copy.deepcopy(Example2)
Example4['Equipment1']['Model_Parameters']['Shell_Method'] = 'Bell'
Example4['Equipment1']['Model_Parameters']['Tube_Method'] = 'Dewiit_Saunders'

# endregion

###################################################################################################################

# region INPUT EXAMPLE 5 - STHE + Aircooler

Example5 = {

    'Number_of_Equipment': 2,

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
            'Nss': 0,           # Number of sealing strips
            'plbmax1': 52,      # maximum unsupported span of tubes -> 52 for steel and steel alloys and 46 for aluminum and copper alloys
            'plbmax2': 0.532,   # maximum unsupported span of tubes -> 0.532 for steel and steel alloys and 0.436 for aluminum and copper alloys

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
            'Type_Equipment': 'Aircooler',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                [0, 1, 2, 3, 4],  # finnedsurface

                [4.572, 6.096, 7.315, 9.114, 10.973],  # L

                [2, 2.5],  # rp

                [1, 2],  # Nbay

                [1, 2, 3],  # Nbbay

                [35, 38, 41, 44, 47, 50, 53, 56],  # Ntr

                [0, 1, 2, 3, 4, 5, 6, 7, 8],  # aircoolerconfig

                [1, 2],  # Nfanbay

                [1.2, 2.2, 3.2, 4.2, 5.2]  # Dfan

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
            'Rfc': 0.0,         # Fouling Factor (m**2*oC*W**-1)

            # Data of material
            'kt': 44.998,       # Thermal conductivity of material (W*(m*K)**-1)
            'kf': 237.97,       # Fins thermal conductivity
            'thk': 0.002413,    # Tube thickness (m)

            # Selection
            'draft': 1,         # 1 = induced draft - 2 = forced draft

            # Fan system
            'etafan': 0.7,      # Efficiency of fan
            'etasr': 0.95,      # Speed reducer
            'etamotor': 1,      # Efficiency of motor

            'alphat': 0.003175,  # Minimum spacing between the fins of adjacent tubes (m)
            'fd': 0.1524,        # Minimum distance between the fan and the bay width (m)
            'fl': 0.1524,        # Minimum distance between the fan and the bay length (m)

            # Problem data
            'Aexc': 1.1,       # Area excess
            'Tci': 30,         # Inlet temperature of the cold stream (oC)
            'Tco': 50,         # Outlet temperature of the cold stream (oC)
            'Thi': 56,         # Inlet temperature of the hot stream (oC)
            'Tho': 47,         # Outlet temperature of the hot stream (oC)
            'vhmax': 3,        # Upper bound on the hot stream velocity (m*s**(-1))
            'vhmin': 1,        # Lower bound on the hot stream velocity (m*s**(-1))
            'Rehmin': 10000,   # Upper bound on the Reynolds number of hot stream
            'Recmin': 1800,    # Lower bound on the Reynolds number of cold stream
            'Recmax': 1e5,     # Upper bound on the Reynolds number of cold stream
            'LDti_lb': 10,     # Lower bound on the L/Dti
            'Ltpmin': 0.0274,  # Pitch ratio bounds
            'Ltpmax': 0.0986,  # Pitch ratio bounds
            'AotAr_lb': 1,     # Aot/Ar ratio bounds
            'AotAr_ub': 50,    # Aot/Ar ratio bounds
            'Lftf_lb': 3,      # Lower bound on the Lf/tf ratio
            'DfDte_ub': 3,     # Upper bound on the Df/Dte ratio

            'ppNpt': np.array([1, 1, 1, 1, 3, 4, 5, 6, 2]),

            'ppNr': np.array([3, 4, 5, 6, 3, 4, 5, 6, 4]),

            'ppDte': np.array([0.0254, 0.0254, 0.0254, 0.0254, 0.0254]),

            'ppLf': np.array([0.00635, 0.00635, 0.009525, 0.009525, 0.015875]),

            'ppNf': np.array([275, 393, 275, 393, 393]),

            'pptf': np.array([0.000381, 0.000381, 0.000381, 0.000381, 0.000330]),

            'ppF': np.array([]),  # This parameter will calculate by Parameters_Calculations_List

            # Economic data
            'int_rate': 0.15,   # Interest rate
            'y': 10,            # Project horizon (years)
            'hop': 7920,        # Number of operating hours per year (h/year)
            'Cen': 0.0680       # Average industrial electricity price ($/kWh)
        }
},

#######################################################################

    'Global_Optimizer': {

        'Selected_Optimizer': 'Direct',
        # Bounds must be given in the same order as model optimization variables ['Tci_n', 'mrecirc_n']
        'Lower_Bounds': [50, 50],
        'Upper_Bounds': [52, 51]

    },

}

# endregion

###################################################################################################################

# region INPUT EXAMPLE 6 - STHE + Aircooler Bell Method

Example6 = copy.deepcopy(Example5)
Example6['Equipment1']['Model_Parameters']['Shell_Method'] = 'Bell'
Example6['Equipment1']['Model_Parameters']['Tube_Method'] = 'Dewiit_Saunders'

# endregion

###################################################################################################################

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
Example7['Equipment2']['Model_Declarations']['Discrete_Values_of_Variables'] = [
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

###################################################################################################################

# region Example 8 - Example 2 with larger space search for STHE

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

###################################################################################################################

# region Example 9 - Example 3 with larger space search

Example9 = copy.deepcopy(Example3)
Example9['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
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
Example9['Equipment2']['Model_Declarations']['Discrete_Values_of_Variables'] = [
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

###################################################################################################################

# region Example 10 - Example 4 with larger space search for STHE

Example10 = copy.deepcopy(Example4)
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

###################################################################################################################

# region Example 11 - Example 5 with larger space search for STHE

Example11 = copy.deepcopy(Example5)
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

###################################################################################################################

# region Example 12 - Example 6 with larger space search for STHE

Example12 = copy.deepcopy(Example6)
Example12['Equipment1']['Model_Declarations']['Discrete_Values_of_Variables'] = [
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

###################################################################################################################
