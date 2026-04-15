##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     João Tupinambá                HFM Examples Repository
#   0.1         23-Mar-2026     Diego Oliva                   HFM Example 1 modified to support new HFM model
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add Examples of HFM in this file
'''
This is a HFM Model Examples File, Set Trimming is applied.

The main structure of the dictionary is:

ExampleX = {

    'Number_of_Equipment': N,

    'Equipment1': {}

    'Equipment2': {}

         ...

    'EquipmentN': {}

}

For each 'HFM' Type_Equipment the following data are required:

'EquipmentN': {

    'Model_Declarations': {

        'Type_Equipment': 'HF_Membrane',

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

# region INPUT EXAMPLE 1 - HF_Membrane

Example1 = {

    'Number_of_Equipment': 1,

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
                list(np.round(np.linspace(0.3, 0.5, 21), 2))  # Void_Frac # 0.30,0.31,0.32...
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

            'COMPONENTS': ['CO2', 'CH4','N2'],
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4',
            'KEY_COMPONENT_COMP_RET': 'CO2',

            'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
            'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
            "T": 308,
            "P_Feed": 15e5,
            "P_Permeate": 1e5,
            "f_total": 0.35,
            'U_Feed_Target': 0.35*np.array([0.1, 0.9, 0.0]),
            # "s_flow": 0,
            "comp_f": np.array([0.1, 0.9, 0.0]),
            # "comp_s": np.array([0.0, 0.0, 1.0]),
            'V_Sweep_Target': 0*np.array([0.0, 0.0, 1.0]),
            "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]),
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4,

            # Mechanical stress constants
            # Valores retirados da tabela 13.12 de 'Properties of Polymers' do Van Krevelen
            #                              >> PARA POLI-IMIDAS <<
            'E': 3e9, # Módulo de Young (Pa)
            'sigma_y': 75e6, # Tensão de escoamento (Pa)
            'nu': 0.42, # Coeficiente de Poisson
            # A tabela é para polímero "unmodified". O CO2 vai baixar esses valores através da plastificação.
            'degradation_factor': 0.7, # fator de 0.7 foi escolhido com base no valor de fator de segurança
            'safety_factor': 3.0, # três vezes a espessura mínima calculada no polímero virgem já considerando o fator de degradação


            # Solver options
            'N_Partitions': 20,

            # Bounds and minimal recovery
            'LDLB': 3,                    # Lower bound on L/D
            'LDUB': 10,                   # Upper bound on L/D

            'REC_MIN': 0.97, # Recovery for enumeration
            'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.03,0.30]),
            #Proxy recovery for trimming
            'REC_MIN_PROXY': 0.97

        }
    },
}

# endregion

####################################################################################################################
