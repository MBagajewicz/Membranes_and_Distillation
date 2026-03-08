#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          2025            Andre Nahes               Original
#   0.2          28-Feb-2025     Mariana Mello             Reorganized
#   0.3          04-May-2025     Miguel Bagajewicz         Revision
#   0.4          07-May-2025     Mariana Mello             Fix error in Ntcc/Jr
#   0.5          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
#   0.6          04-Jun-2025     Mariana Mello             Minor changes
##################################################################################################################
#endregion

#region Import Library
import numpy as np
from STHE.Calculations import Calculations_STHE_Reynolds_shellside, Calculations_STHE_countingtable
from math import pi
# endregion

#################################################################################################################

# region Calculations: Parameters

def STHE_shellside_Nusseltparameters(Ds, dte, rp, lay, L, Nb, ms, ros, mis, m_p):
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)
    #print('Res',Res)

    CondLay30 = Res < -10e10   # 30° (lay = 2)
    CondLay45 = Res < -10e10   # 45° (lay = 1)
    CondLay90 = Res < -10e10   # 90° (lay = 3)
    CondRes   = Res < -10e10

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

    # 1° faixa de reynolds

    pa_1[CondLay30] = 1.4
    pa_1[CondLay45] = 1.55
    pa_1[CondLay90] = 0.97

    pa_2[:] = -0.667

    # 2° faixa de reynolds

    CondRes[Res > 10] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 1.36
    pa_1[CondInter45] = 0.498
    pa_1[CondInter90] = 0.9

    pa_2[CondInter30] = -0.657
    pa_2[CondInter45] = -0.656
    pa_2[CondInter90] = -0.631

    # 3° faixa de reynolds

    CondRes   = Res < -10e10
    CondRes[Res > 1e2] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.593
    pa_1[CondInter45] = 0.73
    pa_1[CondInter90] = 0.408

    pa_2[CondInter30] = -0.477
    pa_2[CondInter45] = -0.5
    pa_2[CondInter90] = -0.46

    # 4° faixa de reynolds

    CondRes   = Res < -10e10
    CondRes[Res > 1e3] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.321
    pa_1[CondInter45] = 0.37
    pa_1[CondInter90] = 0.107

    pa_2[CondInter30] = -0.388
    pa_2[CondInter45] = -0.396
    pa_2[CondInter90] = -0.266

    # 5° faixa de reynolds

    CondRes   = Res < -10e10
    CondRes[Res > 1e4] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pa_1[CondInter30] = 0.321
    pa_1[CondInter45] = 0.37
    pa_1[CondInter90] = 0.37

    pa_2[CondInter30] = -0.388
    pa_2[CondInter45] = -0.396
    pa_2[CondInter90] = -0.395

    pa_3[CondLay30] = 1.45
    pa_3[CondLay45] = 1.93
    pa_3[CondLay90] = 1.187

    pa_4[CondLay30] = 0.519
    pa_4[CondLay45] = 0.5
    pa_4[CondLay90] = 0.37

    return pa_1, pa_2, pa_3, pa_4

