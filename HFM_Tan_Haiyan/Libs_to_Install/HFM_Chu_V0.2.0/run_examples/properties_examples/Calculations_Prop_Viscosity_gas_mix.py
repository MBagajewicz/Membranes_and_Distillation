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
#endregion

#region Calculations

def Mean_Viscosity_Mix(fractions,MU,M):
    """
        Viscosity of mixture (Herning & Zipperer) along whole membrane
        https://en.wikipedia.org/wiki/Viscosity_models_for_mixtures#Classic_mixing_rules
        fractions has len = n_comp
    """
    SQRT_M = np.sqrt(M)
    soma = np.sum(fractions)
    y = fractions / soma # Normalização por segurança
    num = np.sum(y * MU * SQRT_M)
    den = np.sum(y * SQRT_M)
    return num / np.maximum(den, 1e-12)