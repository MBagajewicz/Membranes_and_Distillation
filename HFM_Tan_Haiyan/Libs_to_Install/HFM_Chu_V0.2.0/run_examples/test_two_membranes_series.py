import numpy as np

from hfm_simulator import HFMSimulator
from hfm_simulator.stream import Stream

from scenarios_examples.scenarios import SCENARIOS, STREAMS
from properties_examples.Mixture_Properties import MixtureProperties


def main():

    # EN: Toggle output
    # PT-BR: Ativar/desativar saída
    print_results = True
    export_excel = True

    # ====================================================
    # MEMBRANE 1
    # PRIMEIRA MEMBRANA
    # ====================================================

    scenario1 = SCENARIOS[3]
    s1 = STREAMS[3]

    # --------------------------------------
    # FEED 1 (FULL STREAM WITH PROPERTIES)
    # --------------------------------------

    feed1 = Stream(
        flow=s1["flow"],
        composition=s1["composition"],
        pressure=s1["pressure"],
        temperature=s1["temperature"],
        components=s1["components"],
        permeability=s1["permeability"],
        viscosity=s1["viscosity"],
        molecularweight=s1["molecularweight"]
    )

    # --------------------------------------
    # PROPERTIES 1
    # --------------------------------------

    props1 = MixtureProperties(
        components=feed1.components,
        MU=feed1.viscosity,
        M=feed1.molecularweight,
        method="HZ"
    )

    # --------------------------------------
    # SIMULATOR 1
    # --------------------------------------

    mem1 = HFMSimulator()

    mem1.energy = True
    mem1.pressure_drop = True
    mem1.heat_transfer_coef = 4
    mem1.NCells = 50

    mem1.set_scenario(scenario1)
    mem1.set_feed(feed1)
    mem1.set_properties(props1)

    print("\nRunning membrane 1...\n")

    res1 = mem1.run()

    print("Membrane 1 finished")

    if print_results:
        print("Feed:", res1.FRet[0])
        print("Retentate:", res1.FRet[-1])
        print("Permeate:", res1.FPerm[0])
        print("Recovery:", res1.recovery)


    # ====================================================
    # MEMBRANE 2
    # SEGUNDA MEMBRANA (feed = permeate of membrane 1)
    # ====================================================

    # EN: Extract permeate stream from membrane 1
    # PT-BR: Extrai corrente de permeado da membrana 1
    permeate_stream1 = res1.outlet("retentate")

    scenario2 = SCENARIOS[3]  # can be different

    # --------------------------------------
    # PROPERTIES 2
    # --------------------------------------

    props2 = MixtureProperties(
        components=permeate_stream1.components,
        MU=permeate_stream1.viscosity,
        M=permeate_stream1.molecularweight,
        method="HZ"
    )

    # --------------------------------------
    # SIMULATOR 2
    # --------------------------------------

    mem2 = HFMSimulator()

    mem2.energy = True
    mem2.pressure_drop = True
    mem2.heat_transfer_coef = 4
    mem2.NCells = 50

    mem2.set_scenario(scenario2)
    mem2.set_feed(permeate_stream1)
    mem2.set_properties(props2)

    print("\nRunning membrane 2...\n")

    res2 = mem2.run()

    print("Membrane 2 finished")

    if print_results:
        print("Feed:", res2.FRet[0])
        print("Retentate:", res2.FRet[-1])
        print("Permeate:", res2.FPerm[0])
        print("Recovery:", res2.recovery)

    # ====================================================
    # EXPORT RESULTS
    # EXPORTAR RESULTADOS
    # ====================================================

    if export_excel:

        print("\nExporting results...\n")

        if res1.T_ret is not None:
            res1.export_energy_excel("membrane1_energy.xlsx")

        if res2.T_ret is not None:
            res2.export_energy_excel("membrane2_energy.xlsx")

        print("Excel files generated")


if __name__ == "__main__":
    main()