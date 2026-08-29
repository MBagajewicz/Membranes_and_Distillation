import numpy as np

# Reuse of existing physics (procedural)
from .Calculations_Prop_Viscosity_gas_mix import (
    Mean_Viscosity_Mix
)


class MixtureProperties:
    """
    Gas mixture properties.

    This class acts as an OO ADAPTER:
    - Reuses existing physical functions (procedural)
    - Exposes a single interface to the model
    - Allows changing the calculation method without touching the model
    """
    # Esta classe atua como um ADAPTER OO:
    # - Reutiliza funções físicas existentes (procedural)
    # - Expõe uma interface única para o modelo
    # - Permite alterar o método de cálculo sem modificar o modelo

    def __init__(self, components, MU=None, M=None, method="HZ"):
        """
        Parameters
        ----------
        components : list[str]
            List of components (e.g. ["CO2", "CH4"])
            Lista de componentes (ex. ["CO2", "CH4"])
        MU : array-like, optional
            Pure viscosities [Pa.s] (required for HZ)
            Viscosidades puras [Pa.s] (necessário para HZ)
        M : array-like, optional
            Molecular weights [kg/kmol] (required for HZ)
            Pesos moleculares [kg/kmol] (necessário para HZ)
        method : str
            Viscosity method: "HZ" or "CoolProp"
            Método de viscosidade: "HZ" ou "CoolProp"
        """
        self.components = components
        self.MU = MU
        self.M = M
        self.method = method

    # ==========================================================
    # PUBLIC INTERFACE (the ONLY one the model should use)
    # INTERFACE PÚBLICA (a ÚNICA que o modelo deve usar)
    # ==========================================================
    def viscosity(self, mol_fractions, T=None, P=None):
        """
        Returns the mixture viscosity.

        The HFM model only calls this method.
        Retorna a viscosidade da mistura.

        O modelo HFM chama apenas este método.
        """
        if self.method == "HZ":
            return self._viscosity_HZ(mol_fractions)

        elif self.method == "CoolProp":
            return self._viscosity_coolprop(mol_fractions, T, P)

        else:
            raise ValueError(
                f"Unsupported viscosity method: {self.method}"
                f"Método de viscosidade não suportado: {self.method}"
            )

    # ==========================================================
    # INTERNAL IMPLEMENTATIONS
    # IMPLEMENTAÇÕES INTERNAS
    # ==========================================================
    def _viscosity_HZ(self, mol_fractions):
        """
        Mixture viscosity – Herning & Zipperer
        Viscosidade da mistura – Herning & Zipperer
        """
        if self.MU is None or self.M is None:
            raise ValueError(
                "HZ method requires MU and M, individual component viscosity and molecular weigth"
                "Método HZ requer MU e M, viscosidades puras y pesos moleculares"
            )

        soma = np.sum(mol_fractions)
        if soma < 1e-12:
            return np.mean(self.MU)

        return Mean_Viscosity_Mix(
            mol_fractions,
            self.MU,
            self.M
        )

    def _viscosity_coolprop(self, mol_fractions, T, P):
        """
        Viscosity using CoolProp (simple ideal mixture).

        NOTE:
        - CoolProp calculates pure properties
        - The mixing rule here is linear (approximation)
        
        Viscosidade usando CoolProp (mistura ideal simples).

        NOTA:
        - CoolProp calcula propriedades puras
        - A regra de mistura aqui é linear (aproximação)
        """
        if T is None or P is None:
            raise ValueError(
                "CoolProp requires T and P for viscosity calculations"
                "CoolProp requer T e P pra calcular viscosidade"
            )

        try:
            import CoolProp.CoolProp as CP
        except ImportError:
            raise ImportError(
                "CoolProp is not installed"
                "CoolProp não está instalado"
            )

        mu_mix = 0.0
        for yi, comp in zip(mol_fractions, self.components):
            mu_i = CP.PropsSI(
                "V",     # viscosity [Pa.s] / viscosidade [Pa.s]
                "T", T,
                "P", P,
                comp
            )
            mu_mix += yi * mu_i

        return mu_mix
    

# Usage examples / Exemplos de USO

###################################
# Herning & Zipperer
###################################
# props = MixtureProperties(
#     components=["CO2", "CH4"],
#     MU=MU,
#     M=M,
#     method="HZ"
# )

# mu = props.viscosity(x)

###################################
# Cool Prop
###################################
# props = MixtureProperties(
#     components=["CO2", "CH4"],
#     method="CoolProp"
# )

# mu = props.viscosity(x, T=T_loc, P=P_loc)


