import numpy as np

# Constante dos gases (SI)
R = 8.314462618  # J/mol/K

# Dados críticos: Tc (K), Pc (Pa), acêntrico w (-)
crit_data = {
    "CO2": {"Tc": 304.1282, "Pc": 7.3773e6, "w": 0.22394},
    "CH4": {"Tc": 190.564, "Pc": 4.5992e6, "w": 0.01142},
    "N2": {"Tc": 126.192, "Pc": 3.3958e6, "w": 0.03720},
}


def PR_fugacity(T, P, y):
    """
    Calcula fugacidades de CO2, CH4, N2 em mistura.

    T : temperatura (K)
    P : pressão (Pa)
    y : frações molares np.array([y_CO2, y_CH4, y_N2])

    Retorna:
        f (Pa) : fugacidades de cada componente
        phi   : coeficientes de fugacidade
    """
    # Lista dos componentes na mesma ordem
    comps = ["CO2", "CH4", "N2"]
    y = np.array(y)

    # --- 1) Parâmetros puros a_i, b_i, alfa_i ---
    a_i = np.zeros(3)
    b_i = np.zeros(3)
    alpha_i = np.zeros(3)

    for i, c in enumerate(comps):
        Tc = crit_data[c]["Tc"]
        Pc = crit_data[c]["Pc"]
        w = crit_data[c]["w"]

        kappa = 0.37464 + 1.54226 * w - 0.26992 * w ** 2
        Tr = T / Tc
        alpha = (1 + kappa * (1 - np.sqrt(Tr))) ** 2

        a = 0.45724 * R ** 2 * Tc ** 2 / Pc
        b = 0.07780 * R * Tc / Pc

        a_i[i] = a
        b_i[i] = b
        alpha_i[i] = alpha

    # --- 2) Mistura: regras de mistura a_m, b_m ---
    # regra de desconto para a_ij
    a_ij = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            a_ij[i, j] = np.sqrt(a_i[i] * alpha_i[i] * a_i[j] * alpha_i[j])  # sem fator kij

    a_mix = 0.0
    for i in range(3):
        for j in range(3):
            a_mix += y[i] * y[j] * a_ij[i, j]

    b_mix = np.sum(y * b_i)

    # --- 3) Parâmetros adimensionais ---
    A = a_mix * P / (R * T) ** 2
    B = b_mix * P / (R * T)

    # --- 4) Resolver Z cúbico: Z³ - (1−B)Z² + (A − 3B² − 2B)Z − (AB − B² − B³) = 0 ---
    coef = [
        1.0,
        -(1.0 - B),
        A - 3 * B ** 2 - 2 * B,
        -(A * B - B ** 2 - B ** 3)
    ]

    roots = np.roots(coef)
    roots_real = np.real(roots[np.isreal(roots)])

    # para fases gasosas: pegar a maior raiz real
    Z = np.max(roots_real)

    # --- 5) Coeficientes de fugacidade φ_i ---
    phi = np.zeros(3)

    for i in range(3):
        Bi = b_i[i] * P / (R * T)
        Ai = a_i[i] * alpha_i[i] * P / (R * T) ** 2

        # termo ∑ y_j * a_ij
        sum_aij = np.sum(y * a_ij[i])

        ln_phi = (Bi / B) * (Z - 1) \
                 - np.log(Z - B) \
                 + (A / (2 * np.sqrt(2) * B)) * (2 * sum_aij / a_mix - Bi / B) \
                 * np.log((Z + (1 + np.sqrt(2)) * B) / (Z + (1 - np.sqrt(2)) * B))

        phi[i] = np.exp(ln_phi)

    # --- 6) Fugacidades ---
    f = phi * y * P  # Pa

    return f, phi
