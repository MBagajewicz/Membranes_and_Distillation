#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        06-Nov-2025     João Tupinambá               Proposed
#  0.1        23-Mar-2026     Diego Oliva                  Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
# from HFM.Calculations.Calculations_HFM_Solve_FDM import solve_HFM_model_FDM
# #endregion

# #region Calculations
# def model_HFM_Recovery(N_parts, U_Feed_Target, V_Sweep_Target, Q, P_Feed, P_Permeate, T, dfi, dfo, Ntf, D, MU, M, Dz,Key_Comp_index):
#     '''Recovery is the ammount of a key component that is present the Permeate over the ammount
#     of that component present in the Feed'''
#     # solve the model

#     U_fin, V_fin, P_fin, p_fin = solve_HFM_model_FDM(N_parts, U_Feed_Target, V_Sweep_Target, Q, P_Feed, P_Permeate, T, dfi, dfo, Ntf, D, MU, M, Dz)

#     if isinstance(U_fin,int):
#         rec = 0
#     else:
#         rec = V_fin[N_parts, Key_Comp_index] / U_Feed_Target[Key_Comp_index]
#     # Calculate recovery (%) of Key compound in the permeate from the feed.
#     print(rec)
#     return rec

from hfm_simulator import HFMSimulator
from hfm_simulator.stream import Stream

# from HFM.HFM_Chu_Scenarios import SCENARIOS, STREAMS
from Common_Equations_Properties.Mixture_Properties import MixtureProperties

