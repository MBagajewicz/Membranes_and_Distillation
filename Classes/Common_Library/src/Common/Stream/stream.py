"""
Stream - Thermodynamic state representation for process simulation.

This module provides the ``Stream`` class, which encapsulates a
thermodynamic state (composition, pressure, temperature, flow) and
exposes derived properties (density, enthalpy, viscosity, etc.)
through a unified interface backed by CoolProp.

Design principles (non-negotiable):
    1. Stream represents a thermodynamic state, not equipment.
    2. The user supplies ONLY independent information.
    3. Properties are read-only consequences of the state.
    4. Every state mutation triggers an automatic internal update.
    5. The implementation is backend-agnostic; the public API never
       exposes CoolProp internals.
"""
import warnings
import numpy as np

import copy
from typing import Any, Dict, List, Optional

import CoolProp
import CoolProp.CoolProp as CP

from .exceptions import BackendError, CompositionError, FlowSpecificationError
from .thermo_backend import ThermoBackend


# ----------------------------------------------------------------------
# Fluid aliases: user-friendly names -> CoolProp canonical names
# ----------------------------------------------------------------------
_FLUID_ALIASES: Dict[str, str] = {
    # Hydrocarbons
    "Propane": "n-Propane",
    "Butane": "n-Butane",
    "Isobutane": "IsoButane",
    "i-Butane": "IsoButane",
    "iButane": "IsoButane",
    "Pentane": "n-Pentane",
    "Hexane": "n-Hexane",
    "Heptane": "n-Heptane",
    "Octane": "n-Octane",
    "Nonane": "n-Nonane",
    "Decane": "n-Decane",
    # Inorganics / common names
    "CO2": "CarbonDioxide",
    "CO": "CarbonMonoxide",
    "N2": "Nitrogen",
    "O2": "Oxygen",
    "H2": "Hydrogen",
    "H2O": "Water",
    "NH3": "Ammonia",
    "Ar": "Argon",
    "He": "Helium",
    "CH4": "Methane",
    "C2H6": "Ethane",
    "C3H8": "n-Propane",
    "C4H10": "n-Butane",
}


