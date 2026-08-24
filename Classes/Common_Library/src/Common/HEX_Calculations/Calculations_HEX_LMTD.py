"""
####################################################################################################################
HEX Library
Calculation: Log Mean Temperature Difference (LMTD)
####################################################################################################################
"""

import numpy as np


def HEX_lmtd(
    Thi,
    Tho,
    Tci,
    Tco,
):
    """
    Calculate the Log Mean Temperature Difference (LMTD).

    Parameters
    ----------
    Thi : float
        Hot fluid inlet temperature.
    Tho : float
        Hot fluid outlet temperature.
    Tci : float
        Cold fluid inlet temperature.
    Tco : float
        Cold fluid outlet temperature.

    Returns
    -------
    float
        Log Mean Temperature Difference.

    Raises
    ------
    ValueError
        If either terminal temperature difference is zero or negative.
    """

    delta1 = Thi - Tco
    delta2 = Tho - Tci

    if delta1 <= 0 or delta2 <= 0:
        raise ValueError(
            f"Cannot compute LMTD: ΔT1={delta1:.6f}, "
            f"ΔT2={delta2:.6f} (both must be > 0)"
        )

    # If ΔT1 and ΔT2 are almost identical, return ΔT1 directly (limit case)
    # if abs(delta1 - delta2) < 1e-6:
    #     return delta1

    return (delta1 - delta2) / np.log(delta1 / delta2)