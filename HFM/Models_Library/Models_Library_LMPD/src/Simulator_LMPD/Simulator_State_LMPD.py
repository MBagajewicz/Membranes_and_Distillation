#region Title: SimulatorStateLMPD
# Nature: State assembly from the unknown vector
# Methodology: Given the permeated amounts and the sealed-end permeate pressure,
#              everything else follows by material balance, by the Weller-Steiner
#              closure at the sealed end and by the two integrated pressure
#              relations.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       11-Aug-2026    J.V.A. Tupinamba               First version, ported into library layout
##################################################################################################################
#endregion

import math
from typing import Tuple

import numpy as np

from .Correction_Factor_LMPD.Flow_Closure_LMPD import flow_integral


def log_mean(a, b):
    """
    EN: Logarithmic mean, safe when the two arguments coincide.

        np.where alone is NOT enough: it selects after evaluating both branches,
        so the division still runs on the degenerate entries and raises. The
        quotient is therefore computed with an explicit mask, and the degenerate
        entries -- which are the isobaric, near-constant-driving-force case, not
        an edge case -- take the common value directly.
    PT-BR: Media logaritmica. O np.where sozinho nao basta, porque avalia os dois
           ramos; a divisao usa mascara explicita.
    """
    a = np.asarray(a, float); b = np.asarray(b, float)
    out = np.array(np.broadcast_to(a, np.broadcast(a, b).shape), dtype=float)
    dif = a - b
    # EN: Where the two terminals coincide the mean is the common value; the
    #     rest is a division, masked so the degenerate entries never reach it.
    #     np.where alone would not do, because it selects AFTER evaluating both
    #     branches and the division would still run.
    #
    #     THE CLIP ON THE RATIO IS LOAD-BEARING AND IS NOT COSMETIC. When a
    #     species is at or past a pinch one terminal driving force turns
    #     non-positive, and the logarithmic mean is then undefined. Returning a
    #     flat zero there is the physically tidy answer and it BREAKS THE SOLVER:
    #     it makes the residual locally constant, the Jacobian singular, and
    #     Newton stops converging -- measured, on the CO2/propane module at
    #     selectivity 882 the stage cut went from -0.23 % to +116 % error. The
    #     clip instead continues the function smoothly through the degeneracy,
    #     giving a small negative mean that carries a gradient and steers the
    #     iteration back into the physical region, where the converged solution
    #     never sits. It is a numerical continuation, not a physical claim.
    # PT-BR: O clip na razao e ESTRUTURAL. Devolver zero no pinch e fisicamente
    #        arrumado e quebra o solver: resIduo localmente constante, jacobiano
    #        singular. O clip continua a funcao suavemente pela degeneracao.
    igual = np.abs(dif) < 1e-12 * np.maximum(np.abs(a), 1e-300)
    m = ~igual
    if np.any(m):
        q = np.divide(a, b, out=np.ones_like(out), where=m & (b != 0.0))
        q = np.where(m & (b == 0.0), np.inf, q)
        r = np.log(np.clip(q, 1e-300, None))
        np.divide(dif, r, out=out, where=m & np.isfinite(r) & (r != 0.0))
        out[m & ~(np.isfinite(r) & (r != 0.0))] = 0.0
    return out


def weller_steiner(Q: np.ndarray, PR: float, xR: np.ndarray,
                   PP: float) -> Tuple[np.ndarray, float]:
    """
    EN: Permeate composition at the sealed end. No permeate arrives from
        downstream there, so the local composition IS the local ratio of fluxes.
        Introducing the total flux S as a single scalar unknown turns the
        n_c-dimensional problem into one monotone scalar equation,

            g(S) = sum_i Q_i P_R x_R,i / (S + Q_i P_P) - 1 = 0

        whose root is unique and is bracketed by bisection. Solving the vector
        form directly by Newton fails at high selectivity, because the Jacobian
        becomes nearly singular when one component dominates the flux.

    PT-BR: Composicao do permeado na ponta fechada, pelo fecho ESCALAR em S.
    """
    num = Q * PR * xR
    lo, hi = 1e-30, float(num.sum()) + 1.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if float((num / (m + Q * PP)).sum()) - 1.0 > 0.0:
            lo = m
        else:
            hi = m
    S = 0.5 * (lo + hi)
    return num / (S + Q * PP), S


def build_state(u: np.ndarray, PPL: float, feed: dict, geo: dict,
                muR: float, muP: float, pressure_drop: bool,
                closure: str) -> dict:
    """
    EN: Assemble the full terminal state from the unknown vector.

        The retentate outlet pressure needs the flow closure, which needs the
        chord slopes, which need the retentate outlet pressure. That circle is
        closed by a short inner fixed point on P_R,out alone -- five passes to
        machine precision -- and NOT by adding an unknown to the Newton system,
        which would couple a well-conditioned scalar to the rest for no gain.

    PT-BR: Monta o estado terminal a partir do vetor de incognitas. A pressao de
           saida do retentado sai de um ponto fixo interno curto, escalar.
    """
    Q = feed["Q"]; xF = feed["xF"]; nF = feed["nF"]
    PF, PPout, T = feed["PF"], feed["PPout"], feed["T"]
    A = geo["Atot"]
    KB = geo["K_bore"] * muP * T if pressure_drop else 0.0
    KS = geo["K_shell"] * muR * T if pressure_drop else 0.0

    ut = float(u.sum())
    nR = nF * xF - u
    FR = float(nR.sum())
    xR = nR / FR
    yP = u / max(ut, 1e-30)
    th0 = PF * xF - PPout * yP
    S0 = float((Q * th0).sum())

    PRo = PF
    for _ in range(60):
        yPC, SL = weller_steiner(Q, PRo, xR, PPL)
        thL = PRo * xR - PPL * yPC
        c = np.log(np.clip(th0 / np.clip(thL, 1e-300, None), 1e-300, None))
        If = flow_integral(closure, c, Q, th0, u, S0, SL)
        IR = nF - ut + ut * If                      # int_0^1 F_R dzeta
        new = math.sqrt(max(PF ** 2 - KS * IR, 1.0)) if pressure_drop else PF
        if abs(new - PRo) < 1e-9:
            PRo = new
            break
        PRo = new

    yPC, SL = weller_steiner(Q, PRo, xR, PPL)
    thL = PRo * xR - PPL * yPC
    c = np.log(np.clip(th0 / np.clip(thL, 1e-300, None), 1e-300, None))
    If = flow_integral(closure, c, Q, th0, u, S0, SL)

    return dict(Q=Q, xF=xF, nF=nF, A=A, KB=KB, KS=KS, ut=ut, FR=FR, xR=xR,
                yP=yP, PRo=PRo, yPC=yPC, S0=S0, SL=SL, If=If, th0=th0, thL=thL,
                PPL=PPL, PF=PF, PPout=PPout, T=T)
