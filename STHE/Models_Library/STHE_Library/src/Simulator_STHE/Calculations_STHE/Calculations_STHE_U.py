from . import Calculations_STHE_hshellside
from . import Calculations_STHE_htubeside

import numpy as np


def STHE_overall_coefficient(
    mt: float,
    rot: float,
    Cpt: float,
    mit: float,
    kt: float,
    Rft: float,
    ms: float,
    ros: float,
    Cps: float,
    mis: float,
    ks: float,
    Rfs: float,
    thk: float,
    ktube: float,
    yfluid,
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
    Calculate the overall heat transfer coefficient.

    The overall heat transfer coefficient is calculated from the tube-side
    and shell-side heat transfer coefficients, including wall conduction
    and fouling thermal resistances.

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    Cpt : float
        Tube-side specific heat capacity [J/(kg·K)].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
    kt : float
        Tube-side thermal conductivity [W/(m·K)].
    Rft : float
        Tube-side fouling thermal resistance [m²·K/W].
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
    Rfs : float
        Shell-side fouling thermal resistance [m²·K/W].
    thk : float
        Tube wall thickness [m].
    ktube : float
        Tube thermal conductivity [W/(m·K)].
    yfluid
        Tube-side fluid composition.
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
        Overall heat transfer coefficient [W/(m²·K)].
    """

    # Tube inside diameter
    dti = dte - (2 * thk)

    # Tube-side heat transfer coefficient
    ht = Calculations_STHE_htubeside.STHE_h_tubeside(
        mt,
        rot,
        Cpt,
        mit,
        kt,
        thk,
        yfluid,
        Ds,
        dte,
        Npt,
        rp,
        lay,
        L,
        m_p,
    )

    # Shell-side heat transfer coefficient
    hs = Calculations_STHE_hshellside.STHE_h_shellside(
        ms,
        ros,
        Cps,
        mis,
        ks,
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

    # Overall heat transfer coefficient
    U = 1 / (
        (1 / ht) * (dte / dti)
        + Rft * (dte / dti)
        + dte * np.log(dte / dti) / (2 * ktube)
        + Rfs
        + (1 / hs)
    )

    return U


