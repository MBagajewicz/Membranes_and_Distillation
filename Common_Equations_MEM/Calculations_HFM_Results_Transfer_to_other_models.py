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
from math import pi
# endregion

#region Calculations


def SU_DC_2FEEDS(results, m_p):

    # Retentate Toluene to be transferred to 
    m_p['z_f'] = (results['xxxx'].tolist()
    m_p['F_f'] = (results['xxxx'].tolist()
    m_p['T_f'] = (results['xxxx'].tolist()

# z_f, F_f and T_f are in a form of vectors for the two feeds. 
#'z_f' : [[0.7, 0.2, 0.1], [0.2, 0.2, 0.6]], 
#'F_f' :  [100, 100],                  
#'T_f' :  [1350, 360],                   )

# I do not know how the results from the membrane are reported, so you need to figure that out. 

    return m_p

#endregion