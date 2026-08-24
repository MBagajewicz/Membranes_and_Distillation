from . import Calculations_STHE_Reynolds_tubeside
from . import Calculations_STHE_frictionfactor


def STHE_Nusselt_tubeside(
    mt: float,
    rot: float,
    Cpt: float,
    mit: float,
    kt: float,
    thk: float,
    yfluid,
    Ds: float,
    dte: float,
    Npt: int,
    rp: float,
    lay,
    L: float,
    m_p: dict,
) -> float:
    """
    Calculate the tube-side Nusselt number.

    The tube-side Nusselt number is calculated according to the method
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
    Cpt : float
        Tube-side specific heat capacity [J/(kg·K)].
    mit : float
        Tube-side dynamic viscosity [Pa·s].
    kt : float
        Tube-side thermal conductivity [W/(m·K)].
    thk : float
        Tube wall thickness [m].
    yfluid
        Tube-side fluid identifier.
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
    m_p : dict
        Dictionary containing the model parameters.

    Returns
    -------
    float
        Tube-side Nusselt number.

    Raises
    ------
    ValueError
        If the selected tube-side method is not supported.
    """

    tube_method = m_p["Tube_Method"]

    if tube_method == "Dewiit_Saunders":

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

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side Prandtl number
        Prt = (Cpt * mit) / kt

        # Gnielinski correlation
        NutGni = (
            (ft / 8)
            * (Ret - 1000)
            * Prt
            / (1 + 12.7 * (ft / 8) ** (1 / 2) * (Prt ** (2 / 3) - 1))
        )

        # Hausen correlation
        NutHau = 3.66 + (
            (0.0668 * (dti / L) * Ret * Prt)
            / (1 + (0.04 * (((dti / L) * Ret * Prt) ** (2 / 3))))
        )

        # Sieder and Tate correlation
        NutSeT = 1.86 * (((Ret * Prt) / (L / dti)) ** (1 / 3))

        if Prt > 5:
            Nut = NutHau
            Nut[Ret > 2300] = NutGni[Ret > 2300]

        elif Prt <= 5:
            Nut = NutSeT
            Nut[NutSeT < 3.66] = 3.66
            Nut[Ret > 2300] = NutGni[Ret > 2300]

    elif tube_method == "Gnielinski":

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

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side Prandtl number
        Prt = (Cpt * mit) / kt

        # Gnielinski correlation
        Nut = (
            (ft / 8)
            * (Ret - 1000)
            * Prt
            / (1 + 12.7 * (ft / 8) ** (1 / 2) * (Prt ** (2 / 3) - 1))
        )

    elif tube_method == "Hausen":

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

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side Prandtl number
        Prt = (Cpt * mit) / kt

        # Hausen correlation
        Nut = 3.66 + (
            (0.0668 * (dti / L) * Ret * Prt)
            / (1 + (0.04 * (((dti / L) * Ret * Prt) ** (2 / 3))))
        )

    elif tube_method == "Sieder_Tate":

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

        # Tube inside diameter
        dti = dte - (2 * thk)

        # Tube-side Prandtl number
        Prt = (Cpt * mit) / kt

        # Sieder and Tate correlation
        Nut = 1.86 * (((Ret * Prt) / (L / dti)) ** (1 / 3))

    elif tube_method == "Dittus_Boelter":

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

        # Tube-side Prandtl number
        Prt = (Cpt * mit) / kt

        # Dittus-Boelter exponent
        if yfluid == "cold_stream":
            n = 0.4
        else:
            n = 0.3

        # Dittus-Boelter correlation
        Nut = 0.023 * Ret ** 0.8 * Prt ** n

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

    return Nut