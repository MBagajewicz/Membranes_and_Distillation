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
===============================================================================
HFM MODEL EXAMPLES
===============================================================================

This is a HFM Model Examples File.

The examples define the complete design space and the physical/model parameters
used by the HFM optimization framework.

Set Trimming and Enumeration are controlled through the Model_Declarations
section.

The main structure of the dictionary is:

ExampleX = {
    'Number_of_Equipment': N,
    'Equipment1': {},
    'Equipment2': {},
    ...
    'EquipmentN': {}
}

===============================================================================
1. EQUIPMENT STRUCTURE
===============================================================================

For each 'HFM' Type_Equipment the following data are required:

'EquipmentN': {
    'Model_Declarations': {
        'Type_Equipment': 'HFM',
        'Discrete_Values_of_Variables': [
                [],  # L
                [],  # D
                [],  # Tuple of (Dfo, esp)
                [],  # Void_Frac
                []   # Material
        ],
        'Type_Enumeration': 'Smart',
        'Selected_OF': ['AREA_OF'],
    },
    'Model_Parameters': {
        ...
    }
}

===============================================================================
2. DISCRETE DESIGN VARIABLES
===============================================================================

'Discrete_Values_of_Variables' defines the discrete design space explored by
the optimization framework.

The order of the lists is important and must correspond to the HFM design
variables:

        1. L
        2. D
        3. dfo_esp
        4. Void_Frac
        5. Material

The resulting candidate vector has the form:

    [L, D, dfo_esp, Void_Frac, Material]

where:

    L          = Module/fiber length [m]
    D          = Module/bore diameter [m]
    dfo_esp    = Tuple containing (Dfo, esp)
    Void_Frac  = Void fraction
    Material   = Membrane material identifier

Example:

'Discrete_Values_of_Variables': [
    [...],                     # L
    [...],                     # D
    [...],                     # (Dfo, esp)
    [...],                     # Void_Frac
    ['PI', 'CA']               # Material
]

The Material variable is mandatory in the new configuration, even when only
one material is available:

    ['PI']

If multiple materials are available:

    ['PI', 'CA']

Material-dependent parameters such as Q, S, E, sigma_y, nu,
degradation_factor and safety_factor are indexed using this material name.

===============================================================================
3. ENUMERATION
===============================================================================

'Type_Enumeration' controls the enumeration strategy.

Available options are:

    'Exhaustive'
    'Smart'
    'Segmental_Smart'

The default/recommended strategy is:

    'Smart'

'Selected_OF' defines the objective function(s) selected for the optimization.

Example:

    'Selected_OF': ['AREA_OF']

===============================================================================
4. MODEL PARAMETERS
===============================================================================

'Model_Parameters' contains the physical, operating, transport, mechanical
and numerical parameters required by the HFM simulator and by the constraint
and objective functions.

-------------------------------------------------------------------------------
4.1 Mixture definition
-------------------------------------------------------------------------------

'COMPONENTS':

    List of components present in the feed.

Example:

    'COMPONENTS': ['CO2', 'Propane']

'KEY_COMPONENT_RECOVERY_PERM':

    Component whose recovery to the permeate is constrained.

Example:

    'KEY_COMPONENT_RECOVERY_PERM': 'Propane'

'KEY_COMPONENT_COMP_RET':

    Component used for the retentate composition constraint.

Example:

    'KEY_COMPONENT_COMP_RET': 'CO2'

-------------------------------------------------------------------------------
4.2 Simulation options
-------------------------------------------------------------------------------

'Energy_bool':

    Boolean indicating whether the energy balance is evaluated.

    True  -> energy balance activated
    False -> energy balance deactivated

'Pressure_Drop_bool':

    Boolean indicating whether pressure drop is evaluated.

    True  -> pressure drop activated
    False -> pressure drop deactivated

'UseFugacity':

    Boolean indicating whether fugacity-based calculations are used.

    True  -> fugacity calculation activated
    False -> alternative formulation

