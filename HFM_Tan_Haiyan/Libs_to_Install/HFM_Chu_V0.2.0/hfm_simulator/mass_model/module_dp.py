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
        Permeance,
        K_shell,
        K_bore,
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

        # permeance of each component
        # Permeancia de cada componente
        self.Permeance = Permeance

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

        # Axial discretization length
        # Comprimento da discretização axial
        # dz = self.geom.dz
        dz = np.asarray(self.geom.dz).item()

        # Membrane area per segment
        # Área de membrana por segmento
        AREA = self.geom.AREA_SEG

        # Number of variables per node
        # Variáveis por nó: F_i, G_i, P, p
        width = 2 * nc + 2

        # Reshape solver vector into 2D matrix (nodes × variables)
        # Reorganiza o vetor do solver em matriz (nós × variáveis)
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

        # Total retentate flow at each node
        # Vazão total do retentado em cada nó
        SumFRet_Comp = FRet_Comp.sum(axis=1)

        # Total permeate flow at each node
        # Vazão total do permeado em cada nó
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)

        # Precompute inverse sums to speed calculations
        # Pré-calcula os inversos das vazões totais para acelerar cálculos
        invSumFRet_Comp = 1 / np.maximum(SumFRet_Comp, eps)
        invSumFPerm_Comp = 1 / np.maximum(SumFPerm_Comp, eps)

        # Total number of residual equations
        # Número total de equações residuais
        nR = 2*nc + 2 + NCells*(2*nc + 2)

        # Residual vector initialization
        # Inicialização do vetor de resíduos
        Res_Vec = np.zeros(nR)

        # Residual index pointer
        # Ponteiro de índice do vetor de resíduos
        i = 0

        # ===============================
        # Boundary conditions
        # Condições de contorno
        # ===============================

        # Feed composition boundary condition
        # Condição de contorno da alimentação
        Res_Vec[i:i+nc] = (FRet_Comp[0] - self.FFeed)/Fref
        i += nc

        # Retentate inlet pressure
        # Pressão de entrada do retentado
        Res_Vec[i] = (PRetCell[0] - self.PFeed)/self.PFeed
        i += 1

        # Permeate outlet pressure
        # Pressão de saída do permeado
        Res_Vec[i] = (PPermCell[0] - self.PPerm)/self.PPerm
        i += 1

        # Permeate plug condition at module end
        # Condição de fluxo nulo no final do permeado
        Res_Vec[i:i+nc] = (FPerm_Comp[NCells])/Fref
        i += nc


        # ===============================
        # Spatial discretization loop
        # Loop espacial da discretização
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

            # Last node: permeate composition undefined
            # Último nó: composição do permeado indefinida
            if k==NCells:
                ZPerm_k[:] = 0

            # Viscosity in retentate
            # Viscosidade no retentado
            # viscVRet = self.props.viscosity(ZRet_k, T=self.T, P=PRetCell[k])
            viscVRet = self.props.viscosity(ZRet_k, T=self.T, P=PRetCell[k])
            
            # Viscosity in permeate
            # Viscosidade no permeado
            # viscVPerm = self.props.viscosity(ZPerm_km, T=self.T, P=PPermCell[k])
            viscVPerm = self.props.viscosity(ZPerm_km, T=self.T, P=PPermCell[k])

            # Membrane flux driving force
            # Força motriz do fluxo através da membrana
            FMemb = self.Permeance * AREA * (PRetCell[k]*ZRet_k - PPermCell[km]*ZPerm_km)

            # ===============================
            # Mass balance (retentate)
            # Balanço de massa (retentado)
            # ===============================

            Res_Vec[i:i+nc] = (FRet_Comp[k] - FRet_Comp[km] + FMemb)/Fref
            i += nc

            # ===============================
            # Mass balance (permeate)
            # Balanço de massa (permeado)
            # ===============================

            if k < NCells:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FPerm_Comp[k] - FMemb)/Fref
            else:
                Res_Vec[i:i+nc] = (FPerm_Comp[km] - FMemb)/Fref

            i += nc

            # ===============================
            # Pressure drop calculations
            # Cálculo da queda de pressão
            # ===============================
            dPCellRet = np.asarray(self.K_shell).item() * viscVRet * self.R * self.T * SumFRet_Comp[k] / PRetCell[k] * dz
            dPCellPerm = np.asarray(self.K_bore).item() * viscVPerm * self.R * self.T * SumFPerm_Comp[k] / PPermCell[k] * dz

            # Retentate momentum balance
            # Balanço de momento do retentado
            Res_Vec[i] = (PRetCell[km] - PRetCell[k] - dPCellRet)/self.PFeed
            i += 1

            # Permeate momentum balance
            # Balanço de momento do permeado
            Res_Vec[i] = (PPermCell[k] - PPermCell[km] - dPCellPerm)/self.PPerm
            i += 1

        return Res_Vec

    def build_jac_sparsity(self):
        """
        Exact Jacobian sparsity pattern for the pressure-drop model,
        with frozen viscosity derivatives omitted.

        Estrutura esparsa exata do Jacobiano para o modelo com queda
        de pressão, omitindo derivadas de viscosidade.
        """
        from scipy.sparse import lil_matrix

        NCells = self.geom.NCells
        nc = self.nc
        width = 2 * nc + 2

        nvar = (NCells + 1) * width
        neq = 2 * nc + 2 + NCells * (2 * nc + 2)

        Spa_Mat = lil_matrix((neq, nvar), dtype=int)

        row = 0

        # =========================================
        # Boundary conditions
        # =========================================

        for j in range(nc):
            Spa_Mat[row, j] = 1
            row += 1

        Spa_Mat[row, 2 * nc] = 1
        row += 1

        Spa_Mat[row, 2 * nc + 1] = 1
        row += 1

        baseN = NCells * width
        for j in range(nc):
            Spa_Mat[row, baseN + nc + j] = 1
            row += 1

        # =========================================
        # Interior equations
        # =========================================

        for k in range(1, NCells + 1):
            km = k - 1

            base_k = k * width
            base_km = km * width

            # -----------------------------------------
            # Retentate mass balance
            # depends on:
            # FRet[k,:], PRet[k], FRet[km,:], FPerm[km,:], PPerm[km]
            # -----------------------------------------
            for _ in range(nc):
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_k + 2 * nc] = 1
                Spa_Mat[row, base_km:base_km + nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2 * nc] = 1
                Spa_Mat[row, base_km + 2 * nc + 1] = 1
                row += 1

            # -----------------------------------------
            # Permeate mass balance
            # depends on:
            # FRet[k,:], PRet[k], FPerm[km,:], PPerm[km]
            # and FPerm[k,:] if k < NCells
            # -----------------------------------------
            for _ in range(nc):
                Spa_Mat[row, base_k:base_k + nc] = 1
                Spa_Mat[row, base_k + 2 * nc] = 1
                Spa_Mat[row, base_km + nc:base_km + 2 * nc] = 1
                Spa_Mat[row, base_km + 2 * nc + 1] = 1

                if k < NCells:
                    Spa_Mat[row, base_k + nc:base_k + 2 * nc] = 1

                row += 1

            # -----------------------------------------
            # Retentate momentum balance
            # depends on:
            # FRet[k,:], PRet[km], PRet[k]
            # -----------------------------------------
            Spa_Mat[row, base_k:base_k + nc] = 1
            Spa_Mat[row, base_km + 2 * nc] = 1
            Spa_Mat[row, base_k + 2 * nc] = 1
            row += 1

            # -----------------------------------------
            # Permeate momentum balance
            # depends on:
            # FPerm[k,:], PPerm[km], PPerm[k]
            # -----------------------------------------
            Spa_Mat[row, base_k + nc:base_k + 2 * nc] = 1
            Spa_Mat[row, base_km + 2 * nc + 1] = 1
            Spa_Mat[row, base_k + 2 * nc + 1] = 1
            row += 1

        return Spa_Mat.tocsr()

    def jacobian(self, x):
        """
        Analytical sparse Jacobian for the pressure-drop model,
        treating viscosities as constants inside the Jacobian.

        Jacobiano analítico esparso para o modelo com queda de pressão,
        tratando viscosidades como constantes dentro do Jacobiano.
        """
        from scipy.sparse import lil_matrix

        NCells = self.geom.NCells
        nc = self.nc
        dz = np.asarray(self.geom.dz).item()
        AREA = self.geom.AREA_SEG
        width = 2 * nc + 2

        X = x.reshape((NCells + 1, width))

        FRet_Comp = X[:, :nc]
        FPerm_Comp = X[:, nc:2 * nc]
        PRetCell = X[:, 2 * nc]
        PPermCell = X[:, 2 * nc + 1]

        eps = 1e-12
        Fref = max(np.sum(self.FFeed), eps)

        SumFRet_Comp = FRet_Comp.sum(axis=1)
        SumFPerm_Comp = FPerm_Comp.sum(axis=1)

        nR = 2 * nc + 2 + NCells * (2 * nc + 2)
        nV = (NCells + 1) * width

        J = lil_matrix((nR, nV), dtype=float)
        I_nc = np.eye(nc)

        row = 0

        # =========================================
        # Boundary conditions
        # =========================================

        # FRet_Comp[0] = FFeed
        for j in range(nc):
            J[row + j, j] = 1.0 / Fref
        row += nc

        # PRetCell[0] = PFeed
        J[row, 2 * nc] = 1.0 / self.PFeed
        row += 1

        # PPermCell[0] = PPerm
        J[row, 2 * nc + 1] = 1.0 / self.PPerm
        row += 1

        # FPerm_Comp[NCells] = 0
        baseN = NCells * width
        for j in range(nc):
            J[row + j, baseN + nc + j] = 1.0 / Fref
        row += nc

        # =========================================
        # Interior equations
        # =========================================

        for k in range(1, NCells + 1):
            km = k - 1

            base_k = k * width
            base_km = km * width

            # Local normalized compositions and their Jacobians
            zR, dZRet_dFRet = self._normalized_and_jac(FRet_Comp[k], eps)
            zP, dZPerm_dFPermPrev = self._normalized_and_jac(FPerm_Comp[km], eps)

            # Frozen viscosities: same values used by residual()
            viscVRet = self.props.viscosity(zR, T=self.T, P=PRetCell[k])
            viscVPerm = self.props.viscosity(zP, T=self.T, P=PPermCell[k])

            M = self.Permeance * AREA

            # -----------------------------------------
            # FMemb derivatives
            # FMemb = M * (PRet[k]*zR - PPerm[km]*zP)
            # -----------------------------------------
            dFMemb_dFRet = (M[:, None] * PRetCell[k]) * dZRet_dFRet
            dFMemb_dPRet = M * zR

            dFMemb_dFPermPrev = -(M[:, None] * PPermCell[km]) * dZPerm_dFPermPrev
            dFMemb_dPPermPrev = -M * zP

            # -----------------------------------------
            # Retentate mass balance
            # Res = (FRet[k] - FRet[km] + FMemb)/Fref
            # -----------------------------------------
            rows = slice(row, row + nc)

            # d / d FRet[k,:]
            J[rows, base_k:base_k + nc] = (I_nc + dFMemb_dFRet) / Fref

            # d / d FRet[km,:]
            J[rows, base_km:base_km + nc] = -I_nc / Fref

            # d / d PRet[k]
            for j in range(nc):
                J[row + j, base_k + 2 * nc] = dFMemb_dPRet[j] / Fref

            # d / d FPerm[km,:]
            J[rows, base_km + nc:base_km + 2 * nc] = dFMemb_dFPermPrev / Fref

            # d / d PPerm[km]
            for j in range(nc):
                J[row + j, base_km + 2 * nc + 1] = dFMemb_dPPermPrev[j] / Fref

            row += nc

            # -----------------------------------------
            # Permeate mass balance
            # if k < NCells:
            #   Res = (FPerm[km] - FPerm[k] - FMemb)/Fref
            # else:
            #   Res = (FPerm[km] - FMemb)/Fref
            # -----------------------------------------
            rows = slice(row, row + nc)

            # d / d FRet[k,:]
            J[rows, base_k:base_k + nc] = -dFMemb_dFRet / Fref

            # d / d PRet[k]
            for j in range(nc):
                J[row + j, base_k + 2 * nc] = -dFMemb_dPRet[j] / Fref

            # d / d FPerm[km,:]
            J[rows, base_km + nc:base_km + 2 * nc] = (I_nc - dFMemb_dFPermPrev) / Fref

            # d / d PPerm[km]
            for j in range(nc):
                J[row + j, base_km + 2 * nc + 1] = -dFMemb_dPPermPrev[j] / Fref

            # explicit -FPerm[k,:] only for k < NCells
            if k < NCells:
                J[rows, base_k + nc:base_k + 2 * nc] = -I_nc / Fref

            row += nc

            # -----------------------------------------
            # Retentate momentum balance
            # Res = (PRet[km] - PRet[k] - dPCellRet)/PFeed
            # dPCellRet = K_shell * muRet * R*T * SumFRet[k] / PRet[k] * dz
            # with muRet treated as constant
            # -----------------------------------------
            Cret = np.asarray(self.K_shell).item() * viscVRet * self.R * self.T * dz
            Sret = SumFRet_Comp[k]
            Pret = PRetCell[k]

            # dRes / d PRet[km]
            J[row, base_km + 2 * nc] = 1.0 / self.PFeed

            # dRes / d FRet[k,:]
            # d/dF_i of (-Cret * Sret/Pret) = -(Cret/Pret)
            for j in range(nc):
                J[row, base_k + j] = -(Cret / Pret) / self.PFeed

            # dRes / d PRet[k]
            # d/dP of [ -PRet[k] - Cret*Sret/P ] = -1 + Cret*Sret/P^2
            J[row, base_k + 2 * nc] = (-1.0 + Cret * Sret / (Pret ** 2)) / self.PFeed

            row += 1

            # -----------------------------------------
            # Permeate momentum balance
            # Res = (PPerm[k] - PPerm[km] - dPCellPerm)/PPerm
            # dPCellPerm = K_bore * muPerm * R*T * SumFPerm[k] / PPerm[k] * dz
            # with muPerm treated as constant
            # -----------------------------------------
            Cperm = np.asarray(self.K_bore).item() * viscVPerm * self.R * self.T * dz
            Sperm = SumFPerm_Comp[k]
            Pperm = PPermCell[k]

            # dRes / d PPerm[km]
            J[row, base_km + 2 * nc + 1] = -1.0 / self.PPerm

            # dRes / d FPerm[k,:]
            # d/dF_i of (-Cperm * Sperm/Pperm) = -(Cperm/Pperm)
            for j in range(nc):
                J[row, base_k + nc + j] = -(Cperm / Pperm) / self.PPerm

            # dRes / d PPerm[k]
            # d/dP of [ PPerm[k] - Cperm*Sperm/P ] = 1 + Cperm*Sperm/P^2
            J[row, base_k + 2 * nc + 1] = (1.0 + Cperm * Sperm / (Pperm ** 2)) / self.PPerm

            row += 1

        J = J.tocsr()
        J.data[np.abs(J.data) < 1e-14] = 0.0
        J.eliminate_zeros()
        return J

    def _normalized_and_jac(self, F, eps=1e-12):
        """
        Returns:
            z    = F / max(sum(F), eps)
            dzdF = analytical Jacobian of z wrt F, consistent with clipping
        """
        F = np.asarray(F, dtype=float)
        n = F.size
        I = np.eye(n)
        Sraw = F.sum()

        if Sraw > eps:
            z = F / Sraw
            dzdF = (I - z[:, None]) / Sraw
        else:
            z = F / eps
            dzdF = I / eps

        return z, dzdF