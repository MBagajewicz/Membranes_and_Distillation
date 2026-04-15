import numpy as np
import CoolProp
from CoolProp.CoolProp import AbstractState


class ThermoModelWithMixture:
    """
    Thermodynamic helper based on CoolProp (PR EOS).
    Fully robust version with gas-phase enforcement and error handling.
    """

    def __init__(self, components, PRet, PPerm, ZRet, ZPerm, ZMemb):

        self.components = components
        self.PRet = np.asarray(PRet)
        self.PPerm = np.asarray(PPerm)
        self.ZRet = np.asarray(ZRet)
        self.ZPerm = np.asarray(ZPerm)
        self.ZMemb = np.asarray(ZMemb)

        self.NCells = len(PRet) - 1

        # Fix composition at permeate outlet
        self.ZPerm[self.NCells] = self.ZPerm[self.NCells - 1]

        fluid_string = "&".join(components)

        self.states_ret = []
        self.states_per = []
        self.states_J = []

        for k in range(self.NCells + 1):

            st_r = AbstractState("HEOS", fluid_string)
            st_r.set_mole_fractions(self.ZRet[k])
            self.states_ret.append(st_r)

            st_p = AbstractState("HEOS", fluid_string)
            st_p.set_mole_fractions(self.ZPerm[k])
            self.states_per.append(st_p)

            st_J = AbstractState("HEOS", fluid_string)
            st_J.set_mole_fractions(self.ZMemb[k])
            self.states_J.append(st_J)

    # ==========================================================
    # 🔒 SAFE UPDATE (CORE FIX)
    # ==========================================================
    def _safe_update_gas(self, st, P, T):
        """
        Safe update enforcing gas phase and avoiding PR failures.
        """

        # Clamp temperature (avoid nonsense values)
        T = max(150.0, min(1000.0, T))

        # Force gas phase
        st.specify_phase(CoolProp.iphase_gas)

        try:
            st.update(CoolProp.PT_INPUTS, P, T)

        except ValueError:
            try:
                st.update(CoolProp.PT_INPUTS, P, T + 1e-6)
            except ValueError:
                try:
                    st.update(CoolProp.PT_INPUTS, P, T + 1e-3)
                except ValueError:
                    st.update(CoolProp.PT_INPUTS, P * 0.999, T)

    # ==========================================================
    # ENTHALPIES
    # ==========================================================
    def get_h_ret(self, k, T):
        st = self.states_ret[k]
        self._safe_update_gas(st, self.PRet[k], T)
        return st.hmolar()

    def get_h_per(self, k, T):
        st = self.states_per[k]
        self._safe_update_gas(st, self.PPerm[k], T)
        return st.hmolar()

    def get_h_J(self, k, T):
        st = self.states_J[k]
        self._safe_update_gas(st, self.PRet[k], T)
        return st.hmolar()

    # ==========================================================
    # INVERSION: RETENTATE
    # ==========================================================
    def get_T_from_h_ret(self, k, h_target, T_guess=None,
                        T_min=100.0, T_max=800.0,
                        tol=1e-8, maxiter=20):

        st = self.states_ret[k]

        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        # Newton
        for _ in range(maxiter):

            self._safe_update_gas(st, self.PRet[k], T)

            h = st.hmolar()
            dh = h - h_target

            if abs(dh) < tol:
                return T

            Cp = st.cpmolar()

            # evitar división por cero
            if Cp == 0:
                break

            T -= dh / Cp

            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # Bisección (fallback robusto)
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            self._safe_update_gas(st, self.PRet[k], T_mid)

            h_mid = st.hmolar()

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(f"T(h) inversion failed at k={k}, h={h_target}")

    # ==========================================================
    # INVERSION: PERMEATE
    # ==========================================================
    def get_T_from_h_per(self, k, h_target, T_guess=None,
                        T_min=100.0, T_max=800.0,
                        tol=1e-8, maxiter=20):

        st = self.states_per[k]

        if T_guess is None:
            T = 0.5 * (T_min + T_max)
        else:
            T = float(T_guess)

        # Newton
        for _ in range(maxiter):

            self._safe_update_gas(st, self.PPerm[k], T)

            h = st.hmolar()
            dh = h - h_target

            if abs(dh) < tol:
                return T

            Cp = st.cpmolar()

            if Cp == 0:
                break

            T -= dh / Cp

            if T < T_min:
                T = T_min
            elif T > T_max:
                T = T_max

        # Bisección
        T_low, T_high = T_min, T_max

        for _ in range(50):

            T_mid = 0.5 * (T_low + T_high)

            self._safe_update_gas(st, self.PPerm[k], T_mid)

            h_mid = st.hmolar()

            if abs(h_mid - h_target) < tol:
                return T_mid

            if h_mid > h_target:
                T_high = T_mid
            else:
                T_low = T_mid

        raise RuntimeError(f"T(h) inversion failed at k={k}, h={h_target}")

    # ==========================================================
    # TRANSPORT / THERMAL PROPERTIES
    # ==========================================================
    def _get_transport_props(self, st, P, T):
        self._safe_update_gas(st, P, T)

        return {
            "rho_mass": st.rhomass(),       # kg/m3
            "rho_molar": st.rhomolar(),     # mol/m3
            "mu": st.viscosity(),           # Pa.s
            "k": st.conductivity(),         # W/m/K
            "cp_mass": st.cpmass(),         # J/kg/K
            "cp_molar": st.cpmolar(),       # J/mol/K
            "MW": st.molar_mass(),          # kg/mol
        }

    def get_transport_ret(self, k, T):
        st = self.states_ret[k]
        return self._get_transport_props(st, self.PRet[k], T)

    def get_transport_per(self, k, T):
        st = self.states_per[k]
        return self._get_transport_props(st, self.PPerm[k], T)

    # -------------------------------------------------
    # COKER B7
    # -------------------------------------------------
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





















