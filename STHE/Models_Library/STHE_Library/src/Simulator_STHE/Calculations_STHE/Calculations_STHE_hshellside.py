from . import Calculations_STHE_Auxiliary_Bell_Method
from . import Calculations_STHE_Nusselt_shellside

from math import pi
import numpy as np


def STHE_h_shellside(
    ms: float,
    ros: float,
    Cps: float,
    mis: float,
    ks: float,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
) -> float:
    """
    Calculate the shell-side heat transfer coefficient.

    The shell-side heat transfer coefficient is calculated according to the
    method specified in ``m_p["Shell_Method"]``.

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
    Npt : int
        Number of tube passes.
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-side heat transfer coefficient [W/(m²·K)].

    Raises
    ------
    ValueError
        If the selected shell-side method is not supported.
    """

    shell_method = m_p["Shell_Method"]

    if shell_method == "Bell":

        phi = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Idealcrossflowh(
            Ds,
            dte,
            rp,
            lay,
            L,
            Nb,
            ms,
            ros,
            mis,
            Cps,
            ks,
            m_p,
        )

        Jc = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jc(
            Ds,
            dte,
            Bc,
            m_p,
        )

        Jl = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jl(
            Ds,
            dte,
            Npt,
            rp,
            lay,
            L,
            Nb,
            Bc,
            m_p,
        )

        Jb1 = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jb1(
            Ds,
            dte,
            Npt,
            rp,
            lay,
            ms,
            ros,
            mis,
            L,
            Nb,
            Bc,
            m_p,
        )

        Jr = Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_Jr(
            Ds,
            dte,
            Npt,
            rp,
            lay,
            L,
            Nb,
            ms,
            ros,
            mis,
            Bc,
            m_p,
        )

        Jtot = Jc * Jl * Jb1 * Jr

        hs = phi * Jc * Jl * Jb1 * Jr

    elif shell_method == "Kern":

        Nus = Calculations_STHE_Nusselt_shellside.STHE_Nusselt_shellside(
            ms,
            ros,
            Cps,
            mis,
            ks,
            Ds,
            dte,
            rp,
            lay,
            L,
            Nb,
            m_p,
        )

        K_Deq = 4 * np.ones(lay.shape)

        K_Deq[lay == 2] = 3.46

        ltp = rp * dte

        Deq = (K_Deq * ltp ** 2) / (pi * dte) - dte

        hs = Nus * ks / Deq

    else:

        raise ValueError(
            f"Unknown shell-side method '{shell_method}'. "
            "Supported methods are 'Bell' and 'Kern'."
        )

    return hs