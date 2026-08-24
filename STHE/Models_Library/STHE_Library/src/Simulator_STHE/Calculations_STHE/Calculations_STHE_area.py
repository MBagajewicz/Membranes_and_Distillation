"""
####################################################################################################################
STHE Library
Calculation: Heat Transfer Area
####################################################################################################################
"""

from math import pi

from . import Calculations_STHE_countingtable


def STHE_area(
    Ds,
    dte,
    Npt,
    rp,
    lay,
    L,
    m_p,
):
    """
    Calculate the total external heat transfer area.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    Npt : int
        Number of tube passes.
    rp : float
        Tube pitch ratio.
    lay : str
        Tube layout.
    L : float
        Tube length [m].
    m_p : m_p
        m_p options.

    Returns
    -------
    float
        Total external tube area [m²].
    """

    number_of_tubes = (
        Calculations_STHE_countingtable.STHE_counting_table(
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )
    )

    return number_of_tubes * pi * dte * L