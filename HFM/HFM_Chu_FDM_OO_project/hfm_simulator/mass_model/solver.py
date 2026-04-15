# HFM/HFM_Chu_FDM_OO/solver.py

# Import NumPy for numerical operations
# Importa NumPy para operações numéricas
import numpy as np

# Import nonlinear least squares solver from SciPy
# Importa o solver de mínimos quadrados não lineares do SciPy
from scipy.optimize import least_squares

# Import time module to measure computation time
# Importa o módulo time para medir o tempo de computação
import time


class HFMSolver:
    """
    Numerical solver for the HFM model.

    SINGLE RESPONSIBILITY:
    - assemble the initial vector
    - call least_squares
    - return the solution
    """
    """
    Solver numérico para o modelo HFM.

    RESPONSABILIDADE ÚNICA:
    - montar o vetor inicial
    - chamar least_squares
    - retornar a solução
    """

    def __init__(self, module):
        """
        Numerical solver for the HFM model.

        Parameters
        ----------
        module : HollowFiberModule
            Physical model (defines residuals)
        """
        """
        Solver numérico para o modelo HFM.

        Parameters
        ----------
        module : HollowFiberModule
            Modelo físico (define os resíduos)
        """

        # Store reference to the physical module model
        # Armazena a referência ao modelo físico do módulo
        self.module = module


    def solve(self, x0, tol=1e-9, maxfev=20000, verbose=False):
        """
        Solves the nonlinear system using least squares
        with positivity constraints.

        Returns
        -------
        sol : ndarray
            Solution vector
        info : dict
            Convergence information
        """
        """
        Resolve o sistema não linear usando mínimos quadrados.

        Returns
        -------
        sol : ndarray
            Vetor solução
        info : dict
            Informações de convergência
        """

        # Record start time of the solver
        # Registra o tempo inicial do solver
        t00 = time.time()

        # Build sparsity pattern of the Jacobian matrix
        # Constrói a estrutura esparsa do Jacobiano
        S = self.module.build_jac_sparsity()

        # Call SciPy nonlinear least squares solver
        # Chama o solver de mínimos quadrados não lineares do SciPy
        result = least_squares(

            # Residual function provided by the physical module
            # Função de resíduos fornecida pelo modelo físico
            fun=self.module.residuals,

            # Initial guess vector
            # Vetor inicial de estimativa
            x0=x0,

            # Finite-difference Jacobian approximation
            # Aproximação do Jacobiano por diferenças finitas
            jac='2-point',

            # Provide sparsity pattern to accelerate computation
            # Fornece estrutura esparsa para acelerar o cálculo
            jac_sparsity=S,

            # Trust-region reflective algorithm
            # Algoritmo trust-region reflective
            method='trf',

            # Linear solver used internally
            # Solver linear usado internamente
            tr_solver='lsmr',

            # Scale variables using Jacobian magnitude
            # Escala variáveis usando magnitude do Jacobiano
            x_scale='jac',

            # Verbose output from solver
            # Saída detalhada do solver
            verbose=0
        )

        # Compute total elapsed computation time
        # Calcula o tempo total de computação
        elapsed = time.time() - t00

        # Optionally print computation time
        # Opcionalmente imprime o tempo de computação
        if verbose:
            print(f"Computation time mass balance: {elapsed:.2f} s")

        # Check solver convergence
        # Verifica se o solver convergiu
        if not result.success:

            # Raise an error if solver failed
            # Lança erro caso o solver falhe
            raise RuntimeError(
                f"Convergence failure:\n{result.message}"
            )

        # Return solution vector and diagnostic information
        # Retorna vetor solução e informações diagnósticas
        return result.x, {

            # Number of function evaluations
            # Número de avaliações da função
            "iterations": result.nfev,

            # Total computation time
            # Tempo total de computação
            "time": elapsed,

            # Final least squares cost
            # Valor final da função de custo
            "cost": result.cost,

            # Optimality measure (gradient norm)
            # Medida de otimalidade (norma do gradiente)
            "optimality": result.optimality
        }