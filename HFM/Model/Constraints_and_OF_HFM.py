###################################################################################################################
# region Titles and Header
# Nature: Here we put the constraints and Objective Function used in Set Trimming
# methodology
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          2024            Diego Oliva               Original
#   0.2          01-Dec-2024     Mariana Mello             Add constraints
#   0.3          03-Mar-2025     Mariana Mello             Changes after add options of tube and shell methods
#   0.4          23-Apr-2025     Mariana Mello             Update to fix error and add constraint Fmin
#   0.5          12-May-2025     Mariana Mello             Changed name from 'pd' to 'm_p'
##################################################################################################################
# INPUT: Define Constraints as def and return + or - values depending the > or < inequality
##################################################################################################################
# INSTRUCTIONS
# Add python functions (def)  for each constraint defined in the "Examples_Repository.py" dictionary
#                          named Model_Declarations['Active_Constraints_List']
# Then add an Objective Function to be minimized before declared in:
#                            Model_Declarations['Standard_Objective_Function']['Equation_Name']
# Finally, add the Lower Bound x
# endregion
############################################################################################

##################################################################################################################
# region Import Library
from math import pi
import numpy as np
import ast
from Simulator_HFM.Calculations_HFM import (
    Calculations_HFM_Area,
    Calculations_HFM_Simulation_Results,
    Calculations_HFM_Nf,
    Calculations_HFM_Min_Thickness,
    Calculations_HFM_Min_Area_XR_Comp,
    Calculations_HFM_Reynolds_Bore,
    Calculations_HFM_Reynolds_Shell,
    Calculations_HFM_Max_Area_Loss,
    Calculations_HFM_Mach_Shell,
    Calculations_HFM_Mach_Bore,
)
# endregion
##################################################################################################################

##################################################################################################################
# region Constraints
# Negatives survive


def LD_LB_UB(L,D,dfo_esp,Void_Frac,Material,m_p):
    # Lower and upper bounds on L/D_shell
    L = L.astype(np.float64)
    D = D.astype(np.float64)

    fun_val_lb = m_p['LDLB'] - L / D
    fun_val_up = L/D -m_p['LDUB']
    return np.array([fun_val_lb, fun_val_up])

def HFM_shell_velocity(L,D,dfo_esp,Void_Frac,Material,m_p):
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    vel_s = Calculations_HFM_Velocity_Shell(molar_flow_shell, comp_shell, M, rho, D, dfo, Ntf)
    raise NotImplementedError("Velocity proxy is under construction")
    return vel_s

def Min_Area_Specification(L,D,dfo_esp,Void_Frac,Material,m_p):
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)

    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Area = Ntf * pi * dfo * L

    Key_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])

    results = Calculations_HFM_Min_Area_XR_Comp.compute_rayleigh_area_floor(
        Q=m_p['Q'], A_t=Area, Pf=m_p['P_Feed'],
        F_f=m_p['f_total'], x_feed=m_p['comp_f'],  Material= Material,
        Key_Comp_index=Key_Comp_index, return_all=True)
    fun_val = results[1]['A_floor'] - Area
    return fun_val

def max_comp_ret_first_proxy(L,D,dfo_esp,Void_Frac,Material,m_p):
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)

    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Area = Ntf * pi * dfo * L

    max_transfer = m_p['Q'][:, None] * Area * ((m_p['P_Feed'] * m_p['comp_f'])[:, None])
    Key_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])

    x_r2 = (
            ((m_p['f_total'] * m_p['comp_f'])[:, None] - max_transfer) /
            (m_p['f_total'] - np.sum(max_transfer, axis=0, keepdims=True))
            )

    fun_val = x_r2[Key_Comp_index, :] - m_p['MAX_COMP_RET']
    return fun_val

def Re_Shell_Feed(L,D,dfo_esp,Void_Frac,Material,m_p):
    '''Max reynolds shell side is at feed'''
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)

    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)

    Re_fibers = Calculations_HFM_Reynolds_Shell.shell_reynolds(
        feed_flow=m_p['f_total'],
        feed_composition=m_p['comp_f'],
        molar_masses=m_p['M'],
        viscosities=m_p['MU'],
        D_shell=D,
        d_fo=dfo,
        n_fibers=Ntf
    )
    fun_val = Re_fibers - 2100

    return fun_val

