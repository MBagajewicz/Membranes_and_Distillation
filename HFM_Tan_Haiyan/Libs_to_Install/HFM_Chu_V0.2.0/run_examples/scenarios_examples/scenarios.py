import numpy as np

SCENARIOS = {
    1: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix', 
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption 
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308, # K
        "PFeed": 35e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.35, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.1, 0.9, 0.0]), # %mol
        "comp_s": np.array([0.0, 0.0, 1.0]), # %mol
        "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]), # [mol/(m2 Pa s)]
        "S": np.array([3.207e-9, 1.33e-10, 3.968e-10])*25e-6, # Permeability [mol/
        "t_mem": 25e-6, # m
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.1, # m
        "DiamFiber_o": 250e-6, # m
        "DiamFiber_i": 200e-6, # m
        "LHidraulic": 0.6, # m
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Co",
        "Void_Frac": 0.625
    },

    2: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption          
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308,
        "PFeed": 35e5,
        "PPerm": 1e5,
        "FFeed": 0.35,
        "s_flow": 0,
        "ZFeed": np.array([0.1, 0.9, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.1,
        "DiamFiber_o": 250e-6,
        "DiamFiber_i": 200e-6,
        "LHidraulic": 0.6,
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },

    3: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308,
        "PFeed": 15e5,
        "PPerm": 1e5,
        "FFeed": 0.35,
        "s_flow": 0,
        "ZFeed": np.array([0.1, 0.9, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.05,
        "DiamFiber_o": 170e-6,
        "DiamFiber_i": 120e-6,
        "LHidraulic": 1.5,
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.3064
    },
    4: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 298,
        "PFeed": 5e5,
        "PPerm": 1e5,
        "FFeed": 3.718e-4,
        "s_flow": 0,
        "ZFeed": np.array([0.1, 0.9, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([1.749e-9, 1.227e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.024,
        "DiamFiber_o": 180e-6,
        "DiamFiber_i": 126e-6,
        "LHidraulic": 0.8,
        "N": 2805,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.8422
    },
    5: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 298,
        "PFeed": 5e5,
        "PPerm": 1e5,
        "FFeed": 4.464e-4,
        "s_flow": 2.012e-5,
        "ZFeed": np.array([0.4, 0.6, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([8.405e-9, 1.323e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.012,
        "DiamFiber_o": 200e-6,
        "DiamFiber_i": 150e-6,
        "LHidraulic": 0.3,
        "N": 106,
        "Feed": "Bore",
        "Current": "Counter",
        "Void_Frac": 0.9706
    },
    'best1': {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3,28.02e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5,2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308,
        "PFeed": 15e5,
        "PPerm": 1e5,
        "FFeed": 0.35,
        "s_flow": 0,
        "ZFeed": np.array([0.1, 0.9, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.18,
        "DiamFiber_o": 0.00019,
        "DiamFiber_i": 0.00018,
        "LHidraulic": 0.6,
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.48
    },
    'best2': {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,  # J/(mol·K)
        'Components': ["CO2","CH4","N2"], # Components
        'M': np.array([44.01e-3, 16.04e-3, 28.02e-3]),  # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5, 2.85e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308,
        "PFeed": 15e5,
        "PPerm": 1e5,
        "FFeed": 0.35,
        "s_flow": 0,
        "ZFeed": np.array([0.1, 0.9, 0.0]),
        "comp_s": np.array([0.0, 0.0, 1.0]),
        "Q": np.array([3.207e-9, 1.33e-10, 3.968e-10]),
        'kD': np.array([1.34, 0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052, 0.022]),
        "DiamShell": 0.19,
        "DiamFiber_o": 0.00017,
        "DiamFiber_i": 0.00016,
        "LHidraulic": 0.6,
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.45
    },
    6: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","CH4"], # Components
        'M': np.array([44.01e-3, 16.04e-3]), # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': np.array([1.48e-5, 1.11e-5]),  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": 308, # K
        "PFeed": 35e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.35, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.1, 0.9]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([3.207e-9, 1.33e-10]), # [mol/(m2 Pa s)]
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.1, # m
        "DiamFiber_o": 250e-6, # m
        "DiamFiber_i": 200e-6, # m
        "LHidraulic": 0.6, # m
        "N": 60_000,
        "Feed": "Shell",
        "Current": "Co",
        "Void_Frac": 0.625
    },
    # 7: First example point 1 of paper Modeling Gas Permeation by Linking Nonideal Effects - Marco Scholz
    7: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","Propane"], # Components
        'M': np.array([44.01e-3, 4.41e-2]), # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.3e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 323, # K
        "PFeed": 3e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.00333333, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.5, 0.5]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.0394, # m
        "DiamFiber_o": 4.15e-4, # m
        "DiamFiber_i": 3.41e-4, # m
        "LHidraulic": 0.2, # m
        "N": 3380,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },
    # 8: First example point 2 of paper Modeling Gas Permeation by Linking Nonideal Effects - Marco Scholz
    8: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","Propane"], # Components
        'M': np.array([44.01e-3, 4.41e-2]), # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.3e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 323, # K
        "PFeed": 3e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.0077777, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.5, 0.5]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.0394, # m
        "DiamFiber_o": 4.15e-4, # m
        "DiamFiber_i": 3.41e-4, # m
        "LHidraulic": 0.2, # m
        "N": 3380,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },
    # 9: First example point 3 of paper Modeling Gas Permeation by Linking Nonideal Effects - Marco Scholz
    9: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","Propane"], # Components
        'M': np.array([44.01e-3, 4.41e-2]), # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.3e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 323, # K
        "PFeed": 3e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.014444444, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.5, 0.5]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.0394, # m
        "DiamFiber_o": 4.15e-4, # m
        "DiamFiber_i": 3.41e-4, # m
        "LHidraulic": 0.2, # m
        "N": 3380,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },
    # 10: First example point 4 of paper Modeling Gas Permeation by Linking Nonideal Effects - Marco Scholz
    10: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","Propane"], # Components
        'M': np.array([44.01e-3, 4.41e-2]), # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.3e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 323, # K
        "PFeed": 3e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.02166666, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.5, 0.5]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.0394, # m
        "DiamFiber_o": 4.15e-4, # m
        "DiamFiber_i": 3.41e-4, # m
        "LHidraulic": 0.2, # m
        "N": 3380,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },

    # 11: Case Study on the separation of Propane and CO2 paper Modeling Gas Permeation by Linking Nonideal Effects - Marco Scholz
    11: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS 
        # NoMix = ideal/averaged enthalpy assumption  
        'R': 8.314,      # J/(mol·K)
        'Components': ["CO2","Propane"], # Components
        'M': np.array([0.044009, 0.044097]), # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.5e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 313, # K
        "PFeed": 10e5, # Pa
        "PPerm": 1e5, # Pa
        "FFeed": 0.0033, # mol/s
        "s_flow": 0, # mol/s
        "ZFeed": np.array([0.5, 0.5]), # %mol
        "comp_s": np.array([0.0, 0.0]), # %mol
        "Q": np.array([6.8e-8, 7.71e-11]), # [mol/(m2 Pa s)]
        "S": np.array([6.8e-8, 7.71e-11])*(4.15e-4-3.41e-4)/2,
        "t_mem": (4.15e-4-3.41e-4)/2,
        'kD': np.array([1.34,0.1263]),
        'CH': np.array([30.78, 27.15]),
        'b': np.array([0.395, 0.092]),
        'F': np.array([0.51, 0.07]),
        'D0': np.array([1e-8, 5.35e-9]),
        'beta': np.array([0.052,0.022]),
        "DiamShell": 0.0394, # m
        "DiamFiber_o": 4.15e-4, # m
        "DiamFiber_i": 3.41e-4, # m
        "LHidraulic": 0.2, # m
        "N": 3380,
        "Feed": "Shell",
        "Current": "Counter",
        "Void_Frac": 0.625
    },

    112: {
        'PressureDrop': True,
        'EnergyBalance': True,
        'EnthalpyMode': 'Mix',
        # Mix = real mixture enthalpy from Peng–Robinson EOS
        # NoMix = ideal/averaged enthalpy assumption
        'R': 8.314,  # J/(mol·K)
        'Components': ["CO2", "Propane"],  # Components
        'M': np.array([0.044009, 0.044097]),  # Molar Mass [CO2, Propane] (kg/mol)
        'MU': np.array([1.48e-5, 8.5e-6]),  # Viscosities [CO2, Propane] (Pa·s)
        "T": 313,  # K
        "PFeed": 10e5,  # Pa
        "PPerm": 1e5,  # Pa
        "FFeed": 0.0033,  # mol/s
        "s_flow": 0,  # mol/s
        "ZFeed": np.array([0.5, 0.5]),  # %mol
        "comp_s": np.array([0.0, 0.0]),  # %mol
        "Q": np.array([6.8e-8, 7.71e-11]),  # [mol/(m2 Pa s)]
        "S": np.array([6.8e-8, 7.71e-11]) * (4.15e-4 - 3.41e-4) / 2,
        "t_mem": 2e-05,
        "DiamShell": 0.03,  # m
        "DiamFiber_o": 0.00024,  # m
        "DiamFiber_i": 0.00024 - 2*2e-05,  # m
        "LHidraulic": 0.3,  # m
        # "N": 3380,
        # "Feed": "Shell",
        # "Current": "Counter",
        "Void_Frac": 0.5
    },
}

# =========================================================
# STREAMS (generated automatically from scenarios)
# =========================================================

STREAMS = {}

for key, s in SCENARIOS.items():

    STREAMS[key] = {

        "flow": s["FFeed"],

        "composition": s["ZFeed"],

        "pressure": s["PFeed"],

        "temperature": s["T"],

        "components": s["Components"],

        "permeability": s["S"] / s["t_mem"] if "S" in s else s["Q"],

        "viscosity": s["MU"],

        "molecularweight": s["M"]

    }


