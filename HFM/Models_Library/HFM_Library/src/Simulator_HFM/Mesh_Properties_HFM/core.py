#region Title: MixPropertiesCoolPropHEOS – Core Orchestrator
# Nature: Common Calculations
# Methodology: Uses CoolProp library to calculate physical and thermal properties with EOS HEOS
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

import numpy as np
from CoolProp.CoolProp import AbstractState
from .mixins.state_updater import StateUpdaterMixin
from .mixins.phase import PhaseMixin


class MixPropertiesCoolPropHEOS(StateUpdaterMixin, PhaseMixin):
    """
    Thermodynamic and transport properties using CoolProp HEOS.

    Features
    --------
    - Accepts scalar or vector P, T, Z
    - Reuses persistent AbstractState objects
    - Safe PT update for gas phase
    - Centralized property update
    - Properties cached in self.props
    - Fugacity and fugacity coefficients
    """

    def __init__(
        self,
        components,
        P,
        T,
        Z,
        force_gas_phase=True,
        eos="PR",
        bulk_props=None,
        want_fugacity=True,
    ):

        self.components = components
        self.force_gas_phase = force_gas_phase
        self.eos = eos

        # Which properties to actually evaluate per flash. Defaults reproduce
        # the original behavior exactly (HEOS: full bulk set; PR: hmolar only;
        # fugacity always). Callers can pass a minimal set to skip the
        # (expensive, for HEOS) evaluation of unused properties.
        if bulk_props is None:
            if self.eos == "HEOS":
                bulk_props = ["hmolar", "rhomass", "rhomolar", "viscosity",
                              "conductivity", "cpmass", "cpmolar", "molar_mass"]
            else:
                bulk_props = ["hmolar"]
        self.bulk_props = list(bulk_props)
        self.want_fugacity = bool(want_fugacity)

        # ==========================================================
        # Convert inputs
        # ==========================================================
        self.P = np.atleast_1d(np.array(P, dtype=float))
        self.T = np.atleast_1d(np.array(T, dtype=float))
        self.Z = np.array(Z, dtype=float)

        # ==========================================================
        # Handle composition dimensions
        # ==========================================================
        # Single composition -> shape (1, ncomp)
        if self.Z.ndim == 1:
            self.Z = self.Z[np.newaxis, :]

        # ==========================================================
        # Number of states
        # ==========================================================
        self.NStates = max(
            len(self.P),
            len(self.T),
            len(self.Z)
        )

        # ==========================================================
        # Broadcasting
        # ==========================================================
        if len(self.P) == 1:
            self.P = np.full(self.NStates, self.P[0])
        if len(self.T) == 1:
            self.T = np.full(self.NStates, self.T[0])
        if len(self.Z) == 1:
            self.Z = np.tile(self.Z, (self.NStates, 1))

        # ==========================================================
        # Validation
        # ==========================================================
        if len(self.P) != self.NStates:
            raise ValueError("Invalid size for P")
        if len(self.T) != self.NStates:
            raise ValueError("Invalid size for T")
        if len(self.Z) != self.NStates:
            raise ValueError("Invalid size for Z")

        # ==========================================================
        # Avoid zero molar fractions
        # ==========================================================
        self.Z[self.Z < 1e-16] = 1e-16
        # Normalize compositions
        self.Z = self.Z / self.Z.sum(axis=1, keepdims=True)

        # ==========================================================
        # Create CoolProp states
        # ==========================================================
        fluid_string = "&".join(components)
        self.states = []
        for k in range(self.NStates):
            st = AbstractState(self.eos, fluid_string)
            st.set_mole_fractions(self.Z[k])
            self.states.append(st)

        # Composition already pushed to the AbstractState objects above.
        # _comp_dirty tracks whether set_mole_fractions must be re-issued
        # (only needed when Z actually changes). Crucial for HEOS, where
        # set_mole_fractions rebuilds the mixture reducing functions.
        self._comp_dirty = False

        # ==========================================================
        # Property storage
        # ==========================================================
        self.props = [None] * self.NStates
        # Properties requested but not supported by this backend
        # (e.g. conductivity/viscosity under PR).
        self.unavailable_props = set()
        # Secondary HEOS states, built ONLY if the primary backend cannot supply
        # some requested property (see _fallback_state).
        self._fb_states = None

    # ==============================================================
    # IN-PLACE CONDITION UPDATE (reuse AbstractState objects)
    # ==============================================================
    def set_conditions(self, P=None, T=None, Z=None):
        """Update P, T and/or Z in place WITHOUT reconstructing the
        AbstractState objects. Returns self so calls can be chained.

        This lets a single property object be reused across the outer,
        fugacity and energy iterations of one simulation, avoiding the
        (expensive, especially for HEOS) re-creation of NStates states.
        """
        if P is not None:
            P = np.atleast_1d(np.asarray(P, dtype=float))
            if len(P) == 1:
                P = np.full(self.NStates, P[0])
            self.P = np.array(P, dtype=float)
        if T is not None:
            T = np.atleast_1d(np.asarray(T, dtype=float))
            if len(T) == 1:
                T = np.full(self.NStates, T[0])
            self.T = np.array(T, dtype=float)
        if Z is not None:
            Z = np.asarray(Z, dtype=float)
            if Z.ndim == 1:
                Z = Z[np.newaxis, :]
            if len(Z) == 1:
                Z = np.tile(Z, (self.NStates, 1))
            Z = Z.copy()
            Z[Z < 1e-16] = 1e-16
            Z = Z / Z.sum(axis=1, keepdims=True)
            self.Z = Z
            self._comp_dirty = True
        return self
