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
        F_ret,
        G_per,
        P_ret,
        P_per,
        x_ret,
        y_per,
        thermo,
        T_ret_in,
        UA,
        J_per,
        z_J
    ):

        # Retentate molar flow profile along the module
        # Perfil de vazão molar do retentado ao longo do módulo
        self.F = np.asarray(F_ret, dtype=float)

        # Permeate molar flow profile (clipped to avoid negative values)
        # Perfil de vazão molar do permeado (limitado para evitar valores negativos)
        self.G = np.clip(np.asarray(G_per, dtype=float), 0, None)

        # Retentate pressure profile
        # Perfil de pressão do retentado
        self.P_ret = np.asarray(P_ret)

        # Permeate pressure profile
        # Perfil de pressão do permeado
        self.P_per = np.asarray(P_per)

        # Retentate composition profile
        # Perfil de composição molar do retentado
        self.x_ret = np.asarray(x_ret)

        # Permeate composition profile
        # Perfil de composição molar do permeado
        self.y_per = np.asarray(y_per)

        # Thermodynamic model used to compute enthalpies
        # Modelo termodinâmico usado para calcular entalpias
        self.thermo = thermo

        # Inlet temperature of the retentate stream
        # Temperatura de entrada do retentado
        self.T_ret_in = float(T_ret_in)

        # Overall heat transfer coefficient per segment (UA)
        # Coeficiente global de transferência de calor por segmento (UA)
        self.UA = np.asarray(UA, dtype=float)

        # Number of axial segments (nodes = N+1)
        # Número de segmentos axiais (nós = N+1)
        self.N = len(self.F) - 1

        # Total molar flux through the membrane
        # Fluxo molar total através da membrana
        self.J_per = np.asarray(J_per)

        # Composition of the permeating flux
        # Composição do fluxo que atravessa a membrana
        self.z_J = np.asarray(z_J)

    # -------------------------------------------------
    # Residual function
    # Função de resíduos
    # -------------------------------------------------
    def residual(self, X):

        # Number of spatial segments
        # Número de segmentos espaciais
        N = self.N

        # Extract retentate temperature profile from solver vector
        # Extrai perfil de temperatura do retentado do vetor do solver
        T_ret = np.clip(X[0:N+1], 100, 600)

        # Extract permeate temperature profile
        # Extrai perfil de temperatura do permeado
        T_per = np.clip(X[N+1:2*(N+1)], 100, 600)

        # Initialize residual vector
        # Inicializa vetor de resíduos
        R = np.zeros(2*(N+1))

        # ----------------------------
        # Boundary condition
        # Condição de contorno
        # ----------------------------

        # Enforce retentate inlet temperature
        # Impõe temperatura de entrada do retentado
        R[0] = T_ret[0] - self.T_ret_in

        # ----------------------------
        # Precompute enthalpies
        # Pré-calcula entalpias
        # ----------------------------

        # Retentate enthalpy profile
        # Perfil de entalpia do retentado
        h_ret = np.array([self.thermo.get_h_ret(k, T_ret[k]) for k in range(N+1)])

        # Permeate enthalpy profile
        # Perfil de entalpia do permeado
        h_per = np.array([self.thermo.get_h_per(k, T_per[k]) for k in range(N+1)])

        # Enthalpy of the permeating stream
        # Entalpia do fluxo que atravessa a membrana
        h_J   = np.array([self.thermo.get_h_J(k, T_ret[k]) for k in range(N+1)])

        # ----------------------------
        # Interior nodes
        # Nós internos
        # ----------------------------
        for k in range(1, N):

            # Heat conduction through the membrane wall
            # Condução de calor através da parede da membrana
            conduction = self.UA[k] * (T_ret[k] - T_per[k-1])

            # Retentate energy balance
            # Balanço de energia no retentado
            R[k] = (
                self.F[k-1] * h_ret[k-1]
                - self.F[k] * h_ret[k]
                - self.J_per[k] * h_J[k]
                - conduction
            )

            # Permeate energy balance
            # Balanço de energia no permeado
            R[N+k] = (
                self.G[k] * h_per[k]
                - self.G[k-1] * h_per[k-1]
                + self.J_per[k] * h_J[k]
                + conduction
            )

        # ----------------------------
        # Last node (module outlet)
        # Último nó (saída do módulo)
        # ----------------------------
        k = N

        # Heat conduction between retentate and permeate
        # Condução de calor entre retentado e permeado
        conduction = self.UA[k] * (T_ret[k] - T_per[k-1])

        # Retentate energy balance at outlet
        # Balanço de energia do retentado na saída
        R[k] = (
            self.F[k-1] * h_ret[k-1]
            - self.F[k] * h_ret[k]
            - self.J_per[k] * h_J[k]
            - conduction
        )

        # Permeate energy balance at outlet
        # Balanço de energia do permeado na saída
        R[N+k] = (
            - self.G[k-1] * h_per[k-1]
            + self.J_per[k] * h_J[k]
            + conduction
        )

        # Return residual vector
        # Retorna vetor de resíduos
        return R

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
        N = self.N

        # Total number of temperature variables
        # Número total de variáveis de temperatura
        n = 2*(N+1)

        # Initialize sparse matrix
        # Inicializa matriz esparsa
        S = lil_matrix((n, n), dtype=int)

        # Loop over internal nodes
        # Loop sobre nós internos
        for k in range(1, N+1):

            # Retentate energy equation
            # Equação de energia do retentado
            row = k
            S[row, k] = 1
            S[row, k-1] = 1
            S[row, (N+1)+(k-1)] = 1

            # Permeate energy equation
            # Equação de energia do permeado
            row = N + k
            S[row, (N+1)+k] = 1
            S[row, (N+1)+(k-1)] = 1
            S[row, k] = 1

        # Boundary condition dependency
        # Dependência da condição de contorno
        S[0,0] = 1

        # Convert to CSR sparse format for efficient solver use
        # Converte para formato CSR para uso eficiente no solver
        return S.tocsr()