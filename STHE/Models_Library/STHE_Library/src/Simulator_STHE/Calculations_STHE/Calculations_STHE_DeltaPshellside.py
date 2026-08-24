from . import Calculations_STHE_Auxiliary_Bell_Method
from . import Calculations_STHE_Reynolds_shellside
from . import Calculations_STHE_velocity_shellside

from math import pi

import numpy as np


def STHE_shellside_DeltaP(
    ms: float,
    ros: float,
    mis: float,
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
    Calculate the shell-side pressure drop.

    The shell-side pressure drop is calculated according to the method
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
        Tube outside diameter [m].
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
        Shell-side pressure drop [Pa].

    Raises
    ------
    ValueError
        If the selected shell-side method is not supported.
    """

    shell_method = m_p["Shell_Method"]

    if shell_method == "Bell":

        # Cross-flow pressure drop
        DPc = (
            Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_crossflowDeltaP(
                ms,
                ros,
                mis,
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
        )

        # Window pressure drop
        DPw = (
            Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_BaffleWidownDeltaP(
                ms,
                ros,
                mis,
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
        )

        # End-zone pressure drop
        DPe = (
            Calculations_STHE_Auxiliary_Bell_Method.STHE_shellside_EndZonesDeltaP(
                ms,
                ros,
                mis,
                Ds,
                dte,
                rp,
                lay,
                L,
                Nb,
                Bc,
                m_p,
            )
        )

        # Total shell-side pressure drop
        DPs = DPc + DPw + DPe

    elif shell_method == "Kern":

        # Equivalent diameter correction factor
        K_Deq = 4 * np.ones(lay.shape)

        if isinstance(lay, float) or isinstance(lay, int):

            if lay == 2:
                K_Deq = 3.46

        else:

            K_Deq[lay == 2] = 3.46

        # Equivalent diameter
        ltp = rp * dte
        Deq = (K_Deq * ltp ** 2) / (pi * dte) - dte

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

        # Shell-side friction factor
        fs = 1.728 / (Res ** 0.188)

        # Shell-side pressure drop
        DPs = (ros * fs * Ds * (Nb + 1) * vs ** 2) / (2 * Deq)

    else:

        raise ValueError(
            f"Unknown shell-side method '{shell_method}'. "
            "Supported methods are 'Bell' and 'Kern'."
        )

    return DPs