def STHE_shellside_DeltaPparameters(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p):

    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    CondLay30 = Res < -10e10 # 30° (lay = 2)
    CondLay45 = Res < -10e10 # 45° (lay = 1)
    CondLay90 = Res < -10e10 # 90° (lay = 3)
    CondRes   = Res < -10e10

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

    # 1° faixa de reynolds

    pb_1[CondLay30] = 48
    pb_1[CondLay45] = 32
    pb_1[CondLay90] = 35

    pb_2[:] = -1

    # 2° faixa de reynolds

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

    # 3° faixa de reynolds

    CondRes   = Res < -10e10
    CondRes[Res > 1e2] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 4.57
    pb_1[CondInter45] = 3.5
    pb_1[CondInter90] = 6.09

    pb_2[CondInter30] = -0.476
    pb_2[CondInter45] = -0.476
    pb_2[CondInter90] = -0.602

    # 4° faixa de reynolds

    CondRes   = Res < -10e10
    CondRes[Res > 1e3] = True
    CondInter30 = np.logical_and(CondRes, CondLay30)
    CondInter45 = np.logical_and(CondRes, CondLay45)
    CondInter90 = np.logical_and(CondRes, CondLay90)

    pb_1[CondInter30] = 0.486
    pb_1[CondInter45] = 0.333
    pb_1[CondInter90] = 0.0815

    pb_2[CondInter30] = -0.152
    pb_2[CondInter45] = -0.136
    pb_2[CondInter90] =  0.022

    # 5° faixa de reynolds

    CondRes   = Res < -10e10
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

    pb_3[CondLay30] = 7
    pb_3[CondLay45] = 6.59
    pb_3[CondLay90] = 6.3

    pb_4[CondLay30] = 0.5
    pb_4[CondLay45] = 0.52
    pb_4[CondLay90] = 0.378

    #print('param DP',pb_1, pb_2, pb_3, pb_4)

    return pb_1, pb_2, pb_3, pb_4

# endregion

#################################################################################################################

# region Calculations: General

def STHE_Lbb_func(Ds, m_p):

    #if len(m_p['Lbb_g']) == 0:
    Lbb = 0.0048*Ds + 0.0128
    #else:
    #    Lbb = np.array(m_p['Lbb_g'])
    #print('Lbb',Lbb)

    return Lbb

def STHE_Ltb_func(Ds, dte, m_p):
    # Create a NumPy array Ltb of the same shape as Ds, filled with the value 0.8e-3 (i.e., 0.0008)
    # Lbmax is the same but filled with 0.9.

    Ltb = np.ones(Ds.shape) * 0.8e-3
    Lbmax = np.ones(Ds.shape) * 0.9

    # Initializes three boolean arrays (Cond_1, Cond_2, and CondInter) that are all initially False
    # (assuming Ds <= 10e10 everywhere).
    # Using Ds > 10e10 as a base is just a placeholder for all-False arrays (as 10e10 is very large).

    Cond_1 = Ds > 10e10
    Cond_2 = Ds > 10e10
    Cond_3 = Ds > 10e10
    CondInter = Ds > 10e10

    Cond_3[dte >= 0.0195] = True
    Lbmax[Cond_3] = 52 * dte[Cond_3] + 0.532
    Lbmax[~Cond_3] = 68 * dte[~Cond_3] + 0.228

    # Wherever the dte array has values ≤ 0.03175, the corresponding elements in Cond_1 are set to True.
    # If Lbmax is greater than 0.9, set Cond_2 to True.

    Cond_1[dte <= 31.75e-3] = True
    Cond_2[Lbmax > 0.9] = True

    # CondInter is updated to be True only where both Cond_1 and Cond_2 are True.
    CondInter = np.logical_and(Cond_1, Cond_2)

    # For all positions where CondInter is True, set the value of Ltb to 0.4e-3 (i.e., 0.0004).
    Ltb[CondInter] = 0.4e-3
    #print('Ltb', Ltb)

    return Ltb

def STHE_Lsb_func(Ds, m_p):

    #Lsb = 3.1e-3 + 0.004*Ds
    Lsb = 1.6e-3 + 0.004*Ds
    #print('Lsb', Lsb)

    return Lsb

def STHE_Ltp_func(rp, dte):
    Ltp = rp*dte
    #print('Ltp',Ltp)
    return Ltp

def STHE_Lbc_func(L, Nb):
    Lbc = L / (Nb + 1)
    # print('lbc',lbc)
    return Lbc

def STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p):
    # Cross flow area
    # fts_thk = fts_thk * 0
    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb
    #print('Dotl', Dotl)

    # Circumference of the centers of the external tube
    Dctl = Dotl - dte
    #print('Dctl',Dctl)

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Effective pitch
    Ltpeff = np.ones(lay.shape) * Ltp
    Ltpeff[lay == 3] = 0.707 * Ltp[lay == 3]

    # Baffle spacing
    lbc = STHE_Lbc_func(L, Nb)

    # Cross flow area considering the hydraulic impact
    #Sm = lbc * (Lbb - 4*fts_thk + Dctl * ((Ltp - dte - 2*fts_thk) / Ltpeff))

    # Cross flow area considering the hydraulic impact
    # Sm = lbc * (Lbb + Dctl * ( ( Ltp - dte - 2 * fts_thk ) / Ltpeff ) )

    # Cross flow area without considering the hydraulic impact

    Sm = lbc * (Lbb + Dctl * ((Ltp - dte) / Ltpeff))
    #print('Sm', Sm)

    return Sm

def STHE_shellside_Ssb(Ds, Bc, m_p):
    # By-pass area between the shell and baffles

    #fts_thk = fts_thk * 0

    # Central angle of the rope relative to the cutting of the baffle in relation to the diameter of the shell
    teta_Ds = 2*np.arccos((1 - (2*Bc)))
    #print('teta_Ds',teta_Ds)

    # Shell - baffle leakage
    Lsb = STHE_Lsb_func(Ds, m_p)

    # By-pass area considering the fouling thickness
    #Ssb = pi * Ds * ( ( Lsb - 2 * fts_thk) / 2) * (((2 * pi) - teta_Ds) / (2 * pi))

    # By-pass area considering the fouling thickness
    #Ssb = pi * Ds * (Lsb/2) * (((2 * pi) - teta_Ds) / (2 * pi))

    #Ssb[Ssb < 0] = 1e-15

    # No fouling model equation (original one)
    Ssb = pi * Ds * (Lsb/2) * (((2*pi) - teta_Ds)/(2*pi))
    #print('Ssb',Ssb)

    return Ssb

def STHE_shellside_Stb(Ds, dte, Npt, rp, lay, Bc, m_p):
    # Leakage area between the tube and the baffles

    #fts_thk = fts_thk * 0

    # Number of tubes (counting table)
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(Ds, dte, Npt, rp, lay, m_p)

    # Tube - baffle leakage
    Ltb = STHE_Ltb_func(Ds, dte, m_p)

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut with the circumference of the centers of the external tubes
    teta_ctl = 2 * np.arccos((Ds/Dctl) * (1 - 2*Bc))
    #print('teta_ctl',teta_ctl)

    # Tube fraction in the window
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)
    #print('Fw',Fw)

    # Fouling model
    #Stb = Ntt * (1 - Fw) * ((pi / 4) * ((dte + Ltb) ** 2 - (dte + 2 * fts_thk) ** 2))

    # Fouling model is ignored for the time being
    Stb = Ntt * (1 - Fw) * ((pi/4) * (((dte + Ltb)**2) - (dte**2)))

    # No fouling model
    #Stb = max(0,Ntt * (1 - Fw) * ((pi / 4) * ((dte + Ltb) ** 2 - (dte ** 2))))

    Stb[Stb < 0] = 0
    #print('Stb', Stb)

    return Stb

def STHE_shellside_Sb(Ds, L, Nb, m_p):
    # By-pass area between the shell and tube bundle

    #fts_thk = fts_thk * 0

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Baffle spacing
    lbc = STHE_Lbc_func(L, Nb)

    # By pass area considering the hydraulic impact with the fouling model
    #Sb = (lbc) * ((Lbb - 4 * fts_thk))

    # By pass area considering the hydraulic impact with the fouling model
    # Sb = (lbc) * ((Lbb - 2 * fts_thk))

    #Sb[Sb < 0] = 0

    # Lpl
    Lpl = 0
    #print('Lpl',Lpl)

    # By pass area without considering the hydraulic impact with the fouling model
    Sb = lbc*((Ds - Dotl)+Lpl)
    #print('Sb',Sb)

    return Sb

def STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc):
    # Number of tube rows in cross flow (without window tubes)

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Tubes distance in the flow direction
    Lpp = Ltp  # Lpp for square bundle
    Lpp[lay == 2] = 0.866 * Ltp[lay == 2]  # Lpp for triangular bundle
    Lpp[lay == 3] = 0.707 * Ltp[lay == 3]  # Lpp for rotate triangular bundle
    #print('Lpp',Lpp)

    Ntcc = (Ds / Lpp) * (1 - (2*Bc))
    #print('Ntcc',Ntcc)

    return Ntcc

def STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p):
    # Number of tube rows in window region

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Tubes distance in the flow direction
    Lpp = Ltp  # Lpp for square bundle
    Lpp[lay == 2] = 0.866 * Ltp[lay == 2] # Lpp for triangular bundle
    Lpp[lay == 3] = 0.707 * Ltp[lay == 3]  # Lpp for rotate triangular bundle

    Ntcw = (0.8 / Lpp) * (((Ds * Bc)) - ((Ds - Dctl) / 2))
    #print('Ntcw',Ntcw)

    return Ntcw

def STHE_shellside_WindowAreas(Ds, dte, Npt, rp, lay, Bc, m_p):
    # Window areas - Area occupied by the tubes (Swt), Total window area (Swg), Free window area (Sw)

    # Number of tubes (Counting table)
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(Ds, dte, Npt, rp, lay, m_p)

    # Central angle of the rope relative to the cutting of the baffle in relation to the diameter of the shell
    teta_Ds = 2 * np.arccos((1 - (2 * Bc)))

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut with the circumference of the centers of the external tubes
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - 2 * Bc))

    # Tube fraction in the window
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Number of tubes in the window
    Ntw = (Ntt * Fw)
    #print('Ntw',Ntw)

    # Area occupied by the tubes // Á (Swt)
    #Swt = Ntw * (pi / 4) * (dte + 2 * fts_thk) ** 2
    Swt = Ntw * ((pi/4) * (dte**2))

    # Window area (Swg)
    # Fouling model
    #Swg = (pi / 4) * (Ds - 2 * fts_thk) ** 2 * ((teta_Ds - np.sin(teta_Ds)) / (2 * pi))

    # No fouling
    Swg = (pi/4)*(Ds**2) * ((teta_Ds - np.sin(teta_Ds))/(2 * pi))

    # Window free area
    Sw = Swg - Swt
    #print('Swg', Swg)
    #print('Swt', Swt)
    #print('Sw', Sw)

    return Swt, Swg, Sw

def STHE_shellside_Dw(Ds, dte, Npt, rp, lay, Bc, m_p):
    # Hydraulic diameter

    # Total number of tubes (Counting table)
    Ntt = Calculations_STHE_countingtable.STHE_counting_table(Ds, dte, Npt, rp, lay, m_p)

    # Central angle of the rope relative to the cutting of the baffle in relation to the diameter of the shell
    teta_Ds = 2 * np.arccos((1 - (2 * Bc)))

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut with the circumference of the centers of the external tubes
    teta_ctl = 2 * np.arccos((Ds / Dctl) * (1 - 2 * Bc))

    # Tube fraction in the window (Fw)
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2 * pi)

    # Number of tubes in the window (Ntw)
    Ntw = (Ntt * Fw)

    # Window areas
    Swt, Swg, Sw = STHE_shellside_WindowAreas(Ds, dte, Npt, rp, lay, Bc, m_p)

    # Fouling model
    #Dw = (4 * Sw) / ((pi * (dte + 2 * fts_thk) * Ntw) + (pi * (Ds - 2 * fts_thk) * (teta_Ds / (2 * pi))))

    # No fouling model
    Dw = (4*Sw) / ((pi*dte*Ntw) + (pi*Ds*(teta_Ds)))
    #print('Dw',Dw)

    return Dw

