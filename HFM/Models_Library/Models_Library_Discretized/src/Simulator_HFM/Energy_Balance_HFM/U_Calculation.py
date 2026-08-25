#region Title: UCalculation
# Nature: Global Heat Transfer Coefficient Calculation
# Methodology: Coker Calculation (1999)
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    João Victor Tupinambá          Created in Mix_Enthalpy.py
#   0.0      16-May-2025    Diego Gabriel Oliva            Class UCalculation creation
##################################################################################################################
#endregion

import numpy as np

class UCalculation:
    """
    Overall heat transfer coefficient based on:

        Coker (1999) - Appendix B - Equation B7

    Using outer area basis.

    Notes
    -----
    - Thermodynamic/transport properties are intentionally decoupled.
    - User can later plug any thermo package:
        * CoolProp
        * REFPROP
        * Peng-Robinson
        * SRK
        * custom correlations
    """

    def __init__(
        self,
        geom,
        support_porosity=0.5,
        k_polymer=0.2
    ):

        self.geom = geom

        self.support_porosity = support_porosity

        self.k_polymer = k_polymer

    # ==============================================================
    # MAIN CALCULATION
    # ==============================================================

    def calculate(
        self,
        k,
        ret_props,
        per_props,
        FPerm,
        FRet
    ):
        """
        Parameters
        ----------
        k : int
            Axial cell index

        ret_props : dict
            Retentate properties at cell k

        per_props : dict
            Permeate properties at cell k-1

        FPerm : ndarray
            Permeate molar flow array

        FRet : ndarray
            Retentate molar flow array

        Returns
        -------
        uo : float
            Overall heat transfer coefficient [W/m2/K]
        """

        geom = self.geom

        # ==========================================================
        # GEOMETRY
        # ==========================================================
        Ri = 0.5 * geom.DiamFiber_i
        Rext = 0.5 * geom.DiamFiber_o

        # ==========================================================
        # PERMEATE SIDE (BORE)
        # ==========================================================
        # Permeate properties are taken at node k-1, not k. In the
        # counter-current arrangement node k-1 is the outlet of control volume k
        # on the permeate side: the docstring above says so, the mass flow below
        # already uses FPerm[k-1], and the energy balance pairs cell k with
        # T_per[k-1]. Reading per_props[k] here was inconsistent with all three.
        kb = k - 1
        _need = ("conductivity", "viscosity", "cpmass", "molar_mass", "rhomass")
        _missing = [p for p in _need if p not in per_props[kb]["bulk"]]
        if _missing:
            raise RuntimeError(
                f"UCalculation could not obtain: {_missing}. Under a cubic EOS "
                "(PR, SRK) CoolProp cannot evaluate conductivity or viscosity, "
                "so those are normally taken from a secondary HEOS state while "
                "the thermodynamics stay on the primary backend; reaching this "
                "error means that fallback ALSO failed, i.e. HEOS could not "
                "flash this mixture at these conditions. Give 'U' a numeric "
                "value to bypass the resistance-in-series model."
            )
        k_g_b = per_props[kb]["bulk"]["conductivity"]
        mu_b = per_props[kb]["bulk"]["viscosity"]
        cp_b = per_props[kb]["bulk"]["cpmass"]
        MW_b = per_props[kb]["bulk"]["molar_mass"]
        rho_b = per_props[kb]["bulk"]["rhomass"]

        # ==========================================================
        # RETENTATE SIDE (SHELL)
        # ==========================================================
        k_g_s = ret_props[k]["bulk"]["conductivity"]
        mu_s = ret_props[k]["bulk"]["viscosity"]
        cp_s = ret_props[k]["bulk"]["cpmass"]
        MW_s = ret_props[k]["bulk"]["molar_mass"]
        rho_s = ret_props[k]["bulk"]["rhomass"]

        # ==========================================================
        # LOCAL MASS FLOWRATES
        # ==============================================================
        mdot_b = max(FPerm[k - 1], 0.0) * MW_b
        mdot_s = max(FRet[k], 0.0) * MW_s

        # ==========================================================
        # B2: BORE SIDE HTC
        # ==============================================================
        A_bore = geom.NFibers * np.pi * Ri**2
        vb = mdot_b / max(rho_b * A_bore, 1e-30)
        Re_b = rho_b * vb * (2.0 * Ri) / max(mu_b, 1e-30)
        Pr_b = cp_b * mu_b / max(k_g_b, 1e-30)

        # Graetz / Hausen, thermally developing laminar flow at constant wall
        # temperature:
        #
        #     Nu = 3.66 + 0.0668 Gz / (1 + 0.04 Gz^(2/3)) ,   Gz = (d/L) Re Pr
        #
        # Re_b and Pr_b were previously computed here and then DISCARDED: the
        # coefficient was the bare fully-developed asymptote Nu = 3.66, with no
        # entrance effect, although Supplemental S3.2 states that "Graetz and
        # Hausen correlations depending on the flow regime and thermal
        # development conditions" are used. Nu -> 3.66 as Gz -> 0, so long
        # fibers reproduce the previous value exactly; short ones no longer
        # under-predict the coefficient.
        #
        # Only the laminar branch is needed: the Reynolds trimming cut keeps the
        # bore below Re = 2300 by construction, so a turbulent correlation would
        # be unreachable.
        d_bore = 2.0 * Ri
        Gz = (d_bore / max(geom.LHidraulic, 1e-30)) * Re_b * Pr_b
        Nu_b = 3.66 + 0.0668 * Gz / (1.0 + 0.04 * Gz ** (2.0 / 3.0))
        h_b = Nu_b * k_g_b / d_bore

        # ==========================================================
        # B3: POROUS SUPPORT CONDUCTIVITY
        # ==============================================================
        f_p = 1.0 - self.support_porosity
        k_supp = (
            f_p * self.k_polymer
            + (1.0 - f_p) * k_g_b
        )

        # ==========================================================
        # B6: SHELL SIDE HTC
        # ==============================================================
        A_shell_open = (np.pi / 4.0) * (
            geom.DiamShell**2
            - geom.NFibers * geom.DiamFiber_o**2
        )

        A_shell_open = max(A_shell_open, 1e-30)

        Gs = mdot_s / A_shell_open

        D_h = (
            geom.DiamShell**2
            - geom.NFibers * geom.DiamFiber_o**2
        ) / (
            geom.DiamShell
            + geom.NFibers * geom.DiamFiber_o
        )
        Re_s = Gs * D_h / max(mu_s, 1e-30)

        Pr_s = cp_s * mu_s / max(k_g_s, 1e-30)

        h_s = (
            k_g_s / (2.0 * Rext)
        ) * (
            3.66
            + 1.077 * (
                Re_s
                * Pr_s
                * (Rext / max(D_h, 1e-30))
            )**(1.0 / 3.0)
        )

        # ==========================================================
        # B7
        # ==============================================================
        inv_uo = (
            (Rext / Ri) / max(h_b, 1e-30)
            + (Rext / max(k_supp, 1e-30))
            * np.log(Rext / Ri)
            + 1.0 / max(h_s, 1e-30)
        )

        uo = 1.0 / max(inv_uo, 1e-30)

        return uo

