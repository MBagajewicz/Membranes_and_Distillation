"""
####################################################################################################################
STHE Library
Calculation: Required Heat Transfer Area
####################################################################################################################
"""


def STHE_required_area(
    heat_load,
    overall_coefficient,
    lmtd,
    correction_factor,
):
    """
    Calculate the required heat transfer area.

    Parameters
    ----------
    heat_load : float
        Heat duty.
    overall_coefficient : float
        Overall heat transfer coefficient.
    lmtd : float
        Log Mean Temperature Difference.
    correction_factor : float
        LMTD correction factor.

    Returns
    -------
    float
        Required heat transfer area.
    """

    return (
        heat_load
        / (
            overall_coefficient
            * lmtd
            * correction_factor
        )
    )