# # Import NumPy for numerical operations and array handling
# # Importa NumPy para operações numéricas e manipulação de arrays
# import numpy as np

# # Import CoolProp main module
# # Importa módulo principal do CoolProp
# import CoolProp

# # Import AbstractState interface from CoolProp
# # Importa interface AbstractState do CoolProp
# from CoolProp.CoolProp import AbstractState


# class ThermoModelWithMixture:
#     """
#     Thermodynamic helper based on CoolProp.
#     Provides h(T,P,x) and inversion T(h,P,x).
#     """
#     """
#     Auxiliar termodinâmico baseado no CoolProp.
#     Fornece cálculo de h(T,P,x) e inversão T(h,P,x).
#     """

#     def __init__(self, components, PRet, PPerm, ZRet, ZPerm, ZMemb):

#         # List of components present in the mixture
#         # Lista de componentes presentes na mistura
#         self.components = components

#         # Retentate pressure profile along the membrane
#         # Perfil de pressão do retentado ao longo da membrana
#         self.PRet = np.asarray(PRet)

#         # Permeate pressure profile
#         # Perfil de pressão do permeado
#         self.PPerm = np.asarray(PPerm)

#         # Retentate composition profile
#         # Perfil de composição do retentado
#         self.ZRet = np.asarray(ZRet)

#         # Permeate composition profile
#         # Perfil de composição do permeado
#         self.ZPerm = np.asarray(ZPerm)

#         # Composition of the permeating flux
#         # Composição do fluxo que atravessa a membrana
#         self.ZMemb = np.asarray(ZMemb)

#         # Number of axial segments
#         # Número de segmentos axiais
#         self.NCells = len(PRet) - 1

#         # --------------------------------------------------
#         # 🔒 Composition fix at permeate outlet (k = N)
#         # Correção da composição na saída do permeado
#         # --------------------------------------------------

#         # At k = N the permeate flow goes to zero.
#         # Composition becomes numerically undefined.
#         # We inherit the composition from node N-1 to
#         # preserve thermodynamic consistency.
#         #
#         # Em k = N o fluxo do permeado tende a zero.
#         # A composição fica numericamente indefinida.
#         # Copiamos a composição do nó N-1 para manter
#         # consistência termodinâmica.
#         self.ZPerm[self.NCells] = self.ZPerm[self.NCells - 1]

#         # Create CoolProp mixture string
#         # Cria string da mistura para o CoolProp
#         fluid_string = "&".join(components)

#         # Lists storing thermodynamic states at each node
#         # Listas que armazenam estados termodinâmicos em cada nó
#         self.states_ret = []
#         self.states_per = []
#         self.states_J = []

#         # Create CoolProp state objects for each node
#         # Cria objetos de estado do CoolProp para cada nó
#         for k in range(self.NCells + 1):

#             # Retentate mixture state
#             # Estado da mistura do retentado
#             st_r = AbstractState("PR", fluid_string)

#             # Set mole fractions
#             # Define frações molares
#             st_r.set_mole_fractions(self.ZRet[k])

#             # Store state
#             # Armazena estado
#             self.states_ret.append(st_r)

#             # Permeate mixture state
#             # Estado da mistura do permeado
#             st_p = AbstractState("PR", fluid_string)
#             st_p.set_mole_fractions(self.ZPerm[k])
#             self.states_per.append(st_p)

#             # Membrane flux mixture state
#             # Estado da mistura do fluxo que atravessa a membrana
#             st_J = AbstractState("PR", fluid_string)
#             st_J.set_mole_fractions(self.ZMemb[k])
#             self.states_J.append(st_J)


#     # ----------------------------
#     # Enthalpies in flow direction
#     # Entalpias na direção do escoamento
#     # ----------------------------
#     def get_h_ret(self, k, T):

#         # Retrieve thermodynamic state for retentate at node k
#         # Obtém estado termodinâmico do retentado no nó k
#         st = self.states_ret[k]

#         # Update thermodynamic state with pressure and temperature
#         # Atualiza estado com pressão e temperatura
#         st.update(CoolProp.PT_INPUTS, self.PRet[k], T)

#         # Return molar enthalpy
#         # Retorna entalpia molar
#         return st.hmolar()


#     def get_h_per(self, k, T):