def Re_Bore_Out(L,D,dfo_esp,Void_Frac,Material,m_p):
    '''Max reynolds bore side is at outlet'''
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)
    dfi = dfo - 2 * esp

    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Key_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])

    Re_fibers = Calculations_HFM_Reynolds_Bore.bore_reynolds(
        feed_flow=m_p['f_total'],
        feed_composition=m_p['comp_f'],
        molar_masses=m_p['M'],
        viscosities=m_p['MU'],
        theta_key=m_p['MAX_COMP_RET'],
        d_fi=dfi,
        n_fibers=Ntf,
        key_index=Key_Comp_index
    )
    fun_val = Re_fibers - 2100

    return fun_val

def esp_LB_UB(L,D,dfo_esp,Void_Frac,Material,m_p):
    # Lower and Upper bounds on L/Ds
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)
    delta_esp = np.round(np.unique(esp)[1] - np.unique(esp)[0],7)

    esp_min = Calculations_HFM_Min_Thickness.Min_Thickness(m_p['P_Feed'], m_p['P_Permeate'], dfo, m_p['E'], m_p['nu'], m_p['degradation_factor'], m_p['safety_factor'], Material)
    fun_val_lb = esp_min - esp
    fun_val_up = - (esp_min - (esp)) - delta_esp # GOES FOR NEXT ESP IN THE SET OF ESPS FOR THAT DIAMETER
    # esp_min <= esp <= delta_esp
    return np.array([fun_val_lb, fun_val_up])

def Max_Area_Loss(L, D, dfo_esp, Void_Frac, Material, m_p):
    '''Área máxima admissível pela restrição de perda do componente restrito'''
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)

    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Loss_Comp_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY_PERM'])

    A_M = Calculations_HFM_Area.HFM_area(dfo, L, Ntf)

    A_UB = Calculations_HFM_Max_Area_Loss.max_area_by_material(
        permeance_by_material=m_p['Q'],
        materials=Material,
        retained_index=Loss_Comp_index,
        feed_flow=m_p['f_total'],
        x_m_feed=m_p['comp_f'][Loss_Comp_index],
        psi_max=m_p['MAX_LOSS_PERM'],
        P_ret_min=m_p['P_Feed'] - m_p['MAX_DP_RET'],
        P_perm_max=m_p['MAX_P_PERM']
    )

    fun_val = A_M - A_UB
    return fun_val

def Max_Mach_Shell(L, D, dfo_esp, Void_Frac, Material, m_p):
    '''Mach máximo admissível no casco (validade de Hagen-Poiseuille)'''

    a_feed, v_molar_feed = Calculations_HFM_Mach_Shell.feed_state(
        components=m_p['COMPONENTS'],
        x_feed=m_p['comp_f'],
        T=m_p['T'],
        P_feed=m_p['P_Feed'],
    )
    Ma_shell = Calculations_HFM_Mach_Shell.mach_shell(
        D=D,
        Void_Frac=Void_Frac,
        feed_flow=m_p['f_total'],
        v_molar_feed=v_molar_feed,
        a_feed=a_feed,
    )
    fun_val = Ma_shell - m_p['MAX_MACH']
    return fun_val


def Max_Mach_Bore(L, D, dfo_esp, Void_Frac, Material, m_p):
    '''Mach máximo admissível no bore (validade de Hagen-Poiseuille)'''
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D, dfo, Void_Frac)
    Key_index = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])
    F_P_min = Calculations_HFM_Mach_Bore.min_permeate_flow(
        feed_flow=m_p['f_total'],
        x_key_feed=m_p['comp_f'][Key_index],
        theta_max=m_p['MAX_COMP_RET'],
    )
    a_UB = Calculations_HFM_Mach_Bore.sound_speed_UB(
        components=m_p['COMPONENTS'],
        T=m_p['T'],
    )
    Ma_bore = Calculations_HFM_Mach_Bore.mach_bore(
        dfo=dfo, esp=esp, Ntf=Ntf,
        F_P_min=F_P_min,
        T=m_p['T'],
        P_perm=m_p['P_Permeate'],
        a_UB=a_UB,
    )
    fun_val = Ma_bore - m_p['MAX_MACH']
    return fun_val
######################################################################################################################

# region LB function

