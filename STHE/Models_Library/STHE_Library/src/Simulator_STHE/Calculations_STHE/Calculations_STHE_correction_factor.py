"""
####################################################################################################################
STHE Library
Calculation: LMTD Correction Factor
####################################################################################################################
"""

import numpy as np


def STHE_correction_factor(
    Thi,
    Tho,
    Tci,
    Tco,
    Npt,
    Xp,
):
    """
    Calculate the LMTD correction factor.

    Parameters
    ----------
    Thi : float
        Hot fluid inlet temperature.
    Tho : float
        Hot fluid outlet temperature.
    Tci : float
        Cold fluid inlet temperature.
    Tco : float
        Cold fluid outlet temperature.
    Npt : int or ndarray
        Number of tube passes.
    Xp : float
        Correction factor parameter.

    Returns
    -------
    float or ndarray
        LMTD correction factor.
    """

    F = np.ones(np.shape(Npt))

    R = (Thi - Tho) / (Tco - Tci)
    P = (Tco - Tci) / (Thi - Tci)

    Pmax = 2 / (R + 1 + np.sqrt(R**2 + 1))

    cond = (Pmax * Xp) > P

    try:

        if cond:

            if R == 1:

                F_1N = (
                    np.sqrt(2) * P
                ) / (
                    (1 - P)
                    * np.log(
                        (2 - P * (2 - np.sqrt(2)))
                        / (2 - P * (2 + np.sqrt(2)))
                    )
                )

            else:

                F_1N = (
                    np.sqrt(R**2 + 1)
                    * np.log((1 - P) / (1 - R * P))
                ) / (
                    (R - 1)
                    * np.log(
                        (
                            2
                            - P
                            * (
                                R
                                + 1
                                - np.sqrt(R**2 + 1)
                            )
                        )
                        /
                        (
                            2
                            - P
                            * (
                                R
                                + 1
                                + np.sqrt(R**2 + 1)
                            )
                        )
                    )
                )

            F[Npt > 1] = F_1N

        else:

            F[Npt > 1] = 1e-15

    except Exception:

        if cond.all():

            if np.all(R) == 1:

                F_1N = (
                    np.sqrt(2) * P
                ) / (
                    (1 - P)
                    * np.log(
                        (2 - P * (2 - np.sqrt(2)))
                        / (2 - P * (2 + np.sqrt(2)))
                    )
                )

            else:

                F_1N = (
                    np.sqrt(R**2 + 1)
                    * np.log((1 - P) / (1 - R * P))
                ) / (
                    (R - 1)
                    * np.log(
                        (
                            2
                            - P
                            * (
                                R
                                + 1
                                - np.sqrt(R**2 + 1)
                            )
                        )
                        /
                        (
                            2
                            - P
                            * (
                                R
                                + 1
                                + np.sqrt(R**2 + 1)
                            )
                        )
                    )
                )

            F[Npt > 1] = F_1N[Npt > 1]

        else:

            F[Npt > 1] = 1e-15

    return F