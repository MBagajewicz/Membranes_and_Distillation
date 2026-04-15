#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        06-Nov-2025     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
from math import pi
#endregion

#region Calculations

def HFM_area_per_L(dfo, Ntf):
    # Hollow fiber membrane exchanger area per L
    AREA_PER_L = Ntf * pi * dfo
    return AREA_PER_L