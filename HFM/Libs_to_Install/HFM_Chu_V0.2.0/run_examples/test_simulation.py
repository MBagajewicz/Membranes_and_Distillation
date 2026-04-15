import numpy as np

from hfm_simulator import HFMSimulator
from hfm_simulator.stream import Stream

from scenarios_examples.scenarios import SCENARIOS, STREAMS # You mut create scenarios before run
from properties_examples.Mixture_Properties import MixtureProperties # You mut create Mixture_Properties before run

def main():
    # EN: True if you want to print results
    # PT-BR: True se deseja imprimir or resultados
    print_results_screen = True
    print_results_excel = False

    # --------------------------------------
    # Scenario and feed stream
    # Cenário e corrente de alimentação
    # --------------------------------------
    
    # EN: Select a predefined membrane scenario (geometry + operating conditions)
    # PT-BR: Seleciona um cenário da membrana (geometria + condições operacionais)
    scenario = SCENARIOS[11]

    # EN: Load feed data dictionary associated with the scenario
    # PT-BR: Carrega os dados da corrente de alimentação associados ao cenário
    s = STREAMS[11]


    # --------------------------------------
    # FEED STREAM (VERY IMPORTANT)
    # CORRENTE DE ALIMENTAÇÃO (MUITO IMPORTANTE)
    # --------------------------------------

    # EN: Create a Stream object representing the feed entering the membrane
    # PT-BR: Cria um objeto Stream representando a alimentação da membrana

    feed = Stream(

        # EN: Total molar flow [mol/s]
        # PT-BR: Vazão molar total [mol/s]
        flow=s["flow"],
        # Example manual:
        # flow=0.0033


        # EN: Mole fraction vector (must sum to 1)
        # PT-BR: Fração molar (deve somar 1)
        composition=s["composition"],
        # Example manual:
        # composition=np.array([0.5, 0.5])


        # EN: Feed pressure [Pa]
        # PT-BR: Pressão da alimentação [Pa]
        pressure=s["pressure"],
        # Example manual:
        # pressure=3e5


        # EN: Feed temperature [K]
        # PT-BR: Temperatura da alimentação [K]
        temperature=s["temperature"],
        # Example manual:
        # temperature=323


        # EN: List of component names (order MUST match composition)
        # PT-BR: Lista de componentes (ordem deve coincidir com composição)
        components=s["components"],
        # Example manual:
        # components=["CO2", "Propane"]


        # EN: permeance of each component [mol/(m2 Pa s)]
        # PT-BR: Permeabilidade de cada componente
        permeance=scenario["S"]/scenario["t_mem"],
        # Example manual:
        # permeance=np.array([6.8e-8, 7.7e-11])


        # EN: Dynamic viscosity of each component [Pa·s]
        # PT-BR: Viscosidade dinâmica de cada componente [Pa·s]
        viscosity=s["viscosity"],
        # Example manual:
        # viscosity=np.array([1.48e-5, 8.3e-6])


        # EN: Molecular weight [kg/mol]
        # PT-BR: Massa molar [kg/mol]
        molecularweight=s["molecularweight"]
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
    sim.energy = scenario["EnergyBalance"]
    sim.pressure_drop = scenario["PressureDrop"]
    sim.enthalpy_method = scenario["EnthalpyMode"]

    # EN: Global heat transfer coefficient [W/(m2 K)]
    # PT-BR: Coeficiente global de transferência de calor
    sim.heat_transfer_coef = 4

    # EN: Number of discretization segments
    # PT-BR: Número de segmentos de discretização
    sim.NCells = 50

    # EN: Assign inputs to simulator
    # PT-BR: Define entradas do simulador
    sim.set_scenario(scenario)
    sim.set_feed(feed)
    sim.set_properties(props)


    # --------------------------------------
    # Run simulation
    # Rodar simulação
    # --------------------------------------

    print("Running simulation...")

    results = sim.run()

    print("Simulation finished")


    # --------------------------------------
    # Results
    # Resultados
    # --------------------------------------
    if print_results_screen:
        # EN: Check mass balance results
        # PT-BR: Verifica resultados de balanço de massa
        print("Feed flow:", results.FRet[0])
        if results.T_ret is not None:
            print("Feed Temperature:", results.T_ret[0], " K")
            print("Retentate outlet Temperature:", results.T_ret[-1], " K")
        print("Retentate outlet:", results.FRet[-1])

        # EN: Counter-current → permeate outlet is index 0
        # PT-BR: Contracorrente → saída do permeado é índice 0
        print("Permeate outlet:", results.FPerm[0])
        if results.T_per is not None:
            print("Permeate outlet Temperature:", results.T_per[0], " K")
            print("Permeate closed end Temperature:", results.T_per[-2], " K")
        # print("Permeate (closed end - 1) Temperature:", results.T_per[-2], " K")

        print("Recovery:", results.recovery)
        if sim.heat_transfer_coef == None:
            print("U:", results.U[1:])
        print("-------------------------------")
        print("Permeate flow outlet via oulet method [mol/s]:", results.outlet("permeate").flow)
        print("Permeate composition outlet via oulet method:", results.outlet("permeate").composition)
        print("Permeate pressure outlet via oulet method [Pa]:", results.outlet("permeate").pressure)
        print("Permeate temperature outlet via oulet method [K]:", results.outlet("permeate").temperature)
        print("Permeate components outlet via oulet method:", results.outlet("permeate").components)
        print("Permeate permeance outlet via oulet method [mol/(m2 Pa s)]:", results.outlet("permeate").permeance)
        print("Permeate viscosity outlet via oulet method [Pa s]:", results.outlet("permeate").viscosity)
        print("Permeate molecular weight outlet via oulet method [kg/mol]:", results.outlet("permeate").molecularweight)
        print("-------------------------------")
        print("Retentate flow outlet via oulet method [mol/s]:", results.outlet("retentate").flow)
        print("Retentate composition outlet via oulet method:", results.outlet("retentate").composition)
        print("Retentate pressure outlet via oulet method [Pa]:", results.outlet("retentate").pressure)
        print("Retentate temperature outlet via oulet method [K]:", results.outlet("retentate").temperature)
        print("Retentate components outlet via oulet method:", results.outlet("retentate").components)
        print("Retentate permeance outlet via oulet method [mol/(m2 Pa s)]:", results.outlet("retentate").permeance)
        print("Retentate viscosity outlet via oulet method [Pa s]:", results.outlet("retentate").viscosity)
        print("Retentate molecular weight outlet via oulet method [kg/mol]:", results.outlet("retentate").molecularweight)




    if print_results_excel:
        # --------------------------------------
        # Export Excel
        # Exportar resultados
        # --------------------------------------

        print("Exporting results...")

        # EN: Export only mass balance (optional)
        # PT-BR: Exporta apenas balanço de massa (opcional)
        # results.export_mass_excel("mass_results.xlsx")

        # EN: Export energy and mass results if energy model is active
        # PT-BR: Exporta resultados de energia e massa se ativado
        if results.T_ret is not None:
            results.export_energy_excel("energy_results.xlsx")

        print("Excel files generated")


if __name__ == "__main__":
    main()