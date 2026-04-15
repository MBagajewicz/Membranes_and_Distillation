# Import NumPy for numerical operations and array handling
# Importa NumPy para operações numéricas e manipulação de arrays
import numpy as np

# Import CoolProp main module
# Importa módulo principal do CoolProp
import CoolProp

# Import AbstractState interface from CoolProp
# Importa interface AbstractState do CoolProp
from CoolProp.CoolProp import AbstractState


class ThermoModelWithMixture:
    """
    Thermodynamic helper based on CoolProp.
    Provides h(T,P,x) and inversion T(h,P,x).
    """
    """
    Auxiliar termodinâmico baseado no CoolProp.
    Fornece cálculo de h(T,P,x) e inversão T(h,P,x).
    """

    def __init__(self, components, P_ret, p_per, x_ret, y_per, z_J):

        # List of components present in the mixture
        # Lista de componentes presentes na mistura
        self.components = components

        # Retentate pressure profile along the membrane
        # Perfil de pressão do retentado ao longo da membrana
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

        # Composition of the permeating flux
        # Composição do fluxo que atravessa a membrana
        self.z_J = np.asarray(z_J)

        # Number of axial segments
        # Número de segmentos axiais
        self.N = len(P_ret) - 1

        # --------------------------------------------------
        # 🔒 Composition fix at permeate outlet (k = N)
        # Correção da composição na saída do permeado
        # --------------------------------------------------

        # At k = N the permeate flow goes to zero.
        # Composition becomes numerically undefined.
        # We inherit the composition from node N-1 to
        # preserve thermodynamic consistency.
        #
        # Em k = N o fluxo do permeado tende a zero.
        # A composição fica numericamente indefinida.
        # Copiamos a composição do nó N-1 para manter
        # consistência termodinâmica.
        self.y_per[self.N] = self.y_per[self.N - 1]

        # Create CoolProp mixture string
        # Cria string da mistura para o CoolProp
        fluid_string = "&".join(components)

        # Lists storing thermodynamic states at each node
        # Listas que armazenam estados termodinâmicos em cada nó
        self.states_ret = []
        self.states_per = []
        self.states_J = []

        # Create CoolProp state objects for each node
        # Cria objetos de estado do CoolProp para cada nó
        for k in range(self.N + 1):

            # Retentate mixture state
            # Estado da mistura do retentado
            st_r = AbstractState("HEOS", fluid_string)

            # Set mole fractions
            # Define frações molares
            st_r.set_mole_fractions(self.x_ret[k])

            # Store state
            # Armazena estado
            self.states_ret.append(st_r)

            # Permeate mixture state
            # Estado da mistura do permeado
            st_p = AbstractState("HEOS", fluid_string)
            st_p.set_mole_fractions(self.y_per[k])
            self.states_per.append(st_p)

            # Membrane flux mixture state
            # Estado da mistura do fluxo que atravessa a membrana
            st_J = AbstractState("HEOS", fluid_string)
            st_J.set_mole_fractions(self.z_J[k])
            self.states_J.append(st_J)


    # ----------------------------
    # Enthalpies in flow direction
    # Entalpias na direção do escoamento
    # ----------------------------
    def get_h_ret(self, k, T):

        # Retrieve thermodynamic state for retentate at node k
        # Obtém estado termodinâmico do retentado no nó k
        st = self.states_ret[k]

        # Update thermodynamic state with pressure and temperature
        # Atualiza estado com pressão e temperatura
        st.update(CoolProp.PT_INPUTS, self.P_ret[k], T)

        # Return molar enthalpy
        # Retorna entalpia molar
        return st.hmolar()


    def get_h_per(self, k, T):

        # Retrieve permeate thermodynamic state
        # Obtém estado termodinâmico do permeado
        st = self.states_per[k]

        # Update state
        # Atualiza estado
        st.update(CoolProp.PT_INPUTS, self.p_per[k], T)

        # Return molar enthalpy
        # Retorna entalpia molar
        return st.hmolar()


    def get_h_J(self, k, T):

        # Retrieve state for permeating flux mixture
        # Obtém estado da mistura que atravessa a membrana
        st = self.states_J[k]

        # Update state
        # Atualiza estado
        st.update(CoolProp.PT_INPUTS, self.P_ret[k], T)

        # Return molar enthalpy
        # Retorna entalpia molar
        return st.hmolar()


    # ----------------------------
    # Enthalpies inversion retentate
    # Inversão de entalpia do retentado
    # ----------------------------
    def get_T_from_h_ret(self, k, h_target, T_guess=None,
                        T_min=100.0, T_max=800.0,
                        tol=1e-8, maxiter=20):
        """
        Invert h(T,P,x) -> T for retentate stream at node k
        """
        """
        Inverte h(T,P,x) -> T para o retentado no nó k
        """

        # Retrieve CoolProp state
        # Obtém estado CoolProp
        st = self.states_ret[k]

        # -------------------------
        # Initial temperature guess
        # Estimativa inicial de temperatura
        # -------------------------
        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        # -------------------------
        # Newton iteration
        # Iteração de Newton
        # -------------------------
        for _ in range(maxiter):

            # Update thermodynamic state
            # Atualiza estado termodinâmico
            st.update(CoolProp.PT_INPUTS, self.P_ret[k], T)

            # Compute enthalpy
            # Calcula entalpia
            h = st.hmolar()

            # Residual
            # Resíduo
            dh = h - h_target

            # Convergence check
            # Verificação de convergência
            if abs(dh) < tol:
                return T

            # Heat capacity at constant pressure
            # Capacidade calorífica a pressão constante
            Cp = st.cpmolar()

            # Newton temperature update
            # Atualização de temperatura pelo método de Newton
            dT = - dh / Cp
            T += dT

            # Soft bounding to maintain physical limits
            # Limitação suave para manter limites físicos
            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # -------------------------
        # Fallback: bisection
        # Método da bisseção (fallback)
        # -------------------------
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            st.update(CoolProp.PT_INPUTS, self.P_ret[k], T_mid)

            h_mid = st.hmolar()

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(
            f"T(h) inversion failed at k={k}, h={h_target}"
        )
    

    # ----------------------------
    # Enthalpies inversion permeate
    # Inversão de entalpia do permeado
    # ----------------------------
    def get_T_from_h_per(self, k, h_target, T_guess=None,
                        T_min=100.0, T_max=800.0,
                        tol=1e-8, maxiter=20):

        # Retrieve permeate thermodynamic state
        # Obtém estado termodinâmico do permeado
        st = self.states_per[k]

        # Initial temperature guess
        # Estimativa inicial de temperatura
        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        # Newton iteration
        # Iteração de Newton
        for _ in range(maxiter):

            st.update(CoolProp.PT_INPUTS, self.p_per[k], T)

            h = st.hmolar()
            dh = h - h_target

            if abs(dh) < tol:
                return T

            Cp = st.cpmolar()

            # Newton update
            # Atualização de Newton
            T -= dh / Cp

            # Bound temperature
            # Limita temperatura
            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # Fallback: bisection
        # Método da bisseção como fallback
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            st.update(CoolProp.PT_INPUTS, self.p_per[k], T_mid)

            h_mid = st.hmolar()

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(
            f"T(h) inversion failed at k={k}, h={h_target}"
        )
