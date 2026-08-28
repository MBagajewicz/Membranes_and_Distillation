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

# region INPUT EXAMPLE 1 - HFM + DC

Example1 = {

    'Number_of_Equipment': 2,

    'Equipment1': {

 'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'HFM',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                list(np.round(np.linspace(0.5, 2, 16), 2)), #L
                list(np.linspace(50, 200, 16)*1e-3),        #D
                # list(np.round(np.linspace(50, 200, 16)*1e-6,6)),  #dfo  # 50,60,70... | Richard W. Baker(auth.) - Membrane Technology and Applications pg 148
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(np.linspace(0.2, 0.3, 11), 2))  # Void_Frac # 0.20,0.21,0.22...
                # note on membrane thickness: Most gas separation processes using polymer membranes require that the selective
                # membrane layer be extremely thin to achieve economical fluxes. Typical membrane thicknesses are less
                # than 0.5 μm and often less than 0.1 μm >>FOR THE SELECTIVE PART<< | Richard W. Baker(auth.) - Membrane Technology and Applications pg 335
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',  
            
            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CO2', 'CH4','N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate
            'Energy_bool': False, # Boolean to evaluate energy balance
            'Pressure_Drop_bool': False, # Boolean to evaluate pressure drop
            'EnthalpyMode': 'NoMix', # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption

            'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
            'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
            "T": 308, # Temperature (K)
            "P_Feed": 15e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 0.35, # Total feed molar flow
            "comp_f": np.array([0.1, 0.9, 0]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "S": np.array([3.207e-9, 1.33e-10, 3.968e-10])*25e-6, # Permeability [mol/(m Pa s)] # Permeabilities of components (order must be that of 'COMPONENTS')
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants
            # Using table 13.12 from Van Krevelen's 'Properties of Polymers'
            #                              >> FOR POLY-IMIDES <<
            'E': 3e9,  # Young Modulus (Pa)
            'sigma_y': 75e6,  # Hoop Stress (Not implemented, to be used when feed is on bore side) (Pa)
            'nu': 0.42,  # Poisson's Coefficient
            # The table is for "unmodified" polymer. The following empirical factors account for plasticization.
            'degradation_factor': 0.7,  # will change Young Modulus
            'safety_factor': 3.0,  # will change thickness found by sqrt(safety_factor)

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.03, 0.30]), # Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            'X_RET_KEY_MAX_PROXY': 0.03 # Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)

        }
    },
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


Example2 = {

    'Number_of_Equipment': 2,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'HFM',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                list(np.round(np.linspace(0.5, 2, 16), 2)),  # L
                list(np.linspace(50, 200, 16) * 1e-3),  # D
                # list(np.round(np.linspace(50, 200, 16)*1e-6,6)),  #dfo  # 50,60,70... | Richard W. Baker(auth.) - Membrane Technology and Applications pg 148
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)',
                 '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)',
                 '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)',
                 '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)',
                 '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)',
                 '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)',
                 '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)',
                 '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)',
                 '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)',
                 '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)',
                 '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)',
                 '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)',
                 '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)',
                 '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)',
                 '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)',
                 '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)',
                 '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)',
                 '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)',
                 '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)',
                 '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)',
                 '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)',
                 '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)',
                 '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)',
                 '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)',
                 '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)',
                 '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)',
                 '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)',
                 '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)',
                 '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)',
                 '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)',
                 '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)',
                 '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)',
                 '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)',
                 '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)',
                 '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)',
                 '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)',
                 '(0.0003,0.00014)'],
                list(np.round(np.linspace(0.2, 0.3, 11), 2))  # Void_Frac # 0.20,0.21,0.22...
                # note on membrane thickness: Most gas separation processes using polymer membranes require that the selective
                # membrane layer be extremely thin to achieve economical fluxes. Typical membrane thicknesses are less
                # than 0.5 μm and often less than 0.1 μm >>FOR THE SELECTIVE PART<< | Richard W. Baker(auth.) - Membrane Technology and Applications pg 335
            ],
            # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',


        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['PROPYLENE', 'PROPANE'],
            # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'PROPANE',  # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'PROPYLENE',  # Component that has a max molar fraction value acceptable at retentate
            'Energy_bool': False,  # Boolean to evaluate energy balance
            'Pressure_Drop_bool': False,  # Boolean to evaluate pressure drop
            'EnthalpyMode': 'NoMix',
            # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption

            'M': np.array([42.08e-3, 44.10e-3]),  # Molar Mass [CO2, CH4,N2] (kg/mol)
            'MU': np.array([8.0e-6, 7.5e-6]),  # Viscosities [CO2, CH4,N2] (Pa·s)
            "T": 323.15,  # Temperature (K)
            "P_Feed": 3e5,  # Feed pressure (Pa)
            "P_Permeate": 1e5,  # Permeate outlet pressure (Pa)
            "f_total": 0.5,  # Total feed molar flow
            "comp_f": np.array([0.5,0.5]),  # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": np.array([3.0e-7, 3.0e-8]),  # Permeance [mol/(m²·Pa·s)]
            "S": np.array([3.0e-7, 3.0e-8]) * 2e-6,#得改一下
            # Permeability [mol/(m Pa s)] # Permeabilities of components (order must be that of 'COMPONENTS')
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4,
            # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants
            # Using table 13.12 from Van Krevelen's 'Properties of Polymers'
            #                              >> FOR POLY-IMIDES <<
            'E': 2.8e9,  # Young Modulus (Pa)
            'sigma_y': 80e6,  # Hoop Stress (Not implemented, to be used when feed is on bore side) (Pa)
            'nu': 0.42,  # Poisson's Coefficient
            # The table is for "unmodified" polymer. The following empirical factors account for plasticization.
            'degradation_factor': 0.8,  # will change Young Modulus
            'safety_factor': 3.0,  # will change thickness found by sqrt(safety_factor)

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 30,  # Upper bound on L/D

            'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.32, 0.20]),
            # Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            'X_RET_KEY_MAX_PROXY': 0.3,
            # Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)

        }

},

