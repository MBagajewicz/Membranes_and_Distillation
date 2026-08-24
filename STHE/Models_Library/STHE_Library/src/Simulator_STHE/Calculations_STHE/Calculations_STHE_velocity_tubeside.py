from . import Calculations_STHE_countingtable

from math import pi


def STHE_tubeside_velocity(
    mt: float,
    rot: float,
    thk: float,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side fluid velocity.

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    thk : float
        Tube wall thickness [m].
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    Npt : int
        Number of tube passes.
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-side fluid velocity [m/s].
    """

    # Tube-side volumetric flow rate
    qt = mt / rot

    # Tube inside diameter
    dti = dte - (2 * thk)

    # Number of tubes
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Number of tubes per pass
    Ntp = Ntt / Npt

    # Tube-side velocity
    vt = (qt / Ntp) / (pi * dti ** 2 / 4)

    return vt