def STHE_shellside_Rl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    # Correction factor for baffle leakage effects

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and baffle
    Ssb = STHE_shellside_Ssb(Ds, Bc, m_p)

    # Tube and baffle leakage area (Stb)
    Stb = STHE_shellside_Stb(Ds, dte, Npt, rp, lay, Bc, m_p)

    rs = Ssb / (Ssb + Stb)
    #print('rs',rs)

    rlm = (Ssb + Stb) / Sm
    #print('rlm',rlm)

    p = (-0.15*(1+rs)) + 0.81
    #print('p',p)

    Rl = np.exp(-1.33 * (1 + rs) * (rlm**p))
    #print('Rl',Rl)

    return Rl

def STHE_shellside_Rb(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p):
    # Correction factor for bundle bypass

    # Reynolds Number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Cbp parameters
    Cbp = np.ones(Ds.shape)*4.5
    Cbp[Res > 100] = 3.7
    #print('Cbp',Cbp)

    # Tube rows in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    rss = m_p['Nss'] / Ntcc
    #print('rss',rss)

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and bundle
    Sb = STHE_shellside_Sb(Ds, L, Nb, m_p)

    # By-pass area between the shell and bundle and the cross flow area ratio (Fsbp)
    Fsbp = Sb / Sm
    #print('Fsbp',Fsbp)

    Rb = np.exp(- Cbp * Fsbp * (1 - ((2*rss)**(1/3))))
    #print('Rb',Rb)

    return Rb

# endregion

#################################################################################################################

# region Calculations: Convective Coefficient shell-side

def STHE_shellside_Idealcrossflowh(Ds, dte, rp, lay, L, Nb, ms, ros, mis, Cps, ks, m_p):
    # Convective heat transfer coefficient

    # Reynolds Number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Prandtl number
    #Prs = m_p['Cps'] * m_p['mis'] / m_p['ks']
    Prs = Cps*mis / ks
    #print('Prs',Prs)

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Mass flux
    #Gs = m_p['ms'] / Sm
    Gs = ms / Sm
    #print('Gs',Gs)

    # Model parameters
    pa1, pa2, pa3, pa4 = STHE_shellside_Nusseltparameters(Ds, dte, rp, lay, L, Nb, ms, ros, mis, m_p)

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    par_a = pa3 / (1 + (0.14*(Res**pa4)))

    #pji = pa1 * (1.33 / (Ltp / (dte + 2 * fts_thk))) ** ( pa3 / (1 + 0.14 * Res ** pa4)) * Res ** pa2
    #pji = pa1 * (1.33/(Ltp/dte))**(pa3 / (1 + 0.14*Res**pa4)) * Res**pa2
    pji = pa1 * ((1.33 / (Ltp / dte))**par_a) * (Res**pa2)
    #print('pji',pji)

    #phi = pji * m_p['Cps'] * Gs * (Prs ** (-2 / 3))
    phi = pji*Cps*Gs*(Prs**(-2/3))
    #print('phi',phi)

    return phi

def STHE_shellside_Jc(Ds, dte, Bc, m_p):
    # Segmental baffle window correction

    # Shell - bundle leakage
    Lbb = STHE_Lbb_func(Ds, m_p)

    # Circumference of tube bundle
    Dotl = Ds - Lbb

    # Circumference of the centers of the external tubes
    Dctl = Dotl - dte

    # Central angle of the intersection of the baffle cut with the circumference of the centers of the external tubes
    teta_ctl = 2 * np.arccos((Ds/Dctl) * (1 - 2*Bc))

    # Tube fraction in window region (Fw)
    Fw = (teta_ctl - np.sin(teta_ctl)) / (2*pi)

    # Tube fraction in cross flow
    Fc = 1 - (2*Fw)
    #print('Fc',Fc)

    Jc = 0.55 + (0.72*Fc)
    #print('Jc',Jc)

    return Jc

