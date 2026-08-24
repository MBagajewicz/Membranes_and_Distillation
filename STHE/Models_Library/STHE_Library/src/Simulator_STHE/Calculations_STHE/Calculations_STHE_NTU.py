"""
Calculations_STHE_NTU.py

Calculates the thermal performance of a shell-and-tube heat exchanger
using the Effectiveness–NTU method.

Author
------
Diego Oliva
"""

import numpy as np


def STHE_NTU(
    U,
    InstalledArea,
    m_hot,
    cp_hot,
    Tin_hot,
    m_cold,
    cp_cold,
    Tin_cold,
    shell_passes=1,
):
    """
    Calculates the heat duty and outlet temperatures using the
    Effectiveness–NTU method.

    Parameters
    ----------
    U : float
        Overall heat transfer coefficient [W/(m²·K)].

    InstalledArea : float
        Heat transfer area [m²].

    m_hot : float
        Hot stream mass flow rate [kg/s].

    cp_hot : float
        Hot stream specific heat [J/(kg·K)].

    Tin_hot : float
        Hot stream inlet temperature [K].

    m_cold : float
        Cold stream mass flow rate [kg/s].

    cp_cold : float
        Cold stream specific heat [J/(kg·K)].

    Tin_cold : float
        Cold stream inlet temperature [K].

    shell_passes : int, optional
        Number of shell passes.

        Currently only one shell pass (TEMA E) is implemented.

    Returns
    -------
    dict
        Dictionary containing:

        - UA
        - Ch
        - Cc
        - Cmin
        - Cmax
        - Cr
        - NTU
        - Effectiveness
        - HeatDuty
        - ToutHot
        - ToutCold
    """

    if shell_passes != 1:
        raise NotImplementedError(
            "Only one shell pass (TEMA E) is currently implemented."
        )

    # ------------------------------------------------------------------
    # Heat capacity rates
    # ------------------------------------------------------------------

    Ch = m_hot * cp_hot
    Cc = m_cold * cp_cold

    Cmin = min(Ch, Cc)
    Cmax = max(Ch, Cc)

    Cr = Cmin / Cmax

    # ------------------------------------------------------------------
    # Overall conductance
    # ------------------------------------------------------------------

    UA = U * InstalledArea

    # ------------------------------------------------------------------
    # Number of Transfer Units
    # ------------------------------------------------------------------

    NTU = UA / Cmin

    # ------------------------------------------------------------------
    # Effectiveness
    #
    # TEMA E
    # One shell pass, two (or any even number of) tube passes.
    #
    # References
    # ----------
    # Incropera et al.
    # Fundamentals of Heat and Mass Transfer
    #
    # Shah & Sekulic
    # Fundamentals of Heat Exchanger Design
    # ------------------------------------------------------------------

    if NTU <= 0.0:

        Effectiveness = 0.0

    else:

        A = np.sqrt(1.0 + Cr**2)

        Effectiveness = (
            2.0
            / (
                1.0
                + Cr
                + A
                * (1.0 + np.exp(-NTU * A))
                / (1.0 - np.exp(-NTU * A))
            )
        )

    # ------------------------------------------------------------------
    # Heat duty
    # ------------------------------------------------------------------

    HeatDuty = (
        Effectiveness
        * Cmin
        * (Tin_hot - Tin_cold)
    )

    # ------------------------------------------------------------------
    # Outlet temperatures
    # ------------------------------------------------------------------

    ToutHot = Tin_hot - HeatDuty / Ch

    ToutCold = Tin_cold + HeatDuty / Cc

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    return {
        "UA": UA,
        "Ch": Ch,
        "Cc": Cc,
        "Cmin": Cmin,
        "Cmax": Cmax,
        "Cr": Cr,
        "NTU": NTU,
        "Effectiveness": Effectiveness,
        "HeatDuty": HeatDuty,
        "ToutHot": ToutHot,
        "ToutCold": ToutCold,
    }