"""
Calculations_STHE_NoNTU.py

Calculates the thermal performance of a shell-and-tube heat exchanger
using equation (32) from NoNTU and Bagajewicz (2004), with the
LMTD correction factor set to F_T = 1 for the current implementation.

The formulation uses the two inlet stream conditions, U and the
installed heat-transfer area to calculate the hot-side outlet
temperature directly. The heat duty and cold-side outlet temperature
are then obtained from the energy balances.

Reference
---------
NoNTU, J. H.; Bagajewicz, M. J. (2004).
On a New MILP Model for the Planning of Heat-Exchanger Network Cleaning.
Ind. Eng. Chem. Res. 43, 3924-3938.
Eq. (32), p. 3927.
"""

import numpy as np


def STHE_NoNTU(
    U,
    InstalledArea,
    m_hot,
    cp_hot,
    Tin_hot,
    m_cold,
    cp_cold,
    Tin_cold,
    F_T=1.0,
):
    """
    Calculate heat duty and outlet temperatures using NoNTU Eq. (32).

    Parameters
    ----------
    U : float
        Overall heat-transfer coefficient [W/(m²·K)].
    InstalledArea : float
        Heat-transfer area [m²].
    m_hot : float
        Hot-stream mass flow rate [kg/s].
    cp_hot : float
        Hot-stream specific heat [J/(kg·K)].
    Tin_hot : float
        Hot-stream inlet temperature [K].
    m_cold : float
        Cold-stream mass flow rate [kg/s].
    cp_cold : float
        Cold-stream specific heat [J/(kg·K)].
    Tin_cold : float
        Cold-stream inlet temperature [K].
    F_T : float, optional
        LMTD correction factor. The current STHE implementation uses
        F_T = 1.0. It is exposed as an argument so that the future
        Gardner/Underwood correction can be introduced without
        changing the calculation interface.

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
        - R
        - NTU
        - Effectiveness
        - F_T
        - HeatDuty
        - ToutHot
        - ToutCold

    Notes
    -----
    The equation is written in terms of

        R = Cc / Ch

    and, for F_T = 1, is

        Th2 = [
            (R - 1) Th1
            + (exp(x) - 1) R Tc1
        ] / [
            R exp(x) - 1
        ]

    where

        x = UA (R - 1) / Cc.

    ``expm1(x)`` is used for numerical stability when R is close to 1.
    The exact R = 1 limiting solution is handled separately.
    """

    # Convert scalar-like NumPy values to ordinary floats. The STHE
    # calculation layer currently supplies scalar values here.
    U = float(np.asarray(U))
    InstalledArea = float(np.asarray(InstalledArea))
    m_hot = float(np.asarray(m_hot))
    cp_hot = float(np.asarray(cp_hot))
    Tin_hot = float(np.asarray(Tin_hot))
    m_cold = float(np.asarray(m_cold))
    cp_cold = float(np.asarray(cp_cold))
    Tin_cold = float(np.asarray(Tin_cold))
    F_T = float(np.asarray(F_T))

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    if not np.isfinite(
        [
            U,
            InstalledArea,
            m_hot,
            cp_hot,
            Tin_hot,
            m_cold,
            cp_cold,
            Tin_cold,
            F_T,
        ]
    ).all():
        raise ValueError("All STHE thermal inputs must be finite.")

    if U < 0.0:
        raise ValueError("U must be non-negative.")

    if InstalledArea < 0.0:
        raise ValueError("InstalledArea must be non-negative.")

    if m_hot <= 0.0 or m_cold <= 0.0:
        raise ValueError("Hot and cold mass flow rates must be positive.")

    if cp_hot <= 0.0 or cp_cold <= 0.0:
        raise ValueError("Hot and cold specific heats must be positive.")

    if F_T <= 0.0:
        raise ValueError("F_T must be positive.")

    # ------------------------------------------------------------------
    # Heat-capacity rates
    # ------------------------------------------------------------------

    Ch = m_hot * cp_hot
    Cc = m_cold * cp_cold

    Cmin = min(Ch, Cc)
    Cmax = max(Ch, Cc)

    Cr = Cmin / Cmax

    # NoNTU Eq. (33):
    R = Cc / Ch

    # ------------------------------------------------------------------
    # Overall conductance
    #
    # For F_T = 1 this is exactly the UA term in Eq. (32).
    #
    # Keeping F_T here provides the extension point for the future
    # LMTD-correction iteration.
    # ------------------------------------------------------------------

    UA = U * InstalledArea
    UA_effective = UA * F_T

    # ------------------------------------------------------------------
    # NTU diagnostic
    # ------------------------------------------------------------------

    NTU = UA_effective / Cmin if Cmin > 0.0 else 0.0

    # ------------------------------------------------------------------
    # Outlet temperature from NoNTU Eq. (32)
    # ------------------------------------------------------------------
    #
    # Eq. (32):
    #
    # Th2 = [
    #     (R - 1) Th1
    #     + (exp(x) - 1) R Tc1
    # ] / [
    #     R exp(x) - 1
    # ]
    #
    # with
    #
    # x = UA_effective / Cc * (R - 1).
    #
    # Rewriting the denominator as
    #
    #     (R - 1) + R * expm1(x)
    #
    # avoids cancellation when x is close to zero.

    r_minus_1 = R - 1.0

    # This tolerance is relative to the scale of the two heat-capacity
    # rates and only determines when the exact R=1 limit is used.
    R_tolerance = 1.0e-10

    if abs(r_minus_1) <= R_tolerance:
        # Exact limiting solution for Ch = Cc:
        #
        # epsilon = NTU / (1 + NTU)
        # Th2 = Th1 - epsilon (Th1 - Tc1)
        Effectiveness = (
            NTU / (1.0 + NTU)
            if NTU > 0.0
            else 0.0
        )

        HeatDuty = (
            Effectiveness
            * Cmin
            * (Tin_hot - Tin_cold)
        )

        ToutHot = Tin_hot - HeatDuty / Ch

    else:
        x = UA_effective / Cc * r_minus_1

        # Avoid exp() overflow for very large positive x. In that
        # limit the exchanger approaches the corresponding maximum
        # heat-transfer temperature relation.
        if x > 700.0:
            # Divide numerator and denominator of Eq. (32) by exp(x).
            # The terms proportional to exp(-x) vanish.
            ToutHot = Tin_cold

        else:
            expm1_x = np.expm1(x)

            numerator = (
                r_minus_1 * Tin_hot
                + expm1_x * R * Tin_cold
            )

            denominator = (
                r_minus_1
                + R * expm1_x
            )

            if abs(denominator) <= np.finfo(float).eps:
                raise ArithmeticError(
                    "NoNTU Eq. (32) became numerically singular."
                )

            ToutHot = numerator / denominator

        # Heat duty from the hot-side energy balance.
        HeatDuty = Ch * (Tin_hot - ToutHot)

        # Effectiveness is reported as a diagnostic quantity.
        if Cmin > 0.0 and Tin_hot != Tin_cold:
            Effectiveness = (
                HeatDuty
                / (Cmin * (Tin_hot - Tin_cold))
            )
        else:
            Effectiveness = 0.0

    # ------------------------------------------------------------------
    # Cold-side outlet temperature from energy balance
    # ------------------------------------------------------------------

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
        "R": R,
        "NTU": NTU,
        "Effectiveness": Effectiveness,
        "F_T": F_T,
        "HeatDuty": HeatDuty,
        "ToutHot": ToutHot,
        "ToutCold": ToutCold,
    }
