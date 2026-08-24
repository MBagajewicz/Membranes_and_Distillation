from . import Calculations_STHE_velocity_tubeside


def STHE_Reynolds_tubeside(
    mt: float,
    rot: float,
    mit: float,
    thk: float,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side Reynolds number.

    The tube-side Reynolds number is calculated from the tube-side velocity.

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
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
        Tube-side Reynolds number.
    """

    # Tube-side velocity
    vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
        mt,
        rot,
        thk,
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Tube inside diameter
    dti = dte - (2 * thk)

    # Tube-side Reynolds number
    Ret = (dti * vt * rot) / mit

    return Ret