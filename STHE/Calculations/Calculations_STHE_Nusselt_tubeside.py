#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          01-Dec-2024     Mariana Mello             Proposed
#   0.2          28-Feb-2025     Mariana Mello             Add options of Tube Method
#   0.3          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
#endregion


#region Import Library
from STHE.Calculations import Calculations_STHE_Reynolds_tubeside, Calculations_STHE_frictionfactor
#endregion

#region Calculations

def STHE_Nusselt_tubeside(mt, rot, Cpt, mit, kt, thk, yfluid, Ds, dte, Npt, rp, lay, L, m_p):
    # Tube-side Nusselt number
    if m_p['Tube_Method'] == "Dewiit_Saunders":
        # Reynolds number
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)

        # Friction factor
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)

        # Inside diameter/fouling diameter
        dti = dte - 2 * thk
        #df = dti - 2 * ft_thk

        # Prandtl Number
        Prt = Cpt * mit / kt
        #print('Prt',Prt)

        # Gnielinski correlation
        NutGni = (ft/8) * (Ret - 1000) * Prt / (1 + 12.7 * (ft/8)**(1/2) * (Prt**(2/3) - 1))
        #print('NutGni',NutGni)

        # Hausen correlation
        #NutHau = 3.66 + ((0.0668*(df/L)*Ret*Prt) / (1 + (0.04*(((df/L)*Ret*Prt)**(2/3)))))
        NutHau = 3.66 + ((0.0668 * (dti/L) * Ret * Prt) / (1 + (0.04 * (((dti/L) * Ret * Prt) ** (2 / 3)))))
        #print('NutHAU', NutHau)

        # Sieder and Tate correlation
        #NutSeT = 1.86 * (((Ret*Prt) / (L/df))**(1/3))
        NutSeT = 1.86 * (((Ret * Prt) / (L/dti)) ** (1 / 3))

        if Prt > 5:
            Nut = NutHau
            Nut[Ret > 2300] = NutGni[Ret > 2300]
            #print('Nut1',Nut)
        elif Prt <= 5:
            Nut = NutSeT
            Nut[NutSeT < 3.66] = 3.66
            Nut[Ret > 2300] = NutGni[Ret > 2300]
            #print('Nut2', Nut)

    elif m_p['Tube_Method'] == 'Gnielinski':
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        # Inside diameter/fouling diameter
        dti = dte - 2 * thk
        #df = dti - 2 * ft_thk

        Prt = Cpt * mit / kt

        # Gnielinski correlation
        NutGni = (ft / 8) * (Ret - 1000) * Prt / (1 + 12.7 * (ft / 8) ** (1 / 2) * (Prt ** (2 / 3) - 1))

        Nut = NutGni

    elif m_p['Tube_Method'] == 'Hausen':
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        # Inside diameter/fouling diameter
        dti = dte - 2 * thk
        # df = dti - 2 * ft_thk

        Prt = Cpt * mit / kt

        # Hausen correlation
        NutHau = 3.66 + ((0.0668 * (dti/L) * Ret * Prt) / (1 + (0.04 * (((dti/L) * Ret * Prt) ** (2 / 3)))))

        Nut = NutHau

    elif m_p['Tube_Method'] == 'Sieder_Tate':
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)
        ft = Calculations_STHE_frictionfactor.STHE_tubeside_frictionfactor(mt, rot, mit, Ds, dte, Npt, rp, lay, thk, m_p)
        # Inside diameter/fouling diameter
        dti = dte - 2 * thk
        # df = dti - 2 * ft_thk

        Prt = Cpt * mit / kt

        # Sieder and Tate correlation
        #NutST = 1.86 * (((Ret*Prt) / (L/df))**(1/3))
        NutST = 1.86 * (((Ret * Prt) / (L/dti)) ** (1 / 3))

        Nut = NutST

    elif m_p['Tube_Method'] == "Dittus_Boelter":
        Ret = Calculations_STHE_Reynolds_tubeside.STHE_Reynolds_tubeside(mt, rot, mit, thk, Ds, dte, Npt, rp, lay, m_p)
        Prt = Cpt * mit / kt
        if yfluid == 'cold_stream':
            n = 0.4
        else:
            n = 0.3
        Nut = 0.023 * Ret**0.8 * Prt**n


    else:
        raise ValueError(f"Invalid Tube Method: {m_p['Tube_Method']}.")

    # print('Nut',Nut)
    return Nut

#endregion