# -------------------------------------------------------------------------------------------------------------------
# Lower Bound Function
# --------------------------------------------------------------------------------------------------------------------

def scenario_name_from_params(m_p):
    """Identify which scenario a Model_Parameters dict belongs to.

    The discrete candidate grid is SHARED by every scenario, so the same
    geometry appears in all of them and a logged candidate is ambiguous without
    the scenario name. `m_p` is passed by reference all the way from the
    Examples module, so identity matching resolves it exactly; a descriptive
    signature is used as a fallback if the module cannot be imported.
    """
    try:
        import Examples_HFM as _EX
        for _name in dir(_EX):
            _obj = getattr(_EX, _name, None)
            if isinstance(_obj, dict):
                try:
                    if _obj['Equipment1']['Model_Parameters'] is m_p:
                        return _name
                except Exception:
                    continue
    except Exception:
        pass
    try:
        return (f"?[{'+'.join(m_p['COMPONENTS'])}@{m_p['P_Feed'] / 1e5:g}bar"
                f"/{m_p['KEY_COMPONENT_COMP_RET']}<={m_p['MAX_COMP_RET']}]")
    except Exception:
        return "?"


def _log_timed_out_candidate(L, D, dfo_esp, Void_Frac, Material, m_p):
    """Append a candidate skipped on its time budget to `timed_out_candidates.log`.

    These are UNRESOLVED, not infeasible: the enumeration rejected them for cost
    only. The file is written next to the project root so the set can be re-run
    later with SIM_TIME_BUDGET_S raised (or removed).
    """
    import os, time
    def _f(v):
        try:
            return v[0]
        except Exception:
            return v
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "timed_out_candidates.log")
    # The scenario MUST be recorded: the candidate grid is shared, so the same
    # geometry occurs in every scenario and the entry is otherwise ambiguous.
    line = (f"{time.strftime('%Y-%m-%d %H:%M:%S')}  "
            f"scenario={scenario_name_from_params(m_p)}  "
            f"budget={m_p.get('SIM_TIME_BUDGET_S')}s  L={_f(L)}  D={_f(D)}  "
            f"dfo_esp={_f(dfo_esp)}  Void_Frac={_f(Void_Frac)}  "
            f"Material={_f(Material)}\n")
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception as exc:
        # Do NOT swallow this. The skipped set is what makes the enumeration
        # auditable; losing it silently would leave no record that candidates
        # were dropped at all. Warned once, then the console line below is the
        # only remaining trace.
        if not getattr(_log_timed_out_candidate, "_warned", False):
            _log_timed_out_candidate._warned = True
            print(f"[TIMEOUT] WARNING: cannot write {path} ({type(exc).__name__}: "
                  f"{exc}). Timed-out candidates will appear on the console only.",
                  flush=True)
    print(f"[TIMEOUT] candidate skipped (UNRESOLVED, not infeasible): {line.strip()}",
          flush=True)


