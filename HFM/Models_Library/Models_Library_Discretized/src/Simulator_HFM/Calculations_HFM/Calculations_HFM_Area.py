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

def HFM_area(dfo, L, Ntf):
    # Hollow fiber membrane exchanger area ( Chu model, requires further adaptation for non square pitch)
    Area = Ntf * pi * dfo * L
    return Area