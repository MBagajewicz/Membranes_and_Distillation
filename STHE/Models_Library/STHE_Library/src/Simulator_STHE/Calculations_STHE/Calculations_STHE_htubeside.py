from . import Calculations_STHE_Nusselt_tubeside


def STHE_h_tubeside(
    mt: float,
    rot: float,
    Cpt: float,
    mit: float,
    kt: float,
    thk: float,
    yfluid,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    L: float,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side heat transfer coefficient.

    The tube-side heat transfer coefficient is calculated from the tube-side
    Nusselt number.

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    Cpt : float
        Tube-side specific heat capacity [J/(kg·K)].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
    kt : float
        Tube-side thermal conductivity [W/(m·K)].
    thk : float
        Tube wall thickness [m].
    yfluid
        Tube-side fluid identifier.
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
    L : float
        Tube length [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-side heat transfer coefficient [W/(m²·K)].
    """

    # Tube-side Nusselt number
    Nut = Calculations_STHE_Nusselt_tubeside.STHE_Nusselt_tubeside(
        mt,
        rot,
        Cpt,
        mit,
        kt,
        thk,
        yfluid,
        Ds,
        dte,
        Npt,
        rp,
        lay,
        L,
        m_p,
    )

    # Tube inside diameter
    dti = dte - (2 * thk)

    # Tube-side heat transfer coefficient
    ht = (Nut * kt) / dti

    return ht