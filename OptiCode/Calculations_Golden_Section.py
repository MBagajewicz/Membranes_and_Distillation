#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          12-Jun-2024     Mariana Mello             Proposed
##################################################################################################################
##################################################################################################################
#endregion

# region Import Library
import math
# endregion

####################################################################################################################
#region Golden Section Function

def golden_section(f, a, b, tol=1e-4, max_iter=100, args=()):
    gr = (math.sqrt(5) + 1) / 2
    c = b - (b - a) / gr
    d = a + (b - a) / gr

    for _ in range(max_iter):
        if abs(b - a) < tol:
            break

        fc = f([c], *args)
        fd = f([d], *args)

        if fc < fd:
            b = d

        else:
            a = c

        c = b - (b - a) / gr
        d = a + (b - a) / gr

    x_min = (b + a) / 2
    return [x_min], f([x_min], *args)


#endregion
####################################################################################################################