########################################################################

'Equipment2': {

    'Model_Declarations': {

        # Type of Equipment - Models_List
        'Type_Equipment': 'DC_2FEEDS',

        # Discrete_Values_of_Variables
        # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
        'Discrete_Values_of_Variables': [

        list(range(6,18)),


        list(range(15,31)),


        list(range(30,60))


        ],
           'Type_Enumeration': 'Smart',

            'Enumeration_Constraints_List': ['ST_Nf1_Nf2', 'ST_Nf2', 'ST_Ns0'],

            # Segmentation parameters - to be used when Segmental Smart Enumeration is true --> Leave it empty otherwise []
            'Segmentation_Parameters': ['Ns', 6, 0.5],
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
            'Nc': 2,  # Number of components
            'Nsmin': 7,  # Minimum number of stages (Condenser + 11 stages within the column + Reboiler)
            'Nfmin': 3,  # Minimum feed tray
            'Pcol': 1e5,
            # Column Pressure (Pa) - constant throughout the column --> Pendência: consider some pressure drop

            # Feed Data
            'z_f': [[0.3200,0.6800],[0.7686,0.2314]],  # [Feed 1,Feed2] molar composition [Benzene, Toluene]
            'F_f': [0.6466,0.4334],  # [Feed 1,Feed2] flow (kmol/h)
            'T_f': [50 + 273.15, 50 + 273.15],  # [Feed 1,Feed2] temperature (K)

            # Separation Task Specification
            'xB_TOP': 0.98,  # Top benzene purity
            'xB_BOTTOM': 0.02,  # Bottom benzene purity

            # Components - NAMES MUST BE THE SAME AS SET IN ASPEN PLUS (if Aspen is to be used)!! CASE SENSITIVE
            'Comp_name': ['C3H6', 'C3H8'],

            # ---------------------------
            # Thermal Utilities Data
            # ---------------------------
            # Global heat exchange coefficient (W/m²K) - Cheng - 2009 and Douglas book
            'Ur': 1050,  # Reboiler
            'Uc': 850,  # Condenser
            # Utilities temperatures (K)
            'Tlpst': 160 + 273.15,  # Low pressure steam
            'Tcwin': 303.15,  # Cooling water inlet
            'Tcwout': 323.15,  # Cooling water outlet

            # ---------------------------
            # Costing Data
            # ---------------------------
            'Ccw': 0.378e-6,  # Utilities costs ($/kJ) from Turton -> page 245 5ed
            'Clpst': 2.78e-6,  # Utilities costs ($/kJ) from Turton -> page 245 5ed
            'hours': 8150,  # Number of operation hours in a year (considering 7% of idle capacity)
            'Pb': 4,  # Payback period (years)
            'lt': 0.6096,  # Tray spacing
            'roshell': 7900,  # roshell (kg/m³)

            # ---------------------------
            # Reflux Drum Data
            # ---------------------------
            'L_D': 4,  # L/D ratio
            'TRL_min': 5,  # Reflux Drum residence time (min)

            # ---------------------------
            # Aspen Related Data
            # ---------------------------
            # File, block and streams - ATTENTION: THIS NAMES ARE CASE SENSITIVE, MUST BE THE SAME AS IN ASPEN FILE
            'file_name': ['PP Column-2FEEDS(2).bkp'],
            'block_name': ['COLUMN1'],
            'stream_names': ['FEED1', 'FEED2', 'D-TOP', 'B-BOTTOM'],
            # Bounds for manipulated variables within Aspen Active Specs
            'reflux_ratio_bounds': [0, 100],  # Reflux ratio
            'distillate_rate_bounds': [0, 1.08]  # Distillate rate


        }

},

#######################################################################

'Global_Optimizer': {

    'Selected_Optimizer': 'Parameter_Enumeration',
    # Bounds must be given in the same order as model optimization variables ['Separation']
   # Separation_Retentate,Separation_Permeate

    'Lower_Bounds': [0.1,0.1],

    'Upper_Bounds': [0.3,0.3],

    'step1': 0.025,

    'step2':0.025
    }
}


#######################################################################

    'Global_Optimizer': {

        'Selected_Optimizer': 'Parameter_Enumeration',
        # Bounds must be given in the same order as model optimization variables ['Separation']
        
        'Lower_Bounds': [0.1],
       
        'Upper_Bounds': [0.95],

        'step1':0.025
    }
}
# endregion

######################################################################################################################

# region INPUT EXAMPLE 2 - 

# Example2 = {

#   }
# endregion

###################################################################################################################
