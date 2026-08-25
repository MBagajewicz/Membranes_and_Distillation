#region Title: MixPropertiesCoolPropHEOS – Constants
# Nature: Property name mappings
# Methodology: Maps human-readable property names to CoolProp AbstractState getters.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

"""
Bulk property getters.

This dictionary maps a property name to a lambda that calls the
corresponding AbstractState method. It is used by the update_state
routine to evaluate ONLY the properties a given consumer needs.
This is a big performance saving for HEOS mixtures, where every
getter can trigger an expensive flash or residual calculation.
"""

_BULK_GETTERS = {
    "hmolar":       lambda st: st.hmolar(),
    "rhomass":      lambda st: st.rhomass(),
    "rhomolar":     lambda st: st.rhomolar(),
    "viscosity":    lambda st: st.viscosity(),
    "conductivity": lambda st: st.conductivity(),
    "cpmass":       lambda st: st.cpmass(),
    "cpmolar":      lambda st: st.cpmolar(),
    "molar_mass":   lambda st: st.molar_mass(),
}
