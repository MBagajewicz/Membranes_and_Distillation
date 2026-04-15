# Import NumPy for numerical operations
# Importa NumPy para operações numéricas
import numpy as np

# Import CoolProp main module
# Importa módulo principal do CoolProp
import CoolProp

# Import AbstractState interface from CoolProp
# Importa interface AbstractState do CoolProp
from CoolProp.CoolProp import AbstractState


class ThermoModel:
    """
    Thermodynamic helper based on CoolProp.

    SAME INTERFACE as thermo_model.py
    but:
      - NO mixture enthalpies
      - Ideal molar averaging of pure-component enthalpies
    """
    """
    Auxiliar termodinâmico baseado no CoolProp.

    MESMA INTERFACE do arquivo thermo_model.py
    porém:
      - NÃO usa entalpia de mistura real
      - Usa média molar ideal das entalpias de componentes puros
    """

    def __init__(self, components, P_ret, p_per, x_ret, y_per, z_J):

        # List of components in the mixture
        # Lista de componentes na mistura
        self.components = components

        # Retentate pressure profile
        # Perfil de pressão do retentado
        self.P_ret = np.asarray(P_ret)

        # Permeate pressure profile
        # Perfil de pressão do permeado
        self.p_per = np.asarray(p_per)

        # Retentate composition profile
        # Perfil de composição do retentado
        self.x_ret = np.asarray(x_ret)

        # Permeate composition profile
        # Perfil de composição do permeado
        self.y_per = np.asarray(y_per)

        # Composition of the membrane permeation flux
        # Composição do fluxo que atravessa a membrana
        self.z_J = np.asarray(z_J)

        # Number of axial segments
        # Número de segmentos axiais
        self.N = len(P_ret) - 1

        # --------------------------------------------------
        # 🔒 Composition fix at permeate outlet (k = N)
        # Correção da composição na saída do permeado
        # --------------------------------------------------

        # At the module outlet the permeate flow tends to zero,
        # so the composition becomes numerically undefined.
        # We copy the upstream composition to avoid numerical issues.
        #
        # Na saída do módulo o fluxo do permeado tende a zero,
        # então a composição fica numericamente indefinida.
        # Copiamos a composição do nó anterior para evitar problemas numéricos.
        self.y_per[self.N] = self.y_per[self.N - 1]

        # --------------------------------------------------
        # Pure-component states (NO mixtures)
        # Estados termodinâmicos de componentes puros (SEM mistura)
        # --------------------------------------------------

        # Dictionary storing CoolProp states for each component
        # Dicionário que armazena estados CoolProp para cada componente
        self.states_pure = {}

        for comp in components:

            # Create CoolProp thermodynamic state using Peng-Robinson EOS
            # Cria estado termodinâmico no CoolProp usando equação de estado Peng-Robinson
            st = AbstractState("PR", comp)

            # Store state object
            # Armazena objeto de estado
            self.states_pure[comp] = st


    # --------------------------------------------------
    # Ideal enthalpy of mixture (molar)
    # Entalpia ideal da mistura (molar)
    # --------------------------------------------------
    def _h_mix_ideal(self, P, T, x):

        # Initialize mixture enthalpy
        # Inicializa entalpia da mistura
        h = 0.0

        # Loop over each component
        # Loop sobre cada componente
        for xi, comp in zip(x, self.components):

            # Skip components with zero mole fraction
            # Ignora componentes com fração molar zero
            if xi == 0.0:
                continue

            # Get CoolProp state object
            # Obtém objeto de estado do CoolProp
            st = self.states_pure[comp]

            # Update state with pressure and temperature
            # Atualiza estado com pressão e temperatura
            st.update(CoolProp.PT_INPUTS, P, T)

            # Add weighted enthalpy contribution
            # Soma contribuição de entalpia ponderada
            h += xi * st.hmolar()

        return h


    def _cp_mix_ideal(self, P, T, x):

        # Initialize mixture heat capacity
        # Inicializa capacidade calorífica da mistura
        Cp = 0.0

        # Loop over components
        # Loop sobre componentes
        for xi, comp in zip(x, self.components):

            # Skip components with zero mole fraction
            # Ignora componentes com fração molar zero
            if xi == 0.0:
                continue

            st = self.states_pure[comp]

            # Update thermodynamic state
            # Atualiza estado termodinâmico
            st.update(CoolProp.PT_INPUTS, P, T)

            # Add weighted heat capacity
            # Soma capacidade calorífica ponderada
            Cp += xi * st.cpmolar()

        return Cp


    # ----------------------------
    # Enthalpies in flow direction
    # Entalpias na direção do escoamento
    # ----------------------------
    def get_h_ret(self, k, T):

        # Compute retentate enthalpy at node k
        # Calcula entalpia do retentado no nó k
        return self._h_mix_ideal(self.P_ret[k], T, self.x_ret[k])


    def get_h_per(self, k, T):

        # Compute permeate enthalpy at node k
        # Calcula entalpia do permeado no nó k
        return self._h_mix_ideal(self.p_per[k], T, self.y_per[k])
    

    def get_h_J(self, k, T):

        # Compute enthalpy of permeating flux
        # Calcula entalpia do fluxo que atravessa a membrana
        return self._h_mix_ideal(self.P_ret[k], T, self.z_J[k])
    

    # ----------------------------
    # Enthalpy inversion retentate
    # Inversão de entalpia do retentado
    # ----------------------------
    def get_T_from_h_ret(self, k, h_target, T_guess=None,
                         T_min=100.0, T_max=800.0,
                         tol=1e-8, maxiter=20):

        # Pressure and composition at node k
        # Pressão e composição no nó k
        P = self.P_ret[k]
        x = self.x_ret[k]

        # Initialize temperature guess
        # Inicializa estimativa de temperatura
        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        # ----------------------------
        # Newton method
        # Método de Newton
        # ----------------------------
        for _ in range(maxiter):

            # Compute enthalpy
            # Calcula entalpia
            h = self._h_mix_ideal(P, T, x)

            dh = h - h_target

            # Check convergence
            # Verifica convergência
            if abs(dh) < tol:
                return T

            # Compute heat capacity
            # Calcula capacidade calorífica
            Cp = self._cp_mix_ideal(P, T, x)

            # Safety check
            # Verificação de segurança
            if Cp <= 0.0:
                break

            # Newton step
            # Passo de Newton
            T -= dh / Cp

            # Enforce bounds
            # Impõe limites físicos
            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # ----------------------------
        # Bisection fallback
        # Método da bisseção (fallback)
        # ----------------------------
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            h_mid = self._h_mix_ideal(P, T_mid, x)

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(
            f"T(h) inversion failed (ideal mix) at k={k}, h={h_target}"
        )


    # ----------------------------
    # Enthalpy inversion permeate
    # Inversão de entalpia do permeado
    # ----------------------------
    def get_T_from_h_per(self, k, h_target, T_guess=None,
                         T_min=100.0, T_max=800.0,
                         tol=1e-8, maxiter=20):

        # Pressure and composition
        # Pressão e composição
        P = self.p_per[k]
        x = self.y_per[k]

        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        for _ in range(maxiter):

            h = self._h_mix_ideal(P, T, x)
            dh = h - h_target

            if abs(dh) < tol:
                return T

            Cp = self._cp_mix_ideal(P, T, x)

            if Cp <= 0.0:
                break

            T -= dh / Cp

            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # Bisection fallback
        # Método da bisseção como fallback
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            h_mid = self._h_mix_ideal(P, T_mid, x)

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(
            f"T(h) inversion failed (ideal mix) at k={k}, h={h_target}"
        )