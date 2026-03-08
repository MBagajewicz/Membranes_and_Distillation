
#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Original
#   0.1          23-Apr-2025     Mariana Mello             Update to fix error
#   0.2          23-Apr-2025     Sung Young Kim            Edit delta T (if delta T < 0)
##################################################################################################################
#endregion

#region Import Library
#from math import log
import math
import numpy as np
#endregion

#region Calculations

#def HEX_lmtd(Thi, Tho, Tci, Tco):
#    # Logarithmic mean temperature difference
#    LMTD = ((Thi - Tco) - (Tho - Tci)) / log((Thi - Tco)/(Tho - Tci))
#    return LMTD

def HEX_lmtd(Thi, Tho, Tci, Tco):
    #Log mean temperature difference.
    #ΔT₁ = Thi - Tco, ΔT₂ = Tho - Tci 
    #LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
    #ΔT₁, ΔT₂ must be positive. Both ΔT1 and ΔT2 must be positive. 
    # If they are nearly equal (within 1e-6), return ΔT1 to avoid division by zero in the logarithm.
    
    delta1 = Thi - Tco
    delta2 = Tho - Tci
    # Prevent zero values- 
    if delta1 <= 0 or delta2 <= 0:
        raise ValueError(f"Cannot compute LMTD: ΔT1={delta1:.6f}, ΔT2={delta2:.6f} (both must be > 0)")

    # If ΔT1 and ΔT2 are almost identical, return ΔT1 directly (limit case)
    #if abs(delta1 - delta2) < 1e-6:
    #    return delta1

    # Standard LMTD calculation
    return (delta1 - delta2) / np.log(delta1 / delta2)
#endregion