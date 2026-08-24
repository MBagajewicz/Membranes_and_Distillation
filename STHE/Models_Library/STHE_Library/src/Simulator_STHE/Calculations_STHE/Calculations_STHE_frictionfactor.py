from . import Calculations_STHE_Reynolds_tubeside


def STHE_tubeside_frictionfactor(
    mt: float,
    rot: float,
    mit: float,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    thk: float,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side Darcy friction factor.

    The friction factor is calculated as a function of the tube-side
    Reynolds number.

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
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
    thk : float
        Tube wall thickness [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-side Darcy friction factor.
    """

    # Tube-side Reynolds number
    Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(
        mt,
        rot,
        mit,
        thk,
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Tube-side friction factor
    ft = 64 / Ret

    ft[Ret > 1311] = 0.048

    ft[Ret > 3380] = 0.014 + 1.056 / (Ret[Ret > 3380] ** 0.42)

    return ft