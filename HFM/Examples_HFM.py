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

        'Type_Equipment': 'HFM',

        'Discrete_Values_of_Variables': [
                [],  # L

                [],  # D

                [],  # Tuple of (Dfo,esp)

                [],  # Void_Frac
    },

    'Model_Parameters': {

            'COMPONENTS': ['CO2', 'CH4','N2'],
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate
            'Energy_bool': False, #Boolean to evaluate energy balance
            'Pressure_Drop_bool': False, # Boolean to evaluate pressure drop
            'EnthalpyMode': 'NoMix', # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption

            'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
            'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
            "T": 308, # Temperature (K)
            "P_Feed": 15e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 0.35, # Total feed molar flow
            'U_Feed_Target': 0.35*np.array([0.1, 0.9, 0.0]), # Vector of feed molar flow by component (order must be that of 'COMPONENTS')
            # "s_flow": 0, # Total Sweep Flow (not implemented)
            "comp_f": np.array([0.1, 0.9, 0]), # Feed molar fractions (order must be that of 'COMPONENTS')
            # "comp_s": np.array([0.0, 0.0, 1.0]), # Sweep molar fractions (order must be that of 'COMPONENTS', not implemented)
            'V_Sweep_Target': 0*np.array([0.0, 0.0, 1.0]), # Vector of sweep molar flow by component (order must be that of 'COMPONENTS', not implemented)
            "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]), # Permeance [mol/(m2 Pa s)] # Permeances as fallback when permeability is not available
            "S": np.array([3.207e-9, 1.33e-10, 3.968e-10])*25e-6, # Permeability [mol/(m Pa s)] # Permeabilities of components (order must be that of 'COMPONENTS')
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants
            # Using table 13.12 from Van Krevelen's 'Properties of Polymers'
            #                              >> FOR POLY-IMIDES <<
            'E': 3e9, # Young Modulus (Pa)
            'sigma_y': 75e6, # Hoop Stress (Not implemented, to be used when feed is on bore side) (Pa)
            'nu': 0.42, # Poisson's Coefficient
            # The table is for "unmodified" polymer. The following empirical factors account for plasticization.
            'degradation_factor': 0.7, # will change Young Modulus
            'safety_factor': 3.0,  # will change thickness found by sqrt(safety_factor)


            # Solver options
            'N_Partitions': 20, # Empirical value, a routine for grid optimization will be developed

            # Bounds and minimal recovery
            'LDLB': 3,                    # Lower bound on L/D
            'LDUB': 15,                   # Upper bound on L/D

            'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.03,0.30]), #Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            #Proxy recovery for trimming
            'X_RET_KEY_MAX_PROXY': 0.03 #Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)

        }
}
'''

##################################################################################################################

# region Import Library
import numpy as np
import copy

from STHE.Examples_STHE import Example2

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
}

Example11 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'HFM',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                list(np.round(np.linspace(0.3, 2, 18), 2)),  # L
                list(np.linspace(30, 200, 18) * 1e-3),  # D
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

            'COMPONENTS': ["CO2","Propane"],
            'KEY_COMPONENT_RECOVERY_PERM': 'Propane',
            'KEY_COMPONENT_COMP_RET': 'CO2',
            'Energy_bool': False,
            'Pressure_Drop_bool': False,
            'EnthalpyMode': 'NoMix',
            # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption

            'M': np.array([0.044009, 0.044097]), # Molar Mass [CO2, Propane] (kg/mol)
            'MU': np.array([1.48e-5, 8.5e-6]),  # Viscosities [CO2, Propane] (Pa·s)
            "T": 313, # K,
            "P_Feed": 10e5,
            "P_Permeate": 1e5,
            "f_total": 0.0033,
            'U_Feed_Target': 0.0033 * np.array([0.5, 0.5]),
            # "s_flow": 0,
            "comp_f": np.array([0.5, 0.5]),
            # "comp_s": np.array([0.0, 0.0, 1.0]),
            'V_Sweep_Target': 0 * np.array([0.0, 0.0]),
            "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
            "S": np.array([6.8e-8, 7.71e-11])*(4.15e-4-3.41e-4)/2,  # Permeability [mol/(m Pa s)]
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4,  # float or None

            # Mechanical stress constants
            # Valores retirados da tabela 13.12 de 'Properties of Polymers' do Van Krevelen
            #                              >> PARA POLI-IMIDAS <<
            'E': 3e9,  # Módulo de Young (Pa)
            'sigma_y': 75e6,  # Tensão de escoamento (Pa)
            'nu': 0.42,  # Coeficiente de Poisson
            # A tabela é para polímero "unmodified". O CO2 vai baixar esses valores através da plastificação.
            'degradation_factor': 0.7,  # fator de 0.7 foi escolhido com base no valor de fator de segurança
            'safety_factor': 3.0,
            # três vezes a espessura mínima calculada no polímero virgem já considerando o fator de degradação

            # Solver options
            'N_Partitions': 50,

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            'REC_MIN': 0.97,  # Recovery for enumeration
            'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.03, 0.30]), # Enumeration

            # Proxy recovery for trimming
            # 'REC_MIN_PROXY': 0.97,
            'X_RET_KEY_MAX_PROXY': 1000

        }
    },
}


xample2 = {

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

            'COMPONENTS': ['BENZENE', 'TOLUENE'],
            'KEY_COMPONENT_RECOVERY_PERM': 'TOLUENE',
            'KEY_COMPONENT_COMP_RET': 'BENZENE',
            'Energy_bool': False,
            'Pressure_Drop_bool': False,
            'EnthalpyMode': 'NoMix', # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption

            'M': np.array([44.01e-3, 16.04e-3]), # Molar Mass ['BENZENE', 'TOLUENE'] (kg/mol)
            'MU': np.array([1.48e-5, 1.11e-5]),  # Viscosities ['BENZENE', 'TOLUENE'] (Pa·s)
            "T": 308,
            "P_Feed": 15e5,
            "P_Permeate": 1e5,
            "f_total": 0.35,
            "comp_f": np.array([0.1, 0.9]),
            "S": np.array([3.207e-9, 1.33e-10])*25e-6, # Permeability [mol/(m Pa s)]
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None

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

             'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.1, 0.30]), # Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            'X_RET_KEY_MAX_PROXY': 0.1 # Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)
        }
    },
}
# endregion

####################################################################################################################
