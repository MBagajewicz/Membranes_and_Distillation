# Import NumPy for numerical operations and array handling
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np


class EnergyModule:
    """
    Physical energy model of the hollow fiber membrane.

    SINGLE RESPONSIBILITY:
    - define residual equations
    - define jacobian sparsity
    """
    """
    Modelo físico de energia da membrana de fibra oca.

    RESPONSABILIDADE ÚNICA:
    - definir as equações de resíduo
    - definir a estrutura esparsa do Jacobiano
    """

    def __init__(
        self,
        FRet,
        FPer,
        PRet,
        PPerm,
        ZRet,
        ZPerm,
        thermo,
        T_ret_in,
        UA,
        FMemb,
        ZMemb,
        geom
    ):

        # Retentate molar flow profile along the module
        # Perfil de vazão molar do retentado ao longo do módulo
        self.FRet = np.asarray(FRet, dtype=float)

        # Permeate molar flow profile (clipped to avoid negative values)
        # Perfil de vazão molar do permeado (limitado para evitar valores negativos)
        self.FPerm = np.clip(np.asarray(FPer, dtype=float), 0, None)

        # Retentate pressure profile
        # Perfil de pressão do retentado
        self.PRet = np.asarray(PRet)

        # Permeate pressure profile
        # Perfil de pressão do permeado
        self.PPerm = np.asarray(PPerm)

        # Retentate composition profile
        # Perfil de composição molar do retentado
        self.ZRet = np.asarray(ZRet)

        # Permeate composition profile
        # Perfil de composição molar do permeado
        self.ZPerm = np.asarray(ZPerm)

        # Thermodynamic model used to compute enthalpies
        # Modelo termodinâmico usado para calcular entalpias
        self.thermo = thermo

        # Inlet temperature of the retentate stream
        # Temperatura de entrada do retentado
        self.T_ret_in = float(T_ret_in)

        # Overall heat transfer coefficient per segment (UA)
        # Coeficiente global de transferência de calor por segmento (UA)
        self.UA = np.asarray(UA, dtype=float) if UA is not None else None
        self.eval_UA = True if UA is None else False

        # Number of axial segments (nodes = N+1)
        # Número de segmentos axiais (nós = N+1)
        self.NCells = len(self.FRet) - 1

        # Total molar flux through the membrane
        # Fluxo molar total através da membrana
        self.FMemb = np.asarray(FMemb)

        # Composition of the permeating flux
        # Composição do fluxo que atravessa a membrana
        self.ZMemb = np.asarray(ZMemb)

        # geometry
        self.geom = geom

    # -------------------------------------------------
    # Residual function
    # Função de resíduos
    # -------------------------------------------------
    def residual(self, X):

        # Number of spatial segments
        # Número de segmentos espaciais
        NCells = self.NCells

        # Extract retentate temperature profile from solver vector
        # Extrai perfil de temperatura do retentado do vetor do solver
        T_ret = np.clip(X[0:NCells+1], 100, 600)

        # Extract permeate temperature profile
        # Extrai perfil de temperatura do permeado
        T_per = np.clip(X[NCells+1:2*(NCells+1)], 100, 600)

        # Initialize residual vector
        # Inicializa vetor de resíduos
        Res_Vec = np.zeros(2*(NCells+1))

        # ----------------------------
        # Boundary condition
        # Condição de contorno
        # ----------------------------

        # Enforce retentate inlet temperature
        # Impõe temperatura de entrada do retentado
        Res_Vec[0] = T_ret[0] - self.T_ret_in

        # ----------------------------
        # Precompute enthalpies
        # Pré-calcula entalpias
        # ----------------------------

        # Retentate enthalpy profile
        # Perfil de entalpia do retentado
        hRet = np.array([self.thermo.get_h_ret(k, T_ret[k]) for k in range(NCells+1)])

        # Permeate enthalpy profile
        # Perfil de entalpia do permeado
        hPerm = np.array([self.thermo.get_h_per(k, T_per[k]) for k in range(NCells+1)])

        # Enthalpy of the permeating stream
        # Entalpia do fluxo que atravessa a membrana
        hMemb = np.array(
            [0.0 if k == 0 else self.thermo.get_h_J(k, T_ret[k]) for k in range(NCells + 1)]
        )

        # Overall Heat Transfer Coef
        if self.eval_UA:
            self.UA = self.geom.AREA_SEG * np.array(
                [0.0 if k == 0 else self.thermo._uo_b7(k, T_ret[k], T_per[k-1], self.FPerm, self.FRet, self.geom) for k in range(NCells+1)]
            )
        # ----------------------------
        # Interior nodes
        # Nós internos
        # ----------------------------
        for k in range(1, NCells + 1):

            # Heat conduction through the membrane wall
            # Condução de calor através da parede da membrana
            # ACREDITO QUE VAMOS CALCULAR U AQUI
            conduction = self.UA[k] * (T_ret[k] - T_per[k-1])

            # Retentate energy balance
            # Balanço de energia no retentado
            Res_Vec[k] = (
                self.FRet[k-1] * hRet[k-1]
                - self.FRet[k] * hRet[k]
                - self.FMemb[k] * hMemb[k]
                - conduction
            )

            # Permeate energy balance
            # Balanço de energia no permeado

            Res_Vec[NCells+k] = (
                self.FPerm[k] * hPerm[k]
                - self.FPerm[k-1] * hPerm[k-1]
                + self.FMemb[k] * hMemb[k]
                + conduction
            )

        # # ----------------------------
        # # Last node (module outlet)
        # # Último nó (saída do módulo)
        # # ----------------------------
        # k = NCells
        #
        # # Heat conduction between retentate and permeate
        # # Condução de calor entre retentado e permeado
        # conduction = self.UA[k] * (T_ret[k] - T_per[k-1])
        #
        # # Retentate energy balance at outlet
        # # Balanço de energia do retentado na saída
        # Res_Vec[k] = (
        #     self.FRet[k-1] * hRet[k-1]
        #     - self.FRet[k] * hRet[k]
        #     - self.FMemb[k] * hMemb[k]
        #     - conduction
        # )
        #
        # # Permeate energy balance at outlet
        # # Balanço de energia do permeado na saída
        # Res_Vec[NCells+k] = (
        #     - self.FPerm[k-1] * hPerm[k-1]
        #     + self.FMemb[k] * hMemb[k]
        #     + conduction
        # )

        # Return residual vector
        # Retorna vetor de resíduos
        return Res_Vec

    # -------------------------------------------------
    # Jacobian sparsity
    # Estrutura esparsa do Jacobiano
    # -------------------------------------------------
    def build_jac_sparsity(self):

        # Import sparse matrix constructor locally
        # Importa construtor de matriz esparsa localmente
        from scipy.sparse import lil_matrix

        # Number of segments
        # Número de segmentos
        NCells = self.NCells

        # Total number of temperature variables
        # Número total de variáveis de temperatura
        n = 2 * (NCells + 1)

        # Initialize sparse matrix
        # Inicializa matriz esparsa
        Spa_Mat = lil_matrix((n, n), dtype=int)

        # Loop over internal nodes
        # Loop sobre nós internos
        for k in range(1, NCells + 1):
            # Retentate energy equation
            # Equação de energia do retentado
            row = k
            Spa_Mat[row, k] = 1
            Spa_Mat[row, k - 1] = 1
            Spa_Mat[row, (NCells + 1) + (k - 1)] = 1

            # Permeate energy equation
            # Equação de energia do permeado
            row = NCells + k
            Spa_Mat[row, (NCells + 1) + k] = 1
            Spa_Mat[row, (NCells + 1) + (k - 1)] = 1
            Spa_Mat[row, k] = 1

        # Boundary condition dependency
        # Dependência da condição de contorno
        Spa_Mat[0, 0] = 1

        # Convert to CSR sparse format for efficient solver use
        # Converte para formato CSR para uso eficiente no solver
        return Spa_Mat.tocsr()