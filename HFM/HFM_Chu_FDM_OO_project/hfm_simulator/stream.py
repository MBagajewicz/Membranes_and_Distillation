import numpy as np


class Stream:
    """
    EN: Material stream used to connect unit operations.
    PT-BR: Corrente material usada para conectar operações unitárias.
    """

    def __init__(
        self,
        flow,
        composition,
        pressure,
        temperature,
        components,
        permeability,
        viscosity,
        molecularweight
    ):

        # EN: Total molar flow rate [mol/s]
        # PT-BR: Vazão molar total [mol/s]
        self.flow = float(flow)

        # EN: Mole fraction vector (must sum to 1)
        # PT-BR: Vetor de fração molar (deve somar 1)
        self.composition = np.asarray(composition, dtype=float)

        # EN: Stream pressure [Pa]
        # PT-BR: Pressão da corrente [Pa]
        self.pressure = pressure

        # EN: Stream temperature [K]
        # PT-BR: Temperatura da corrente [K]
        self.temperature = temperature

        # EN: List of components (order must match composition)
        # PT-BR: Lista de componentes (ordem deve coincidir com composição)
        self.components = list(components)

        # EN: Permeability of each component [mol/(m2 Pa s)]
        # PT-BR: Permeabilidade de cada componente
        self.permeability = permeability

        # EN: Dynamic viscosity of each component [Pa·s]
        # PT-BR: Viscosidade dinâmica de cada componente [Pa·s]
        self.viscosity = viscosity

        # EN: Molecular weight of each component [kg/mol]
        # PT-BR: Massa molar de cada componente [kg/mol]
        self.molecularweight = molecularweight

    # ---------------------------
    # utilities
    # utilities / utilidades
    # ---------------------------

    def component_index(self, comp):

        # EN: Returns the index of a component in the component list
        # PT-BR: Retorna o índice de um componente na lista de componentes
        return self.components.index(comp)

    def component_flow(self, comp):

        # EN: Returns molar flow of a specific component [mol/s]
        # PT-BR: Retorna a vazão molar de um componente específico [mol/s]

        i = self.component_index(comp)

        return self.flow * self.composition[i]

    def component_flows(self):

        # EN: Returns molar flow of all components [mol/s]
        # PT-BR: Retorna a vazão molar de todos os componentes [mol/s]

        return self.flow * self.composition

    # ---------------------------
    # representation
    # representação
    # ---------------------------

    def summary(self):

        # EN: Prints a summary of the stream properties
        # PT-BR: Imprime um resumo das propriedades da corrente

        print("Stream")
        print("------")

        print("flow [mol/s]:", self.flow)
        print("pressure [Pa]:", self.pressure)
        print("temperature [K]:", self.temperature)

        print("permeability [mol/(m2 Pa s)]:", self.permeability)
        print("viscosity [Pa s]:", self.viscosity)
        print("molecular weight [kg/mol]:", self.molecularweight)        

        # EN: Print composition of each component
        # PT-BR: Imprime a composição de cada componente
        for c, x in zip(self.components, self.composition):

            print(f"{c}: {x}")