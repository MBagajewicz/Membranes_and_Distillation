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

    def __init__(self, components, PRet, PPerm, ZRet, ZPerm, ZMemb):

        # List of components in the mixture
        # Lista de componentes na mistura
        self.components = components

        # Retentate pressure profile
        # Perfil de pressão do retentado
        self.PRet = np.asarray(PRet)

        # Permeate pressure profile
        # Perfil de pressão do permeado
        self.PPerm = np.asarray(PPerm)

        # Retentate composition profile
        # Perfil de composição do retentado
        self.ZRet = np.asarray(ZRet)

        # Permeate composition profile
        # Perfil de composição do permeado
        self.ZPerm = np.asarray(ZPerm)

        # Composition of the membrane permeation flux
        # Composição do fluxo que atravessa a membrana
        self.ZMemb = np.asarray(ZMemb)

        # Number of axial segments
        # Número de segmentos axiais
        self.NCells = len(PRet) - 1

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
        self.ZPerm[self.NCells] = self.ZPerm[self.NCells - 1]

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
            st = AbstractState("HEOS", comp)

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
        return self._h_mix_ideal(self.PRet[k], T, self.ZRet[k])


    def get_h_per(self, k, T):

        # Compute permeate enthalpy at node k
        # Calcula entalpia do permeado no nó k
        return self._h_mix_ideal(self.PPerm[k], T, self.ZPerm[k])
    

    def get_h_J(self, k, T):

        # Compute enthalpy of permeating flux
        # Calcula entalpia do fluxo que atravessa a membrana
        return self._h_mix_ideal(self.PRet[k], T, self.ZMemb[k])
    

    # ----------------------------
    # Enthalpy inversion retentate
    # Inversão de entalpia do retentado
    # ----------------------------
    def get_T_from_h_ret(self, k, h_target, T_guess=None,
                         T_min=100.0, T_max=800.0,
                         tol=1e-8, maxiter=20):

        # Pressure and composition at node k
        # Pressão e composição no nó k
        P = self.PRet[k]
        x = self.ZRet[k]

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
        P = self.PPerm[k]
        x = self.ZPerm[k]

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

    # ==========================================================
    # TRANSPORT / THERMAL PROPERTIES
    # ==========================================================
    def _get_transport_props(self, P, T, x):

        rho_mass = 0
        rho_molar = 0
        mu = 0
        k = 0
        cp_mass = 0
        cp_molar = 0
        MW = 0

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
            rho_mass += xi * st.cpmolar()
            rho_molar += xi * st.rhomolar()
            mu += xi * st.viscosity()
            k += xi * st.conductivity()
            cp_mass += xi * st.cpmass()
            cp_molar += xi * st.cpmolar()
            MW += xi * st.molar_mass()

        return {
            "rho_mass": rho_mass,       # kg/m3
            "rho_molar": rho_molar,     # mol/m3
            "mu": mu,           # Pa.s
            "k": k,         # W/m/K
            "cp_mass": cp_mass,         # J/kg/K
            "cp_molar": cp_molar,       # J/mol/K
            "MW": MW,          # kg/mol
        }

    def get_transport_ret(self, k, T):
        return self._get_transport_props(self.PRet[k], T, self.ZRet[k])

    def get_transport_per(self, k, T):
        return self._get_transport_props(self.PPerm[k], T, self.ZPerm[k])

    def _uo_b7(self, k, T_ret_k, T_per_km1, FPerm, FRet, geom, support_porosity=0.5, k_polymer=0.2):
        """
        Overall heat transfer coefficient based on outer area
        using Coker (1999), Appendix B, form B7.
        """


        # geometria
        Ri = 0.5 * geom.DiamFiber_i
        Rext = 0.5 * geom.DiamFiber_o

        # propriedades locais via CoolProp
        ret = self.get_transport_ret(k, T_ret_k)
        per = self.get_transport_per(k - 1, T_per_km1)

        # bore side (permeado)
        k_g_b = per["k"]
        mu_b = per["mu"]
        cp_b = per["cp_mass"]
        MW_b = per["MW"]
        rho_b = per["rho_mass"]

        # shell side (retentado)
        k_g_s = ret["k"]
        mu_s = ret["mu"]
        cp_s = ret["cp_mass"]
        MW_s = ret["MW"]
        rho_s = ret["rho_mass"]

        # vazões mássicas locais
        mdot_b = max(FPerm[k - 1], 0.0) * MW_b
        mdot_s = max(FRet[k], 0.0) * MW_s

        # ----------------------------------
        # B2: bore-side heat transfer
        # ----------------------------------
        A_bore = geom.NFibers * np.pi * Ri**2
        vb = mdot_b / max(rho_b * A_bore, 1e-30)

        Re_b = rho_b * vb * (2.0 * Ri) / max(mu_b, 1e-30)
        Pr_b = cp_b * mu_b / max(k_g_b, 1e-30)

        h_b = 3.66 * k_g_b / (2.0 * Ri)

        # ----------------------------------
        # B3: porous support conductivity
        # ----------------------------------
        f_p = 1.0 - support_porosity
        k_supp = f_p * k_polymer + (1.0 - f_p) * k_g_b

        # ----------------------------------
        # B6: shell-side heat transfer
        # ----------------------------------
        A_shell_open = (np.pi / 4.0) * (
            geom.DiamShell**2
            - geom.NFibers * geom.DiamFiber_o**2
        )
        A_shell_open = max(A_shell_open, 1e-30)

        # v_s = mdot_s / max(rho_s * A_shell_open, 1e-30)
        Gs = mdot_s / A_shell_open

        D_h = (geom.DiamShell**2 - geom.NFibers * geom.DiamFiber_o**2) / (geom.DiamShell + geom.NFibers * geom.DiamFiber_o) #todo: revisar Dh

        Re_s = Gs * D_h / max(mu_s, 1e-30)
        Pr_s = cp_s * mu_s / max(k_g_s, 1e-30)

        h_s = (k_g_s / (2.0 * Rext)) * (
            3.66 + 1.077 * (Re_s * Pr_s * (Rext / max(D_h, 1e-30)))**(1.0 / 3.0)
        )

        # ----------------------------------
        # B7
        # ----------------------------------

        inv_uo = (
                (Rext / Ri)/max(h_b, 1e-30)
            + (Rext / max(k_supp, 1e-30)) * np.log(Rext / Ri)
            + 1.0 / max(h_s, 1e-30)
                )

        uo = 1.0 / max(inv_uo, 1e-30)
        return uo