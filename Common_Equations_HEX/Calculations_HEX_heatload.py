#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello               Original

##################################################################################################################
#endregion

#region Calculations

def HEX_heat_load(mh, Cph, Thi, Tho):
    # Heat load
    Q = mh * Cph * (Thi - Tho)
    return Q

#endregion