class Stream:
    """
    Represents a single thermodynamic material stream.

    The user supplies only independent information:
        - composition : dict of {CoolProp fluid name: mole fraction}
        - P           : pressure [Pa]
        - T           : temperature [K]
        - exactly one flow specification:
            * mass_flow  [kg/s], or
            * molar_flow [mol/s]
        - backend     : ThermoBackend enum member

    Everything else is derived automatically. There are no public
    ``calculate()`` or ``update_properties()`` methods; every time the
    state is modified the internal cache is refreshed and all properties
    remain consistent without requiring an explicit user call.

    Properties such as ``viscosity``, ``cp_mass``, ``enthalpy_mass``,
    etc. are read-only. They have no setters because they are
    consequences of the state, not inputs to it.

    The architecture is backend-agnostic. Today it delegates to CoolProp.
    Tomorrow it could delegate to REFPROP, GERG-2008, or a custom EOS
    without changing the public interface. Downstream equipment models
    (heat exchangers, membrane modules, etc.) simply read:

        stream.cp_mass
        stream.viscosity
        stream.density_mass

    and remain unaware of the implementation details.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(
        self,
        composition: Dict[str, float],
        P: float,
        T: float,
        mass_flow: Optional[float] = None,
        molar_flow: Optional[float] = None,
        backend: ThermoBackend = ThermoBackend.HEOS,
    ):
        """
        Create a new Stream.

        Parameters
        ----------
        composition : dict
            Mapping of CoolProp fluid names to mole fractions.
            Example: {"Methane": 0.85, "Ethane": 0.15}
            Fractions are normalised automatically if they do not sum to 1.
            Common aliases (e.g. "CO2", "N2", "Propane") are resolved
            automatically.
        P : float
            Pressure [Pa].
        T : float
            Temperature [K].
        mass_flow : float, optional
            Mass flow rate [kg/s]. Exactly one of ``mass_flow`` or
            ``molar_flow`` must be provided.
        molar_flow : float, optional
            Molar flow rate [mol/s]. Exactly one of ``mass_flow`` or
            ``molar_flow`` must be provided.
        backend : ThermoBackend, optional
            CoolProp backend to use. Defaults to ``ThermoBackend.HEOS``.
            If the mixture is not supported by the backend (missing binary
            pairs), Stream falls back to pure-component calculations with
            ideal mixing rules and emits a warning.
        """
        # Store the backend first because later steps need it.
        self._backend: ThermoBackend = backend

        # Validate, resolve aliases, and store composition.
        self._composition: Dict[str, float] = self._validate_composition(composition)
        self._components: List[str] = list(self._composition.keys())
        self._mole_fractions: List[float] = list(self._composition.values())

        # Store independent thermodynamic variables.
        self._P: float = float(P)
        self._T: float = float(T)

        # ------------------------------------------------------------------
        # 1. Try to build the mixture AbstractState.
        #    If CoolProp lacks a binary pair, fall back to pure-component mode.
        # ------------------------------------------------------------------
        self._AS: Optional[Any] = None
        self._mixture_supported: bool = False
        try:
            self._create_abstract_state()
            self._mixture_supported = True
        except (ValueError, BackendError) as exc:
            err_msg = str(exc)
            if "binary pair" in err_msg.lower() or "could not match" in err_msg.lower():
                warnings.warn(
                    "\n[Stream] CoolProp " + self._backend.name + " does not support the "
                    "binary interaction matrix for this " + str(len(self._components)) + "-component "
                    "mixture. \n"
                    "  -> Falling back to PURE-COMPONENT calculations only.\n"
                    "  -> Mixture properties (density, enthalpy, cp, etc.) will be "
                    "estimated via IDEAL MIXING rules.\n"
                    "  -> For exact mixture EOS, use ThermoBackend.REFPROP or reduce "
                    "the component list.\n"
                    "  Missing pair details: " + err_msg + "\n",
                    UserWarning,
                    stacklevel=2,
                )
                self._AS = None
                self._mixture_supported = False
            else:
                raise

        # ------------------------------------------------------------------
        # 2. Pure-component properties (always needed, even in fallback mode)
        # ------------------------------------------------------------------
        self._component_molar_masses = np.empty(len(self._components))
        self._component_viscosities = np.empty(len(self._components))
        for i, comp in enumerate(self._components):
            as_pure = CP.AbstractState(self._backend.value, comp)
            as_pure.update(CoolProp.PT_INPUTS, self._P, self._T)
            self._component_molar_masses[i] = as_pure.molar_mass()
            try:
                self._component_viscosities[i] = as_pure.keyed_output(CoolProp.iviscosity)
            except ValueError:
                # Some fluids (e.g. CarbonylSulfide, H2S) lack transport models in CoolProp HEOS.
                # Mark as NaN; downstream correlations can use a fallback or skip the component.
                self._component_viscosities[i] = np.nan

        # Mixture molar mass is always well-defined (mole-fraction weighted)
        self._molar_mass: float = float(
            np.dot(self._mole_fractions, self._component_molar_masses)
        )

        # Validate and store flow. Exactly one specification is required.
        self._initialize_flow(mass_flow, molar_flow)

        # Pre-compute all thermodynamic properties and cache them.
        self._update_cache()

        # Ports for flowsheet
        self.producer = None   # Port that produces this stream (OUTPUT port of upstream unit)
        self.consumer = None   # Port that consumes this stream (INPUT port of downstream unit)        

    # ------------------------------------------------------------------
    # Private helpers -- composition
    # ------------------------------------------------------------------
    def _validate_composition(self, composition: Dict[str, float]) -> Dict[str, float]:
        """
        Ensure the composition dictionary is valid and resolve aliases.

        Returns the resolved composition dict with CoolProp canonical names.
        """
        if not composition:
            raise CompositionError("Composition dictionary cannot be empty.")

        available = set(CP.get_global_param_string("FluidsList").split(","))

        resolved: Dict[str, float] = {}
        for name, frac in composition.items():
            # 1. Exact match
            if name in available:
                canonical = name
            # 2. Alias table
            elif name in _FLUID_ALIASES:
                canonical = _FLUID_ALIASES[name]
                if canonical not in available:
                    raise CompositionError(
                        "Alias '" + name + "' maps to '" + canonical + "', but that fluid "
                        "is not available in CoolProp."
                    )
            # 3. Case-insensitive fallback
            else:
                lower = name.lower()
                canonical = None
                for fluid in available:
                    if fluid.lower() == lower:
                        canonical = fluid
                        break
                if canonical is None:
                    raise CompositionError(
                        "Component '" + name + "' is not available in CoolProp and "
                        "has no registered alias. Call Stream.list_fluids() "
                        "to see the full catalogue."
                    )

            # Accumulate fractions if two aliases resolve to the same canonical
            resolved[canonical] = resolved.get(canonical, 0.0) + float(frac)

        return self._normalise_composition(resolved)

    def _normalise_composition(self, composition: Dict[str, float]) -> Dict[str, float]:
        """
        Normalise mole fractions so they sum exactly to 1.0.

        This is idempotent: if the fractions already sum to 1 (within
        tolerance) the dictionary is returned unchanged.
        """
        total = sum(composition.values())
        if abs(total - 1.0) > 1e-9:
            return {k: v / total for k, v in composition.items()}
        return composition

    # ------------------------------------------------------------------
    # Private helpers -- AbstractState
    # ------------------------------------------------------------------
    def _create_abstract_state(self) -> None:
        """
        Instantiate and configure the CoolProp AbstractState.

        The fluid string for mixtures uses ampersand separators.
        After creation the mole fractions are injected and the state
        is evaluated at the current P and T.
        """
        fluid_string = "&".join(self._components)
        try:
            self._AS = CP.AbstractState(self._backend.value, fluid_string)
        except ValueError as exc:
            raise BackendError(
                "Failed to create AbstractState with backend=" + self._backend.name +
                " and fluids='" + fluid_string + "'. Is the backend installed? "
                "Original error: " + str(exc)
            ) from exc

        self._AS.set_mole_fractions(self._mole_fractions)
        self._update_thermo_state()

    def _update_thermo_state(self) -> None:
        """
        Refresh the CoolProp AbstractState with the current P and T.

        This is the *only* place where the low-level thermodynamic state
        is updated. Every public setter that changes P or T calls this
        method, which guarantees that all derived properties remain
        consistent without requiring an explicit user call.
        """
        if self._AS is not None:
            self._AS.update(CoolProp.PT_INPUTS, self._P, self._T)

    # ------------------------------------------------------------------
    # Private helpers -- flow
    # ------------------------------------------------------------------
    def _initialize_flow(
        self,
        mass_flow: Optional[float],
        molar_flow: Optional[float],
    ) -> None:
        """
        Validate flow specification and derive the dependent flow.

        Exactly one of ``mass_flow`` or ``molar_flow`` must be given.
        The provided value becomes the *independent* flow; the other is
        derived from it using the mixture molar mass.
        """
        if mass_flow is not None and molar_flow is not None:
            raise FlowSpecificationError(
                "Only one flow specification is allowed. Provide either "
                "mass_flow or molar_flow, not both."
            )
        if mass_flow is None and molar_flow is None:
            raise FlowSpecificationError(
                "A flow specification is required. Provide either mass_flow "
                "[kg/s] or molar_flow [mol/s]."
            )

        if molar_flow is not None:
            self._molar_flow = float(molar_flow)
            self._mass_flow = self._molar_flow * self._molar_mass
            self._independent_flow = "molar"
        else:
            self._mass_flow = float(mass_flow)
            self._molar_flow = self._mass_flow / self._molar_mass
            self._independent_flow = "mass"

    def _recalculate_dependent_flow(self) -> None:
        """
        Recompute the dependent flow after a state change that affects
        the mixture molar mass (e.g. composition change).

        The independent flow (the one originally specified by the user)
        is kept constant.
        """
        if self._independent_flow == "mass":
            self._molar_flow = self._mass_flow / self._molar_mass
        else:
            self._mass_flow = self._molar_flow * self._molar_mass

    # ------------------------------------------------------------------
    # Private helpers -- property cache
    # ------------------------------------------------------------------
    def _update_cache(self) -> None:
        """
        Evaluate every supported property from CoolProp and store it.

        If the full mixture EOS is available, uses it directly.
        Otherwise falls back to ideal mixing rules from pure-component data.
        """
        if self._mixture_supported and self._AS is not None:
            try:
                as_ = self._AS
                self._cache = {
                    "viscosity":          as_.keyed_output(CoolProp.iviscosity),
                    "conductivity":       as_.keyed_output(CoolProp.iconductivity),
                    "prandtl":            as_.keyed_output(CoolProp.iPrandtl),
                    "speed_of_sound":     as_.keyed_output(CoolProp.ispeed_sound),
                    "density_mass":       as_.keyed_output(CoolProp.iDmass),
                    "density_molar":      as_.keyed_output(CoolProp.iDmolar),
                    "enthalpy_mass":      as_.keyed_output(CoolProp.iHmass),
                    "enthalpy_molar":     as_.keyed_output(CoolProp.iHmolar),
                    "entropy_mass":       as_.keyed_output(CoolProp.iSmass),
                    "entropy_molar":      as_.keyed_output(CoolProp.iSmolar),
                    "internal_energy_mass":  as_.keyed_output(CoolProp.iUmass),
                    "internal_energy_molar": as_.keyed_output(CoolProp.iUmolar),
                    "gibbs_mass":         as_.keyed_output(CoolProp.iGmass),
                    "gibbs_molar":        as_.keyed_output(CoolProp.iGmolar),
                    "cp_mass":            as_.keyed_output(CoolProp.iCpmass),
                    "cp_molar":           as_.keyed_output(CoolProp.iCpmolar),
                    "cv_mass":            as_.keyed_output(CoolProp.iCvmass),
                    "cv_molar":           as_.keyed_output(CoolProp.iCvmolar),
                }
            except ValueError:
                # CoolProp lacks transport models for this mixture → fallback
                self._cache = self._ideal_mixture_cache()
        else:
            self._cache = self._ideal_mixture_cache()

    def _ideal_mixture_cache(self) -> Dict[str, float]:
        """
        Compute mixture properties from pure-component states when the full
        mixture EOS is unavailable (e.g. missing binary pairs in HEOS).

        Uses ideal mixing rules:
          - Molar properties: mole-fraction weighted average.
          - Specific (mass) properties: mass-fraction weighted average.
        """
        x = np.array(self._mole_fractions)
        M_i = self._component_molar_masses
        M_mix = self._molar_mass
        w = x * M_i / M_mix  # mass fractions

        # Property keys and their CoolProp constants
        _keys = {
            "iHmolar": CoolProp.iHmolar, "iHmass": CoolProp.iHmass,
            "iSmolar": CoolProp.iSmolar,
            "iCpmolar": CoolProp.iCpmolar, "iCpmass": CoolProp.iCpmass,
            "iCvmolar": CoolProp.iCvmolar, "iCvmass": CoolProp.iCvmass,
            "iUmolar": CoolProp.iUmolar, "iUmass": CoolProp.iUmass,
            "iGmolar": CoolProp.iGmolar, "iGmass": CoolProp.iGmass,
            "iDmass": CoolProp.iDmass, "iDmolar": CoolProp.iDmolar,
        }

        pure = {k: np.empty(len(self._components)) for k in _keys}

        for i, comp in enumerate(self._components):
            s = CP.AbstractState(self._backend.value, comp)
            s.update(CoolProp.PT_INPUTS, self._P, self._T)
            for k, cp_key in _keys.items():
                pure[k][i] = s.keyed_output(cp_key)

        return {
            "viscosity":          float(np.nansum(x * self._component_viscosities) / np.nansum(x * np.isfinite(self._component_viscosities))) if np.any(np.isfinite(self._component_viscosities)) else float("nan"),
            "conductivity":       float("nan"),
            "surface_tension":    float("nan"),
            "prandtl":            float("nan"),
            "speed_of_sound":     float("nan"),
            "density_mass":       float(np.dot(w, pure["iDmass"])),
            "density_molar":      float(np.dot(x, pure["iDmolar"])),
            "enthalpy_mass":      float(np.dot(w, pure["iHmass"])),
            "enthalpy_molar":     float(np.dot(x, pure["iHmolar"])),
            "entropy_mass":       float(np.dot(w, pure["iSmolar"])),
            "entropy_molar":      float(np.dot(x, pure["iSmolar"])),
            "internal_energy_mass":  float(np.dot(w, pure["iUmass"])),
            "internal_energy_molar": float(np.dot(x, pure["iUmolar"])),
            "gibbs_mass":         float(np.dot(w, pure["iGmass"])),
            "gibbs_molar":        float(np.dot(x, pure["iGmolar"])),
            "cp_mass":            float(np.dot(w, pure["iCpmass"])),
            "cp_molar":           float(np.dot(x, pure["iCpmolar"])),
            "cv_mass":            float(np.dot(w, pure["iCvmass"])),
            "cv_molar":           float(np.dot(x, pure["iCvmolar"])),
        }

    # ------------------------------------------------------------------
    # State modifiers (the only public interface that changes the state)
    # ------------------------------------------------------------------
    def set_PT(self, P: float, T: float) -> None:
        """Update pressure and temperature simultaneously."""
        self._P = float(P)
        self._T = float(T)
        self._update_thermo_state()
        self._update_cache()

    def set_P(self, P: float) -> None:
        """Update pressure while keeping temperature constant."""
        self.set_PT(P, self._T)

    def set_T(self, T: float) -> None:
        """Update temperature while keeping pressure constant."""
        self.set_PT(self._P, T)

    def set_mass_flow(self, mass_flow: float) -> None:
        """
        Set the mass flow rate [kg/s] and derive the molar flow.

        This becomes the new independent flow specification.
        """
        self._mass_flow = float(mass_flow)
        self._molar_flow = self._mass_flow / self._molar_mass
        self._independent_flow = "mass"

    def set_molar_flow(self, molar_flow: float) -> None:
        """
        Set the molar flow rate [mol/s] and derive the mass flow.

        This becomes the new independent flow specification.
        """
        self._molar_flow = float(molar_flow)
        self._mass_flow = self._molar_flow * self._molar_mass
        self._independent_flow = "molar"

    def set_composition(self, composition: Dict[str, float]) -> None:
        """
        Replace the mixture composition and re-derive all properties.
        ...
        """
        self._composition = self._validate_composition(composition)
        self._components = list(self._composition.keys())
        self._mole_fractions = list(self._composition.values())

        # Rebuild the AbstractState because the fluid list changed.
        try:
            self._create_abstract_state()
            self._mixture_supported = True
        except (ValueError, BackendError) as exc:
            err_msg = str(exc)
            if "binary pair" in err_msg.lower() or "could not match" in err_msg.lower():
                warnings.warn(
                    "\n[Stream] CoolProp " + self._backend.name + " does not support the "
                    "binary interaction matrix for this " + str(len(self._components)) + "-component "
                    "mixture. \n"
                    "  -> Falling back to PURE-COMPONENT calculations only.\n"
                    "  -> Mixture properties (density, enthalpy, cp, etc.) will be "
                    "estimated via IDEAL MIXING rules.\n"
                    "  -> For exact mixture EOS, use ThermoBackend.REFPROP or reduce "
                    "the component list.\n"
                    "  Missing pair details: " + err_msg + "\n",
                    UserWarning,
                    stacklevel=2,
                )
                self._AS = None
                self._mixture_supported = False
            else:
                raise

        # Update molar mass and recompute flows.
        self._molar_mass = self._AS.molar_mass() if self._AS is not None else float(
            np.dot(self._mole_fractions, self._component_molar_masses)
        )
        self._recalculate_dependent_flow()

        # Refresh property cache.
        self._update_cache()

    def update(self, **kwargs: Any) -> None:
        """
        Batch-update multiple state variables in a single call.

        Accepted keywords: P, T, mass_flow, molar_flow, composition.
        The internal order of application guarantees consistency.

        Example
        -------
        stream.update(P=2e5, T=350, composition={"Water": 1.0})
        """
        # Extract values, defaulting to current state.
        new_P = kwargs.get("P", self._P)
        new_T = kwargs.get("T", self._T)
        new_mass = kwargs.get("mass_flow", None)
        new_molar = kwargs.get("molar_flow", None)
        new_comp = kwargs.get("composition", None)

        # Composition changes require a full rebuild, so handle it first.
        if new_comp is not None:
            self._composition = self._validate_composition(new_comp)
            self._components = list(self._composition.keys())
            self._mole_fractions = list(self._composition.values())

            # ------------------------------------------------------------------
            # FALLBACK: same logic as __init__ — if CoolProp lacks binary pairs,
            # fall back to pure-component mode instead of crashing.
            # ------------------------------------------------------------------
            try:
                self._create_abstract_state()
                self._mixture_supported = True
            except (ValueError, BackendError) as exc:
                err_msg = str(exc)
                if "binary pair" in err_msg.lower() or "could not match" in err_msg.lower():
                    warnings.warn(
                        "\n[Stream] CoolProp " + self._backend.name + " does not support the "
                        "binary interaction matrix for this " + str(len(self._components)) + "-component "
                        "mixture. \n"
                        "  -> Falling back to PURE-COMPONENT calculations only.\n"
                        "  -> Mixture properties (density, enthalpy, cp, etc.) will be "
                        "estimated via IDEAL MIXING rules.\n"
                        "  -> For exact mixture EOS, use ThermoBackend.REFPROP or reduce "
                        "the component list.\n"
                        "  Missing pair details: " + err_msg + "\n",
                        UserWarning,
                        stacklevel=2,
                    )
                    self._AS = None
                    self._mixture_supported = False
                else:
                    raise

            self._molar_mass = self._AS.molar_mass() if self._AS is not None else float(
                np.dot(self._mole_fractions, self._component_molar_masses)
            )
            self._recalculate_dependent_flow()

        # Update P and T.
        self._P = float(new_P)
        self._T = float(new_T)
        self._update_thermo_state()

        # Update flows if given (override the preserved values above).
        if new_mass is not None and new_molar is not None:
            raise FlowSpecificationError(
                "Provide only one of mass_flow or molar_flow."
            )
        if new_mass is not None:
            self.set_mass_flow(new_mass)
        if new_molar is not None:
            self.set_molar_flow(new_molar)

        # Refresh the cache once at the end.
        self._update_cache()

    # ------------------------------------------------------------------
    # Serialization (foundation for JSON, pandas, databases)
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the stream state to a plain dictionary.

        The resulting dict is JSON-serializable and contains everything
        needed to reconstruct the stream via ``from_dict``.
        """
        return {
            "composition": self._composition,
            "P": self._P,
            "T": self._T,
            "mass_flow": self._mass_flow,
            "molar_flow": self._molar_flow,
            "backend": self._backend.name,
            "independent_flow": self._independent_flow,  # "mass" | "molar"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stream":
        """
        Reconstruct a Stream from a dictionary (e.g. produced by ``to_dict``).

        Parameters
        ----------
        data : dict
            Dictionary with keys matching the ``to_dict`` output.

        Returns
        -------
        Stream
        """
        data = copy.deepcopy(data)
        backend = ThermoBackend[data.pop("backend")]
        indep = data.pop("independent_flow")  # "mass" or "molar"

        # Let the flow necessary for the constructor
        if indep == "mass":
            data.pop("molar_flow", None)
            flow_kw = {"mass_flow": data.pop("mass_flow")}
        else:
            data.pop("mass_flow", None)
            flow_kw = {"molar_flow": data.pop("molar_flow")}

        return cls(
            composition=data.pop("composition"),
            P=data.pop("P"),
            T=data.pop("T"),
            backend=backend,
            **flow_kw,
        )

    # ------------------------------------------------------------------
    # Cloning
    # ------------------------------------------------------------------
    def clone(self) -> "Stream":
        """
        Create an independent deep copy of the current stream.

        This is a common operation in process simulation: an inlet stream
        is cloned to produce outlet streams that are then modified
        (e.g. retentate and permeate in membrane separation).

        The cloned stream has its own AbstractState instance; modifying
        the clone does not affect the original.

        Returns
        -------
        Stream
            A new Stream object with identical state.
        """
        # Determine which flow was the independent specification so the
        # clone can reconstruct itself correctly.
        if self._independent_flow == "mass":
            flow_kw = {"mass_flow": self._mass_flow}
        else:
            flow_kw = {"molar_flow": self._molar_flow}

        new_stream = Stream(
            composition=copy.deepcopy(self._composition),
            P=self._P,
            T=self._T,
            backend=self._backend,
            **flow_kw,
        )
        # Copy the independent-flow flag so that future composition changes
        # on the clone behave identically to the original.
        new_stream._independent_flow = self._independent_flow
        return new_stream

    # ------------------------------------------------------------------
    # Read-only thermodynamic properties (cached)
    # ------------------------------------------------------------------
    @property
    def viscosity(self) -> float:
        """Dynamic viscosity [Pa*s]."""
        return self._cache["viscosity"]

    @property
    def conductivity(self) -> float:
        """Thermal conductivity [W/m*K]."""
        return self._cache["conductivity"]

    @property
    def surface_tension(self) -> float:
        """Surface tension [N/m]."""
        return self._cache["surface_tension"]

    @property
    def prandtl(self) -> float:
        """Prandtl number [-]."""
        return self._cache["prandtl"]

    @property
    def speed_of_sound(self) -> float:
        """Speed of sound [m/s]."""
        return self._cache["speed_of_sound"]

    @property
    def density_mass(self) -> float:
        """Mass density [kg/m3]."""
        return self._cache["density_mass"]

    @property
    def density_molar(self) -> float:
        """Molar density [mol/m3]."""
        return self._cache["density_molar"]

    @property
    def enthalpy_mass(self) -> float:
        """Specific enthalpy [J/kg]."""
        return self._cache["enthalpy_mass"]

    @property
    def enthalpy_molar(self) -> float:
        """Molar enthalpy [J/mol]."""
        return self._cache["enthalpy_molar"]

    @property
    def entropy_mass(self) -> float:
        """Specific entropy [J/kg*K]."""
        return self._cache["entropy_mass"]

    @property
    def entropy_molar(self) -> float:
        """Molar entropy [J/mol*K]."""
        return self._cache["entropy_molar"]

    @property
    def internal_energy_mass(self) -> float:
        """Specific internal energy [J/kg]."""
        return self._cache["internal_energy_mass"]

    @property
    def internal_energy_molar(self) -> float:
        """Molar internal energy [J/mol]."""
        return self._cache["internal_energy_molar"]

    @property
    def gibbs_mass(self) -> float:
        """Specific Gibbs free energy [J/kg]."""
        return self._cache["gibbs_mass"]

    @property
    def gibbs_molar(self) -> float:
        """Molar Gibbs free energy [J/mol]."""
        return self._cache["gibbs_molar"]

    @property
    def cp_mass(self) -> float:
        """Specific heat capacity at constant pressure [J/kg*K]."""
        return self._cache["cp_mass"]

    @property
    def cp_molar(self) -> float:
        """Molar heat capacity at constant pressure [J/mol*K]."""
        return self._cache["cp_molar"]

    @property
    def cv_mass(self) -> float:
        """Specific heat capacity at constant volume [J/kg*K]."""
        return self._cache["cv_mass"]

    @property
    def cv_molar(self) -> float:
        """Molar heat capacity at constant volume [J/mol*K]."""
        return self._cache["cv_molar"]

    @property
    def molar_mass(self) -> float:
        """Mixture molar mass [kg/mol]."""
        return self._molar_mass

    @property
    def component_molar_masses(self) -> np.ndarray:
        """Molar masses of the pure components [kg/mol]."""
        return self._component_molar_masses.copy()

    @property
    def component_viscosities(self) -> np.ndarray:
        """Dynamic viscosities of the pure components at stream T/P [Pa*s]."""
        return self._component_viscosities.copy()

    # ------------------------------------------------------------------
    # Extensive (flow-based) properties
    # ------------------------------------------------------------------
    @property
    def total_enthalpy_mass(self) -> float:
        """Total enthalpy flow rate [W] based on mass flow."""
        return self._mass_flow * self.enthalpy_mass

    @property
    def total_enthalpy_molar(self) -> float:
        """Total enthalpy flow rate [W] based on molar flow."""
        return self._molar_flow * self.enthalpy_molar

    @property
    def total_cp_mass(self) -> float:
        """Total heat capacity flow rate [W/K] based on mass flow."""
        return self._mass_flow * self.cp_mass

    @property
    def total_cp_molar(self) -> float:
        """Total heat capacity flow rate [W/K] based on molar flow."""
        return self._molar_flow * self.cp_molar

    # ------------------------------------------------------------------
    # Independent state accessors (read-only)
    # ------------------------------------------------------------------
    @property
    def P(self) -> float:
        """Pressure [Pa]."""
        return self._P

    @property
    def T(self) -> float:
        """Temperature [K]."""
        return self._T

    @property
    def mass_flow(self) -> float:
        """Mass flow rate [kg/s]."""
        return self._mass_flow

    @property
    def molar_flow(self) -> float:
        """Molar flow rate [mol/s]."""
        return self._molar_flow

    @property
    def composition(self) -> Dict[str, float]:
        """Mole-fraction composition dictionary {name: fraction}."""
        return copy.deepcopy(self._composition)

    @property
    def components(self) -> List[str]:
        """List of component names."""
        return list(self._components)

    @property
    def mole_fractions(self) -> List[float]:
        """List of mole fractions in the same order as ``components``."""
        return list(self._mole_fractions)

    @property
    def backend(self) -> ThermoBackend:
        """CoolProp backend used by this stream."""
        return self._backend

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def summary(self) -> str:
        """
        Return a human-readable summary of the stream state.

        Useful for quick debugging or logging.
        """
        lines = [
            "=" * 60,
            " STREAM SUMMARY",
            "=" * 60,
            "Backend        : " + self._backend.name,
            "Mixture EOS    : " + ("CoolProp HEOS" if self._mixture_supported else "IDEAL MIXING (fallback)"),
            "P              : " + f"{self._P:,.2f}" + " Pa  (" + f"{self._P/1e5:.3f}" + " bar)",
            "T              : " + f"{self._T:.2f}" + " K  (" + f"{self._T - 273.15:.2f}" + " C)",
            "Mass flow      : " + f"{self._mass_flow:,.4g}" + " kg/s",
            "Molar flow     : " + f"{self._molar_flow:,.4g}" + " mol/s",
            "Molar mass     : " + f"{self._molar_mass*1e3:.4f}" + " g/mol",
            "-" * 60,
            "Dens. mass     : " + f"{self.density_mass:,.4f}" + " kg/m3",
            "Dens. molar    : " + f"{self.density_molar:,.4f}" + " mol/m3",
            "Enthalpy mass  : " + f"{self.enthalpy_mass/1e3:,.2f}" + " kJ/kg",
            "Enthalpy molar : " + f"{self.enthalpy_molar/1e3:,.2f}" + " kJ/mol",
            "Cp mass        : " + f"{self.cp_mass:,.3f}" + " J/kg*K",
            "Cp molar       : " + f"{self.cp_molar:,.3f}" + " J/mol*K",
            "Cv mass        : " + f"{self.cv_mass:,.3f}" + " J/kg*K",
            "Cv molar       : " + f"{self.cv_molar:,.3f}" + " J/mol*K",
            "Entropy mass   : " + f"{self.entropy_mass/1e3:,.4f}" + " kJ/kg*K",
            "Viscosity      : " + f"{self.viscosity:.6e}" + " Pa*s",
            "Conductivity   : " + f"{self.conductivity:.4f}" + " W/m*K",
            "Prandtl        : " + f"{self.prandtl:.4f}",
            "Speed of sound : " + f"{self.speed_of_sound:.2f}" + " m/s",
            "=" * 60,
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        comp_str = ", ".join(f"{k}={v:.4f}" for k, v in self._composition.items())
        return (
            "Stream(backend=" + self._backend.name + ", P=" + f"{self._P:.2f}" + " Pa, "
            "T=" + f"{self._T:.2f}" + " K, composition={" + comp_str + "}, "
            "mass_flow=" + f"{self._mass_flow:.4g}" + " kg/s, "
            "molar_flow=" + f"{self._molar_flow:.4g}" + " mol/s)"
        )

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------
    @staticmethod
    def list_fluids() -> List[str]:
        """Return every pure fluid available in the current CoolProp install."""
        return CP.get_global_param_string("FluidsList").split(",")