'EOS':

    Equation of State used by the HFM thermodynamic calculations.

Example:

    'EOS': 'PR'

where 'PR' represents Peng-Robinson.

'EnthalpyMode':

    Controls the enthalpy calculation mode.

    'Mix'   -> real mixture enthalpy from Peng-Robinson EOS
    'NoMix' -> ideal/averaged enthalpy assumption

Example:

    'Energy_bool': True,
    'Pressure_Drop_bool': True,
    'UseFugacity': True,
    'EOS': 'PR',
    'EnthalpyMode': 'Mix'

-------------------------------------------------------------------------------
4.3 Molecular and transport properties
-------------------------------------------------------------------------------

'M':

    Molecular masses of the components [kg/mol].

The order must correspond to 'COMPONENTS'.

Example:

    'M': np.array([
        44.009,
        44.097
    ])

'MU':

    Dynamic viscosities of the components [Pa.s].

The order must correspond to 'COMPONENTS'.

Example:

    'MU': np.array([
        1.48e-5,
        8.5e-6
    ])

-------------------------------------------------------------------------------
4.4 Operating conditions
-------------------------------------------------------------------------------

'T':

    Feed temperature [K].

'P_Feed':

    Feed pressure [Pa].

'P_Permeate':

    Permeate pressure [Pa].

'f_total':

    Total feed molar flow.

'comp_f':

    Feed molar fractions.

The order must correspond to 'COMPONENTS'.

'U_Feed_Target':

    Target feed molar flow vector by component.

The order must correspond to 'COMPONENTS'.

'V_Sweep_Target':

    Target sweep molar flow vector.

Sweep operation is not currently implemented.

-------------------------------------------------------------------------------
4.5 Membrane transport properties
-------------------------------------------------------------------------------

'Q':

    Permeance of each component.

In the new configuration, transport properties are indexed by membrane
material.

Structure:

    'Q': {
        'PI': np.array([...]),
        'CA': np.array([...])
    }

The order of the array must correspond to 'COMPONENTS'.

Units:

    mol / (m2 Pa s)

'S':

    Permeability of each component.

In the new configuration, permeability is also indexed by membrane material.

Structure:

    'S': {
        'PI': np.array([...]),
        'CA': np.array([...])
    }

Units:

    mol / (m Pa s)

-------------------------------------------------------------------------------
4.6 Heat transfer
-------------------------------------------------------------------------------

'U':

    Heat transfer coefficient [W/(m2 K)].

If U is a numerical value, a constant heat transfer coefficient is used.

If U is None, it is calculated for each control volume.

-------------------------------------------------------------------------------
4.7 Mechanical properties
-------------------------------------------------------------------------------

Mechanical properties are indexed by membrane material.

'E':

    Young's modulus [Pa].

Example:

    'E': {
        'PI': 3e9,
        'CA': 487.3e6
    }

'sigma_y':

    Yield stress [Pa].

Example:

    'sigma_y': {
        'PI': 75e6,
        'CA': 6.6e6
    }

'nu':

    Poisson's ratio.

Example:

    'nu': {
        'PI': 0.42,
        'CA': 0.35
    }

'degradation_factor':

    Empirical factor accounting for material degradation/plasticization.

Example:

    'degradation_factor': {
        'PI': 0.7,
        'CA': 0.8
    }

'safety_factor':

    Mechanical safety factor used in the membrane thickness calculation.

Example:

    'safety_factor': {
        'PI': 3.0,
        'CA': 2.0
    }

===============================================================================
5. SOLVER PARAMETERS
===============================================================================

The following parameters control the numerical solution of the HFM model.

'N_Partitions':

    Number of discretization/control-volume partitions.

Example:

    'N_Partitions': 20

'iteration_tolerance':

    Convergence tolerance for iterative calculations.

'max_num_iterations':

    Maximum number of iterations allowed.

'solver_tolerance':

    Numerical solver tolerance.

'SIM_TIME_BUDGET_S':

    Maximum allowed simulation time [s].

