"""
####################################################################################################################
STHE Library
Calculation: Total Annual Cost (TAC)
####################################################################################################################
"""

from . import Calculations_STHE_DeltaPtubeside
from . import Calculations_STHE_DeltaPshellside
from . import Calculations_STHE_area


def STHE_TAC(
    int_rate: float,
    n: int,
    par_a: float,
    par_b: float,
    Nop: float,
    pc: float,
    eta: float,
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    ms: float,
    mt: float,
    ros: float,
    rot: float,
    mis: float,
    mit: float,
    thk: float,
    Nb: int,
    Bc: float,
    m_p: dict,
) -> float:
    """
    Calculate the total annual cost of the shell-and-tube heat exchanger.

    The total annual cost includes the annualized capital cost and the
    yearly operating costs associated with the shell-side and tube-side
    pressure drops.

    Parameters
    ----------
    int_rate : float
        Interest rate.
    n : int
        Annualization period [years].
    par_a : float
        Capital cost correlation coefficient.
    par_b : float
        Capital cost correlation exponent.
    Nop : float
        Number of operating hours per year [h/year].
    pc : float
        Electricity cost [currency/kWh].
    eta : float
        Pump efficiency.
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
    ms : float
        Shell-side mass flow rate [kg/s].
    mt : float
        Tube-side mass flow rate [kg/s].
    ros : float
        Shell-side fluid density [kg/m³].
    rot : float
        Tube-side fluid density [kg/m³].
    mis : float
        Shell-side dynamic viscosity [Pa·s].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
    thk : float
        Tube wall thickness [m].
    Nb : int
        Number of baffles.
    Bc : float
        Baffle cut.
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Total annual cost.
    """

    # Capital recovery factor
    r = (int_rate * (1 + int_rate) ** n) / (((1 + int_rate) ** n) - 1)

    # Heat transfer area
    Atot = Calculations_STHE_area.STHE_area(
        Ds,
        dte,
        Npt,
        rp,
        lay,
        L,
        m_p,
    )

    # Capital cost
    Cap = par_a * Atot**par_b

    # Shell-side pressure drop
    deltaPs = Calculations_STHE_DeltaPshellside.STHE_shellside_DeltaP(
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

    # Tube-side pressure drop
    deltaPt = Calculations_STHE_DeltaPtubeside.STHE_tubeside_DeltaP(
        mt,
        rot,
        mit,
        thk,
        Ds,
        dte,
        Npt,
        rp,
        lay,
        L,
        m_p,
    )

    # Yearly operating cost for the shell-side stream
    Cop_s = Nop * (pc / 1000) * ((deltaPs * ms) / (eta * ros))

    # Yearly operating cost for the tube-side stream
    Cop_t = Nop * (pc / 1000) * ((deltaPt * mt) / (eta * rot))

    # Total annual cost
    TAC = r * Cap + Cop_s + Cop_t

    return TAC