def model_HFM_Recovery(L,D,dfo,dfi,Void_Frac,m_p,Ntf):

    # EN: True if you want to print results
    # PT-BR: True se deseja imprimir or resultados
    print_results_screen = False
    print_results_excel = False


    # --------------------------------------
    # Scenario and feed stream
    # Cenário e corrente de alimentação
    # --------------------------------------

    # EN: Select a predefined membrane scenario (geometry + operating conditions)
    # PT-BR: Seleciona um cenário da membrana (geometria + condições operacionais)
    scenario = {
        'R': 8.314,      # J/(mol·K)
        'Components': m_p['COMPONENTS'], # Components
        'M': m_p['M'], # Molar Mass [CO2, CH4,N2] (kg/mol)
        'MU': m_p['MU'],  # Viscosities [CO2, CH4,N2] (Pa·s)
        "T": m_p['T'], # K
        "P_f": m_p['P_Feed'], # Pa
        "P_p": m_p['P_Permeate'], # Pa
        "f_total": m_p['f_total'], # mol/s
        "s_flow": 0, # mol/s
        "comp_f": m_p['comp_f'], # %mol
        # "comp_s": m_p['comp_s'], # %mol
        "Q": m_p['Q'], # [mol/(m2 Pa s)]
        # 'kD': np.array([1.34,0.1263]),
        # 'CH': np.array([30.78, 27.15]),
        # 'b': np.array([0.395, 0.092]),
        # 'F': np.array([0.51, 0.07]),
        # 'D0': np.array([1e-8, 5.35e-9]),
        # 'beta': np.array([0.052,0.022]),
        "D": D, # m
        "D_o": dfo, # m
        "D_i": dfi, # m
        "L": L, # m
        "N": Ntf,
        "Feed": "Shell",
        "Current": "Co",
        "Void_Frac": Void_Frac
    }

    # --------------------------------------
    # FEED STREAM (VERY IMPORTANT)
    # CORRENTE DE ALIMENTAÇÃO (MUITO IMPORTANTE)
    # --------------------------------------

    # EN: Create a Stream object representing the feed entering the membrane
    # PT-BR: Cria um objeto Stream representando a alimentação da membrana

    feed = Stream(

        # EN: Total molar flow [mol/s]
        # PT-BR: Vazão molar total [mol/s]
        flow=scenario["f_total"],
        # Example manual:
        # flow=0.0033


        # EN: Mole fraction vector (must sum to 1)
        # PT-BR: Fração molar (deve somar 1)
        composition=scenario["comp_f"],
        # Example manual:
        # composition=np.array([0.5, 0.5])


        # EN: Feed pressure [Pa]
        # PT-BR: Pressão da alimentação [Pa]
        pressure=scenario["P_f"],
        # Example manual:
        # pressure=3e5


        # EN: Feed temperature [K]
        # PT-BR: Temperatura da alimentação [K]
        temperature=scenario["T"],
        # Example manual:
        # temperature=323


        # EN: List of component names (order MUST match composition)
        # PT-BR: Lista de componentes (ordem deve coincidir com composição)
        components=scenario["Components"],
        # Example manual:
        # components=["CO2", "Propane"]


        # EN: Permeability of each component [mol/(m2 Pa s)]
        # PT-BR: Permeabilidade de cada componente
        permeability=scenario["Q"],
        # Example manual:
        # permeability=np.array([6.8e-8, 7.7e-11])


        # EN: Dynamic viscosity of each component [Pa·s]
        # PT-BR: Viscosidade dinâmica de cada componente [Pa·s]
        viscosity=scenario["MU"],
        # Example manual:
        # viscosity=np.array([1.48e-5, 8.3e-6])


        # EN: Molecular weight [kg/mol]
        # PT-BR: Massa molar [kg/mol]
        molecularweight=scenario["M"]
        # Example manual:
        # molecularweight=np.array([0.044, 0.0441])
    )


    # --------------------------------------
    # Properties
    # Propriedades termodinâmicas
    # --------------------------------------

    # EN: Create mixture properties model
    # PT-BR: Cria modelo de propriedades da mistura
    props = MixtureProperties(
        components=feed.components,   # EN/PT: component list
        MU=feed.viscosity,            # EN/PT: viscosity array from Stream
        M=feed.molecularweight,       # EN/PT: molecular weights from Stream
        method="HZ"                   # EN/PT: calculation method
    )


    # --------------------------------------
    # Simulator
    # Simulador
    # --------------------------------------

    # EN: Instantiate simulator
    # PT-BR: Instancia o simulador
    sim = HFMSimulator()

    # EN: Activate/deactivate physics
    # PT-BR: Ativa/desativa física do modelo
    sim.energy = False
    sim.pressure_drop = False

    # EN: Global heat transfer coefficient [W/(m2 K)]
    # PT-BR: Coeficiente global de transferência de calor
    sim.heat_transfer_coef = m_p['U']

    # EN: Number of discretization segments
    # PT-BR: Número de segmentos de discretização
    sim.segments = m_p['N_Partitions']

    # EN: Assign inputs to simulator
    # PT-BR: Define entradas do simulador
    sim.set_scenario(scenario)
    sim.set_feed(feed)
    sim.set_properties(props)


    # --------------------------------------
    # Run simulation
    # Rodar simulação
    # --------------------------------------

    # print("Running simulation...")

    results = sim.run()

    # print("Simulation finished")
    Key_Comp_index_Perm = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY_PERM'])
    Key_Comp_index_Ret = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])
    Rec_Perm = ((results.G[0] * results.y_per[0]) / (results.F[0] * results.x_ret[0]))[Key_Comp_index_Perm]
    # Rec_Ret = ((results.F[-1] * results.x_ret[-1]) / (results.F[0] * results.x_ret[0]))[Key_Comp_index_Ret]
    X_ret_key = results.x_ret[-1][Key_Comp_index_Ret]

    # dic_feed = dict(zip(scenario["Components"],scenario["comp_f"]))
    # dic_perm = dict(zip(results.outlet("permeate").components,results.outlet("permeate").composition))
    #
    # f_feed_key = dic_feed.get(m_p['KEY_COMPONENT_RECOVERY_PERM'])*scenario['f_total']
    # f_out_per_key = dic_perm.get(m_p['KEY_COMPONENT_RECOVERY_PERM'])*results.outlet("permeate").flow
    #
    # rec = f_out_per_key/f_feed_key
    return np.array([X_ret_key,Rec_Perm])