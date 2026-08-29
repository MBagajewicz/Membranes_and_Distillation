# Import NumPy for numerical operations and array handling
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np

# Import nonlinear least-squares solver from SciPy
# Importa solver de mínimos quadrados não lineares do SciPy
from scipy.optimize import least_squares

# Import time module to measure computation time
# Importa módulo time para medir tempo de execução
import time


class EnergySolver:
    """
    Numerical solver for the energy balance.

    RESPONSIBILITY:
    - call nonlinear solver
    - compute enthalpies
    - return all energy variables
    """
    """
    Solver numérico para o balanço de energia.

    RESPONSABILIDADE:
    - chamar o solver não linear
    - calcular entalpias
    - retornar todas as variáveis de energia
    """

    def __init__(self, module, thermo):

        # Store reference to the energy balance model
        # Armazena referência ao modelo de balanço de energia
        self.module = module

        # Store thermodynamic model used to compute enthalpies
        # Armazena o modelo termodinâmico usado para calcular entalpias
        self.thermo = thermo


    def solve(self, x0):

        # Record start time of the solver
        # Registra o tempo inicial da execução do solver
        t0 = time.time()

        # Build sparsity structure of the Jacobian matrix
        # Constrói a estrutura esparsa do Jacobiano
        Spa_Mat = self.module.build_jac_sparsity()

        # Solve nonlinear system using SciPy least-squares solver
        # Resolve o sistema não linear usando o solver least-squares do SciPy
        result = least_squares(

            # Residual function defined in the energy module
            # Função de resíduos definida no módulo de energia
            fun=self.module.residual,

            # Initial guess vector for temperatures
            # Vetor de estimativa inicial para as temperaturas
            x0=x0,

            # Trust-region reflective algorithm
            # Algoritmo trust-region reflective
            method='trf',

            # Physical bounds for temperatures (K)
            # Limites físicos para temperaturas (K)
            bounds=(100, 500),

            # Jacobian computed via finite differences
            # Jacobiano calculado por diferenças finitas
            jac='2-point',

            # Sparse Jacobian structure
            # Estrutura esparsa do Jacobiano
            jac_sparsity=Spa_Mat,

            # Solver tolerances
            # Tolerâncias do solver
            xtol=1e-8,
            ftol=1e-8,

            # Maximum number of function evaluations
            # Número máximo de avaliações da função
            max_nfev=5000,

            # Verbose output from solver
            # Saída detalhada do solver
            verbose=0
        )

        # Compute total solver runtime
        # Calcula tempo total de execução do solver
        elapsed = time.time() - t0

        # Print computation time
        # Imprime tempo de computação
        print(f"Computation time energy balance: {elapsed:.2f} s")

        # Check if solver converged successfully
        # Verifica se o solver convergiu corretamente
        if not result.success:

            # Raise error if solver failed
            # Lança erro caso o solver falhe
            raise RuntimeError(result.message)

        # Number of axial segments
        # Número de segmentos axiais
        NCells = self.module.NCells

        # Extract retentate temperature profile from solution vector
        # Extrai perfil de temperatura do retentado do vetor solução
        T_ret = result.x[:NCells+1]

        # Extract permeate temperature profile
        # Extrai perfil de temperatura do permeado
        T_per = result.x[NCells+1:]

        # ----------------------------------------
        # Compute enthalpies
        # Calcular entalpias
        # ----------------------------------------

        # Initialize arrays for enthalpies
        # Inicializa vetores de entalpia
        hRet = np.zeros(NCells+1)
        hPerm = np.zeros(NCells+1)
        hMemb   = np.zeros(NCells+1)
        UA = np.zeros(NCells + 1)

        # Loop over all nodes
        # Loop sobre todos os nós
        for k in range(NCells+1):

            # Retentate enthalpy at node k
            # Entalpia do retentado no nó k
            hRet[k] = self.thermo.get_h_ret(k, T_ret[k])

            # Permeate enthalpy at node k
            # Entalpia do permeado no nó k
            hPerm[k] = self.thermo.get_h_per(k, T_per[k])

            # Enthalpy of the permeating stream (membrane flux)
            # Entalpia do fluxo que atravessa a membrana
            if k > 0:
                hMemb[k] = self.thermo.get_h_J(k, T_ret[k])
                UA[k] = self.module.geom.AREA_SEG * self.thermo._uo_b7(k, T_ret[k], T_per[k-1], self.module.FPerm, self.module.FRet, self.module.geom)

        # Return results as dictionary
        # Retorna resultados em formato de dicionário
        return {
            "T_ret": T_ret,
            "T_per": T_per,
            "hRet": hRet,
            "hPerm": hPerm,
            "hMemb": hMemb,
            "UA": UA
        }