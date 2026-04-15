#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        06-Nov-2025     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
# from HFM.HFM_Chu_Scenarios import SCENARIOS
# endregion

# region Calculations

def Number_of_fibers(D,dfo,Void_Frac):
    Ntf = (1 - Void_Frac) * (D ** 2) / (dfo ** 2) # isn't it just?:  >>>(1 - Void_Frac) * (D ** 2) / (dto ** 2)<<<
    
  # need to make Ntf an integer
    Ntf = np.floor(Ntf)
    # Ntf = np.ceil(Ntf)
  
    return Ntf
#endregion

if __name__ == '__main__':
    # print(1-60_000*(170e-6/0.05)**2)
    # print(Number_of_fibers(0.05,170e-6,0.3064)/4)
    for scenario_name in SCENARIOS:
        p = SCENARIOS[scenario_name]
        print(f'Void frac for scenario {scenario_name}: {round(1-p["N"]*(p["D_o"]/p["D"])**2,4)}')
