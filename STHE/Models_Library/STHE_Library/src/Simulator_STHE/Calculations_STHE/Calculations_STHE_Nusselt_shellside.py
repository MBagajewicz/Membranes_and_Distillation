from . import Calculations_STHE_Reynolds_shellside


def STHE_Nusselt_shellside(
    ms: float,
    ros: float,
    Cps: float,
    mis: float,
    ks: float,
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    m_p: dict,
) -> float:
    """
    Calculate the shell-side Nusselt number.

    The shell-side Nusselt number is calculated from the shell-side Reynolds
    and Prandtl numbers.

    Parameters
    ----------
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    Cps : float
        Shell-side specific heat capacity [J/(kg·K)].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    ks : float
        Shell-side thermal conductivity [W/(m·K)].
    Ds : float
        Shell inside diameter [m].
    dte : float
        Equivalent tube diameter [m].
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-side Nusselt number.
    """

    # Shell-side Reynolds number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(
        ms,
        ros,
        mis,
        Ds,
        dte,
        rp,
        lay,
        L,
        Nb,
        m_p,
    )

    # Shell-side Prandtl number
    Prs = (Cps * mis) / ks

    # Shell-side Nusselt number
    Nus = 0.36 * Res ** 0.55 * Prs ** (1 / 3)

    return Nus