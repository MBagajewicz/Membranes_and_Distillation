#region Title: MixPropertiesCoolPropHEOS – Mixins
# Nature: Behavioural composition modules
# Methodology: Split class responsibilities into focused mixin classes.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

"""
Mixin sub-package.

Each module here encapsulates a single responsibility:
  - state_updater : thermodynamic flash and property evaluation
  - phase         : phase-stability tests and dew-point calculations

Mixins are designed to be combined in core.MixPropertiesCoolPropHEOS.
They rely on instance attributes created during __init__ (self.states,
self.P, self.T, self.Z, etc.) but keep the logic physically separated
for readability and testability.
"""
