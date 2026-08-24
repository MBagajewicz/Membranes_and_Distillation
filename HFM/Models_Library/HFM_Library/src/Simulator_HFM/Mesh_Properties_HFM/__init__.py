#region Title: MixPropertiesCoolPropHEOS
# Nature: Common Calculations
# Methodology: Uses CoolProp library to calculate physical and thermal properties with EOS HEOS
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0      16-May-2025    Diego Gabriel Oliva            Commented
##################################################################################################################
#endregion

"""
Package entry point.

This module exposes the public API of the mixprop package.
The class MixPropertiesCoolPropHEOS is the main orchestrator that coordinates
state management, property updates, and phase-stability calculations.
"""

from .core import MixPropertiesCoolPropHEOS

__all__ = ["MixPropertiesCoolPropHEOS"]
