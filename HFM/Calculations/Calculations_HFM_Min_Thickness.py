#
#region Titles and Header
# Nature: Optimization
# Methodology: Set trimming
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0        10-Nov-2025     João Tupinambá               Proposed
##################################################################################################################
#endregion

#region Import Library
import numpy as np
#endregion

#region Calculations

def Min_Thickness(P, p, dfo, E, sigma_y, nu, degradation_factor, safety_factor):
    """
    Calcula a espessura mínima da membrana para resistir ao colapso e escoamento.

    Args:
        P: Pressão no casco (Pa)
        p: Pressão no lúmen (Pa)
        dfo: Raio Externo da fibra (m)
        E: Módulo de Young (Pa),
        sigma_y: Tensão de escoamento (Pa)
        nu: Coeficiente de Poisson

        degradation_factor: Assume 30% de perda de força devido à plasticização por CO2
        safety_factor: Fator de segurança (assumido 3.0 para cobrir excentricidade e creep)

    Returns:
        t_min (m): Espessura mínima recomendada
    """

    P_diff = (P - p) # Pa

    # Aplicar fator de degradação por CO2 (Plasticização)
    # O CO2 amolece a matriz polimérica, reduzindo E e Sigma
    E_deg = E * degradation_factor
    sigma_y = sigma_y * degradation_factor

    # --- CRITÉRIO A: Resistência ao Escoamento (Yielding - Hoop Stress) ---
    # Fórmula aproximada para tubos: sigma = (P * R) / t
    # t_yield = (P * R * FS) / sigma_y
    t_yield = (P_diff * (dfo/2) * safety_factor) / sigma_y

    # --- CRITÉRIO B: Instabilidade Elástica (Buckling/Colapso) ---
    # Fórmula clássica para colapso de tubo longo sob pressão externa
    # P_cr = [2E / (1-nu^2)] * (t / 2Ro)^3
    # Isolando t:
    term_1 = (P_diff * safety_factor * (1 - nu ** 2)) / (2 * E_deg)
    t_buckling = dfo * (term_1) ** (1 / 3)
    # Decisão final
    # print(np.maximum(t_buckling, t_yield))
    return np.maximum(t_buckling, t_yield)
