from . import Calculations_STHE_velocity_shellside

from math import pi
import numpy as np


def STHE_Reynolds_shellside(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    m_p: dict,
) -> float:
    """
    Calculate the shell-side Reynolds number.

    The shell-side Reynolds number is calculated according to the method
    specified in ``m_p["Shell_Method"]``.

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
    mis : float
        Shell-side dynamic viscosity [Pa·s].
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
        Shell-side Reynolds number.

    Raises
    ------
    ValueError
        If the selected shell-side method is not supported.
    """

    shell_method = m_p["Shell_Method"]

    if shell_method == "Bell":

        # Shell-side velocity
        vs = Calculations_STHE_velocity_shellside.STHE_shellside_velocity(
            ms,
            ros,
            Ds,
            rp,
            L,
            Nb,
            dte,
            lay,
            m_p,
        )

        # Reynolds number with the fouling layer
        # Res = (dte + 2 * fts_thk) * vs * ros / mis

        # Reynolds number without the fouling layer
        Res = (dte * vs * ros) / mis

    elif shell_method == "Kern":

        vs = Calculations_STHE_velocity_shellside.STHE_shellside_velocity(
            ms,
            ros,
            Ds,
            rp,
            L,
            Nb,
            dte,
            lay,
            m_p,
        )

        K_Deq = 4 * np.ones(lay.shape)

        if isinstance(lay, float) or isinstance(lay, int):
            if lay == 2:
                K_Deq = 3.46
        else:
            K_Deq[lay == 2] = 3.46

        ltp = rp * dte

        Deq = (K_Deq * ltp ** 2) / (pi * dte) - dte

        Res = (Deq * vs * ros) / mis

    else:

        raise ValueError(
            f"Unknown shell-side method '{shell_method}'. "
            "Supported methods are 'Bell' and 'Kern'."
        )

    return Res