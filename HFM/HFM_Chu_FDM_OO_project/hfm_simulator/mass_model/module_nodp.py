# HFM/HFM_Chu_FDM_OO/module_nodp.py

# Import NumPy for numerical operations and array manipulation
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np

# Import the base class for hollow fiber membrane modules
# Importa a classe base para módulos de membrana de fibras ocas
from .module_base import BaseHFMModule

# Import sparse matrix constructor used for Jacobian sparsity pattern
# Importa o construtor de matriz esparsa usado para definir a estrutura do Jacobiano
from scipy.sparse import lil_matrix


class HFM_NoDP(BaseHFMModule):
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
        # K_shell, # no pressure drop
        # K_bore, # no pressure drop
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

        # Store geometry object (contains discretization and membrane area)
        # Armazena o objeto de geometria (contém discretização e área da membrana)
        self.geom = geometry

        # Store mixture physical properties handler
        # Armazena o manipulador de propriedades físicas da mistura
        self.props = properties

        # Universal gas constant
        # Constante universal dos gases
        self.R = R

        # Operating temperature
        # Temperatura de operação
        self.T = T

        # Permeability of each component through the membrane
        # Permeabilidade de cada componente através da membrana
        self.J = J

        # Pressure drop coefficients are NOT used in this model
        # Coeficientes de queda de pressão NÃO são usados neste modelo
        # self.K_shell = K_shell
        # self.K_bore = K_bore

        # Number of components in the gas mixture
        # Número de componentes na mistura gasosa
        self.nc = n_comp

        # Feed molar flow rate per component
        # Vazão molar de alimentação por componente
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

        # Axial discretization step
        # Passo de discretização axial
        Dz = self.geom.Dz

        # Membrane area per segment
        # Área de membrana por segmento
        AREA = self.geom.AREA_SEG

        # Number of variables per spatial node
        # Número de variáveis por nó espacial
        width = 2 * nc + 2

        # Reshape the solver vector into matrix form (nodes × variables)
        # Reorganiza o vetor do solver em forma matricial (nós × variáveis)
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

        # Total retentate flow
        # Vazão total do retentado
        SumF = F.sum(axis=1)

        # Total permeate flow
        # Vazão total do permeado
        SumG = G.sum(axis=1)

        # Precompute inverse values for numerical efficiency
        # Pré-calcula inversos para melhorar eficiência numérica
        invSumF = 1 / np.maximum(SumF, eps)
        invSumG = 1 / np.maximum(SumG, eps)

        # Total number of residual equations
        # Número total de equações residuais
        nR = 2*nc + 2 + N*(2*nc + 2)

        # Initialize residual vector
        # Inicializa vetor de resíduos
        R = np.zeros(nR)

        # Residual index pointer
        # Ponteiro de índice do vetor de resíduos
        i = 0

        # ===============================
        # Boundary conditions
        # Condições de contorno
        # ===============================

        # Feed composition condition
        # Condição de composição da alimentação
        R[i:i+nc] = (F[0] - self.F_feed)/Fref
        i += nc

        # Retentate inlet pressure condition
        # Condição da pressão de entrada do retentado
        R[i] = (P[0] - self.P_feed)/self.P_feed
        i += 1

        # Permeate outlet pressure condition
        # Condição da pressão de saída do permeado
        R[i] = (p[0] - self.P_perm)/self.P_perm
        i += 1

        # Zero permeate flow at module end
        # Fluxo zero no permeado no final do módulo
        R[i:i+nc] = (G[N])/Fref
        i += nc

        # ===============================
        # Axial discretization loop
        # Loop axial da discretização
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

            # At last node permeate composition is undefined
            # No último nó a composição do permeado é indefinida
            if k==N:
                y_k[:] = 0

            # Viscosity is not required because pressure drop is ignored
            # Viscosidade não é necessária pois a queda de pressão é ignorada
            # mu_f = self.props.viscosity(...)
            # mu_g = self.props.viscosity(...)

            # Membrane permeation driving force
            # Força motriz da permeação na membrana
            Jdrv = self.J * AREA * (P[k]*x_k - p[km]*y_km)

            # Retentate mass balance
            # Balanço de massa no retentado
            R[i:i+nc] = (F[k] - F[km] + Jdrv)/Fref
            i += nc

            # Permeate mass balance
            # Balanço de massa no permeado
            if k < N:
                R[i:i+nc] = (G[km] - G[k] - Jdrv)/Fref
            else:
                R[i:i+nc] = (G[km] - Jdrv)/Fref

            i += nc

            # Pressure drop terms removed
            # Termos de queda de pressão removidos
            # dP = ...
            # dp = ...

            # Retentate pressure remains constant along module
            # Pressão do retentado permanece constante ao longo do módulo
            R[i] = (P[km] - P[k])/self.P_feed
            i += 1

            # Permeate pressure remains constant
            # Pressão do permeado permanece constante
            R[i] = (p[k] - p[km])/self.P_perm
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

        # Sparse Jacobian structure initialization
        # Inicialização da estrutura esparsa do Jacobiano
        S = lil_matrix((neq, nvar), dtype=int)

        # Row index counter
        # Contador de linhas
        row = 0

        # Boundary conditions sparsity pattern
        # Estrutura esparsa das condições de contorno
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

        # Interior nodes sparsity pattern
        # Estrutura esparsa dos nós internos
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

        # Convert to CSR format for efficient solver usage
        # Converte para formato CSR para uso eficiente no solver
        return S.tocsr()