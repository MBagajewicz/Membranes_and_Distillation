#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#   0.0          08-May-2025     Mariana Mello              Proposed

##################################################################################################################
#endregion

# region Import
import sys
# endregion

#region Calculations
def verification_positive_variables(m_p, save_result):
    for key, value in m_p.items():
        if isinstance(value, (int, float)):
            if value < 0:
                save_result(f"Variable/Parameter '{key}' is not positive = {value}\n")
                sys.exit()
        else:
            # ignore string
            continue
    return m_p

def verification_DeltaTmin(m_p, save_result):
    if 'DeltaT_min' in m_p:
        pass
    else:
        m_p['DeltaT_min'] = 5
        save_result(f"DeltaTmin does not exist in the Model_Parameters. A default value of {m_p['DeltaT_min']} °C is adopted.\n")
    return m_p

def verification_Thi_Tho(m_p, save_result):
    if 'Thi' in m_p and 'Tho' in m_p:
        Thi = m_p['Thi']
        Tho = m_p['Tho']
        if Thi > Tho:
            pass
        else:
            save_result('Error data consistency: Tho > Thi\n')
            sys.exit()
        return m_p


def verification_Tco_Tci(m_p, save_result):
    if 'Tco' in m_p and 'Tci' in m_p:
        Tci = m_p['Tci']
        Tco = m_p['Tco']
        if Tco > Tci:
            pass
        else:
            save_result('Error data consistency: Tci > Tco\n')
            sys.exit()
        return m_p

def verification_Tco_Thi(m_p, save_result):
    if 'Tco' in m_p and 'Thi' in m_p:
        Thi = m_p['Thi']
        Tco = m_p['Tco']
        deltaTmin = m_p['DeltaT_min']
        if Tco < Thi-deltaTmin:
            pass
        else:
            save_result('Error data consistency: Tco > Thi - deltaTmin\n')
            sys.exit()
        return m_p

def verification_Tci_Tho(m_p, save_result):
    if 'Tci' in m_p and 'Tho' in m_p:
        Tho = m_p['Tho']
        Tci = m_p['Tci']
        deltaTmin = m_p['DeltaT_min']
        if Tci < Tho-deltaTmin:
            pass
        else:
            save_result('Error data consistency: Tci > Tho - deltaTmin\n')
            sys.exit()
        return m_p

def verification_heatload(m_p, save_result):
    try:
        Qh = m_p['mh']*m_p['Cph']*(m_p['Thi']-m_p['Tho'])
        Qc = m_p['mc']*m_p['Cpc']*(m_p['Tco']-m_p['Tci'])
        eps = 1e-4
        # 0.01% difference is tolerated
        if abs((Qh - Qc)/Qh) > eps:
            pass
        else:
            m_p['Tco'] = Qh/(m_p['mc']*m_p['Cpc']) + m_p['Tci']
            save_result(f"Error data consistency: heat load is inconsistent with the energy balance (within 0.01%). A new value for Tco = {m_p['Tco']} is used.\n")
            return m_p
    except:
        pass
    return m_p


#endregion