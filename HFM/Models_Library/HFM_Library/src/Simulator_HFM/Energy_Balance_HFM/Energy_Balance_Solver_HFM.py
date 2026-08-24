# #region Title: EnergyBalanceSolverHFM
# # Nature: Solver of equations
# # Methodology: Uses least_squares library to minimize energy balance residuals of HFM models 
# ##################################################################################################################
# # VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
# #  0.0       13-May-2025    Diego Gabriel Oliva            Commented
# #  1.0       09-Jun-2026    Qwen                           Added critical diagnostics for x0 stagnation
# ##################################################################################################################
# #endregion

# import numpy as np
from ..Simulation_Deadline import SimulationTimeout
# from scipy.optimize import least_squares
# import time

# class EnergyBalanceSolverHFM:
#     """
#     Numerical solver for the energy balance.
#     """

#     def __init__(self, module):
#         self.module = module

#     def solve(self, x0, tol=1e-6, maxfev=20000, verbose=0):

#         t0 = time.time()
#         Spa_Mat = self.module.build_jac_sparsity()
#         jac_fun = self.module.jacobian if hasattr(self.module, "jacobian") else '2-point'

#         # Forzamos verbose=1 temporalmente para ver qué hace SciPy internamente
#         # Puedes volver a poner 'verbose' si ya funciona
#         solver_verbose = 1 if verbose == 0 else verbose 

#         result = least_squares(
#             fun=self.module.residual,
#             x0=x0,
#             method='trf',
#             bounds=(200.0, 400.0), # Aseguramos que sean floats
#             jac=jac_fun,
#             jac_sparsity=Spa_Mat,
#             xtol=tol,
#             ftol=tol,
#             gtol=tol,
#             max_nfev=maxfev,
#             x_scale='jac',
#             verbose=solver_verbose
#         )

#         elapsed = time.time() - t0
#         print(f"Computation time energy balance: {elapsed:.2f} s")

#         NCells = self.module.NCells
#         T_ret = result.x[:NCells+1]
#         T_per = result.x[NCells+1:]

#         return {
#             "T_ret": T_ret,
#             "T_per": T_per,
#             "success": result.success,
#             "message": result.message
#         }




































#region Title: EnergyBalanceSolverHFM
# Nature: Solver of equations
# Methodology: Uses least_squares library to minimize energy balance residuals of HFM models 
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion


# Import NumPy for numerical operations and array handling
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np

# Import nonlinear least-squares solver from SciPy
# Importa solver de mínimos quadrados não lineares do SciPy
from scipy.optimize import least_squares

# Import time module to measure computation time
# Importa módulo time para medir tempo de execução
import time

class EnergyBalanceSolverHFM:
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

    def __init__(self, module):

        # Store reference to the energy balance model
        # Armazena referência ao modelo de balanço de energia
        self.module = module

        # # Store thermodynamic model used to compute enthalpies
        # # Armazena o modelo termodinâmico usado para calcular entalpias
        # self.thermo = thermo

    def solve(self, x0, tol=1e-6, maxfev=20000, verbose=2):
        """Fast path: damped Newton with a least-squares (min-norm) step,
        which tolerates the single rank-deficient DOF (the closed-end
        permeate temperature, whose energy residual is identically zero).
        Falls back to trust-region least squares if Newton stalls.
        """
        import time as _time
        t0 = _time.time()
        module = self.module
        lo, hi = 200.0, 600.0
        x = np.array(x0, dtype=float)
        try:
            r = module.residual(x)
            rn = np.linalg.norm(r)
            converged = False
            for _it in range(50):
                J = module.jacobian(x)
                Jd = J.toarray() if hasattr(J, "toarray") else np.asarray(J)
                dx, *_ = np.linalg.lstsq(Jd, -r, rcond=None)
                a = 1.0
                accepted = False
                for _ls in range(40):
                    xn = np.clip(x + a * dx, lo, hi)
                    rnew = module.residual(xn)
                    rnn = np.linalg.norm(rnew)
                    if rnn < rn * (1.0 - 1e-4 * a) or rnn < tol:
                        accepted = True
                        break
                    a *= 0.5
                if not accepted:
                    xn = np.clip(x + a * dx, lo, hi)
                    rnew = module.residual(xn)
                    rnn = np.linalg.norm(rnew)
                step = np.max(np.abs(xn - x))
                x, r, rn = xn, rnew, rnn
                if rn < tol or step < tol:
                    converged = True
                    break
            if not converged and rn > 1e-3:
                raise RuntimeError("Newton energy solver did not converge")
        except SimulationTimeout:
            raise   # control-flow signal: never swallow it
        except Exception:
            return self._solve_lsq(x0, tol, maxfev, verbose, t0)

        elapsed = _time.time() - t0
        if verbose:
            print(f"Computation time energy balance (newton): {elapsed:.4f} s")
        NCells = module.NCells
        return {"T_ret": x[:NCells + 1], "T_per": x[NCells + 1:]}

    def _solve_lsq(self, x0, tol=1e-6, maxfev=20000, verbose=2, t0=None):

        # Record start time of the solver
        # Registra o tempo inicial da execução do solver
        if t0 is None:
            t0 = time.time()

        # Build sparsity structure of the Jacobian matrix
        # Constrói a estrutura esparsa do Jacobiano
        Spa_Mat = self.module.build_jac_sparsity()

        jac_fun = self.module.jacobian if hasattr(self.module, "jacobian") else '2-point'


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
            bounds=(200, 600),

            # Jacobian computed via finite differences
            # Jacobiano calculado por diferenças finitas
            jac=jac_fun,

            # Sparse Jacobian structure
            # Estrutura esparsa do Jacobiano
            jac_sparsity=Spa_Mat,

            # Solver tolerances
            # Tolerâncias do solver
            xtol=tol,
            ftol=tol,
            gtol=tol,

            # Maximum number of function evaluations
            # Número máximo de avaliações da função
            max_nfev=maxfev,

            # Scale variables using Jacobian magnitude
            # Escala variáveis usando magnitude do Jacobiano
            x_scale='jac',

            # Verbose output from solver
            # Saída detalhada do solver
            verbose=verbose
        )

        # Compute total solver runtime
        # Calcula tempo total de execução do solver
        elapsed = time.time() - t0

        # Print computation time
        # Imprime tempo de computação
        # print(f"Computation time energy balance: {elapsed:.2f} s")

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
        # for k in range(NCells+1):

        #     # Retentate enthalpy at node k
        #     # Entalpia do retentado no nó k
        #     hRet[k] = self.thermo.get_h_ret(k, T_ret[k])

        #     # Permeate enthalpy at node k
        #     # Entalpia do permeado no nó k
        #     hPerm[k] = self.thermo.get_h_per(k, T_per[k])

        #     # Enthalpy of the permeating stream (membrane flux)
        #     # Entalpia do fluxo que atravessa a membrana
        #     if k > 0:
        #         hMemb[k] = self.thermo.get_h_J(k, T_ret[k])
        #         UA[k] = self.module.geom.AREA_SEG * self.thermo._uo_b7(k, T_ret[k], T_per[k-1], self.module.FPerm, self.module.FRet, self.module.geom)
        # Return results as dictionary
        # Retorna resultados em formato de dicionário
        return {
            "T_ret": T_ret,
            "T_per": T_per,
            # "hRet": hRet,
            # "hPerm": hPerm,
            # "hMemb": hMemb,
            # "UA": UA
        }