def STHE_shellside_Jl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    # Correction factor for baffle leakeage effects

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # By-pass area between the shell and baffle
    Ssb = STHE_shellside_Ssb(Ds, Bc, m_p)

    # Tube and baffle leakage area
    Stb = STHE_shellside_Stb(Ds, dte, Npt, rp, lay, Bc, m_p)

    rs = Ssb / (Ssb + Stb)

    rlm = (Ssb + Stb) / Sm

    Jl = (0.44*(1-rs)) + ((1-(0.44*(1-rs)))*np.exp(-2.2*rlm))

    return Jl

def STHE_shellside_Jb1(Ds, dte, Npt, rp, lay, ms, ros, mis, L, Nb, Bc, m_p):
    # Correction factor for bundle bypass

    # Reynolds Number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Cbp parameter
    Cbh = np.ones(Ds.shape)*1.35
    Cbh[Res > 100] = 1.25
    #print('Cbh',Cbh)

    # Tube rows in the cross flow region
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    #The ratio of number of sealing strips, Nss, by the number of tube rows crossed between baffle tips in one baffle section
    rss = m_p['Nss'] / Ntcc

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Shell and bundle by-pass area
    Sb = STHE_shellside_Sb(Ds, L, Nb, m_p)

    Fsbp = Sb / Sm

    Jb1 = np.exp(- Cbh * Fsbp * (1 - ((2*rss)**(1/3))))

    return Jb1

def STHE_shellside_Jr(Ds, dte, Npt, rp, lay, L, Nb, ms, ros, mis, Bc, m_p):
    # Correction factor for laminar flow

    # Reynolds Number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Tube rows in cross flow region
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Tube rows in window region
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Total number of tubes rows crossed in the entire exchanger
    Nc = (Ntcc + Ntcw) * (Nb + 1)
    #print('Nc',Nc)

    Jr1 = (10/Nc)**0.18

    Jr2 = Jr1 + (((20-Res)/80) * (Jr1 - 1))

    Jr = Jr1
    Jr[Res > 20] = Jr2[Res > 20]
    Jr[Res > 100] = 1

    return Jr

# endregion

#################################################################################################################

# region Calculations: Friction Factor

def STHE_shellside_IdealcrossflowFrictionFactor(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p):
    # Ideal shell-side cross flow friction factor

    # Reynolds number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Friction factor parameters
    pb_1, pb_2, pb_3, pb_4 = STHE_shellside_DeltaPparameters(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)
    #print('param b', pb_1, pb_2, pb_3, pb_4 )

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Model considering the fouling layer
    #fs = pb_1 * (1.33 / (Ltp / (dte + 2 * fts_thk))) ** (pb_3 / (1 + 0.14 * Res ** pb_4)) * Res ** pb_2

    # Model without considering the fouling layer
    par_b = pb_3 / (1 + (0.14*(Res**pb_4)))
    #print('par_b',par_b)

    #fs = pb_1 * (1.33 / (Ltp/dte)) ** (pb_3 / (1 + 0.14 * Res ** pb_4)) * Res ** pb_2
    fs = pb_1 * ((1.33/(Ltp/dte))**par_b) * (Res**pb_2)
    #print('fs',fs)

    return fs

# endregion

#################################################################################################################

# region Calculations: Pressure Drop shell-side

