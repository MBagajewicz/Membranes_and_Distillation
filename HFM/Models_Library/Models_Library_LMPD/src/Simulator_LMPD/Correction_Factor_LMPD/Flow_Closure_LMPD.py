#region Title: FlowClosureLMPD
# Nature: Flow closure for the two pressure integrals
# Methodology: Derived from the LMPD hypothesis itself rather than assumed. Each
#              species contributes its own exponential mode; the closure is the
#              mode-weighted mean, elementary and free of fitted parameters.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, ported into library layout
##################################################################################################################
#endregion

import math
from typing import Optional

import numpy as np

# EN: Names accepted by flow_integral. 'modes' is the derived closure of Eq. (9)
#     and the default; 'linear' is the classical assumption.
# PT-BR: Fechos aceitos. 'modes' e o derivado da Eq. (9) e o padrao.
#
# A NOTE ON THE NAME, because it was a trap. An earlier prototype used the name
# 'modes' for a DIFFERENT weighting -- Q_i theta_i,0 (1-e^-c)/c, which is the
# permeated amount the LMPD hypothesis alone would give, that is, the amount at
# Phi = 1. The published derivation weights by u_i/u_tot, the amount the model
# ACTUALLY solves for, and those two coincide only in the uncorrected model.
# The coherent one is therefore u_i/u_tot, and it is what 'modes' means here.
# The prototype weighting is kept as 'modes_phi1', under a name that says what
# it is, because the numbers currently in the technical note were produced with
# it and the regression test must still be able to reproduce them.
CLOSURES = ("modes", "modes_phi1", "linear", "const", "averaged")


def mode_shape(c: float) -> float:
    """
    EN: g(c) = [(1 - e^-c)/c - e^-c] / (1 - e^-c), the mean-to-terminal ratio of
        one exponential mode. Continuous through c -> 0, where it tends to
        1/2 - c/12, and valid for c < 0 -- which is necessary, since a slow
        species can have a driving force that GROWS along the module.
    PT-BR: g(c), razao media-terminal de um modo exponencial. Continua em c -> 0
           e valida para c de qualquer sinal.
    """
    if abs(c) < 1e-7:
        return 0.5 - c / 12.0
    E = math.exp(-c)
    return ((1.0 - E) / c - E) / (1.0 - E)


def flow_integral(closure: str, c: Optional[np.ndarray] = None,
                  Q: Optional[np.ndarray] = None,
                  th0: Optional[np.ndarray] = None,
                  u: Optional[np.ndarray] = None,
                  S0: float = 0.0, SL: float = 0.0) -> float:
    """
    EN: I_f = int_0^1 F_P dzeta / u_tot, with F_P(0) = u_tot and F_P(1) = 0.
        Both pressure relations collapse onto this single number, so the closure
        is the only place where a profile assumption enters the algebraic model.

        'modes'      -- the derived closure of Eq. (9). Each species contributes
                        one exponential mode, weighted by u_i/u_tot, its actual
                        contribution to the permeate flow at the open end.
        'modes_phi1' -- the same modes weighted by the amounts the LMPD
                        hypothesis alone would give, i.e. at Phi = 1. Coincides
                        with 'modes' only for the uncorrected model. Retained
                        for regression against previously published numbers.
        'linear'   -- F_P falls linearly, I_f = 1/2. This is the assumption of
                      Giglia et al. (1991) and recovers the classical level.
        'const'    -- F_P frozen, I_f = 1. The base derivation.
        'averaged' -- one single mode built from the flux ratio.

    PT-BR: I_f, a unica grandeza pela qual as duas relacoes de pressao passam.
           E, portanto, o unico lugar do modelo algebrico onde entra hipotese de
           perfil.
    """
    if closure == "const":
        return 1.0
    if closure == "linear":
        return 0.5
    if closure == "modes":
        # EN: Eq. (9). F_P(0) = sum_i u_i exactly, so weighting each mode by its
        #     actual contribution to the permeate flow at the open end IS
        #     u_i/u_tot. Coherent with the corrected solution, not with Phi = 1.
        # PT-BR: Eq. (9), peso u_i/u_tot. Coerente com a solucao corrigida.
        if c is None or u is None:
            return 0.5
        ut = float(np.sum(u))
        if ut <= 0.0:
            return 0.5
        return float(sum(u[i] * mode_shape(c[i]) for i in range(len(c))) / ut)
    if closure == "modes_phi1":
        if c is None or Q is None or th0 is None:
            return 0.5
        w = np.array([Q[i] * th0[i] * ((1.0 - math.exp(-c[i])) / c[i]
                                       if abs(c[i]) > 1e-7 else 1.0)
                      for i in range(len(c))])
        if w.sum() <= 0.0:
            return 0.5
        return float(sum(w[i] * mode_shape(c[i]) for i in range(len(c))) / w.sum())
    # averaged: a single mode built from the total flux ratio
    k = max(math.log(max(S0 / max(SL, 1e-300), 1.0 + 1e-12)), 1e-10)
    return mode_shape(k)
