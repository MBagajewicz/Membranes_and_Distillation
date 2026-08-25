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

def HFM_fiber_velocity(molar_flow_fiber, comp_fiber, M, D_i, Ntf, rho):

    qf = sum(molar_flow_fiber*comp_fiber*M/rho) #m^3/s
    vf = (qf / Ntf) / (pi * D_i ** 2 / 4)

    return vf

#endregion