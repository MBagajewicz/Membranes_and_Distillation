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
        Permeance,
        # K_shell, # no pressure drop
        # K_bore, # no pressure drop
        n_comp,
        FFeed,
        PFeed,
        PPerm,
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
        Permeance : array
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
        FFeed : array
            Feed molar flow rate per component
            Vazão molar de alimentação por componente
        PFeed : float
            Retentate inlet pressure
            Pressão de entrada do retentado
        PPerm : float
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

        # permeance of each component through the membrane
        # Permeabilidade de cada componente através da membrana
        self.Permeance = Permeance

        # Pressure drop coefficients are NOT used in this model
        # Coeficientes de queda de pressão NÃO são usados neste modelo
        # self.K_shell = K_shell
        # self.K_bore = K_bore

        # Number of components in the gas mixture
        # Número de componentes na mistura gasosa
        self.nc = n_comp

        # Feed molar flow rate per component
        # Vazão molar de alimentação por componente
        self.FFeed = FFeed

        # Retentate inlet pressure
        # Pressão de entrada do retentado
        self.PFeed = PFeed

        # Permeate outlet pressure
        # Pressão de saída do permeado
        self.PPerm = PPerm


    def residuals(self, x):

        # Number of spatial segments
        # Número de segmentos espaciais
        NCells = self.geom.NCells

        # Number of components
        # Número de componentes
        nc = self.nc

        # Axial discretization step
        # Passo de discretização axial
        dz = self.geom.dz

        # Membrane area per segment
        # Área de membrana por segmento
        AREA = self.geom.AREA_SEG

        # Number of variables per spatial node
        # Número de variáveis por nó espacial
        width = 2 * nc + 2

        # Reshape the solver vector into matrix form (nodes × variables)
        # Reorganiza o vetor do solver em forma matricial (nós × variáveis)
        X = x.reshape((NCells + 1, width))

        # Retentate component molar flows
        # Vazões molares por componente no retentado
        FRet_Comp = X[:, :nc]

        # Permeate component molar flows
        # Vazões molares por componente no permeado
        FPerm_Comp = X[:, nc:2 * nc]

        # Retentate pressure
        # Pressão do retentado
        PRetCell = X[:, 2 * nc]

        # Permeate pressure
        # Pressão do permeado
        PPermCell = X[:, 2 * nc + 1]

        # Small number to avoid division by zero
        # Pequeno número para evitar divisão por zero
        eps = 1e-12

        # Reference flow used for residual scaling
        # Vazão de referência usada para escalar os resíduos
        Fref = max(np.sum(self.FFeed), eps)

        # Total retentate flow
        # Vazão total do retentado
        SumFRet_Comp = FRet_Comp.sum(axis=1)

        # Total permeate flow
        # Vazão total do permeado
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)

        # Precompute inverse values for numerical efficiency
        # Pré-calcula inversos para melhorar eficiência numérica
        invSumFRet_Comp = 1 / np.maximum(SumFRet_Comp, eps)
        invSumFPerm_Comp = 1 / np.maximum(SumFPerm_Comp, eps)

        # Total number of residual equations
        # Número total de equações residuais
        nR = 2*nc + 2 + NCells*(2*nc + 2)

        # Initialize residual vector
        # Inicializa vetor de resíduos
        Res_Vec = np.zeros(nR)

        # Residual index pointer
        # Ponteiro de índice do vetor de resíduos
        i = 0

        # ===============================
        # Boundary conditions
        # Condições de contorno
        # ===============================

        # Feed composition condition
        # Condição de composição da alimentação
        Res_Vec[i:i+nc] = (FRet_Comp[0] - self.FFeed)/Fref
        i += nc

        # Retentate inlet pressure condition
        # Condição da pressão de entrada do retentado
        Res_Vec[i] = (PRetCell[0] - self.PFeed)/self.PFeed
        i += 1

        # Permeate outlet pressure condition
        # Condição da pressão de saída do permeado
        Res_Vec[i] = (PPermCell[0] - self.PPerm)/self.PPerm
        i += 1

        # Zero permeate flow at module end
        # Fluxo zero no permeado no final do módulo
        Res_Vec[i:i+nc] = (FPerm_Comp[NCells])/Fref
        i += nc

        # ===============================
        # Axial discretization loop
        # Loop axial da discretização
        # ===============================

        for k in range(1, NCells+1):

            # Previous node index
            # Índice do nó anterior
            km = k-1

            # Retentate compositions
            # Composição do retentado
            ZRet_k = FRet_Comp[k] * invSumFRet_Comp[k]
            ZRet_km = FRet_Comp[km] * invSumFRet_Comp[km]

            # Permeate compositions
            # Composição do permeado
            ZPerm_k = FPerm_Comp[k] * invSumFPerm_Comp[k]
            ZPerm_km = FPerm_Comp[km] * invSumFPerm_Comp[km]

            # At last node permeate composition is undefined
            # No último nó a composição do permeado é indefinida
            if k==NCells:
                ZPerm_k[:] = 0

            # Viscosity is not required because pressure drop is ignored
            # Viscosidade não é necessária pois a queda de pressão é ignorada
            # mu_f = self.props.viscosity(...)
            # mu_g = self.props.viscosity(...)

            # Membrane permeation driving force
            # Força motriz da permeação na membrana
            FMemb = self.Permeance * AREA * (PRetCell[k]*ZRet_k - PPermCell[km]*ZPerm_km)

            # Retentate mass balance
            # Balanço de massa no retentado
            Res_Vec[i:i+nc] = (FRet_Comp[k] - FRet_Comp[km] + FMemb)/Fref
            i += nc

            # Permeate mass balance
            # Balanço de massa no permeado
            if k < NCells:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FPerm_Comp[k] - FMemb)/Fref
            else:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FMemb)/Fref

            i += nc

            # Pressure drop terms removed
            # Termos de queda de pressão removidos
            # dP = ...
            # dp = ...

            # Retentate pressure remains constant along module
            # Pressão do retentado permanece constante ao longo do módulo
            Res_Vec[i] = (PRetCell[km] - PRetCell[k])/self.PFeed
            i += 1

            # Permeate pressure remains constant
            # Pressão do permeado permanece constante
            Res_Vec[i] = (PPermCell[k] - PPermCell[km])/self.PPerm
            i += 1

        return Res_Vec



    def build_jac_sparsity(self):
        """
        Exact Jacobian sparsity pattern for the no-pressure-drop model.

        Estrutura esparsa exata do Jacobiano para o modelo sem queda de pressão.
        """
        from scipy.sparse import lil_matrix

        # Number of nodes
        NCells = self.geom.NCells

        # Number of components
        nc = self.nc

        # Variables per node
        width = 2 * nc + 2

        # Total number of variables
        nvar = (NCells + 1) * width

        # Total number of equations
        neq = 2 * nc + 2 + NCells * (2 * nc + 2)

        # Sparse structure
        Spa_Mat = lil_matrix((neq, nvar), dtype=int)

        # Row pointer
        row = 0

        # ===============================
        # Boundary conditions
        # ===============================

        # FRet[0,:] = FFeed
        for j in range(nc):
            Spa_Mat[row, j] = 1
            row += 1

        # PRet[0] = PFeed
        Spa_Mat[row, 2 * nc] = 1
        row += 1

        # PPerm[0] = PPerm_out
        Spa_Mat[row, 2 * nc + 1] = 1
        row += 1

        # FPerm[NCells,:] = 0
        baseN = NCells * width
        for j in range(nc):
            Spa_Mat[row, baseN + nc + j] = 1
            row += 1

        # ===============================
        # Interior equations
        # ===============================

        for k in range(1, NCells + 1):
            km = k - 1

            base_k = k * width
            base_km = km * width

            # -------------------------------
            # Retentate mass balance
            # depends on:
            # FRet[k,:], PRet[k], FRet[km,:], FPerm[km,:], PPerm[km]
            # -------------------------------
            for _ in range(nc):
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_k + 2 * nc] = 1
                Spa_Mat[row, base_km:base_km + nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2 * nc] = 1
                Spa_Mat[row, base_km + 2 * nc + 1] = 1
                row += 1

            # -------------------------------
            # Permeate mass balance
            # depends on:
            # FRet[k,:], PRet[k], FPerm[km,:], PPerm[km]
            # and FPerm[k,:] if k < NCells
            # -------------------------------
            for _ in range(nc):
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_k + 2 * nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2 * nc] = 1
                Spa_Mat[row, base_km + 2 * nc + 1] = 1

                if k < NCells:
                    Spa_Mat[row, base_k + nc:base_k + 2 * nc] = 1

                row += 1

            # -------------------------------
            # Retentate pressure equation
            # PRet[km] - PRet[k]
            # -------------------------------
            Spa_Mat[row, base_km + 2 * nc] = 1
            Spa_Mat[row, base_k + 2 * nc] = 1
            row += 1

            # -------------------------------
            # Permeate pressure equation
            # PPerm[k] - PPerm[km]
            # -------------------------------
            Spa_Mat[row, base_km + 2 * nc + 1] = 1
            Spa_Mat[row, base_k + 2 * nc + 1] = 1
            row += 1

        return Spa_Mat.tocsr()

    def jacobian(self, x):
        """
        Analytical sparse Jacobian for the no-pressure-drop model.

        Jacobiano analítico esparso para o modelo sem queda de pressão.
        """
        from scipy.sparse import lil_matrix

        # Number of spatial segments
        NCells = self.geom.NCells

        # Number of components
        nc = self.nc

        # Membrane area per segment
        AREA = self.geom.AREA_SEG

        # Variables per node
        width = 2 * nc + 2

        # Reshape solver vector into matrix form
        X = x.reshape((NCells + 1, width))

        # State variables
        FRet_Comp = X[:, :nc]
        FPerm_Comp = X[:, nc:2 * nc]
        PRetCell = X[:, 2 * nc]
        PPermCell = X[:, 2 * nc + 1]

        # Small number to avoid division by zero
        eps = 1e-12

        # Reference flow used for scaling
        Fref = max(np.sum(self.FFeed), eps)

        # Total flows
        SumFRet_Comp = FRet_Comp.sum(axis=1)
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)

        # Safe totals
        SumFRet_safe = np.maximum(SumFRet_Comp, eps)
        SumFPerm_safe = np.maximum(SumFPerm_Comp, eps)

        # Total number of residual equations
        nR = 2 * nc + 2 + NCells * (2 * nc + 2)

        # Total number of variables
        nV = (NCells + 1) * width

        # Sparse Jacobian
        J = lil_matrix((nR, nV), dtype=float)

        # Identity matrix in component space
        I_nc = np.eye(nc)

        # Residual row pointer
        row = 0

        # ===============================
        # Boundary conditions
        # ===============================

        # Feed composition condition
        # Res = (FRet_Comp[0] - FFeed)/Fref
        for j in range(nc):
            J[row + j, j] = 1.0 / Fref
        row += nc

        # Retentate inlet pressure
        # Res = (PRetCell[0] - PFeed)/PFeed
        J[row, 2 * nc] = 1.0 / self.PFeed
        row += 1

        # Permeate outlet pressure
        # Res = (PPermCell[0] - PPerm)/PPerm
        J[row, 2 * nc + 1] = 1.0 / self.PPerm
        row += 1

        # Zero permeate flow at module end
        # Res = FPerm_Comp[NCells]/Fref
        baseN = NCells * width
        for j in range(nc):
            J[row + j, baseN + nc + j] = 1.0 / Fref
        row += nc

        # ===============================
        # Axial discretization loop
        # ===============================

        for k in range(1, NCells + 1):
            km = k - 1

            base_k = k * width
            base_km = km * width

            # Local compositions used in FMemb
            zR = FRet_Comp[k] / SumFRet_safe[k]
            zP = FPerm_Comp[km] / SumFPerm_safe[km]

            # Short notation
            M = self.Permeance * AREA

            # Derivative of normalized compositions:
            # dz_i/dF_m = (delta_im - z_i) / SumF
            dZRet_dFRet = (I_nc - zR[:, None]) / SumFRet_safe[k]
            dZPerm_dFPermPrev = (I_nc - zP[:, None]) / SumFPerm_safe[km]

            # FMemb = M * (PRet[k]*zR - PPerm[km]*zP)

            # dFMemb / dFRet[k,:]
            dFMemb_dFRet = (M[:, None] * PRetCell[k]) * dZRet_dFRet

            # dFMemb / dPRet[k]
            dFMemb_dPRet = M * zR

            # dFMemb / dFPerm[km,:]
            dFMemb_dFPermPrev = -(M[:, None] * PPermCell[km]) * dZPerm_dFPermPrev

            # dFMemb / dPPerm[km]
            dFMemb_dPPermPrev = -M * zP

            # ===============================
            # Retentate mass balance
            # Res = (FRet[k] - FRet[km] + FMemb)/Fref
            # ===============================
            rows = slice(row, row + nc)

            # dRes / dFRet[k,:]
            J[rows, base_k:base_k + nc] = (I_nc + dFMemb_dFRet) / Fref

            # dRes / dFRet[km,:]
            J[rows, base_km:base_km + nc] = (-I_nc) / Fref

            # dRes / dPRet[k]
            for j in range(nc):
                J[row + j, base_k + 2 * nc] = dFMemb_dPRet[j] / Fref

            # dRes / dFPerm[km,:]
            J[rows, base_km + nc:base_km + 2 * nc] = dFMemb_dFPermPrev / Fref

            # dRes / dPPerm[km]
            for j in range(nc):
                J[row + j, base_km + 2 * nc + 1] = dFMemb_dPPermPrev[j] / Fref

            row += nc

            # ===============================
            # Permeate mass balance
            # if k < NCells:
            #   Res = (FPerm[km] - FPerm[k] - FMemb)/Fref
            # else:
            #   Res = (FPerm[km] - FMemb)/Fref
            # ===============================
            rows = slice(row, row + nc)

            # dRes / dFRet[k,:]
            J[rows, base_k:base_k + nc] = (-dFMemb_dFRet) / Fref

            # dRes / dPRet[k]
            for j in range(nc):
                J[row + j, base_k + 2 * nc] = -dFMemb_dPRet[j] / Fref

            # dRes / dFPerm[km,:]
            J[rows, base_km + nc:base_km + 2 * nc] = (I_nc - dFMemb_dFPermPrev) / Fref

            # dRes / dPPerm[km]
            for j in range(nc):
                J[row + j, base_km + 2 * nc + 1] = -dFMemb_dPPermPrev[j] / Fref

            # dRes / dFPerm[k,:] only if k < NCells
            if k < NCells:
                J[rows, base_k + nc:base_k + 2 * nc] = (-I_nc) / Fref

            row += nc

            # ===============================
            # Retentate pressure equation
            # Res = (PRet[km] - PRet[k])/PFeed
            # ===============================
            J[row, base_km + 2 * nc] = 1.0 / self.PFeed
            J[row, base_k + 2 * nc] = -1.0 / self.PFeed
            row += 1

            # ===============================
            # Permeate pressure equation
            # Res = (PPerm[k] - PPerm[km])/PPerm
            # ===============================
            J[row, base_k + 2 * nc + 1] = 1.0 / self.PPerm
            J[row, base_km + 2 * nc + 1] = -1.0 / self.PPerm
            row += 1

        return J.tocsr()

