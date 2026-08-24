from math import pi

import numpy as np

from . import Calculations_STHE_countingtable
from . import Calculations_STHE_Reynolds_shellside


def STHE_shellside_Nusseltparameters(
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    ms: float,
    ros: float,
    mis: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware heat-transfer correlation parameters.

    These parameters are used by the Bell-Delaware method to evaluate the
    shell-side ideal cross-flow heat-transfer coefficient.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    tuple
        Tuple containing the four Bell-Delaware correlation parameters
        ``(pa_1, pa_2, pa_3, pa_4)``.
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

    # Tube layout masks
    CondLay30 = Res < -10e10      # 30° (lay == 2)
    CondLay45 = Res < -10e10      # 45° (lay == 3)
    CondLay90 = Res < -10e10      # 90° (lay == 1)

    CondRes = Res < -10e10

    CondInter30 = Res < -10e10
    CondInter45 = Res < -10e10
    CondInter90 = Res < -10e10

    CondLay30[lay == 2] = True
    CondLay45[lay == 3] = True
    CondLay90[lay == 1] = True

    pa_1 = np.ones(Res.shape)
    pa_2 = np.ones(Res.shape)
    pa_3 = np.ones(Res.shape)
    pa_4 = np.ones(Res.shape)

    # Reynolds range 1

    pa_1[CondLay30] = 1.4
    pa_1[CondLay45] = 1.55
    pa_1[CondLay90] = 0.97

    pa_2[:] = -0.667

    # Reynolds range 2

    CondRes[Res > 10] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 1.36
    pa_1[CondInter45] = 0.498
    pa_1[CondInter90] = 0.90

    pa_2[CondInter30] = -0.657
    pa_2[CondInter45] = -0.656
    pa_2[CondInter90] = -0.631

    # Reynolds range 3

    CondRes = Res < -10e10
    CondRes[Res > 1e2] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.593
    pa_1[CondInter45] = 0.73
    pa_1[CondInter90] = 0.408

    pa_2[CondInter30] = -0.477
    pa_2[CondInter45] = -0.500
    pa_2[CondInter90] = -0.460

    # Reynolds range 4

    CondRes = Res < -10e10
    CondRes[Res > 1e3] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.321
    pa_1[CondInter45] = 0.370
    pa_1[CondInter90] = 0.107

    pa_2[CondInter30] = -0.388
    pa_2[CondInter45] = -0.396
    pa_2[CondInter90] = -0.266

    # Reynolds range 5

    CondRes = Res < -10e10
    CondRes[Res > 1e4] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.321
    pa_1[CondInter45] = 0.370
    pa_1[CondInter90] = 0.370

    pa_2[CondInter30] = -0.388
    pa_2[CondInter45] = -0.396
    pa_2[CondInter90] = -0.395

    pa_3[CondLay30] = 1.45
    pa_3[CondLay45] = 1.93
    pa_3[CondLay90] = 1.187

    pa_4[CondLay30] = 0.519
    pa_4[CondLay45] = 0.500
    pa_4[CondLay90] = 0.370

    return pa_1, pa_2, pa_3, pa_4

def STHE_shellside_DeltaPparameters(
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
):
    """
    Calculate the Bell-Delaware pressure-drop correlation parameters.

    These parameters are used by the Bell-Delaware method to evaluate the
    ideal shell-side cross-flow friction factor.

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
    tuple
        Tuple containing the four Bell-Delaware pressure-drop parameters
        ``(pb_1, pb_2, pb_3, pb_4)``.
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

    # Tube layout masks
    CondLay30 = Res < -10e10      # 30° (lay == 2)
    CondLay45 = Res < -10e10      # 45° (lay == 3)
    CondLay90 = Res < -10e10      # 90° (lay == 1)

    CondRes = Res < -10e10

    CondInter30 = Res < -10e10
    CondInter45 = Res < -10e10
    CondInter90 = Res < -10e10

    CondLay30[lay == 2] = True
    CondLay45[lay == 3] = True
    CondLay90[lay == 1] = True

    pb_1 = np.ones(Res.shape)
    pb_2 = np.ones(Res.shape)
    pb_3 = np.ones(Res.shape)
    pb_4 = np.ones(Res.shape)

    # Reynolds range 1

    pb_1[CondLay30] = 48
    pb_1[CondLay45] = 32
    pb_1[CondLay90] = 35

    pb_2[:] = -1

    # Reynolds range 2

    CondRes[Res > 10] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 45.1
    pb_1[CondInter45] = 26.2
    pb_1[CondInter90] = 32.1

    pb_2[CondInter30] = -0.973
    pb_2[CondInter45] = -0.913
    pb_2[CondInter90] = -0.963

    # Reynolds range 3

    CondRes = Res < -10e10
    CondRes[Res > 1e2] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 4.57
    pb_1[CondInter45] = 3.50
    pb_1[CondInter90] = 6.09

    pb_2[CondInter30] = -0.476
    pb_2[CondInter45] = -0.476
    pb_2[CondInter90] = -0.602

    # Reynolds range 4

    CondRes = Res < -10e10
    CondRes[Res > 1e3] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 0.486
    pb_1[CondInter45] = 0.333
    pb_1[CondInter90] = 0.0815

    pb_2[CondInter30] = -0.152
    pb_2[CondInter45] = -0.136
    pb_2[CondInter90] = 0.022

    # Reynolds range 5

    CondRes = Res < -10e10
    CondRes[Res > 1e4] = True

    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 0.372
    pb_1[CondInter45] = 0.303
    pb_1[CondInter90] = 0.391

    pb_2[CondInter30] = -0.123
    pb_2[CondInter45] = -0.126
    pb_2[CondInter90] = -0.148

    pb_3[CondLay30] = 7.00
    pb_3[CondLay45] = 6.59
    pb_3[CondLay90] = 6.30

    pb_4[CondLay30] = 0.500
    pb_4[CondLay45] = 0.520
    pb_4[CondLay90] = 0.378

    return pb_1, pb_2, pb_3, pb_4

def STHE_Lbb_func(
    Ds: float,
    m_p: dict,
):
    """
    Calculate the shell-to-bundle clearance.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-to-bundle clearance [m].
    """

    Lbb = (0.0048 * Ds) + 0.0128

    return Lbb

def STHE_Ltb_func(
    Ds: float,
    dte: float,
    m_p: dict,
):
    """
    Calculate the tube-to-baffle diametral clearance.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-to-baffle diametral clearance [m].
    """

    Ltb = np.ones(Ds.shape) * 0.8e-3
    Lbmax = np.ones(Ds.shape) * 0.9

    Cond_1 = Ds > 10e10
    Cond_2 = Ds > 10e10
    Cond_3 = Ds > 10e10

    Cond_3[dte >= 0.0195] = True

    Lbmax[Cond_3] = (52 * dte[Cond_3]) + 0.532
    Lbmax[~Cond_3] = (68 * dte[~Cond_3]) + 0.228

    Cond_1[dte <= 31.75e-3] = True
    Cond_2[Lbmax > 0.9] = True

    CondInter = np.logical_and(Cond_1, Cond_2)

    Ltb[CondInter] = 0.4e-3

    return Ltb

def STHE_Lsb_func(
    Ds: float,
    m_p: dict,
):
    """
    Calculate the shell-to-baffle diametral clearance.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-to-baffle diametral clearance [m].
    """

    Lsb = 1.6e-3 + (0.004 * Ds)

    return Lsb

def STHE_Ltp_func(
    rp: float,
    dte: float,
):
    """
    Calculate the tube pitch.

    Parameters
    ----------
    rp : float
        Tube pitch ratio.
    dte : float
        Tube outside diameter [m].

    Returns
    -------
    float
        Tube pitch [m].
    """

    Ltp = rp * dte

    return Ltp

def STHE_Lbc_func(
    L: float,
    Nb: int,
):
    """
    Calculate the baffle spacing.

    Parameters
    ----------
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.

    Returns
    -------
    float
        Baffle spacing [m].
    """

    Lbc = L / (Nb + 1)

    return Lbc

def STHE_shellside_Sm(
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    m_p: dict,
):
    """
    Calculate the shell-side cross-flow area.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
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
        Shell-side cross-flow area [m²].
    """

    # Shell-to-bundle clearance
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Tube bundle diameter
    Dotl = Ds - Lbb

    # Diameter through the centers of the outermost tubes
    Dctl = Dotl - dte

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Effective tube pitch
    Ltpeff = np.ones(lay.shape) * Ltp
    Ltpeff[lay == 3] = 0.707 * Ltp[lay == 3]

    # Baffle spacing
    Lbc = STHE_Lbc_func(L, Nb)

    # Cross-flow area
    Sm = Lbc * (Lbb + Dctl * ((Ltp - dte) / Ltpeff))

    return Sm

def STHE_shellside_Ssb(
    Ds: float,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the shell-to-baffle leakage area.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-to-baffle leakage area [m²].
    """

    # Baffle-cut central angle
    teta_Ds = 2 * np.arccos(1 - (2 * Bc))

    # Shell-to-baffle clearance
    Lsb = STHE_Lsb_func(Ds, m_p)

    # Shell-to-baffle leakage area
    Ssb = pi * Ds * (Lsb / 2) * (((2 * pi) - teta_Ds) / (2 * pi))

    return Ssb

def STHE_shellside_Stb(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the tube-to-baffle leakage area.

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
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-to-baffle leakage area [m²].
    """

    # Number of tubes
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Tube-to-baffle clearance
    Ltb = STHE_Ltb_func(Ds, dte, m_p)

    # Shell-to-bundle clearance
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Tube bundle diameter
    Dotl = Ds - Lbb

    # Diameter through the centers of the outermost tubes
    Dctl = Dotl - dte

    # Baffle-cut angle at the tube-center diameter
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - (2 * Bc)))

    # Tube fraction in the window
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Tube-to-baffle leakage area
    Stb = Ntt * (1 - Fw) * ((pi / 4) * (((dte + Ltb) ** 2) - (dte ** 2)))

    Stb[Stb < 0] = 0

    return Stb

def STHE_shellside_Sb(
    Ds: float,
    L: float,
    Nb: int,
    m_p: dict,
):
    """
    Calculate the shell-to-bundle bypass area.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Shell-to-bundle bypass area [m²].
    """

    # Shell-to-bundle clearance
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Tube bundle diameter
    Dotl = Ds - Lbb

    # Baffle spacing
    Lbc = STHE_Lbc_func(L, Nb)

    # Sealing-strip width
    Lpl = 0

    # Shell-to-bundle bypass area
    Sb = Lbc * ((Ds - Dotl) + Lpl)

    return Sb

def STHE_shellside_Ntcc(
    Ds: float,
    dte: float,
    rp: float,
    lay,
    Bc: float,
):
    """
    Calculate the number of tube rows in cross-flow.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    Bc : float
        Baffle cut fraction.

    Returns
    -------
    float
        Number of tube rows in cross-flow.
    """

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Tube spacing in the flow direction
    Lpp = Ltp
    Lpp[lay == 2] = 0.866 * Ltp[lay == 2]
    Lpp[lay == 3] = 0.707 * Ltp[lay == 3]

    # Number of tube rows in cross-flow
    Ntcc = (Ds / Lpp) * (1 - (2 * Bc))

    return Ntcc

def STHE_shellside_Ntcw(
    Ds: float,
    dte: float,
    rp: float,
    lay,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the number of tube rows in the window region.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Number of tube rows in the window region.
    """

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Tubes distance in the flow direction
    Lpp = Ltp
    Lpp[lay == 2] = 0.866 * Ltp[lay == 2]
    Lpp[lay == 3] = 0.707 * Ltp[lay == 3]

    # Number of tube rows in the window region
    Ntcw = (0.8 / Lpp) * ((Ds * Bc) - ((Ds - Dctl) / 2))

    return Ntcw

def STHE_shellside_WindowAreas(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the shell-side window areas.

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
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    tuple
        Tuple containing:

        - Swt : Area occupied by the tubes [m²].
        - Swg : Total window area [m²].
        - Sw : Free window area [m²].
    """

    # Number of tubes (Counting table)
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Central angle of the rope relative to the cutting of the baffle
    teta_Ds = 2 * np.arccos(1 - (2 * Bc))

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - (2 * Bc)))

    # Tube fraction in the window
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Number of tubes in the window
    Ntw = Ntt * Fw

    # Area occupied by the tubes
    Swt = Ntw * ((pi / 4) * (dte ** 2))

    # Total window area
    Swg = (pi / 4) * (Ds ** 2) * (
        (teta_Ds - np.sin(teta_Ds)) / (2 * pi)
    )

    # Free window area
    Sw = Swg - Swt

    return Swt, Swg, Sw

def STHE_shellside_Dw(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the hydraulic diameter in the window region.

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
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Hydraulic diameter in the window region [m].
    """

    # Total number of tubes
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        m_p,
    )

    # Central angle of the rope relative to the cutting of the baffle
    teta_Ds = 2 * np.arccos(1 - (2 * Bc))

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - (2 * Bc)))

    # Tube fraction in the window
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Number of tubes in the window
    Ntw = Ntt * Fw

    # Window areas
    Swt, Swg, Sw = STHE_shellside_WindowAreas(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        Bc,
        m_p,
    )

    # Hydraulic diameter
    Dw = (4 * Sw) / ((pi * dte * Ntw) + (pi * Ds * teta_Ds))

    return Dw

