import numpy as np

def Cm_DMS(f, kD, CH, b, F):
    """
    f   : array de fugacidades (Pa) para todos componentes
    kD  : array kD[i] Constante de Henry cm³(STP) / - (cm³ polymer · kPa)
    CH  : array CH[i] Constante de Saturação de poro - cm³(STP) / cm³ polymer
    b   : array b[i] Constante de Afinidade de poro - kPa⁻¹
    F   : array F[i] Fator de imobilização - unitless

    Retorna array Cm[i] = kD[i]*p[i] + F[i]*(CH[i]*b[i]*p[i]) / (1 + Σ b[j] p[j])
    (concentração total sorvida móvel) para cada componente i.
    """
    f = np.array(f)*1e-3 #para kPa

    # termo de competição = Σ_j b[j] * p[j]
    Cm_Henry = kD * f
    Cm_Langmuir = F * (CH * b * f) / (1.0 + np.sum(b * f))
    Cm = Cm_Henry + Cm_Langmuir
    return Cm  # cm³(STP) / cm³(polymer)

def diffusivity(Cm, D0, beta, index_CO2):  #Não será uma função usada, mas vale para entendimento
    """
    Cm      : array Cm[i] - para todos componentes PLASTIFICANTES
    D0      : array D0[i] - Difusividades de cada comp puro na membrana
    beta    : array beta[i] - coef empírico de plasticização
    index_CO2 : índice do CO2 no vetor de componentes (ex.: 0 ou 1)

    Retorna Array D[i] de difusividades.
    """
    Cm_CO2 = Cm[index_CO2]
    D = D0 * np.exp(beta * Cm_CO2) #Sempre Cm_CO2, caso mais de um plastificante usar exp(Σ beta_i * Cm_i) dos plastificantes
    return D # cm²/s

def permeability_CO2(D0_CO2,beta_CO2,f_R_CO2,f_P_CO2,Cm_R_CO2,Cm_P_CO2):
    """
    Permeabilidade do CO2 (considerado único agente plastificante)
    válido para quantos componentes quiser, mas um único plastificante(esse).

    Todos os argumentos são escalares (float)

    Retorna float Perm_CO2 de permeabilidade
    """
    dimensional_factor = D0_CO2/(beta_CO2*(f_R_CO2-f_P_CO2))
    exp_Cm_R_CO2 = np.exp(beta_CO2 * Cm_R_CO2)
    exp_Cm_P_CO2 = np.exp(beta_CO2 * Cm_P_CO2)

    Perm_CO2 = dimensional_factor * (exp_Cm_R_CO2 - exp_Cm_P_CO2) # cm³(STP) / cm(polymer).s.kPa = GPU*cm(polymer)

    FACTOR_STP_to_mol = 1.0 / 22414.0 # cm³(STP) -> mol
    FACTOR_cm2_to_m2 = 1.0e-4  # cm² -> m²
    FACTOR_kPa_to_Pa = 1000.0  # kPa -> Pa
    CONVERSION = FACTOR_STP_to_mol / (FACTOR_cm2_to_m2 * FACTOR_kPa_to_Pa)

    return Perm_CO2*CONVERSION # mol/(m·s·Pa)


def permeability_non_plasticizing(D0, beta, f_R, f_P, Cm_R, Cm_P):
    """
    Cm      : array Cm[i] - para todos componentes
    D0      : array D0[i] - Difusividades de cada comp puro na membrana
    beta    : array beta[i] - coef empírico de plasticização
    f       : array f[i] - Fugacidades de cada componente
    Válido para somente um componente plastificante, do contrário teríamos exp(Σ beta_i * Cm_R_i) dos plastificantes

    Retorna Array Perm[i] de permeabilidades
    """
    dimensional_factor = D0 / (f_R - f_P)
    exp_Cm_R = np.exp(beta * Cm_R)

    Perm = dimensional_factor * exp_Cm_R * (Cm_R - Cm_P)
    #Safeguard para componentes com fração zero
    Perm[(f_R - f_P) == 0] = 0

    FACTOR_STP_to_mol = 1.0 / 22414.0  # cm³(STP) -> mol
    FACTOR_cm2_to_m2 = 1.0e-4  # cm² -> m²
    FACTOR_kPa_to_Pa = 1000.0  # kPa -> Pa
    CONVERSION = FACTOR_STP_to_mol / (FACTOR_cm2_to_m2 * FACTOR_kPa_to_Pa)

    return Perm*CONVERSION # mol/(m·s·Pa)
