from . import Calculations_STHE_Reynolds_tubeside
from . import Calculations_STHE_velocity_tubeside
from . import Calculations_STHE_frictionfactor

import numpy as np


def STHE_tubeside_DeltaP(
    mt: float,
    rot: float,
    mit: float,
    thk: float,
    Ds: float,
    dte: float,
    Npt,
    rp: float,
    lay,
    L: float,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side pressure drop.

    The tube-side pressure drop is calculated according to the method
    specified in ``m_p["Tube_Method"]``.

    Supported methods
    -----------------
    - Dewiit_Saunders
    - Gnielinski
    - Hausen
    - Sieder_Tate
    - Dittus_Boelter

    Parameters
    ----------
    mt : float
        Tube-side mass flow rate [kg/s].
    rot : float
        Tube-side fluid density [kg/m³].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
    thk : float
        Tube wall thickness [m].
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
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-side pressure drop [Pa].

    Raises
    ------
    ValueError
        If the selected tube-side method is not supported.
    """

    tube_method = m_p["Tube_Method"]

    if tube_method == "Dewiit_Saunders":

        # Tube-side velocity
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
            mt,
            rot,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side friction factor
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(
            mt,
            rot,
            mit,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            thk,
            m_p,
        )

        # Inlet and outlet loss coefficient
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side pressure drop
        DPt = (
            (rot * ft * Npt * L * vt ** 2) / (2 * dti)
            + (rot * K * Npt * vt ** 2) / 2
        )

    elif tube_method == "Gnielinski":

        # Tube-side velocity
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
            mt,
            rot,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side friction factor
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(
            mt,
            rot,
            mit,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            thk,
            m_p,
        )

        # Inlet and outlet loss coefficient
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side pressure drop
        DPt = (
            (rot * ft * Npt * L * vt ** 2) / (2 * dti)
            + (rot * K * Npt * vt ** 2) / 2
        )

    elif tube_method == "Hausen":

        # Tube-side velocity
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
            mt,
            rot,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side friction factor
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(
            mt,
            rot,
            mit,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            thk,
            m_p,
        )

        # Inlet and outlet loss coefficient
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side pressure drop
        DPt = (
            (rot * ft * Npt * L * vt ** 2) / (2 * dti)
            + (rot * K * Npt * vt ** 2) / 2
        )

    elif tube_method == "Sieder_Tate":

        # Tube-side velocity
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
            mt,
            rot,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side friction factor
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(
            mt,
            rot,
            mit,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            thk,
            m_p,
        )

        # Inlet and outlet loss coefficient
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side pressure drop
        DPt = (
            (rot * ft * Npt * L * vt ** 2) / (2 * dti)
            + (rot * K * Npt * vt ** 2) / 2
        )

    elif tube_method == "Dittus_Boelter":

        # Tube-side velocity
        vt = Calculations_STHE_velocity_tubeside.STHE_tubeside_velocity(
            mt,
            rot,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side Reynolds number
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(
            mt,
            rot,
            mit,
            thk,
            Ds,
            dte,
            Npt,
            rp,
            lay,
            m_p,
        )

        # Tube-side friction factor
        ft = 0.014 + 1.056 / (Ret ** 0.42)

        # Inlet and outlet loss coefficient
        K = 1.6 * np.ones(Npt.shape)
        K[Npt == 1] = 0.9

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side pressure drop
        DPt = (
            (rot * ft * Npt * L * vt ** 2) / (2 * dti)
            + (rot * K * Npt * vt ** 2) / 2
        )

    else:

        raise ValueError(
            f"Unknown tube-side method '{tube_method}'. "
            "Supported methods are "
            "'Dewiit_Saunders', "
            "'Gnielinski', "
            "'Hausen', "
            "'Sieder_Tate' and "
            "'Dittus_Boelter'."
        )

    return DPt