def STHE_shellside_Rl(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware correction factor for baffle leakage.

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
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware baffle leakage correction factor.
    """

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and baffle
    Ssb = STHE_shellside_Ssb(Ds, Bc, m_p)

    # Tube and baffle leakage area
    Stb = STHE_shellside_Stb(Ds, dte, Npt, rp, lay, Bc, m_p)

    rs = Ssb / (Ssb + Stb)

    rlm = (Ssb + Stb) / Sm

    p = (-0.15 * (1 + rs)) + 0.81

    Rl = np.exp(-1.33 * (1 + rs) * (rlm ** p))

    return Rl

def STHE_shellside_Rb(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware correction factor for bundle bypass.

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
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware bundle bypass correction factor.
    """

    # Reynolds number
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

    # Cbp parameter
    Cbp = np.ones(Ds.shape) * 4.5
    Cbp[Res > 100] = 3.7

    # Tube rows in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    rss = m_p["Nss"] / Ntcc

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and bundle
    Sb = STHE_shellside_Sb(Ds, L, Nb, m_p)

    # By-pass area ratio
    Fsbp = Sb / Sm

    Rb = np.exp(-Cbp * Fsbp * (1 - ((2 * rss) ** (1 / 3))))

    return Rb

def STHE_shellside_Idealcrossflowh(
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    ms: float,
    ros: float,
    mis: float,
    Cps: float,
    ks: float,
    m_p: dict,
):
    """
    Calculate the ideal shell-side cross-flow heat transfer coefficient.

    This function evaluates the ideal Bell-Delaware shell-side convective
    heat transfer coefficient before applying the correction factors.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    rp : float
        Tube pitch ratio.
    lay
        Tube layout.
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    Cps : float
        Shell-side specific heat capacity [J/(kg·K)].
    ks : float
        Shell-side thermal conductivity [W/(m·K)].
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Ideal shell-side heat transfer coefficient.
    """

    # Reynolds Number
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

    # Prandtl number
    Prs = Cps * mis / ks

    # Cross flow area
    Sm = STHE_shellside_Sm(
        Ds,
        dte,
        rp,
        lay,
        L,
        Nb,
        m_p,
    )

    # Mass flux
    Gs = ms / Sm

    # Bell-Delaware parameters
    pa1, pa2, pa3, pa4 = STHE_shellside_Nusseltparameters(
        Ds,
        dte,
        rp,
        lay,
        L,
        Nb,
        ms,
        ros,
        mis,
        m_p,
    )

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    par_a = pa3 / (1 + (0.14 * (Res ** pa4)))

    pji = pa1 * ((1.33 / (Ltp / dte)) ** par_a) * (Res ** pa2)

    phi = pji * Cps * Gs * (Prs ** (-2 / 3))

    return phi

def STHE_shellside_Jc(
    Ds: float,
    dte: float,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware window correction factor.

    Parameters
    ----------
    Ds : float
        Shell inside diameter [m].
    dte : float
        Tube outside diameter [m].
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware window correction factor.
    """

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut with the
    # circumference of the centers of the external tubes
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - 2 * Bc))

    # Tube fraction in window region
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Tube fraction in cross flow
    Fc = 1 - (2 * Fw)

    # Bell-Delaware window correction factor
    Jc = 0.55 + (0.72 * Fc)

    return Jc

def STHE_shellside_Jl(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware leakage correction factor.

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
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware leakage correction factor.
    """

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and baffle
    Ssb = STHE_shellside_Ssb(Ds, Bc, m_p)

    # Tube and baffle leakage area
    Stb = STHE_shellside_Stb(Ds, dte, Npt, rp, lay, Bc, m_p)

    rs = Ssb / (Ssb + Stb)

    rlm = (Ssb + Stb) / Sm

    # Bell-Delaware leakage correction factor
    Jl = (0.44 * (1 - rs)) + (
        (1 - (0.44 * (1 - rs))) * np.exp(-2.2 * rlm)
    )

    return Jl

def STHE_shellside_Jb1(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    ms: float,
    ros: float,
    mis: float,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware bundle bypass correction factor.

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
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware bundle bypass correction factor.
    """

    # Reynolds Number
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

    # Cbh parameter
    Cbh = np.ones(Ds.shape) * 1.35
    Cbh[Res > 100] = 1.25

    # Tube rows in the cross flow region
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # The ratio of number of sealing strips, Nss, by the number of
    # tube rows crossed between baffle tips in one baffle section
    rss = m_p["Nss"] / Ntcc

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Shell and bundle by-pass area
    Sb = STHE_shellside_Sb(Ds, L, Nb, m_p)

    Fsbp = Sb / Sm

    Jb1 = np.exp(-Cbh * Fsbp * (1 - ((2 * rss) ** (1 / 3))))

    return Jb1

def STHE_shellside_Jr(
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    Nb: int,
    ms: float,
    ros: float,
    mis: float,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the Bell-Delaware laminar-flow correction factor.

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
    L : float
        Tube length [m].
    Nb : int
        Number of baffles.
    ms : float
        Shell-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    Bc : float
        Baffle cut fraction.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Bell-Delaware laminar-flow correction factor.
    """

    # Reynolds Number
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

    # Tube rows in cross flow region
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Tube rows in window region
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Total number of tube rows crossed in the entire exchanger
    Nc = (Ntcc + Ntcw) * (Nb + 1)

    Jr1 = (10 / Nc) ** 0.18

    Jr2 = Jr1 + (((20 - Res) / 80) * (Jr1 - 1))

    Jr = Jr1
    Jr[Res > 20] = Jr2[Res > 20]
    Jr[Res > 100] = 1

    return Jr

def STHE_shellside_IdealcrossflowFrictionFactor(
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
):
    """
    Calculate the ideal shell-side cross-flow friction factor.

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
        Ideal shell-side cross-flow friction factor.
    """

    # Reynolds number
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

    # Friction factor parameters
    pb_1, pb_2, pb_3, pb_4 = STHE_shellside_DeltaPparameters(
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

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Bell-Delaware parameter
    par_b = pb_3 / (1 + (0.14 * (Res ** pb_4)))

    # Ideal shell-side friction factor
    fs = pb_1 * ((1.33 / (Ltp / dte)) ** par_b) * (Res ** pb_2)

    return fs

def STHE_shellside_IdealcrossflowDeltaP(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the ideal shell-side cross-flow pressure drop.

    Returns
    -------
    float
        Ideal shell-side cross-flow pressure drop [Pa].
    """

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Ideal shell-side friction factor
    fs = STHE_shellside_IdealcrossflowFrictionFactor(
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

    # Tube rows in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Mass flux
    Gs = ms / Sm

    DeltaPbi = 2 * fs * Ntcc * (1 / ros) * (Gs ** 2)

    return DeltaPbi

def STHE_shellside_crossflowDeltaP(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the shell-side cross-flow pressure drop.

    Returns
    -------
    float
        Shell-side cross-flow pressure drop [Pa].
    """

    # Correction factor for bundle bypass
    Rb = STHE_shellside_Rb(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p)

    # Correction factor for baffle leakage effects
    Rl = STHE_shellside_Rl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)

    # Ideal cross-flow pressure drop
    DPbi = STHE_shellside_IdealcrossflowDeltaP(
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

    DeltaPc = DPbi * (Nb - 1) * Rb * Rl

    return DeltaPc

def STHE_shellside_BaffleWidownDeltaP(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the shell-side baffle-window pressure drop.

    Returns
    -------
    float
        Shell-side baffle-window pressure drop [Pa].
    """

    # Reynolds number
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

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Window areas
    Swt, Swg, Sw = STHE_shellside_WindowAreas(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        Bc,
        m_p,
    )

    # Mass flux in window
    Gw = ms / ((Sm * Sw) ** (1 / 2))

    # Hydraulic diameter
    Dw = STHE_shellside_Dw(Ds, dte, Npt, rp, lay, Bc, m_p)

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Effective number of tube rows in the window
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Baffle spacing
    lbc = STHE_Lbc_func(L, Nb)

    # Correction factor for baffle leakage effects
    Rl = STHE_shellside_Rl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)

    # Laminar-flow pressure drop
    DPwlam = (
        Nb
        * Rl
        * (
            ((26 * Gw * mis) / ros)
            * ((Ntcw / (Ltp - dte)) + (lbc / (Dw ** 2)))
            + ((2 / ros) * (Gw ** 2))
        )
    )

    # Turbulent-flow pressure drop
    DPwturb = Nb * Rl * (2 + (0.6 * Ntcw)) * (1 / (2 * ros)) * (Gw ** 2)

    Delta_Pw = DPwlam
    Delta_Pw[Res >= 100] = DPwturb[Res >= 100]

    return Delta_Pw

def STHE_shellside_EndZonesDeltaP(
    ms: float,
    ros: float,
    mis: float,
    Ds: float,
    dte: float,
    rp: float,
    lay,
    L: float,
    Nb: int,
    Bc: float,
    m_p: dict,
):
    """
    Calculate the shell-side end-zone pressure drop.

    Returns
    -------
    float
        Shell-side end-zone pressure drop [Pa].
    """

    # Number of tube rows in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Effective number of tube rows in window
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Correction factor for bundle bypass
    Rb = STHE_shellside_Rb(
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

    Rs = 2

    # Ideal cross-flow pressure drop
    DPbi = STHE_shellside_IdealcrossflowDeltaP(
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

    DeltaPe = DPbi * Rb * Rs * (1 + (Ntcw / Ntcc))

    return DeltaPe