"""
####################################################################################################################
STHE Library
Calculation: Capital Cost (CAPEX)
####################################################################################################################
"""

from . import Calculations_STHE_area


def STHE_CAPEX(
    par_a: float,
    par_b: float,
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    m_p: dict,
) -> float:
    """
    Calculate the capital cost of the shell-and-tube heat exchanger.

    Parameters
    ----------
    par_a : float
        Capital cost correlation coefficient.
    par_b : float
        Capital cost correlation exponent.
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    Npt
        Number of tube passes.
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Capital cost.
    """

    # Heat transfer area
    Atot = Calculations_STHE_area.STHE_area(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        L,
        m_p,
    )

    # Capital cost
    Cap = par_a * (Atot**par_b)

    return Cap
