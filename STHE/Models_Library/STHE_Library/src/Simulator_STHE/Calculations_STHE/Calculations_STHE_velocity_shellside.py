from . import Calculations_STHE_Auxiliary_Bell_Method


def STHE_shellside_velocity(
    ms: float,
    ros: float,
    Ds: float,
    rp: float,
    L: float,
    Nb: int,
    dte: float,
    lay: str,
    m_p: dict,
) -> float:
    """
    Calculate the shell-side fluid velocity.

    The shell-side velocity is calculated according to the method specified
    in ``m_p["Shell_Method"]``.

    Supported methods
    -----------------
    - Bell
    - Kern

    Parameters
    ----------
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    Ds : float
        Shell inside diameter [m].
    rp : float
        Tube pitch ratio.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    dte : float
        Equivalent tube diameter [m].
    lay : str
        Tube layout.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-side fluid velocity [m/s].

    Raises
    ------
    ValueError
        If the selected shell-side method is not supported.
    """

    shell_method = m_p["Shell_Method"]

    if shell_method == "Bell":

        Sm = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Sm(
            Ds,
            dte,
            rp,
            lay,
            L,
            Nb,
            m_p,
        )

        vs = ms / (Sm * ros)

    elif shell_method == "Kern":

        qs = ms / ros

        FAR = 1.0 - (1.0 / rp)

        lbc = L / (Nb + 1)

        Ar = Ds * FAR * lbc

        vs = qs / Ar

    else:

        raise ValueError(
            f"Unknown shell-side method '{shell_method}'. "
            "Supported methods are 'Bell' and 'Kern'."
        )

    return vs