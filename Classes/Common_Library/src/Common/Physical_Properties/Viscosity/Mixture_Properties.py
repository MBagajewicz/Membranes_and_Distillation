#region Title: MixtureProperties
# Nature: Common Calculations
# Methodology: Mixture viscosity via Herning & Zipperer (HZ) or CoolProp pure-component linear mixing
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0       13-May-2025     Diego Gabriel Oliva          Proposed
#   0.1       30-Jul-2026     DGO with AI Assistant        Merged Calculations_Prop_Viscosity_gas_mix.py here;
#                                                           single-file, self-contained, English comments only.
##################################################################################################################
#endregion

import numpy as np


def _mean_viscosity_hz(fractions, MU, M):
    """
    Mixture viscosity by the Herning & Zipperer correlation.

    Parameters
    ----------
    fractions : array-like, shape (n_comp,)
        Mole fractions of each component.
    MU : array-like, shape (n_comp,)
        Pure-component viscosities [Pa·s].
    M : array-like, shape (n_comp,)
        Molecular weights [kg/kmol].

    Returns
    -------
    float
        Mixture viscosity [Pa·s].

    Reference
    ---------
    https://en.wikipedia.org/wiki/Viscosity_models_for_mixtures#Classic_mixing_rules
    """
    sqrt_M = np.sqrt(M)
    soma = np.sum(fractions)
    y = fractions / soma          # safety normalisation
    num = np.sum(y * MU * sqrt_M)
    den = np.sum(y * sqrt_M)
    return num / np.maximum(den, 1e-12)


class MixtureProperties:
    """
    Gas-mixture viscosity calculator.

    This is a thin adapter that lets the HFM simulator switch between
    the fast Herning–Zipperer (HZ) correlation and a CoolProp-based
    ideal-mixture estimate without touching any calling code.

    Parameters
    ----------
    components : list[str]
        Component names, e.g. ["CO2", "CH4", "N2"].
    MU : array-like, optional
        Pure-component viscosities [Pa·s].  Required for method="HZ".
    M : array-like, optional
        Molecular weights [kg/kmol].  Required for method="HZ".
    method : {"HZ", "CoolProp"}, default "HZ"
        Calculation route.
    """

    def __init__(self, components, MU=None, M=None, method="HZ"):
        self.components = components
        self.MU = MU
        self.M = M
        self.method = method

    # ==========================================================
    # PUBLIC INTERFACE
    # ==========================================================
    def viscosity(self, mol_fractions, T=None, P=None):
        """
        Return the mixture viscosity [Pa·s].

        This is the ONLY method the HFM model should call.
        The implementation is chosen automatically via `self.method`.

        Parameters
        ----------
        mol_fractions : array-like, shape (n_comp,)
            Mole fractions of the mixture.
        T : float, optional
            Temperature [K].  Required for method="CoolProp".
        P : float, optional
            Pressure [Pa].  Required for method="CoolProp".
        """
        if self.method == "HZ":
            return self._viscosity_hz(mol_fractions)

        if self.method == "CoolProp":
            return self._viscosity_coolprop(mol_fractions, T, P)

        raise ValueError(f"Unsupported viscosity method: {self.method}")

    # ==========================================================
    # INTERNAL IMPLEMENTATIONS
    # ==========================================================
    def _viscosity_hz(self, mol_fractions):
        """
        Herning & Zipperer mixture viscosity.

        Fast, composition-only (no T/P flash needed).  This is the
        default route in the HFM simulator because the pressure-drop
        code calls viscosity inside a hot loop.
        """
        if self.MU is None or self.M is None:
            raise ValueError(
                "HZ method requires MU and M (pure viscosities and molecular weights)."
            )

        soma = np.sum(mol_fractions)
        if soma < 1e-12:
            # Degenerate mixture (zero total flow).  Return the arithmetic
            # mean of pure viscosities so the caller never receives NaN.
            return np.mean(self.MU)

        return _mean_viscosity_hz(mol_fractions, self.MU, self.M)

    def _viscosity_coolprop(self, mol_fractions, T, P):
        """
        Ideal-mixture viscosity via CoolProp pure-component flashes.

        NOTE: CoolProp gives pure viscosities; the mixing rule used here
        is simple mole-fraction weighting (approximation).
        """
        if T is None or P is None:
            raise ValueError(
                "CoolProp method requires T [K] and P [Pa] for viscosity calculations."
            )

        try:
            import CoolProp.CoolProp as CP
        except ImportError as exc:
            raise ImportError("CoolProp is not installed.") from exc

        mu_mix = 0.0
        for yi, comp in zip(mol_fractions, self.components):
            mu_i = CP.PropsSI("V", "T", T, "P", P, comp)
            mu_mix += yi * mu_i

        return mu_mix
