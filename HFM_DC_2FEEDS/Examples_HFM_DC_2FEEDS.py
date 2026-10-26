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

        list(range(6,40)),


        list(range(15,50)),


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
            'z_f': [[0.7686,0.2314],[0.3200,0.6800]],  # [Feed 1,Feed2] molar composition [Benzene, Toluene]
            'F_f': [0.4334,0.6466],  # [Feed 1,Feed2] flow (kmol/h)
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

    'step1': 0.05,

    'step2':0.05
    }
}
# endregion

######################################################################################################################

# region INPUT EXAMPLE 2 -

# Example2 = {

#   }
# endregion

###################################################################################################################
