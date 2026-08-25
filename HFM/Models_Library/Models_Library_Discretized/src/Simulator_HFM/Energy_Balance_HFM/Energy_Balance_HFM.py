#region Title: EnergyBalanceHFM
# Nature: Residual of energy balance plus jacobian for HFM
# Methodology: Prepare scaled residual and jacobian to be used in EnergyBalanceSolverHFM Class 
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       13-May-2025    Diego Gabriel Oliva            Commented
#  0.1       08-Jun-2026    Qwen3.7 and Diego Oliva        Added dynamic energy scaling and robust Jacobian
##################################################################################################################
#endregion

import numpy as np
from scipy.sparse import lil_matrix

class EnergyBalanceHFM:
    def __init__(
        self,
        FRet,
        FPer,
        PRet,
        PPerm,
        ZRet,
        ZPerm,
        thermo_retentate,
        thermo_permeate,        
        thermo_membrane,
        T_ret_in,
        UA,
        UCalculation,
        FMemb,
        ZMemb,
        geom
    ):
        self.FRet = np.asarray(FRet, dtype=float)
        self.FPerm = np.clip(np.asarray(FPer, dtype=float), 0, None)
        self.PRet = np.asarray(PRet)
        self.PPerm = np.asarray(PPerm)
        self.ZRet = np.asarray(ZRet)
        self.ZPerm = np.asarray(ZPerm)
        
        self.thermo_retentate = thermo_retentate
        self.thermo_permeate = thermo_permeate
        self.thermo_membrane = thermo_membrane
        
        self.T_ret_in = float(T_ret_in)
        self.UA = np.asarray(UA, dtype=float) if UA is not None else None
        self.eval_UA = True if UA is None else False
        self.UCalculation = UCalculation
        
        self.NCells = len(self.FRet) - 1
        self.FMemb = np.asarray(FMemb)
        self.ZMemb = np.asarray(ZMemb)
        self.geom = geom
        
        # ==========================================================
        # ESCALADO DINÁMICO DE ENERGÍA (CLAVE PARA LA CONVERGENCIA)
        # ==========================================================
        # Estimamos el flujo de energía de entrada para usarlo como referencia.
        # Entalpía típica de gases ~ Cp * T ≈ 30 J/mol·K * 300 K ≈ 9000 J/mol.
        # Usamos 10000 J/mol como referencia segura y conservadora.
        total_molar_flow_in = np.sum(np.abs(self.FRet[0])) + np.sum(np.abs(self.FPerm[-1]))
        ref_enthalpy = 10000.0  # J/mol
        
        # El factor de escala es el flujo de energía de referencia en Watts (J/s).
        # max(..., 1.0) evita división por cero en casos extremos.
        self.scale_energy = max(total_molar_flow_in * ref_enthalpy, 1.0)

    def residual(self, X):
        NCells = self.NCells
        
        # NOTA: Se eliminó np.clip. Usar bounds en least_squares es matemáticamente superior.
        T_ret = X[0:NCells+1]
        T_per = X[NCells+1:2*(NCells+1)]

        Res_Vec = np.zeros(2*(NCells+1))
        S = self.scale_energy  # Usamos el factor dinámico

        # ----------------------------
        # Boundary condition
        # ----------------------------
        # Escalamos también la condición de contorno para mantener coherencia (O(1))
        Res_Vec[0] = (T_ret[0] - self.T_ret_in) / max(self.T_ret_in, 1.0)

        # Actualizar paquetes termodinámicos
        self.thermo_retentate.T[:] = T_ret
        self.thermo_permeate.T[:] = T_per
        self.thermo_membrane.T[:] = T_ret
        self.thermo_retentate.update_all()
        self.thermo_permeate.update_all()
        self.thermo_membrane.update_all()

        # ----------------------------
        # Precompute enthalpies
        # ----------------------------
        hRet = np.array([self.thermo_retentate.props[k]["bulk"]["hmolar"] for k in range(NCells+1)])
        hPerm = np.array([self.thermo_permeate.props[k]["bulk"]["hmolar"] for k in range(NCells+1)])
        hMemb = np.array([0.0 if k == 0 else self.thermo_membrane.props[k]["bulk"]["hmolar"] for k in range(NCells + 1)])

        if self.eval_UA:
            # AREA_SEG is per SEGMENT (length NCells) while UA is per NODE
            # (length NCells+1); multiplying them directly raised
            # "operands could not be broadcast together with shapes (20,) (21,)".
            # Map segments to nodes by repeating the last segment for the closed
            # end -- the same mapping the simulator applies when a constant
            # coefficient is supplied. This path had never run before: it was
            # unreachable while the property class withheld the transport
            # properties.
            _area_seg = np.asarray(self.geom.AREA_SEG, dtype=float)
            _area_node = np.concatenate([_area_seg, _area_seg[-1:]])
            self.UA = _area_node * np.array(
                [0.0 if k == 0 else self.UCalculation.calculate(k, self.thermo_retentate.props, self.thermo_permeate.props, self.FPerm, self.FRet)
                 for k in range(NCells+1)]
            )

        # ----------------------------
        # Interior nodes
        # ----------------------------
        for k in range(1, NCells + 1):
            conduction = self.UA[k] * (T_ret[k] - T_per[k-1])

            # Retentate energy balance
            Res_Vec[k] = (
                self.FRet[k-1] * hRet[k-1]
                - self.FRet[k] * hRet[k]
                - self.FMemb[k] * hMemb[k]
                - conduction
            ) / S

            # Permeate energy balance
            Res_Vec[NCells+k] = (
                self.FPerm[k] * hPerm[k]
                - self.FPerm[k-1] * hPerm[k-1]
                + self.FMemb[k] * hMemb[k]
                + conduction
            ) / S

        # ----------------------------
        # Closed end of the permeate channel
        # ----------------------------
        # The loops above fill 1 + NCells + NCells = 2*NCells+1 of the
        # 2*(NCells+1) entries; index 2*NCells+1 was left at zero, so
        # T_per[NCells] entered NO equation and the Jacobian had an identically
        # zero row (verified: row 41 of 42 for NCells=20). The variable is
        # genuinely decoupled -- the only place it appears is
        # FPerm[NCells]*hPerm[NCells], and FPerm is zero at the closed end -- so
        # the solver simply left it at its initial guess and that stale value was
        # reported as a computed temperature (302.15 K = T_feed - 1, untouched).
        #
        # Anchor it to the local retentate temperature: at the closed end the
        # permeate has just crossed the membrane and carries no axial flow, so
        # thermal equilibrium with the retentate is the natural limit. This
        # closes the system without affecting any other unknown.
        Res_Vec[2*NCells+1] = (T_per[NCells] - T_ret[NCells]) / max(self.T_ret_in, 1.0)
        return Res_Vec

    def jacobian(self, X):
        NCells = self.NCells
        n = 2 * (NCells + 1)
        S = self.scale_energy  # ¡MISMO factor de escala que en el residual!
        
        J = lil_matrix((n, n), dtype=float)

        T_ret = X[0:NCells+1]
        T_per = X[NCells+1:2*(NCells+1)]

        # 1. Actualizar propiedades para obtener Cp exacto
        self.thermo_retentate.T[:] = T_ret
        self.thermo_permeate.T[:] = T_per
        self.thermo_membrane.T[:] = T_ret
        self.thermo_retentate.update_all()
        self.thermo_permeate.update_all()
        self.thermo_membrane.update_all()

        # 2. Extraer Cp molar (con fallback a 30 J/mol-K por seguridad)
        Cp_ret = np.array([self.thermo_retentate.props[k]["bulk"].get("cpmolar", 30.0) for k in range(NCells+1)])
        Cp_perm = np.array([self.thermo_permeate.props[k]["bulk"].get("cpmolar", 30.0) for k in range(NCells+1)])
        Cp_memb = np.array([0.0 if k == 0 else self.thermo_membrane.props[k]["bulk"].get("cpmolar", 30.0) for k in range(NCells+1)])

        # 3. Condición de contorno (derivada de (T - T_in) / T_in)
        J[0, 0] = 1.0 / max(self.T_ret_in, 1.0)

        # 4. Nodos internos
        for k in range(1, NCells + 1):
            UA_k = self.UA[k]
            
            # --- Ecuación de energía del Retentado (fila k) ---
            J[k, k] = (-self.FRet[k] * Cp_ret[k] - self.FMemb[k] * Cp_memb[k] - UA_k) / S
            J[k, k-1] = (self.FRet[k-1] * Cp_ret[k-1]) / S
            J[k, (NCells + 1) + (k - 1)] = (UA_k) / S

            # --- Ecuación de energía del Permeado (fila NCells + k) ---
            row_p = NCells + k
            J[row_p, (NCells + 1) + k] = (self.FPerm[k] * Cp_perm[k]) / S
            J[row_p, (NCells + 1) + (k - 1)] = (-self.FPerm[k-1] * Cp_perm[k-1] - UA_k) / S
            J[row_p, k] = (self.FMemb[k] * Cp_memb[k] + UA_k) / S

        # Closed end of the permeate channel (see residual): T_per[N] - T_ret[N]
        inv = 1.0 / max(self.T_ret_in, 1.0)
        J[2 * NCells + 1, (NCells + 1) + NCells] = inv
        J[2 * NCells + 1, NCells] = -inv

        return J.tocsr()

    def build_jac_sparsity(self):
        NCells = self.NCells
        n = 2 * (NCells + 1)
        Spa_Mat = lil_matrix((n, n), dtype=int)

        for k in range(1, NCells + 1):
            row = k
            Spa_Mat[row, k] = 1
            Spa_Mat[row, k - 1] = 1
            Spa_Mat[row, (NCells + 1) + (k - 1)] = 1

            row = NCells + k
            Spa_Mat[row, (NCells + 1) + k] = 1
            Spa_Mat[row, (NCells + 1) + (k - 1)] = 1
            Spa_Mat[row, k] = 1

        Spa_Mat[0, 0] = 1
        # Closed end of the permeate channel
        Spa_Mat[2 * NCells + 1, (NCells + 1) + NCells] = 1
        Spa_Mat[2 * NCells + 1, NCells] = 1
        return Spa_Mat.tocsr()