'ENERGY_CONVERGENCE_TOL':

    Energy balance convergence tolerance.

Example:

    'N_Partitions': 20,
    'iteration_tolerance': 1e-6,
    'max_num_iterations': 150,
    'solver_tolerance': 1e-6,
    'SIM_TIME_BUDGET_S': 10,
    'ENERGY_CONVERGENCE_TOL': 1e-2,

===============================================================================
6. ENUMERATION BOUNDS AND CONSTRAINTS
===============================================================================

'LDLB':

    Lower bound for the L/D ratio.

'LDUB':

    Upper bound for the L/D ratio.

'REC_MIN':

    Minimum recovery required for the key component.

'MAX_COMP_RET':

    Maximum acceptable molar fraction of the key component at the retentate.

'MAX_LOSS_PERM':

    Maximum acceptable loss/recovery of the component that should be retained.

Example:

    'LDLB': 6,
    'LDUB': 30,
    'REC_MIN': 0.97,
    'MAX_COMP_RET': 0.03,
    'MAX_LOSS_PERM': 0.30,

-------------------------------------------------------------------------------
6.1 Hydraulic and pressure constraints
-------------------------------------------------------------------------------

'MAX_DP_RET':

    Maximum allowable pressure drop at the retentate side [Pa].

'MAX_P_PERM':

    Maximum allowable permeate pressure [Pa].

'MAX_MACH':

    Maximum allowable Mach number in the bore.

Example:

    'MAX_DP_RET': 2e5,
    'MAX_P_PERM': 10e5,
    'MAX_MACH': 0.1

===============================================================================
7. TRIMMING PARAMETERS
===============================================================================

Parameters used by Set Trimming and its associated proxy constraints are
defined here.

'X_RET_KEY_MAX_PROXY':

    Proxy limit used during trimming for the retentate composition/recovery
    evaluation.

Additional trimming parameters may be defined when required by the active
HFM constraint configuration.

===============================================================================
8. MATERIAL-DEPENDENT PARAMETERS
===============================================================================

Whenever a parameter depends on the membrane material, it must be represented
as a dictionary indexed by the material identifier.

Correct:

    'Q': {
        'PI': np.array([...]),
        'CA': np.array([...])
    }

    'E': {
        'PI': 3e9,
        'CA': 487.3e6
    }

The material identifier appearing in:

    'Discrete_Values_of_Variables'

must exist as a key in every material-dependent parameter dictionary.

For example, if:

    ['PI', 'CA']

is used as the Material design variable, the following parameters must provide
both material entries when they are required by the active model:

    Q
    S
    E
    sigma_y
    nu
    degradation_factor
    safety_factor

===============================================================================
9. COMPLETE MINIMAL EXAMPLE
===============================================================================

