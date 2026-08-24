from math import pi, sqrt

import numpy as np


def STHE_counting_table(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    m_p: dict,
):
    """
    Calculate the number of tubes.

    The number of tubes is calculated according to the method specified
    in ``m_p["Shell_Method"]``.

    Supported methods
    -----------------
    - Bell
    - Kern

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    Npt
        Number of tube passes.
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    ndarray or float
        Number of tubes.
    """

    shell_method = m_p["Shell_Method"]

    if shell_method == "Bell":

        # Tube count table
        ppDs = [
            0.2050,
            0.3048,
            0.3874,
            0.4890,
            0.5906,
            0.6858,
            0.7874,
            0.8382,
            0.8890,
            0.9398,
            0.9906,
            1.0668,
            1.1430,
            1.2192,
            1.3716,
            1.5240,
            2.0000,
        ]

        pppsi_1 = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        pppsi_2 = [
            0.18,
            0.09,
            0.06,
            0.046,
            0.042,
            0.036,
            0.034,
            0.033,
            0.032,
            0.030,
            0.028,
            0.025,
            0.024,
            0.0235,
            0.020,
            0.018,
            0.018,
        ]

        pppsi_4 = [
            0.30,
            0.20,
            0.16,
            0.125,
            0.118,
            0.110,
            0.095,
            0.090,
            0.085,
            0.080,
            0.075,
            0.073,
            0.071,
            0.0650,
            0.060,
            0.050,
            0.050,
        ]

        pppsi_6 = [
            0.40,
            0.22,
            0.18,
            0.168,
            0.158,
            0.148,
            0.122,
            0.118,
            0.110,
            0.105,
            0.098,
            0.090,
            0.088,
            0.0870,
            0.080,
            0.074,
            0.074,
        ]

        # Shell-to-bundle clearance
        Lbb = (0.0048 * Ds) + 0.0128

        C1 = np.ones(lay.shape)
        C1[lay == 2] = 0.866

        Ntt1 = (0.78 * (Ds - Lbb - dte) ** 2) / (C1 * (rp * dte) ** 2)

        psi = np.zeros(Ds.shape)

        for i in range(len(pppsi_1)):

            CondDs = Ds > 10e10
            CondNpt = Ds > 10e10
            CondInter = Ds > 10e10

            CondDs[Ds == ppDs[i]] = True

            CondNpt[Npt == 1] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_1[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 2] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_2[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 4] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_4[i]

            CondNpt = Ds > 10e10
            CondNpt[Npt == 6] = True
            CondInter = np.logical_and(CondDs, CondNpt)
            psi[CondInter] = pppsi_6[i]

        Ntt = np.round(Ntt1 * (1 - psi))

    elif shell_method == "Kern":

        # Tube-pass correction factor
        KNPt = sqrt(0.9) * np.ones(Npt.shape)

        if isinstance(Npt, float) or isinstance(Npt, int):

            if Npt == 1:
                KNPt = sqrt(0.93)

        else:

            KNPt[Npt == 1] = sqrt(0.93)

        # Bundle diameter
        Db = Ds * KNPt

        # Tube pitch
        ltp = rp * dte

        # Tube layout correction factor
        Klay = np.ones(lay.shape)
        Klay[lay == 2] = 0.866

        # Number of tubes
        Ntt = np.round((pi * Db ** 2) / (4 * ltp ** 2 * Klay))

    else:

        raise ValueError(
            f"Unknown shell-side method '{shell_method}'. "
            "Supported methods are 'Bell' and 'Kern'."
        )

    return Ntt