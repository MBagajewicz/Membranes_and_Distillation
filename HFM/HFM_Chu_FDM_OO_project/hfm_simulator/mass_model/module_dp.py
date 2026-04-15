# HFM/HFM_Chu_FDM_OO/module_dp.py

# Import NumPy for numerical operations and array handling
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np

# Import the base class for hollow fiber membrane modules
# Importa a classe base para módulos de membrana de fibras ocas
from .module_base import BaseHFMModule

# Import sparse matrix constructor used to define Jacobian sparsity
# Importa construtor de matriz esparsa usado para definir a estrutura do Jacobiano
from scipy.sparse import lil_matrix


class HFM_WithDP(BaseHFMModule):
    """
    FDM model of the hollow fiber module.

    SINGLE RESPONSIBILITY:
    - define the model residuals (mass + momentum)
    - DOES NOT solve
    - DOES NOT print
    - DOES NOT know scenarios
    """
    """
    Modelo FDM do módulo de fibras ocas.

    RESPONSABILIDADE ÚNICA:
    - definir os resíduos do modelo (massa + momento)
    - NÃO resolve
    - NÃO imprime
    - NÃO conhece cenários
    """

    def __init__(
        self,
        geometry,
        properties,
        R,
        T,
        J,
        K_shell,
        K_bore,
        n_comp,
        F_feed,
        P_feed,
        P_perm,
    ):
        """
        Parameters
        ----------
        geometry : Geometry
            Module geometry object
            Objeto com a geometria do módulo
        properties : MixtureProperties
            Physical properties adapter
            Adaptador de propriedades físicas
        R : float
            Gas constant
            Constante dos gases
        T : float
            Temperature [K]
            Temperatura [K]
        J : array
            Permeabilities per component
            Permeabilidades por componente
        K_shell : float
            Shell hydraulic constant
            Constante hidráulica do casco
        K_bore : float
            Bore hydraulic constant
            Constante hidráulica do bore
        n_comp : int
            Number of components
            Número de componentes
        F_feed : array
            Feed molar flow rate per component
            Vazão molar de alimentação por componente
        P_feed : float
            Retentate inlet pressure
            Pressão de entrada do retentado
        P_perm : float
            Permeate outlet pressure
            Pressão de saída do permeado
        """

        # Store geometry object (contains N, Dz, membrane area, etc.)
        # Armazena o objeto de geometria (contém N, Dz, área da membrana, etc.)
        self.geom = geometry

        # Store mixture physical properties handler
        # Armazena o manipulador de propriedades físicas da mistura
        self.props = properties

        # Universal gas constant
        # Constante universal dos gases
        self.R = R

        # System temperature (assumed constant in this model)
        # Temperatura do sistema (assumida constante neste modelo)
        self.T = T

        # Permeability of each component
        # Permeabilidade de cada componente
        self.J = J

        # Hydraulic coefficient for shell side pressure drop
        # Coeficiente hidráulico para queda de pressão no lado do casco
        self.K_shell = K_shell

        # Hydraulic coefficient for bore side pressure drop
        # Coeficiente hidráulico para queda de pressão no lado do bore
        self.K_bore = K_bore

        # Number of components in the mixture
        # Número de componentes na mistura
        self.nc = n_comp

        # Feed molar flow of each component
        # Vazão molar de alimentação de cada componente
        self.F_feed = F_feed

        # Retentate inlet pressure
        # Pressão de entrada do retentado
        self.P_feed = P_feed

        # Permeate outlet pressure
        # Pressão de saída do permeado
        self.P_perm = P_perm


    def residuals(self, x):

        # Number of spatial segments
        # Número de segmentos espaciais
        N = self.geom.N

        # Number of components
        # Número de componentes
        nc = self.nc

        # Axial discretization length
        # Comprimento da discretização axial
        Dz = self.geom.Dz

        # Membrane area per segment
        # Área de membrana por segmento
        AREA = self.geom.AREA_SEG

        # Number of variables per node
        # Variáveis por nó: F_i, G_i, P, p
        width = 2 * nc + 2

        # Reshape solver vector into 2D matrix (nodes × variables)
        # Reorganiza o vetor do solver em matriz (nós × variáveis)
        X = x.reshape((N + 1, width))

        # Retentate component molar flows
        # Vazões molares por componente no retentado
        F = X[:, :nc]

        # Permeate component molar flows
        # Vazões molares por componente no permeado
        G = X[:, nc:2 * nc]

        # Retentate pressure
        # Pressão do retentado
        P = X[:, 2 * nc]

        # Permeate pressure
        # Pressão do permeado
        p = X[:, 2 * nc + 1]

        # Small number to avoid division by zero
        # Pequeno número para evitar divisão por zero
        eps = 1e-12

        # Reference flow used for residual scaling
        # Vazão de referência usada para escalar os resíduos
        Fref = max(np.sum(self.F_feed), eps)

        # Total retentate flow at each node
        # Vazão total do retentado em cada nó
        SumF = F.sum(axis=1)

        # Total permeate flow at each node
        # Vazão total do permeado em cada nó
        SumG = G.sum(axis=1)

        # Precompute inverse sums to speed calculations
        # Pré-calcula os inversos das vazões totais para acelerar cálculos
        invSumF = 1 / np.maximum(SumF, eps)
        invSumG = 1 / np.maximum(SumG, eps)

        # Total number of residual equations
        # Número total de equações residuais
        nR = 2*nc + 2 + N*(2*nc + 2)

        # Residual vector initialization
        # Inicialização do vetor de resíduos
        R = np.zeros(nR)

        # Residual index pointer
        # Ponteiro de índice do vetor de resíduos
        i = 0

        # ===============================
        # Boundary conditions
        # Condições de contorno
        # ===============================

        # Feed composition boundary condition
        # Condição de contorno da alimentação
        R[i:i+nc] = (F[0] - self.F_feed)/Fref
        i += nc

        # Retentate inlet pressure
        # Pressão de entrada do retentado
        R[i] = (P[0] - self.P_feed)/self.P_feed
        i += 1

        # Permeate outlet pressure
        # Pressão de saída do permeado
        R[i] = (p[0] - self.P_perm)/self.P_perm
        i += 1

        # Permeate plug condition at module end
        # Condição de fluxo nulo no final do permeado
        R[i:i+nc] = (G[N])/Fref
        i += nc


        # ===============================
        # Spatial discretization loop
        # Loop espacial da discretização
        # ===============================

        for k in range(1, N+1):

            # Previous node index
            # Índice do nó anterior
            km = k-1

            # Retentate compositions
            # Composição do retentado
            x_k = F[k] * invSumF[k]
            x_km = F[km] * invSumF[km]

            # Permeate compositions
            # Composição do permeado
            y_k = G[k] * invSumG[k]
            y_km = G[km] * invSumG[km]

            # Last node: permeate composition undefined
            # Último nó: composição do permeado indefinida
            if k==N:
                y_k[:] = 0

            # Viscosity in retentate
            # Viscosidade no retentado
            mu_f = self.props.viscosity(x_k, T=self.T, P=P[k])

            # Viscosity in permeate
            # Viscosidade no permeado
            mu_g = self.props.viscosity(y_km, T=self.T, P=p[k])

            # Membrane flux driving force
            # Força motriz do fluxo através da membrana
            Jdrv = self.J * AREA * (P[k]*x_k - p[km]*y_km)

            # ===============================
            # Mass balance (retentate)
            # Balanço de massa (retentado)
            # ===============================

            R[i:i+nc] = (F[k] - F[km] + Jdrv)/Fref
            i += nc

            # ===============================
            # Mass balance (permeate)
            # Balanço de massa (permeado)
            # ===============================

            if k < N:
                R[i:i+nc] = (G[km] - G[k] - Jdrv)/Fref
            else:
                R[i:i+nc] = (G[km] - Jdrv)/Fref

            i += nc

            # ===============================
            # Pressure drop calculations
            # Cálculo da queda de pressão
            # ===============================

            dP = self.K_shell * mu_f * self.R * self.T * SumF[k] / P[k] * Dz
            dp = self.K_bore * mu_g * self.R * self.T * SumG[k] / p[k] * Dz

            # Retentate momentum balance
            # Balanço de momento do retentado
            R[i] = (P[km] - P[k] - dP)/self.P_feed
            i += 1

            # Permeate momentum balance
            # Balanço de momento do permeado
            R[i] = (p[k] - p[km] - dp)/self.P_perm
            i += 1

        return R



    def build_jac_sparsity(self):

        # Number of nodes
        # Número de nós
        N = self.geom.N

        # Number of components
        # Número de componentes
        nc = self.nc

        # Variables per node
        # Variáveis por nó
        width = 2*nc + 2

        # Total number of variables
        # Número total de variáveis
        nvar = (N+1)*width

        # Total number of equations
        # Número total de equações
        neq  = 2*nc + 2 + N*(2*nc + 2)

        # Sparse Jacobian structure
        # Estrutura esparsa do Jacobiano
        S = lil_matrix((neq, nvar), dtype=int)

        # Row counter
        # Contador de linhas
        row = 0

        # ===============================
        # Boundary conditions structure
        # Estrutura das condições de contorno
        # ===============================

        for j in range(nc):
            S[row, j] = 1
            row += 1

        S[row, 2*nc] = 1
        row += 1

        S[row, 2*nc+1] = 1
        row += 1

        base = N*width

        for j in range(nc):
            S[row, base+nc+j] = 1
            row += 1

        # ===============================
        # Interior nodes structure
        # Estrutura dos nós internos
        # ===============================

        for k in range(1, N+1):

            base_k  = k*width
            base_km = (k-1)*width

            for _ in range(2*nc+2):

                # Dependence on current node variables
                # Dependência das variáveis do nó atual
                S[row, base_k:base_k+width] = 1

                # Dependence on previous node variables
                # Dependência das variáveis do nó anterior
                S[row, base_km:base_km+width] = 1

                row += 1

        # Convert to CSR format (faster for solvers)
        # Converte para formato CSR (mais eficiente para solvers)
        return S.tocsr()