ExampleX = {

    'Number_of_Equipment': 1,

    'Equipment1': {

        'Model_Declarations': {

            'Type_Equipment': 'HFM',

            'Discrete_Values_of_Variables': [

                [...],             # L
                [...],             # D
                [...],             # (Dfo, esp)
                [...],             # Void_Frac
                ['PI', 'CA']       # Material
            ],

            'Type_Enumeration': 'Smart',

            'Selected_OF': ['AREA_OF'],
        },

        'Model_Parameters': {

            # Mixture
            'COMPONENTS': ['CO2', 'Propane'],
            'KEY_COMPONENT_RECOVERY_PERM': 'Propane',
            'KEY_COMPONENT_COMP_RET': 'CO2',

            # Simulation
            'Energy_bool': True,
            'Pressure_Drop_bool': True,
            'UseFugacity': True,
            'EOS': 'PR',
            'EnthalpyMode': 'Mix',

            # Physical properties
            'M': np.array([44.009e-3, 44.097e-3]),
            'MU': np.array([1.48e-5, 8.5e-6]),

            # Operating conditions
            'T': 313,
            'P_Feed': 10e5,
            'P_Permeate': 1e5,
            'f_total': 0.0033,
            'comp_f': np.array([0.5, 0.5]),

            # Transport
            'Q': {
                'PI': np.array([...]),
                'CA': np.array([...])
            },

            'S': {
                'PI': np.array([...]),
                'CA': np.array([...])
            },

            # Heat transfer
            'U': 4,

            # Mechanical properties
            'E': {
                'PI': ...,
                'CA': ...
            },

            'sigma_y': {
                'PI': ...,
                'CA': ...
            },

            'nu': {
                'PI': ...,
                'CA': ...
            },

            'degradation_factor': {
                'PI': ...,
                'CA': ...
            },

            'safety_factor': {
                'PI': ...,
                'CA': ...
            },

            # Solver
            'N_Partitions': 20,
            'iteration_tolerance': 1e-6,
            'max_num_iterations': 150,
            'solver_tolerance': 1e-6,
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2,

            # Bounds
            'LDLB': 6,
            'LDUB': 30,

            # Constraints
            'REC_MIN': 0.97,
            'MAX_COMP_RET': 0.03,
            'MAX_LOSS_PERM': 0.30,

            # Hydraulic constraints
            'MAX_DP_RET': 2e5,
            'MAX_P_PERM': 10e5,
            'MAX_MACH': 0.1,

            # Trimming
            'X_RET_KEY_MAX_PROXY': 1000
        }
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

            'Pressure_Drop_bool': False, # Boolean to evaluate pressure drop

            'Energy_bool': False, # Boolean to evaluate energy balance
            'UseFugacity': False, # Boolean to use fugacity as driving force for mass transfer, otherwise partial pressures
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
            'MAX_MACH': 0.1
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
            # Values of the discrete variables
            # (All variables declared in 'List_of_Variables' must be given values)
            'Discrete_Values_of_Variables': [
                list(np.round(np.linspace(0.3, 2, 18), 2)),  # L
                list(np.linspace(30, 200, 18) * 1e-3),  # D
                [
                    '(5e-05,2e-05)', '(6e-05,2e-05)', '(7e-05,2e-05)',
                    '(7e-05,3e-05)', '(8e-05,2e-05)', '(8e-05,3e-05)',
                    '(9e-05,2e-05)', '(9e-05,3e-05)', '(9e-05,4e-05)',
                    '(0.0001,2e-05)', '(0.0001,3e-05)',
                    '(0.0001,4e-05)', '(0.00011,2e-05)',
                    '(0.00011,3e-05)', '(0.00011,4e-05)',
                    '(0.00011,5e-05)', '(0.00012,2e-05)',
                    '(0.00012,3e-05)', '(0.00012,4e-05)',
                    '(0.00012,5e-05)', '(0.00013,2e-05)',
                    '(0.00013,3e-05)', '(0.00013,4e-05)',
                    '(0.00013,5e-05)', '(0.00013,6e-05)',
                    '(0.00014,2e-05)', '(0.00014,3e-05)',
                    '(0.00014,4e-05)', '(0.00014,5e-05)',
                    '(0.00014,6e-05)', '(0.00015,2e-05)',
                    '(0.00015,3e-05)', '(0.00015,4e-05)',
                    '(0.00015,5e-05)', '(0.00015,6e-05)',
                    '(0.00015,7e-05)', '(0.00016,2e-05)',
                    '(0.00016,3e-05)', '(0.00016,4e-05)',
                    '(0.00016,5e-05)', '(0.00016,6e-05)',
                    '(0.00016,7e-05)', '(0.00017,2e-05)',
                    '(0.00017,3e-05)', '(0.00017,4e-05)',
                    '(0.00017,5e-05)', '(0.00017,6e-05)',
                    '(0.00017,7e-05)', '(0.00017,8e-05)',
                    '(0.00018,2e-05)', '(0.00018,3e-05)',
                    '(0.00018,4e-05)', '(0.00018,5e-05)',
                    '(0.00018,6e-05)', '(0.00018,7e-05)',
                    '(0.00018,8e-05)', '(0.00019,2e-05)',
                    '(0.00019,3e-05)', '(0.00019,4e-05)',
                    '(0.00019,5e-05)', '(0.00019,6e-05)',
                    '(0.00019,7e-05)', '(0.00019,8e-05)',
                    '(0.00019,9e-05)', '(0.0002,2e-05)',
                    '(0.0002,3e-05)', '(0.0002,4e-05)',
                    '(0.0002,5e-05)', '(0.0002,6e-05)',
                    '(0.0002,7e-05)', '(0.0002,8e-05)',
                    '(0.0002,9e-05)', '(0.00021,2e-05)',
                    '(0.00021,3e-05)', '(0.00021,4e-05)',
                    '(0.00021,5e-05)', '(0.00021,6e-05)',
                    '(0.00021,7e-05)', '(0.00021,8e-05)',
                    '(0.00021,9e-05)', '(0.00021,0.0001)',
                    '(0.00022,2e-05)', '(0.00022,3e-05)',
                    '(0.00022,4e-05)', '(0.00022,5e-05)',
                    '(0.00022,6e-05)', '(0.00022,7e-05)',
                    '(0.00022,8e-05)', '(0.00022,9e-05)',
                    '(0.00022,0.0001)', '(0.00023,2e-05)',
                    '(0.00023,3e-05)', '(0.00023,4e-05)',
                    '(0.00023,5e-05)', '(0.00023,6e-05)',
                    '(0.00023,7e-05)', '(0.00023,8e-05)',
                    '(0.00023,9e-05)', '(0.00023,0.0001)',
                    '(0.00023,0.00011)', '(0.00024,2e-05)',
                    '(0.00024,3e-05)', '(0.00024,4e-05)',
                    '(0.00024,5e-05)', '(0.00024,6e-05)',
                    '(0.00024,7e-05)', '(0.00024,8e-05)',
                    '(0.00024,0.0001)', '(0.00024,0.00011)',
                    '(0.00025,2e-05)', '(0.00025,3e-05)',
                    '(0.00025,4e-05)', '(0.00025,5e-05)',
                    '(0.00025,6e-05)', '(0.00025,7e-05)',
                    '(0.00025,8e-05)', '(0.00025,9e-05)',
                    '(0.00025,0.0001)', '(0.00025,0.00011)',
                    '(0.00025,0.00012)', '(0.00026,2e-05)',
                    '(0.00026,3e-05)', '(0.00026,4e-05)',
                    '(0.00026,5e-05)', '(0.00026,6e-05)',
                    '(0.00026,7e-05)', '(0.00026,8e-05)',
                    '(0.00026,9e-05)', '(0.00026,0.0001)',
                    '(0.00026,0.00011)', '(0.00026,0.00012)',
                    '(0.00027,2e-05)', '(0.00027,3e-05)',
                    '(0.00027,4e-05)', '(0.00027,5e-05)',
                    '(0.00027,6e-05)', '(0.00027,7e-05)',
                    '(0.00027,8e-05)', '(0.00027,9e-05)',
                    '(0.00027,0.0001)', '(0.00027,0.00011)',
                    '(0.00027,0.00012)', '(0.00027,0.00013)',
                    '(0.00028,2e-05)', '(0.00028,3e-05)',
                    '(0.00028,4e-05)', '(0.00028,5e-05)',
                    '(0.00028,6e-05)', '(0.00028,7e-05)',
                    '(0.00028,8e-05)', '(0.00028,9e-05)',
                    '(0.00028,0.0001)', '(0.00028,0.00011)',
                    '(0.00028,0.00012)', '(0.00028,0.00013)',
                    '(0.00029,2e-05)', '(0.00029,3e-05)',
                    '(0.00029,4e-05)', '(0.00029,5e-05)',
                    '(0.00029,6e-05)', '(0.00029,7e-05)',
                    '(0.00029,8e-05)', '(0.00029,9e-05)',
                    '(0.00029,0.0001)', '(0.00029,0.00011)',
                    '(0.00029,0.00012)', '(0.00029,0.00013)',
                    '(0.00029,0.00014)', '(0.0003,2e-05)',
                    '(0.0003,3e-05)', '(0.0003,4e-05)',
                    '(0.0003,5e-05)', '(0.0003,6e-05)',
                    '(0.0003,7e-05)', '(0.0003,8e-05)',
                    '(0.0003,9e-05)', '(0.0003,0.0001)',
                    '(0.0003,0.00011)', '(0.0003,0.00012)',
                    '(0.0003,0.00013)', '(0.0003,0.00014)'
                ],  # (Dfo, esp)
                list(np.round(np.linspace(0.3, 0.5, 21), 2)),  # Void_Frac
                ['PI']  # Material
            ],
            # Enumeration type
            'Type_Enumeration': 'Smart',
            'Selected_OF': ['AREA_OF'],
        },

        'Model_Parameters': {
            # ==========================================================
            # Feed / mixture
            # ==========================================================
            'COMPONENTS': ["CO2", "Propane"],
            'KEY_COMPONENT_RECOVERY_PERM': 'Propane',
            'KEY_COMPONENT_COMP_RET': 'CO2',

            # ==========================================================
            # Simulation options
            # ==========================================================
            'Energy_bool': True,
            'Pressure_Drop_bool': True,
            'UseFugacity': True,
            'EOS': 'PR',
            'EnthalpyMode': 'NoMix',
            # Mix   = real mixture enthalpy from Peng–Robinson EOS
            # NoMix = ideal/averaged enthalpy assumption

            # ==========================================================
            # Physical properties
            # ==========================================================
            'M': np.array([0.044009, 0.044097]),  # [CO2, Propane] kg/mol
            'MU': np.array([1.48e-5, 8.5e-6]),  # Pa.s
            'T': 313,  # K
            'P_Feed': 10e5,
            'P_Permeate': 1e5,
            'f_total': 0.0033,
            'comp_f': np.array([0.5, 0.5]),

            # ==========================================================
            # Flow targets
            # ==========================================================
            'U_Feed_Target': 0.0033 * np.array([0.5, 0.5]),
            'V_Sweep_Target': 0 * np.array([0.0, 0.0]),

            # ==========================================================
            # Membrane transport properties
            # ==========================================================
            'Q': {
                'PI': np.array([6.8e-8, 7.71e-11])
            },
            'S': {
                'PI': np.array([6.8e-8, 7.71e-11])
                * (4.15e-4 - 3.41e-4) / 2
            },
            # Heat transfer coefficient
            'U': 4,

            # ==========================================================
            # Mechanical properties
            # ==========================================================
            'E': {
                'PI': 3e9
            },
            'sigma_y': {
                'PI': 75e6
            },
            'nu': {
                'PI': 0.42
            },
            'degradation_factor': {
                'PI': 0.7
            },
            'safety_factor': {
                'PI': 3.0
            },

            # ==========================================================
            # Solver options
            # ==========================================================
            'N_Partitions': 20,
            'iteration_tolerance': 1e-6,
            'max_num_iterations': 150,
            'solver_tolerance': 1e-6,
            'SIM_TIME_BUDGET_S': 10,
            'ENERGY_CONVERGENCE_TOL': 1e-2,

            # ==========================================================
            # Bounds
            # ==========================================================
            'LDLB': 3,
            'LDUB': 15,

            # ==========================================================
            # Enumeration / feasibility constraints
            # ==========================================================
            'REC_MIN': 0.97,
            'MAX_COMP_RET': 0.03,
            'MAX_LOSS_PERM': 0.30,

            # ==========================================================
            # Trimming proxy
            # ==========================================================
            'X_RET_KEY_MAX_PROXY': 1000,

            # ==========================================================
            # Hydraulic / pressure constraints
            # ==========================================================
            'MAX_DP_RET': 2e5,
            'MAX_P_PERM': 10e5,
            'MAX_MACH': 0.1
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