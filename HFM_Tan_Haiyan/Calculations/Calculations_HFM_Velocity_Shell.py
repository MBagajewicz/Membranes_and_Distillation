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

def HFM_shell_velocity(molar_flow_shell, comp_shell, M, rho, D, D_o, Ntf):
    qs = sum(molar_flow_shell * comp_shell * M / rho)
    S = (pi / 4) * (D ** 2 - Ntf * D_o ** 2)
    vs = qs / S
    return vs