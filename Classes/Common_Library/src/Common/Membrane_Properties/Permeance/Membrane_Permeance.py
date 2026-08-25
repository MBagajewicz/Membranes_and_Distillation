#region Title: Permeance
# Nature: Common object
# Methodology: Store permeance data or calculate permeance from
#              permeability and membrane thickness
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0         14-May-2026     Diego Gabriel Oliva        Proposed
##################################################################################################################
#endregion

import numpy as np


class Membrane_Permeance:
    """
    EN:
    Permeance model for membrane components.

    The class can:
    - receive permeance directly
    - or calculate permeance from permeability and thickness

    PT-BR:
    Modelo de permeância para componentes de membrana.

    A classe pode:
    - receber permeância diretamente
    - ou calcular permeância a partir da permeabilidade e espessura
    """

    def __init__(
        self,
        components,
        permeance=None,
        permeability=None,
        thickness=None
    ):

        # ==========================================================
        # COMPONENTS
        # ==========================================================

        # EN: Component list
        # PT-BR: Lista de componentes
        self.components = list(components)

        # ==========================================================
        # DIRECT PERMEANCE INPUT
        # ==========================================================

        if permeance is not None:

            # EN: Permeance [mol/(m2 Pa s)]
            # PT-BR: Permeância [mol/(m2 Pa s)]
            self.permeance = np.asarray(permeance, dtype=float)

            # EN: Optional storage
            # PT-BR: Armazenamento opcional
            self.permeability = (
                np.asarray(permeability, dtype=float)
                if permeability is not None
                else None
            )

            # EN: Membrane thickness [m]
            # PT-BR: Espessura da membrana [m]
            self.thickness = thickness

        # ==========================================================
        # CALCULATE PERMEANCE FROM PERMEABILITY
        # ==========================================================

        elif permeability is not None and thickness is not None:

            # EN: Permeability
            # PT-BR: Permeabilidade
            self.permeability = np.asarray(permeability, dtype=float)

            # EN: Membrane thickness [m]
            # PT-BR: Espessura da membrana [m]
            self.thickness = float(thickness)

            # EN: Q = P / delta
            # PT-BR: Q = P / delta
            self.permeance = self.permeability / self.thickness

        # ==========================================================
        # INVALID INPUT
        # ==========================================================

        else:

            raise ValueError(
                "Provide either permeance OR permeability + thickness"
            )

    # --------------------------------------------------------------
    # utilities
    # utilities / utilidades
    # --------------------------------------------------------------

    def component_index(self, comp):

        # EN: Returns component index
        # PT-BR: Retorna o índice do componente
        return self.components.index(comp)

    def component_permeance(self, comp):

        # EN: Returns permeance of a component
        # PT-BR: Retorna a permeância de um componente

        i = self.component_index(comp)

        return self.permeance[i]

    def component_permeability(self, comp):

        # EN: Returns permeability of a component
        # PT-BR: Retorna a permeabilidade de um componente

        if self.permeability is None:

            raise ValueError(
                "Permeability data was not provided"
            )

        i = self.component_index(comp)

        return self.permeability[i]

    # --------------------------------------------------------------
    # representation
    # representação
    # --------------------------------------------------------------

    def summary(self):

        # EN: Prints permeance summary
        # PT-BR: Imprime resumo da permeância

        print("Permeance")
        print("----------")

        print("components:", self.components)

        if self.thickness is not None:

            print("thickness [m]:", self.thickness)

        print()

        for i, comp in enumerate(self.components):

            print(f"{comp}")

            if self.permeability is not None:

                print(
                    "  permeability:",
                    self.permeability[i]
                )

            print(
                "  permeance:",
                self.permeance[i]
            )

            print()