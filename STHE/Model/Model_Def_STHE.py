##################################################################################################################
# region Titles and Header
# Nature: Repository
# Methodology: Dictionary
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         17-Feb-2025     Diego Oliva                STHE Examples Repository
#   0.2         28-Feb-2025     Alice Peccini              Relocating folders
#   0.3         08-May-2025     Mariana Mello              Add consistency check
##################################################################################################################
# INPUT: Setting of examples
##################################################################################################################
# INSTRUCTIONS
# Add STHE Model info in this file
####################################################################################################################
####################################################################################################################
# region

Model_STHE = {

    # =========================================== General Information ============================================
    # The first entries are General (True or False) Information regarding the Model Operation Mode.
    # These entries are required for all models

    'Global_Optimizer': False,      # Set to True if model requires an external global solver. False otherwise

    'Next_Level': False,            # Set to True if model involves a bilevel optimization. False otherwise

    'Set_Trimming_Mode': True,      # Set to True Set Trimming Mode is selected. False otherwise

    'Sorting_Mode': True,           # Set to True if Sorting is required after Trimming. False otherwise

    'Enumeration_Mode': False,      # Set to True if an Enumeration Mode is to be activated (Enumeration type will 
                                    # be selected by user within Example Data if this is set to True)

    # ============================================= Model Information ============================================
    # This entry is required for all models

    'Model_Info': {

        'Parameters_Calculations_List': ['allocation'],
        # This is a list of functions used to generated model calculated parameters and they must be defined 
        # in Model.Parameters_Update_(Model).py file 
        # These parameters are generated before Initial Set generation by Calculations_Initial_Set_Up.py
        # For bilevel optimization models (e.g. Kettle Model used in next_level of DC_ST_HE model), some of the 
        # functions of the list may be skipped and should be called by model programmer inside Next_Level_Set_Up
        # function

        'List_of_Variables': ['Ds', 'dte', 'Npt', 'rp', 'lay', 'L', 'Nb', 'Bc'],
        # List of discrete design variables. User will give discrete options in example file in the same order as 
        # defined here, and this is also the same order that must be used in Constraints_and_OF.py functions

        'Objective_Function': {
            'Equation_Name': ['TAC_OF', 'CAPEX_OF', 'AREA_OF'],
            'Optimization_Variables_Names': ['TAC', 'CAPEX', 'Area'],
            'Unit_OF': ['$/year', '$', 'm²']
        },
        # Objetive Function to be minimized and its corresponding variable and measurement unit
        # Equation_Name must be a function defined in "Constraints_and_FO.py" where Optimization_Variables_Names is 
        # its return variable. When more than one is given, user may select the desired objective function, but the
        # first one on the list will be the default if no selection is made

        'Consistency_Check_Functions': ['consistency'],
        'Standard_Variables_Values': {
            'Ds': [0.2032, 0.254, 0.3048, 0.33655, 0.38735, 0.43815, 0.48895, 0.53975, 0.59055, 0.635, 0.6858, 0.7366,
                   0.7874, 0.8382, 0.8890, 0.9398, 0.9906, 1.0668, 1.143, 1.2192, 1.3716, 1.524, 1.6764, 1.8288, 1.9812,
                   2.1336, 2.286, 2.4384, 2.7432, 3.048,
                   0.7957, 0.804, 0.8122, 0.8128, 0.8205, 0.8288, 0.8371,
                   0.8453, 0.8536, 0.8619, 0.8636, 0.8702, 0.8784, 0.8867, 0.895,
                   0.9033, 0.9115, 0.9144, 0.9198, 0.9281, 0.9364, 0.9447, 0.9529,
                   0.9612, 0.9652, 0.9695, 0.9778, 0.986, 0.9943, 1.0026, 1.0109,
                   1.016, 1.0191, 1.0274, 1.0357, 1.0414, 1.044, 1.0522, 1.0605, 1.0688,
                   1.0771, 1.0854, 1.0922, 1.0936, 1.1019, 1.1102, 1.1176, 1.1185,
                   1.1267, 1.135, 1.1433, 1.1516, 1.1598, 1.1681, 1.1684, 1.1764,
                   1.1847, 1.1929, 1.1938, 1.2012, 1.2095, 1.2178, 1.226, 1.2343,
                   1.2426, 1.2446, 1.2509, 1.2592, 1.2674, 1.27, 1.2757, 1.284, 1.2923,
                   1.2954, 1.3005, 1.3088, 1.3171, 1.3208, 1.3254, 1.3336, 1.3419, 1.3462,
                   1.3502, 1.3585, 1.3667, 1.375, 1.3833, 1.3916, 1.397, 1.3999,
                   1.4081, 1.4164, 1.4224, 1.4247, 1.433, 1.4412, 1.4478, 1.4495, 1.4578,
                   1.4661, 1.4732, 1.4743, 1.4826, 1.4909, 1.4986, 1.4992, 1.5074, 1.5157,
                   ],
            'dte': [0.01905, 0.02540, 0.03175, 0.03810, 0.05080,
                    0.02132, 0.02359, 0.0254, 0.02585, 0.02812, 0.03039, 0.03175,
                    0.03266, 0.03492, 0.03719, 0.0381, 0.03946, 0.04173, 0.044, 0.04626, 0.04853, 0.0508
                    ],
            'Npt': [1, 2, 4, 6, 8],
            'rp': [1.25, 1.33, 1.50],
            'lay': [1, 2, 3],
            'L': [1.2195, 1.524, 1.8288, 2.1336, 2.4384, 2.7432, 3.048, 3.3528, 3.6576, 3.9624, 4.2672, 4.572, 4.8768,
                  5.1816, 5.4864, 5.7912, 6.0976,
                  1.4835, 1.7476, 1.8293, 2.0116, 2.2756, 2.5396, 2.8036, 3.0677, 3.3317, 3.5957, 3.6585,
                  3.8598, 4.1238, 4.3878, 4.6519, 4.8768, 4.9159, 5.1799,
                  5.4439, 5.7079, 5.9719],
            'Nb': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'Bc': [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
        }

        # Functions that checks if Example Data provided by user has any consistency problems (e.g. negative flows or compositions)
        # These functions must be provided on Parameters_Update_{Model}.py file
        
    },

    # ========================================= Set Trimming Information =========================================
    # Set Trimming Information section only needs to be filled if Set_Trimming_Mode is set to True. If not, 
    # model programmer may either leave an empty dictionary or completely skip the entry definition

    'Set_Trimming_Info': {

        'Incremental_Set_Trimming': False,
        # If it is True you will run Set Trimming in incremental mode
        # If it is False you will run Set Triming in tradicional mode (i.e. all variables will be always used)

        'All_Variables_In_The_Problem': ['Ds', 'dte', 'Npt', 'rp', 'lay', 'L', 'Nb', 'Bc'],
        # These are all variables used in the problem constraints ordered as they are declared in constraints; is
        # used when 'Incremental_Set_Trimming" is set to True.

        'Primordial_Set_Trimming_Constraints_List': ['LD_lb', 'LD_ub', 'lbc_lb', 'lbc_ub'],
        # These are the Set_Trimming functions used for Initial Set Generation (they are applied to Primordial Set before
        # solver is called (e.g. Geometric Constraints, that do not depend on problem data)
        # Listed functions must be defined in Constraints_and_OF.py file
        # This entry is optional, if the list is empty, or if the entry is completely skipped, the Initial Set
        # will be the same as the Primordial Set

        'Variables_Used_In_Incremental_For_Each_Primordial_Constraint': [['Ds','L'],['Ds','L'],['Ds','L','Nb'],['Ds','L','Nb']],
        # This is valid if 'Incremental_Set_Trimming' option is set in True
        # Here you need to add the active variables used in each Primordial_Constraint
        # The order used in 'Primordial_Set_Trimming_Constraints_List' is the order
        # of declaration of each group of the correspondent variables declared in 
        # 'Variables_Used_In_Incremental_For_Each_Primordial_Constraint'
        # (i.e. - 'Primordial_Set_Trimming_Constraints_List': ['LD_lb', 'LD_ub']
        #  - 'Variables_Used_In_Incremental_For_Each_Primordial_Constraint': [['x','y'],['z','x']]
        # where LD_lb depends on x and y while LD_ub depends on z and x)

        'Set_Trimming_Constraints_List': ['vs_lb', 'vs_ub', 'vt_lb', 'vt_ub', 'Ret_lb', 'Ret_ub', 'Res_lb',
                                          'Res_ub', 'DPs_ub', 'DPt_ub', 'F_min', 'Areq'],

        'Variables_Used_In_Incremental_For_Each_Set_Trimming_Constraint': [['Ds', 'dte', 'rp', 'lay', 'L', 'Nb'],
                                                                           ['Ds', 'dte', 'rp', 'lay', 'L', 'Nb'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay'],
                                                                           ['Ds', 'dte', 'rp', 'lay', 'L', 'Nb'],
                                                                           ['Ds', 'dte', 'rp', 'lay', 'L', 'Nb'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay', 'L', 'Nb', 'Bc'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay', 'L'],
                                                                           ['Npt'],
                                                                           ['Ds', 'dte', 'Npt', 'rp', 'lay', 'L', 'Nb', 'Bc']],
        # This is valid if 'Incremental_Set_Trimming' option is set in True
        # Here you need to add the active variables used in each Set_Trimming_Constraint
        # The order used in 'Set_Trimming_Constraints_List' is the order
        # of declaration of each group of the correspondent variables declared in 
        # 'Variables_Used_In_Incremental_For_Each_Set_Trimming_Constraint'
        # (i.e. - 'Primordial_Set_Trimming_Constraints_List': ['vs_lb', 'vs_ub']
        #  - 'Variables_Used_In_Incremental_For_Each_Primordial_Constraint': [['x','y'],['z','x']]
        # where vs_lb depends on x and y while vs_ub depends on z and x)



        # These are the Set Trimming Constraints to be applied to Initial Set when Solver is called
        # They also must be defined in Constraints_and_OF.py file

        'Recursive_Set_Trimming': {
            'Variable_Name': 'yfluid',
            'Variable_Options': ['cold_stream', 'hot_stream'],
            'ST_Exclusion_Functions': ['TAC_OF']
            },
        # Recursive Set Trimming Option. It is Optional. If user defines the parameter with the same name, 
        # only one option would be evaluated. If user does not enter a valid option, Variable_Options will be used.

    }

}