def Max_comp_ret_AND_Max_loss_perm_AND_Tdew_AND_dP(L,D,dfo_esp,Void_Frac,Material,m_p):
    # Enumeration Constraints functions.

    #  >>>Variables<<<
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    esp = np.array([t[1] for t in dfo_esp_list], dtype=np.float64)
    dfi = dfo - 2*esp
    Key_Comp_index_Perm = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY_PERM'])
    Key_Comp_index_Ret = m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])

    # Variables that use Calculations.
    Ntf = Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)

    # >>>Simulation<<<
    results = Calculations_HFM_Simulation_Results.HFM_Simulation_Results(L,D,dfo,dfi,Void_Frac,Material,m_p,Ntf)

    # Infeasible simulation (e.g. pressure drop exceeds available driving
    # pressure): all physical result fields are None. Mark every constraint as
    # violated (> 0) so the enumeration rejects this candidate instead of
    # crashing on results.FPerm[0]/PRetCell[...] etc. The number of constraints
    # must match the fun_val list built below for the active flags.
    if not getattr(results, "feasible", True):
        # A candidate that ran out of its time budget is UNRESOLVED, not proven
        # infeasible. It is rejected here so the enumeration can proceed, but it
        # is recorded so the skipped set can be re-run with a larger budget --
        # without that list, no global-optimality claim over the enumeration
        # holds. See SIM_TIME_BUDGET_S in the scenario Model_Parameters.
        if getattr(results, "timed_out", False):
            _log_timed_out_candidate(L, D, dfo_esp, Void_Frac, Material, m_p)
        n_con = 2 + (1 if m_p['Energy_bool'] else 0) + (2 if m_p['Pressure_Drop_bool'] else 0)
        return [np.array([1.0] * n_con)]

    # >>>Constraints<<<
    fun_val = []
    # 1) Recuperation of key component on permeate / Loss of valuable component from feed
    Rec_Perm = ((results.FPerm[0] * results.ZPerm[0]) / (results.FRet[0] * results.ZRet[0]))[Key_Comp_index_Perm]
    fun_val_Rec_Perm = Rec_Perm - m_p['MAX_LOSS_PERM']
    fun_val.append(fun_val_Rec_Perm)

    # 2) Maximum molar fraction of component in retentate
    X_ret_key = results.ZRet[-1][Key_Comp_index_Ret]
    fun_val_X_ret_key = X_ret_key - m_p['MAX_COMP_RET']
    fun_val.append(fun_val_X_ret_key)

    # 3) Dew point verification. Both sides must operate on T > T_dew + approach.
    #
    # Decided by the simulator's PHASE-STABILITY test at T - APPROACH_T_DEW,
    # which is exactly equivalent to the condition above and does not root-find
    # on the phase boundary. The previous implementation compared T against
    # results.Tdew_*, which come from a PQ (Q = 1) flash: on the S0 retentate
    # that flash returns 476 K at one node and NaN at eight others, and since
    # `nan > x` is False the NaN nodes silently PASSED while the spurious root
    # made every candidate FAIL. That is what produced runs with zero incumbents.
    if m_p['Energy_bool']:
        fun_val_T_dew = -1 if getattr(results, "dew_ok", True) else 1
        fun_val.append(fun_val_T_dew)

    # 4) Maximum pressure drop allowed on shell
    if m_p['Pressure_Drop_bool']:
        dP_ret = results.PRetCell[0] - results.PRetCell[-1]
        fun_val_dP_ret = dP_ret - m_p['MAX_DP_RET']
        fun_val.append(fun_val_dP_ret)

    # 4) Maximum pressure on fibers (happens at the CLOSED end -- the max along
    #    the bore, not PPermCell[0] which is the open/outlet end fixed at P_perm).
    if m_p['Pressure_Drop_bool']:
        fun_val_P_max_perm = np.max(results.PPermCell) - m_p['MAX_P_PERM']
        fun_val.append(fun_val_P_max_perm)

    # Prints for debug, temporary code.
    print(f'Comp Ret {m_p['COMPONENTS'][m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_COMP_RET'])]}: {X_ret_key}'
          f' \nRecovery Perm {m_p['COMPONENTS'][m_p['COMPONENTS'].index(m_p['KEY_COMPONENT_RECOVERY_PERM'])]}: {Rec_Perm}')
    if m_p['Pressure_Drop_bool']:
        print(f'dP Ret: {dP_ret*1e-3} Kpa')
    if m_p['Energy_bool']:
        if fun_val_T_dew == -1:
            print("T_Dew_Ret Satisfied")
        else:
            print("T_Dew_Ret Unsatisfied")

    return [np.array(fun_val)]

def LB_HFM(L,D,dfo_esp,Void_Frac,Material,m_p):
    # Lower bound using the Area
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    Ntf=Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    LB = Calculations_HFM_Area.HFM_area(dfo, L, Ntf)
    return LB

# endregion
######################################################################################################################

# region Objective Functions

def LB_Gen():
    # Lower bound -
    pass

def AREA_OF(L,D,dfo_esp,Void_Frac,Material,m_p):
    L = L.astype(np.float64)
    D = D.astype(np.float64)
    Void_Frac = Void_Frac.astype(np.float64)
    dfo_esp_list = [ast.literal_eval(t) for t in dfo_esp]
    dfo = np.array([t[0] for t in dfo_esp_list], dtype=np.float64)
    Ntf=Calculations_HFM_Nf.Number_of_fibers(D,dfo,Void_Frac)
    Area = Calculations_HFM_Area.HFM_area(dfo, L, Ntf)
    return Area

# endregion
##################################################################################################################
