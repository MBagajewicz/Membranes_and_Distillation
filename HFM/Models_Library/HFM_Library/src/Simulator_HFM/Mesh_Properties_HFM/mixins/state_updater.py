#region Title: MixPropertiesCoolPropHEOS – State Updater Mixin
# Nature: Thermodynamic state flash and bulk-property evaluation
# Methodology: Uses CoolProp AbstractState to perform PT flashes and compute
#              bulk / component properties with fallback to HEOS for transport.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

import numpy as np
import CoolProp.CoolProp as CoolProp
from CoolProp.CoolProp import AbstractState
from ..constants import _BULK_GETTERS


class StateUpdaterMixin:
    """
    Mixin responsible for:
      - Safe PT flashes with gas-phase enforcement
      - Fallback HEOS states for transport properties
      - Per-state property evaluation and caching
    """

    # ==============================================================
    # SAFE UPDATE
    # ==============================================================
    def safe_update_gas(self, st, P, T):
        """
        Safe PT update with gas-phase enforcement.
        """

        # Clamp temperature
        T = np.clip(T, 150.0, 1000.0)

        # Force gas phase
        if self.force_gas_phase:
            st.specify_phase(CoolProp.iphase_gas)

        attempts = [
            (P, T),
            (P, T + 1e-8),
            (P, T + 1e-5),
            (P * 0.999, T),
        ]

        last_error = None

        for P_try, T_try in attempts:

            try:

                st.update(
                    CoolProp.PT_INPUTS,
                    P_try,
                    T_try
                )

                return

            except Exception as e:

                last_error = e

        raise RuntimeError(
            f"CoolProp failed at P={P}, T={T}, and Z={st.get_mole_fractions()}"
        ) from last_error

    # ==============================================================
    # FALLBACK HEOS STATE (lazy, per node)
    # ==============================================================
    def _fallback_state(self, k):
        """HEOS state for node k, used only for properties the primary backend
        cannot evaluate.

        CoolProp's cubic backends (PR, SRK) raise "type not set" for the
        TRANSPORT properties -- conductivity and viscosity -- while supplying
        every thermodynamic one. Rather than forcing the whole calculation onto
        HEOS, each property is taken from the most appropriate source: PR keeps
        the thermodynamics (fugacity, enthalpy, Cp, density) that the model is
        specified with, and only the transport properties fall back to HEOS.
        With eos="HEOS" the primary backend answers everything and these states
        are never created.

        The states are built lazily and reused, since this path costs one extra
        flash per node and is only reached when the overall heat-transfer
        coefficient is being computed.
        """
        if self._fb_states is None:
            fluid_string = "&".join(self.components)
            self._fb_states = [AbstractState("HEOS", fluid_string)
                               for _ in range(self.NStates)]
        st = self._fb_states[k]
        st.set_mole_fractions(self.Z[k])
        self.safe_update_gas(st, self.P[k], self.T[k])
        return st

    # ==============================================================
    # UPDATE SINGLE STATE
    # ==============================================================
    def update_state(self, k):
        """
        Update thermodynamic state k and store properties.
        """

        st = self.states[k]

        P = self.P[k]
        T = self.T[k]

        # ==========================================================
        # Update composition
        # ==========================================================
        st.set_mole_fractions(self.Z[k])

        # ==========================================================
        # Thermodynamic update
        # ==========================================================
        self.safe_update_gas(st, P, T)

        # if k == 0:
        #     print("------------------------------------------------")
        #     print("OBJECT")
        #     print("id =", id(st))
        #     print("P input =", P)
        #     print("T input =", T)
        #     print("P CP =", st.p())
        #     print("T CP =", st.T())
        #     print("Z =", st.get_mole_fractions())
        #     for i, comp in enumerate(self.components):
        #         print(
        #             comp,
        #             st.fugacity(i),
        #             st.fugacity_coefficient(i)
        #         )
        #     print("EOS =", self.eos)

        # ==========================================================
        # Component properties
        # ==========================================================
        ncomp = len(self.components)
        fugacity = np.zeros(ncomp)
        fugacity_coefficient = np.zeros(ncomp)
        for i in range(ncomp):
            fugacity[i] = st.fugacity(i)
            fugacity_coefficient[i] = st.fugacity_coefficient(i)

        # ==========================================================
        # Store properties
        # ==========================================================
        # Honour self.bulk_props via _BULK_GETTERS.
        #
        # This block used to hardcode two dictionaries, one per EOS, with every
        # entry except hmolar COMMENTED OUT in the PR branch -- so `bulk_props`,
        # which the constructor accepts and stores, was dead configuration and
        # PR silently produced only the enthalpy. Two consequences, both real:
        # UCalculation raised KeyError('conductivity') the moment it was
        # activated, and the energy Jacobian's `.get("cpmolar", 30.0)` always hit
        # its default, using a hardcoded Cp while claiming an exact one.
        #
        # Note PR genuinely cannot supply the TRANSPORT properties: CoolProp
        # raises "type not set" for conductivity and viscosity on the cubic
        # backends. Those are recorded as unavailable rather than silently
        # skipped, so a consumer can report it clearly instead of failing deep in
        # a solver with a KeyError.
        bulk = {}
        _need_fb = []
        for _name in self.bulk_props:
            _getter = _BULK_GETTERS.get(_name)
            if _getter is None:
                continue
            try:
                bulk[_name] = _getter(st)
            except Exception:
                _need_fb.append(_name)

        if _need_fb:
            # Whatever the primary backend could not give, take from HEOS.
            try:
                _fb = self._fallback_state(k)
            except Exception:
                _fb = None
            for _name in _need_fb:
                if _fb is None:
                    self.unavailable_props.add(_name)
                    continue
                try:
                    bulk[_name] = _BULK_GETTERS[_name](_fb)
                except Exception:
                    self.unavailable_props.add(_name)

        comp = {"fugacity": fugacity}
        if self.want_fugacity:
            comp["fugacity_coefficient"] = fugacity_coefficient

        self.props[k] = {"bulk": bulk, "components": comp}

    # ==============================================================
    # UPDATE ALL STATES
    # ==============================================================
    def update_all(self):
        """
        Update all thermodynamic states.
        """
        for k in range(self.NStates):
            self.update_state(k)

    # ==============================================================
    # GET PROPERTIES
    # ==============================================================
    def get_properties(self, k):
        """
        Return stored properties.
        Requires update_all() beforehand.
        """
        return self.props[k]
