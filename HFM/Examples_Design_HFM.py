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
            'Energy_bool': True, #Boolean to evaluate energy balance
            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop
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

            'MAX_COMP_RET AND MAX_LOSS_PERMM': np.array([0.03,0.30]), #Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            #Proxy recovery for trimming
            'X_RET_KEY_MAX_PROXY': 0.03 #Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)

        }
}
'''

##################################################################################################################

# region Import Library
import numpy as np
import copy

# from STHE.Examples_STHE import Example2

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
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack # 0.20,0.21,0.22...
                ['PI'] # material
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

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
            'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
            "T": 308, # Temperature (K)
            "P_Feed": 15e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 0.35, # Total feed molar flow (mol/s)
            "comp_f": np.array([0.1, 0.9, 0]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([3.207e-9, 1.33e-10, 3.968e-10])}, # permeance [mol/(m² Pa s)] # Permeances of components (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants (FOR THE FIBER, NOT POLYMER)
            'E': {'PI': 121e6,
                  'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6,
                        'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35,
                   'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8,
                                   'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0,
                              'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.03, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K, means temperature on both sides should be at least APPROACH_T_DEW higher than their dew points at every control volume
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end
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
                list(np.round(np.linspace(0.3, 0.5, 21), 2)),  # Void_Frac # 0.30,0.31,0.32...
                ['PI']
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
            'Energy_bool': True,
            'Pressure_Drop_bool': True,
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
            'N_Partitions': 20,

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            'REC_MIN': 0.97,  # Recovery for enumeration
            'MAX_COMP_RET AND MAX_LOSS_PERM': np.array([0.03, 0.30]), # Enumeration

            # Proxy recovery for trimming
            # 'REC_MIN_PROXY': 0.97,
            'X_RET_KEY_MAX_PROXY': 1000

        }
    },
}

Scenario_S0 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['PI', 'CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CO2', 'CH4', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([44.01e-3, 16.04e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.5154e-5, 1.1354e-5, 1.8035e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 303.15, # Temperature (K)
            "P_Feed": 40e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.1, 0.89, 0.01]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([3.282e-8, 1.641e-9, 3.282e-9]),
                  'CA': np.array([1.6905e-8, 1.127e-9, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'PI': 121e6,
                  'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6,
                        'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35,
                   'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8,
                                   'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0,
                              'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.03, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 2e5, # Maximum pressure DROP on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end
            'MAX_MACH': 0.1
        }
    },
}
# region SCENARIO S1
# Rich multicomponent gas (Chu Table 4 scen. 2 + n-butane carved from Propane).
Scenario_S1 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['PI', 'CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CH4', 'Ethane', 'Propane', 'n-Butane', 'CO2', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([16.04e-3, 30.07e-3, 44.10e-3, 58.12e-3, 44.01e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.1354e-5, 9.5003e-6, 8.2806e-6, 7.5313e-6, 1.5154e-5, 1.8035e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 303.15, # Temperature (K)
            "P_Feed": 60e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.774, 0.077, 0.034, 0.005, 0.1, 0.01]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([1.641e-9, 1.094e-9, 5.470e-10, 1.641e-11, 3.282e-8, 3.282e-9]),
                  'CA': np.array([1.127e-9, 3.7567e-10, 3.381e-10, 1.127e-11, 1.6905e-8, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'PI': 121e6, 'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6, 'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35, 'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8, 'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0, 'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.025, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end (S0 default -- adjust per scenario if needed)
            'MAX_MACH': 0.1,
        }
    },
}
# endregion

# region SCENARIO S2
# High pressure (100 bar): activates buckling (Eq.31) and real-gas effects.
Scenario_S2 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['PI', 'CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CH4', 'Ethane', 'Propane', 'n-Butane', 'CO2', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([16.04e-3, 30.07e-3, 44.10e-3, 58.12e-3, 44.01e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.1354e-5, 9.5003e-6, 8.2806e-6, 7.5313e-6, 1.5154e-5, 1.8035e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 303.15, # Temperature (K)
            "P_Feed": 100e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.774, 0.077, 0.034, 0.005, 0.1, 0.01]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([1.641e-9, 1.094e-9, 5.470e-10, 1.641e-11, 3.282e-8, 3.282e-9]), 'CA': np.array([1.127e-9, 3.7567e-10, 3.381e-10, 1.127e-11, 1.6905e-8, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'PI': 121e6, 'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6, 'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35, 'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8, 'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0, 'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.025, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end (S0 default -- adjust per scenario if needed)
            'MAX_MACH': 0.1,
        }
    },
}
# endregion

# region SCENARIO S3
# Sour gas. CA ONLY: no H2S permeance for PI. H2S is the fastest species in CA, so it is the key (proxy admissible for H2S, not for CO2).
Scenario_S3 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CH4', 'CO2', 'H2S', 'Ethane', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'H2S', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([16.04e-3, 44.01e-3, 34.08e-3, 30.07e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.1354e-5, 1.5154e-5, 1.2292e-5, 9.5003e-6, 1.8035e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 303.15, # Temperature (K)
            "P_Feed": 65e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.87, 0.05, 0.03, 0.03, 0.02]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'CA': np.array([1.127e-9, 1.6905e-8, 2.254e-8, 3.7567e-10, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.005, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end (S0 default -- adjust per scenario if needed)
            'MAX_MACH': 0.1,
        }
    },
}
# endregion

# region SCENARIO S4
# Near dew point. Heavy-HC feed; T_dew=275.5 K at 40 bar, T=288 K leaves a 12.5 K margin for Joule-Thomson cooling. A CO2/CH4/N2 feed could never bind the dew-point constraint (cryogenic dew points).
Scenario_S4 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['PI', 'CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CH4', 'Ethane', 'Propane', 'n-Butane', 'CO2', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([16.04e-3, 30.07e-3, 44.10e-3, 58.12e-3, 44.01e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.0775e-5, 8.9658e-6, 7.7911e-6, 7.0727e-6, 1.4282e-5, 1.7191e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 288, # Temperature (K)
            "P_Feed": 40e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.75, 0.1, 0.06, 0.03, 0.05, 0.01]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([1.641e-9, 1.094e-9, 5.470e-10, 1.641e-11, 3.282e-8, 3.282e-9]), 'CA': np.array([1.127e-9, 3.7567e-10, 3.381e-10, 1.127e-11, 1.6905e-8, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'PI': 121e6, 'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6, 'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35, 'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8, 'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0, 'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.025, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end (S0 default -- adjust per scenario if needed)
            'MAX_MACH': 0.1,
        }
    },
}
# endregion

# region SCENARIO S5
# Deep CO2 removal (20% CO2 -> 2% spec). Highest separation difficulty; stresses Smart Enumeration and the CH4-loss constraint.
Scenario_S5 = {

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
                ['(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)', '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)', '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)', '(0.0001,2e-05)', '(0.0001,3e-05)', '(0.0001,4e-05)', '(0.00011,2e-05)', '(0.00011,3e-05)', '(0.00011,4e-05)', '(0.00011,5e-05)', '(0.00012,2e-05)', '(0.00012,3e-05)', '(0.00012,4e-05)', '(0.00012,5e-05)', '(0.00013,2e-05)', '(0.00013,3e-05)', '(0.00013,4e-05)', '(0.00013,5e-05)', '(0.00013,6e-05)', '(0.00014,2e-05)', '(0.00014,3e-05)', '(0.00014,4e-05)', '(0.00014,5e-05)', '(0.00014,6e-05)', '(0.00015,2e-05)', '(0.00015,3e-05)', '(0.00015,4e-05)', '(0.00015,5e-05)', '(0.00015,6e-05)', '(0.00015,7e-05)', '(0.00016,2e-05)', '(0.00016,3e-05)', '(0.00016,4e-05)', '(0.00016,5e-05)', '(0.00016,6e-05)', '(0.00016,7e-05)', '(0.00017,2e-05)', '(0.00017,3e-05)', '(0.00017,4e-05)', '(0.00017,5e-05)', '(0.00017,6e-05)', '(0.00017,7e-05)', '(0.00017,8e-05)', '(0.00018,2e-05)', '(0.00018,3e-05)', '(0.00018,4e-05)', '(0.00018,5e-05)', '(0.00018,6e-05)', '(0.00018,7e-05)', '(0.00018,8e-05)', '(0.00019,2e-05)', '(0.00019,3e-05)', '(0.00019,4e-05)', '(0.00019,5e-05)', '(0.00019,6e-05)', '(0.00019,7e-05)', '(0.00019,8e-05)', '(0.00019,9e-05)', '(0.0002,2e-05)', '(0.0002,3e-05)', '(0.0002,4e-05)', '(0.0002,5e-05)', '(0.0002,6e-05)', '(0.0002,7e-05)', '(0.0002,8e-05)', '(0.0002,9e-05)', '(0.00021,2e-05)', '(0.00021,3e-05)', '(0.00021,4e-05)', '(0.00021,5e-05)', '(0.00021,6e-05)', '(0.00021,7e-05)', '(0.00021,8e-05)', '(0.00021,9e-05)', '(0.00021,0.0001)', '(0.00022,2e-05)', '(0.00022,3e-05)', '(0.00022,4e-05)', '(0.00022,5e-05)', '(0.00022,6e-05)', '(0.00022,7e-05)', '(0.00022,8e-05)', '(0.00022,9e-05)', '(0.00022,0.0001)', '(0.00023,2e-05)', '(0.00023,3e-05)', '(0.00023,4e-05)', '(0.00023,5e-05)', '(0.00023,6e-05)', '(0.00023,7e-05)', '(0.00023,8e-05)', '(0.00023,9e-05)', '(0.00023,0.0001)', '(0.00023,0.00011)', '(0.00024,2e-05)', '(0.00024,3e-05)', '(0.00024,4e-05)', '(0.00024,5e-05)', '(0.00024,6e-05)', '(0.00024,7e-05)', '(0.00024,8e-05)', '(0.00024,9e-05)', '(0.00024,0.0001)', '(0.00024,0.00011)', '(0.00025,2e-05)', '(0.00025,3e-05)', '(0.00025,4e-05)', '(0.00025,5e-05)', '(0.00025,6e-05)', '(0.00025,7e-05)', '(0.00025,8e-05)', '(0.00025,9e-05)', '(0.00025,0.0001)', '(0.00025,0.00011)', '(0.00025,0.00012)', '(0.00026,2e-05)', '(0.00026,3e-05)', '(0.00026,4e-05)', '(0.00026,5e-05)', '(0.00026,6e-05)', '(0.00026,7e-05)', '(0.00026,8e-05)', '(0.00026,9e-05)', '(0.00026,0.0001)', '(0.00026,0.00011)', '(0.00026,0.00012)', '(0.00027,2e-05)', '(0.00027,3e-05)', '(0.00027,4e-05)', '(0.00027,5e-05)', '(0.00027,6e-05)', '(0.00027,7e-05)', '(0.00027,8e-05)', '(0.00027,9e-05)', '(0.00027,0.0001)', '(0.00027,0.00011)', '(0.00027,0.00012)', '(0.00027,0.00013)', '(0.00028,2e-05)', '(0.00028,3e-05)', '(0.00028,4e-05)', '(0.00028,5e-05)', '(0.00028,6e-05)', '(0.00028,7e-05)', '(0.00028,8e-05)', '(0.00028,9e-05)', '(0.00028,0.0001)', '(0.00028,0.00011)', '(0.00028,0.00012)', '(0.00028,0.00013)', '(0.00029,2e-05)', '(0.00029,3e-05)', '(0.00029,4e-05)', '(0.00029,5e-05)', '(0.00029,6e-05)', '(0.00029,7e-05)', '(0.00029,8e-05)', '(0.00029,9e-05)', '(0.00029,0.0001)', '(0.00029,0.00011)', '(0.00029,0.00012)', '(0.00029,0.00013)', '(0.00029,0.00014)', '(0.0003,2e-05)', '(0.0003,3e-05)', '(0.0003,4e-05)', '(0.0003,5e-05)', '(0.0003,6e-05)', '(0.0003,7e-05)', '(0.0003,8e-05)', '(0.0003,9e-05)', '(0.0003,0.0001)', '(0.0003,0.00011)', '(0.0003,0.00012)', '(0.0003,0.00013)', '(0.0003,0.00014)'],
                list(np.round(1-np.linspace(0.4, 0.6, 21), 2)),  # Void_Frac = 1 - Density_Pack
                # NOTE: manuscript text states void in [0.30, 0.50]; this Example1 line gives [0.40, 0.60]. Reconcile before production.
                ['PI', 'CA']  # Material -> keys the 'Q' and mechanical-property dicts below
            ],
             # Enumeration type (Options are 'Exhaustive', 'Smart' or 'Segmental_Smart' ---> Default is 'Smart')
            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],

        },

        # These Problem_Parameters are used for the computation of Constraint and Objective function values
        #                                                                      in "Constraints_and_OF.py"
        'Model_Parameters': {

            'COMPONENTS': ['CH4', 'Ethane', 'Propane', 'CO2', 'N2'], # Components present on feed, further vectors informed will be on this order
            'KEY_COMPONENT_RECOVERY_PERM': 'CH4', # Component you don't want to lose from feed to permeate
            'KEY_COMPONENT_COMP_RET': 'CO2', # Component that has a max molar fraction value acceptable at retentate

            'Pressure_Drop_bool': True, # Boolean to evaluate pressure drop

            'Energy_bool': True, # Boolean to evaluate energy balance
            'UseFugacity': True, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
            'EOS': "PR", # "PR" or "HEOS"
            'EnthalpyMode': 'Mix', # Mix = real mixture enthalpy from Peng-Robinson EOS // NoMix = ideal/averaged enthalpy assumption


            'M': np.array([16.04e-3, 30.07e-3, 44.10e-3, 44.01e-3, 28.02e-3]), # Molar Mass (kg/mol)
            'MU': np.array([1.1354e-5, 9.5003e-6, 8.2806e-6, 1.5154e-5, 1.8035e-5]),  # Viscosities (Pa s), dilute-gas at 1 bar and T (CoolProp HEOS)
            "T": 303.15, # Temperature (K)
            "P_Feed": 60e5, # Feed pressure (Pa)
            "P_Permeate": 1e5, # Permeate outlet pressure (Pa)
            "f_total": 13.889, # Total feed molar flow (mol/s) = 50 kmol/h (Chu Table 4 basis)
            "comp_f": np.array([0.687, 0.069, 0.034, 0.2, 0.01]), # Feed molar fractions (order must be that of 'COMPONENTS')
            "Q": {'PI': np.array([1.641e-9, 1.094e-9, 5.470e-10, 3.282e-8, 3.282e-9]),
                  'CA': np.array([1.127e-9, 3.7567e-10, 3.381e-10, 1.6905e-8, 1.127e-9])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')

            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.

            # Mechanical stress constants -- FIBER (not dense polymer), by material
            # PI (Matrimid): E=121 MPa, Chen 2017 via Kagramanov 2021 Table 2
            # CA (HB-105)  : E=487.3 MPa, Shieh & Chung 1998 Table 2 (fiber 23/19/58, H2O bore)
            # nu = 0.35 (Kagramanov, glassy polymers). sigma_y not implemented.
            'E': {'PI': 121e6, 'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6, 'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35, 'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8, 'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0, 'CA': 2.0},  # will change thickness

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance

            # Bounds and minimal recovery
            'LDLB': 3,  # Lower bound on L/D
            'LDUB': 15,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.02, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 1e5, # Maximum pressure drop on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end (S0 default -- adjust per scenario if needed)
            'MAX_MACH': 0.1,
        }
    },
}
# endregion

####################################################################################################################



Example6 = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            # Type of Equipment - Models_List
            'Type_Equipment': 'HFM',

            # Discrete_Values_of_Variables
            # Values of the discrete variables (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [

                list(np.round(np.linspace(0.2, 0.51, 4), 2)),  # L
                list(np.linspace(50, 200, 10) * 1e-3),  # D
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

                list(np.round(np.linspace(0.44, 0.55, 8), 2)), # Void_Frac # 0.30,0.31,0.32...
                # note on membrane thickness: Most gas separation processes using polymer membranes require that the selective
                # membrane layer be extremely thin to achieve economical fluxes. Typical membrane thicknesses are less
                # than 0.5 μm and often less than 0.1 μm >>FOR THE SELECTIVE PART<< | Richard W. Baker(auth.) - Membrane Technology and Applications pg 335
                ['PI', 'CA']                                      # Material
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

            'Pressure_Drop_bool': False,
            'Energy_bool': False,
            'UseFugacity': False,
            'EOS': "HEOS",
            'EnthalpyMode': 'Mix',
            # Mix = real mixture enthalpy from Peng–Robinson EOS // NoMix = ideal/averaged enthalpy assumption
            # OLD INPUT
            # 'Energy_bool': False,
            # 'Pressure_Drop_bool': False,
            # 'EnthalpyMode': 'Mix',


            'M': np.array([78.11e-3, 92.14e-3]),  # Molar Mass ['BENZENE', 'TOLUENE'] (kg/mol)
            'MU': np.array([9.5e-6, 8.5e-6]),  # Viscosities ['BENZENE', 'TOLUENE'] (Pa·s)
            "T": 393.15,         # K
            "P_Feed": 2.2e5,     # pa
            "P_Permeate": 0.3e5,    # pa
            "f_total": 0.5,    #mol/s
            "comp_f": np.array([0.5, 0.5]),

            "Q": {'PI': np.array([2.5e-7, 5.0e-8]),
                  'CA': np.array([2.5e-7, 5.0e-8])}, # permeance [mol/(m2 Pa s)] by material (order must be that of 'COMPONENTS')
            "K_POLYMER": 0.2,               # [W/(m K)] Polymer thermal conductivity
            "SUPPORT_POROSITY": 0.5,        # [] Membrane support porosity
            # Heat transfer coefficient [W/(m2 K)]
            'U': 4, # float or None. Used on energy balance, if None it is calculated on each control volume. If float, is constant on that value.
            # OLD INPUT
            # "Q": np.array([2.5e-7, 5.0e-8]),   # Permeance [mol/(m²·Pa·s)]
            # "S": np.array([2.5e-6, 5.0e-7]) * 2e-6,
            # # Heat transfer coefficient [W/(m2 K)]
            # 'U': 4,  # float or None

            # Using table 13.12 from Van Krevelen's 'Properties of Polymers'
            #                              >> FOR POLY-IMIDES <<

            #6FDA-type polyimide
            'E': {'PI': 121e6,
                  'CA': 487.3e6},  # Young Modulus (Pa)
            'sigma_y': {'PI': 54.8e6,
                        'CA': 6.6e6},  # Hoop Stress (Not implemented) (Pa)
            'nu': {'PI': 0.35,
                   'CA': 0.35},  # Poisson's Coefficient
            'degradation_factor': {'PI': 0.8,
                                   'CA': 0.8},  # will change Young Modulus
            'safety_factor': {'PI': 2.0,
                              'CA': 2.0},  # will change thickness            
            #OLD INPUT
            # 'E': 3.0e9,  # Young Modulus (Pa)
            # 'sigma_y': 75e6,  # Hoop Stress (Not implemented, to be used when feed is on bore side) (Pa)
            # 'nu': 0.42,  # Poisson's Coefficient
            # # The table is for "unmodified" polymer. The following empirical factors account for plasticization.
            # 'degradation_factor': 0.8,  # will change Young Modulus
            # 'safety_factor': 3.0,  # will change thickness found by sqrt(safety_factor)

            # Solver options
            'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed
            'iteration_tolerance': 1e-6,  # Mass balance loop tolerance
            'max_num_iterations': 150,  # Max mass balance iterations
            'solver_tolerance': 1e-6,  # Least squares solver tolerance
            # Wall-clock budget for ONE candidate [s]. None = unlimited. A candidate that
            # exceeds it is SKIPPED and recorded in timed_out_candidates.log -- it is
            # UNRESOLVED, not proven infeasible, and must be re-run before claiming
            # global optimality over the enumeration.
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2, # Energy balance loop tolerance
            #OLD INPUT
            # 'N_Partitions': 20,  # Empirical value, a routine for grid optimization will be developed

            # Bounds and minimal recovery
            'LDLB': 6,  # Lower bound on L/D
            'LDUB': 30,  # Upper bound on L/D

            # Smart Enumeration Constraints
            'MAX_LOSS_PERM': 0.30, # Max fraction (mol_permeate/mol_feed) from feed to permeate of valuable component you don't want to lose
            'MAX_COMP_RET': 0.03, # Max molar fraction of unwanted component at retentate
            'APPROACH_T_DEW': 10, # Approach delta T in K
            # Evaluate the dew-point condition on the PERMEATE side as well. The permeate
            # is enriched in the fast, light species, so its dew point lies far below the
            # operating temperature (measured 170-181 K against ~300 K) and the test is
            # redundant there; the retentate is always evaluated.
            'check_dew_permeate': False,
            'MAX_DP_RET': 2e5, # Maximum pressure DROP on retentate side (Pa)
            'MAX_P_PERM': 10e5, # Maximum pressure bore-side. Occurs at permeate closed-end
            'MAX_MACH': 0.1
            #OLD INPUT
            # 'MAX_COMP_RET AND MAX_REC_PERM': np.array([0.25, 0.32]),
            # # Max molar fraction of unwanted component at Retentate and max recovery of component you don't want to lose at permeate.
            # 'X_RET_KEY_MAX_PROXY': 0.3
            # # Proxy for maximum mass transfer (considering the unwanted component as the most permeable, checks if at max mass transfer it achieves <x% molar fraction)
        }
    },
}





# endregion