#         # Retrieve permeate thermodynamic state
#         # Obtém estado termodinâmico do permeado
#         st = self.states_per[k]

#         # Update state
#         # Atualiza estado
#         st.update(CoolProp.PT_INPUTS, self.PPerm[k], T)

#         # Return molar enthalpy
#         # Retorna entalpia molar
#         return st.hmolar()


#     def get_h_J(self, k, T):

#         # Retrieve state for permeating flux mixture
#         # Obtém estado da mistura que atravessa a membrana
#         st = self.states_J[k]

#         # Update state
#         # Atualiza estado
#         st.update(CoolProp.PT_INPUTS, self.PRet[k], T)

#         # Return molar enthalpy
#         # Retorna entalpia molar
#         return st.hmolar()


#     # ----------------------------
#     # Enthalpies inversion retentate
#     # Inversão de entalpia do retentado
#     # ----------------------------
#     def get_T_from_h_ret(self, k, h_target, T_guess=None,
#                         T_min=100.0, T_max=800.0,
#                         tol=1e-8, maxiter=20):
#         """
#         Invert h(T,P,x) -> T for retentate stream at node k
#         """
#         """
#         Inverte h(T,P,x) -> T para o retentado no nó k
#         """

#         # Retrieve CoolProp state
#         # Obtém estado CoolProp
#         st = self.states_ret[k]

#         # -------------------------
#         # Initial temperature guess
#         # Estimativa inicial de temperatura
#         # -------------------------
#         if T_guess is None:
#             T = 0.5 * (T_min + T_max)
#         else:
#             T = float(T_guess)

#         # -------------------------
#         # Newton iteration
#         # Iteração de Newton
#         # -------------------------
#         for _ in range(maxiter):

#             # Update thermodynamic state
#             # Atualiza estado termodinâmico
#             st.update(CoolProp.PT_INPUTS, self.PRet[k], T)

#             # Compute enthalpy
#             # Calcula entalpia
#             h = st.hmolar()

#             # Residual
#             # Resíduo
#             dh = h - h_target

#             # Convergence check
#             # Verificação de convergência
#             if abs(dh) < tol:
#                 return T

#             # Heat capacity at constant pressure
#             # Capacidade calorífica a pressão constante
#             Cp = st.cpmolar()

#             # Newton temperature update
#             # Atualização de temperatura pelo método de Newton
#             dT = - dh / Cp
#             T += dT

#             # Soft bounding to maintain physical limits
#             # Limitação suave para manter limites físicos
#             if T < T_min:
#                 T = T_min
#             elif T > T_max:
#                 T = T_max

#         # -------------------------
#         # Fallback: bisection
#         # Método da bisseção (fallback)
#         # -------------------------
#         T_low, T_high = T_min, T_max

#         for _ in range(50):

#             T_mid = 0.5 * (T_low + T_high)

#             st.update(CoolProp.PT_INPUTS, self.PRet[k], T_mid)

#             h_mid = st.hmolar()

#             if abs(h_mid - h_target) < tol:
#                 return T_mid

#             if h_mid > h_target:
#                 T_high = T_mid
#             else:
#                 T_low = T_mid

#         raise RuntimeError(
#             f"T(h) inversion failed at k={k}, h={h_target}"
#         )
    

#     # ----------------------------
#     # Enthalpies inversion permeate
#     # Inversão de entalpia do permeado
#     # ----------------------------
#     def get_T_from_h_per(self, k, h_target, T_guess=None,
#                         T_min=100.0, T_max=800.0,
#                         tol=1e-8, maxiter=20):

#         # Retrieve permeate thermodynamic state
#         # Obtém estado termodinâmico do permeado
#         st = self.states_per[k]

#         # Initial temperature guess
#         # Estimativa inicial de temperatura
#         if T_guess is None:
#             T = 0.5 * (T_min + T_max)
#         else:
#             T = float(T_guess)

#         # Newton iteration
#         # Iteração de Newton
#         for _ in range(maxiter):

#             st.update(CoolProp.PT_INPUTS, self.PPerm[k], T)

#             h = st.hmolar()
#             dh = h - h_target

#             if abs(dh) < tol:
#                 return T

#             Cp = st.cpmolar()

#             # Newton update
#             # Atualização de Newton
#             T -= dh / Cp

#             # Bound temperature
#             # Limita temperatura
#             if T < T_min:
#                 T = T_min
#             elif T > T_max:
#                 T = T_max

#         # Fallback: bisection
#         # Método da bisseção como fallback
#         T_low, T_high = T_min, T_max

#         for _ in range(50):

#             T_mid = 0.5 * (T_low + T_high)

#             st.update(CoolProp.PT_INPUTS, self.PPerm[k], T_mid)

#             h_mid = st.hmolar()

#             if abs(h_mid - h_target) < tol:
#                 return T_mid

#             if h_mid > h_target:
#                 T_high = T_mid
#             else:
#                 T_low = T_mid

#         raise RuntimeError(
#             f"T(h) inversion failed at k={k}, h={h_target}"
#         )
