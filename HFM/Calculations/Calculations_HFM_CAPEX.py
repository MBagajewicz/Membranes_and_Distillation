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

def HFM_CAPEX(Costm2,Area):
    # Hollow fiber membrane exchanger area ( Chu model, requires further adaptation for non square pitch)
    CAPEX=Costm2*Area
    return CAPEX