def STHE_shellside_IdealcrossflowDeltaP(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p):
    # Ideal shell-side cross flow pressure drop

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # ideal cross flow friction factor
    fs = STHE_shellside_IdealcrossflowFrictionFactor(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Tube row in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Mass flux
    #Gs = m_p['ms'] / Sm
    Gs = ms / Sm

    #DeltaPbi = 2 * fs * Ntcc * (1 / m_p['ros']) * (Gs ** 2)
    DeltaPbi = 2 * fs * Ntcc * (1 / ros) * (Gs ** 2)
    #print('DeltaPbi', DeltaPbi)

    return DeltaPbi

def STHE_shellside_crossflowDeltaP(ms, ros, mis, Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    # Cross flow pressure drop

    # Correction factor for bundle bypass
    Rb = STHE_shellside_Rb(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p)

    # Correction factor for baffle leakeage effects
    Rl = STHE_shellside_Rl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)

    # Ideal cross flow pressure drop
    DPbi = STHE_shellside_IdealcrossflowDeltaP(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p)

    DeltaPc = DPbi * (Nb - 1) * Rb * Rl
    #print('DPc',DeltaPc)

    return DeltaPc

def STHE_shellside_BaffleWidownDeltaP(ms, ros, mis, Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p):
    # Baffle window pressure drop

    # Reynolds number
    Res = Calculations_STHE_Reynolds_shellside.STHE_Reynolds_shellside(ms, ros, mis, Ds, dte, rp, lay, L, Nb, m_p)

    # Cross flow area
    Sm = STHE_shellside_Sm(Ds, dte, rp, lay, L, Nb, m_p)

    # Area occupied by the tubes (Swt), Total window area (Swg), Free window area (Sw)
    Swt, Swg, Sw = STHE_shellside_WindowAreas(Ds, dte, Npt, rp, lay, Bc, m_p)

    # Mass flux in window
    #Gw = m_p['ms'] / ((Sm * Sw) ** (1 / 2))
    Gw = ms / ((Sm * Sw)**(1/2))
    #print('Gw',Gw)

    # Hydraulic diameter
    Dw = STHE_shellside_Dw(Ds, dte, Npt, rp, lay, Bc, m_p)

    # Tube pitch
    Ltp = STHE_Ltp_func(rp, dte)

    # Effective number of tube rows in the window
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Baffle spacing
    lbc = STHE_Lbc_func(L, Nb)

    # Correction factor for baffle leakeage effects
    Rl = STHE_shellside_Rl(Ds, dte, Npt, rp, lay, L, Nb, Bc, m_p)

    # Window pressure drop for laminar flow
    #DPwlam = Nb * Rl * (((26 * Gw * m_p['ms']) / m_p['ros']) * ((Ntcw / (Ltp - dte - 2 * fts_thk)) + (lbc / (Dw ** 2))) + ((2 / m_p['ros']) * (Gw ** 2)))

    # Without considering fouling model
    # Window pressure drop for laminar flow // Perda de carga na janela para regime laminar
    #DPwlam = Nb * Rl * (((26 * Gw * ms) / ros) * ((Ntcw / (Ltp - dte)) + (lbc / (Dw ** 2))) + ((2 / ros) * (Gw**2)))
    DPwlam = Nb * Rl * (((26 * Gw * mis) / ros) * ((Ntcw / (Ltp - dte)) + (lbc / (Dw ** 2))) + ((2 / ros) * (Gw**2)))

    # Window pressure drop for turbulent flow
    #DPwturb = Nb * Rl * (2 + (0.6 * Ntcw)) * ((1) / (2 * m_p['ros'])) * (Gw**2)
    DPwturb = Nb * Rl * (2 + (0.6 * Ntcw)) * (1 / (2 * ros)) * (Gw**2)

    # Window pressure drop
    Delta_Pw = DPwlam
    Delta_Pw[Res >= 100] = DPwturb[Res >= 100]
    #print('DPw',Delta_Pw)

    return Delta_Pw

def STHE_shellside_EndZonesDeltaP(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p):
    # End zone pressure drop

    # Number of tube rows in cross flow
    Ntcc = STHE_shellside_Ntcc(Ds, dte, rp, lay, Bc)

    # Effective number of tube rows in window
    Ntcw = STHE_shellside_Ntcw(Ds, dte, rp, lay, Bc, m_p)

    # Correction factor for bundle bypass
    Rb = STHE_shellside_Rb(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p)

    Rs = 2

    # Ideal cross flow pressure drop
    DPbi = STHE_shellside_IdealcrossflowDeltaP(ms, ros, mis, Ds, dte, rp, lay, L, Nb, Bc, m_p)
    DeltaPe = DPbi * Rb * Rs * (1 + (Ntcw / Ntcc))
    #print('DPe',DeltaPe)

    return DeltaPe

# endregion

#################################################################################################################

