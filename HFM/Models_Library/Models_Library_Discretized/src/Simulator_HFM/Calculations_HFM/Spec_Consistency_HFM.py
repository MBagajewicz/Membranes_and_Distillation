"""
Specification consistency -- is the requested separation possible at all?

PURPOSE
-------
Two specifications are imposed on the module: the key component must leave the
retentate below a mole fraction Theta (Eq. 27), and the constrained component
must not be lost to the permeate beyond a fraction Psi (Eq. 28). These are not
independent. Removing the key component always drags some of the constrained
component along, and how much is set by the selectivity. Below a certain loss,
the requested purity is simply unreachable -- by any geometry, any area, any
number of fibers.

This module computes that floor. If the minimum loss exceeds Psi, the design
problem has no solution and the whole enumeration would return empty. Running
this check first costs milliseconds and can save an entire campaign.

THE BOUND AND ITS DIRECTION
---------------------------
The quantity computed is a rigorous LOWER bound on the loss:

    L_min > Psi   =>  specification pair is IMPOSSIBLE (certified)
    L_min <= Psi  =>  not proven impossible; real designs will lose MORE

It is one-sided in the safe direction. A pair that passes still has to be
checked by simulation; a pair that fails needs no further work.

Why it is a lower bound: the loss is minimised when the co-permeation ratio
J_m / J_k is minimised, and that ratio grows with permeate back-pressure. Any
back-pressure depresses the flux of the fast component more than that of the
slow one, because the fast component is the one accumulating on the permeate
side. Evaluating the trajectory at the LOWEST admissible permeate pressure
therefore yields the least possible co-permeation.

TWO LEVELS
----------
* Ideal limit, P_perm = 0. Closed form, no integration. Starting from the
  Rayleigh trajectory of the trimming proxy (Eq. 36),

      F_R,i = F_R,i_feed (F_R,k / F_R,k_feed)^(Q_i/Q_k)

  the whole retentate state is parametrised by the single variable

      u = F_R,k / F_R,k_feed

  Solving x_R,k(u) = Theta gives u_Theta, and the loss follows immediately:

      L_min = 1 - u_Theta^(Q_m/Q_k) = 1 - u_Theta^(1/alpha)

* Design pressures, P_perm = P_perm_out. Tighter, because the specified outlet
  pressure is the lowest the permeate ever reaches inside the module, so it is
  still a valid lower bound -- and a sharper one. No closed form; the trajectory
  is integrated with the local permeate composition solved implicitly at every
  step, from

      y_i = Q_i P_R x_i / (S + Q_i P_P) ,   sum_i y_i = 1

  which is the same relation used per cell by the marching solver.

RULE OF THUMB
-------------
For a binary idealisation, with the separation difficulty ratio

    R = [x_k_feed /(1 - x_k_feed)] / [Theta /(1 - Theta)]

the closed form collapses to

    L_min ~= 1 - R^(-1/alpha)

showing that the minimum loss is governed by ln(R)/alpha -- how hard the
separation is, divided by how selective the material is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import numpy as np


# ---------------------------------------------------------------------------
# Finite permeate pressure -- tighter bound
# ---------------------------------------------------------------------------
def local_permeate_composition(x: np.ndarray,
                               permeance: np.ndarray,
                               P_ret: float,
                               P_perm: float) -> Tuple[np.ndarray, float]:
    """Local permeate composition, solved implicitly.

    Each component satisfies y_i = Q_i P_R x_i / (S + Q_i P_P) with S the total
    flux; imposing sum_i y_i = 1 gives a scalar equation for S, solved by
    bracketing. Returns (y, S).
    """
    Q = np.asarray(permeance, dtype=float)
    x = np.asarray(x, dtype=float)
    if P_perm <= 0.0:
        J = Q * P_ret * x
        tot = J.sum()
        return (J / tot if tot > 0 else np.zeros_like(J)), float(tot)

    def f(S):
        return float(np.sum(Q * P_ret * x / (S + Q * P_perm)) - 1.0)

    hi = max(float(np.sum(Q * P_ret * x)), 1e-30) * 10.0
    guard = 0
    while f(hi) > 0.0 and guard < 200:
        hi *= 10.0
        guard += 1
    S = brentq(f, 1e-30, hi, rtol=1e-12)
    y = Q * P_ret * x / (S + Q * P_perm)
    s = y.sum()
    return (y / s if s > 0 else y), float(S)


def minimum_loss_at_pressure(feed_composition: np.ndarray,
                             permeance: np.ndarray,
                             theta_key: float,
                             P_ret: float,
                             P_perm_out: float,
                             key_index: int = 0,
                             retained_index: int = 1,
                             feed_flow: float = 1.0,
                             area_max: float = 1.0e9) -> Tuple[Optional[float], Optional[float]]:
    """Minimum loss evaluated at the design pressures (tighter than the ideal).

    The retentate pressure is held at its maximum (the feed value) and the
    permeate at its minimum (the specified outlet value); both choices minimise
    co-permeation, so the result remains a rigorous lower bound.

    Returns
    -------
    loss : lower bound of the loss fraction, or None if Theta is unreachable at
           these pressures (pinch -- the driving force for the key component
           vanishes before the specification is met).
    area : trajectory coordinate (area per unit permeance basis) where Theta is
           reached; None on pinch.
    """
    x0 = np.asarray(feed_composition, dtype=float)
    Q = np.asarray(permeance, dtype=float)
    F0 = x0 * feed_flow

    def rhs(_A, F):
        F = np.maximum(F, 1e-20)
        x = F / F.sum()
        y, _ = local_permeate_composition(x, Q, P_ret, P_perm_out)
        J = Q * (P_ret * x - P_perm_out * y)
        return -np.maximum(J, 0.0)          # no back-permeation into the retentate

    def reached(_A, F):
        F = np.maximum(F, 1e-20)
        return F[key_index] / F.sum() - theta_key
    reached.terminal = True
    reached.direction = -1

    sol = solve_ivp(rhs, [0.0, area_max], F0, events=reached,
                    rtol=1e-10, atol=1e-16, max_step=area_max / 1e3)
    if not sol.t_events[0].size:
        return None, None                    # pinch: Theta never reached
    F_end = sol.y_events[0][0]
    loss = 1.0 - F_end[retained_index] / F0[retained_index]
    return float(loss), float(sol.t_events[0][0])


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
@dataclass
class ConsistencyVerdict:
    possible: bool
    loss_min: Optional[float]
    psi_required: Optional[float]
    theta: float
    alpha: float
    basis: str
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if self.loss_min is None:
            return (f"Theta={self.theta:.3f} INATINGÍVEL nas pressões dadas "
                    f"(pinch) -- {self.basis}")
        verdict = "possível" if self.possible else "IMPOSSÍVEL"
        return (f"Theta={self.theta:.3f}, alpha={self.alpha:.1f}: perda mínima "
                f"{self.loss_min*100:.2f}% -> {verdict} ({self.basis})")


def check_specification_consistency(feed_composition: np.ndarray,
                                    permeance: np.ndarray,
                                    theta_key: float,
                                    psi_max: Optional[float] = None,
                                    P_ret: Optional[float] = None,
                                    P_perm_out: Optional[float] = None,
                                    key_index: int = 0,
                                    retained_index: int = 1) -> ConsistencyVerdict:
    """Decide whether the (Theta, Psi) pair is achievable with this material.

    When both pressures are supplied the tighter design-pressure bound is used;
    otherwise the ideal closed form is used. `psi_max` may be omitted, in which
    case the verdict simply reports the minimum loss (the smallest Psi that
    could possibly be specified).
    """
    x = np.asarray(feed_composition, dtype=float)
    Q = np.asarray(permeance, dtype=float)
    alpha = float(Q[key_index] / Q[retained_index])
    notes: List[str] = []

    if P_ret is not None and P_perm_out is not None:
        loss, _ = minimum_loss_at_pressure(x, Q, theta_key, P_ret, P_perm_out,
                                           key_index, retained_index)
        basis = f"pressões de projeto (P_ret={P_ret/1e5:.1f} bar, P_perm={P_perm_out/1e5:.1f} bar)"
        if loss is None:
            notes.append("Força motriz do componente-chave se anula antes de Theta: "
                         "reduza a pressão do permeado ou relaxe Theta.")
            return ConsistencyVerdict(False, None, None, theta_key, alpha, basis, notes)
    else:
        loss, _ = minimum_loss_ideal(x, Q, theta_key, key_index, retained_index)
        basis = "limite ideal (P_perm = 0)"
        notes.append("Cota do limite ideal; usar as pressões de projeto aperta o valor.")

    approx = minimum_loss_rule_of_thumb(x[key_index], theta_key, alpha)
    notes.append(f"Regra de bolso binária: {approx*100:.2f}% "
                 f"(R = {separation_difficulty_ratio(x[key_index], theta_key):.2f})")

    possible = True if psi_max is None else bool(loss <= psi_max)
    if psi_max is not None and not possible:
        notes.append(f"Psi = {psi_max*100:.2f}% está abaixo do piso: nenhuma "
                     f"geometria satisfaz ambas as especificações.")
    return ConsistencyVerdict(possible, loss, loss, theta_key, alpha, basis, notes)


# ---------------------------------------------------------------------------
# Map over (Theta, alpha)
# ---------------------------------------------------------------------------
def loss_map(feed_composition: np.ndarray,
             permeance: np.ndarray,
             thetas: Sequence[float],
             alphas: Sequence[float],
             P_ret: Optional[float] = None,
             P_perm_out: Optional[float] = None,
             key_index: int = 0,
             retained_index: int = 1) -> np.ndarray:
    """Minimum-loss table over a grid of (Theta, alpha).

    The permeance of the constrained component is overridden as
    Q_m = Q_k / alpha, all other components untouched, so the map isolates the
    effect of the key/constrained selectivity. Returns an array of shape
    (len(alphas), len(thetas)); NaN marks pinch.
    """
    x = np.asarray(feed_composition, dtype=float)
    Q0 = np.asarray(permeance, dtype=float)
    out = np.full((len(alphas), len(thetas)), np.nan)
    for i, alpha in enumerate(alphas):
        Q = Q0.copy()
        Q[retained_index] = Q0[key_index] / alpha
        for j, th in enumerate(thetas):
            if P_ret is not None and P_perm_out is not None:
                loss, _ = minimum_loss_at_pressure(x, Q, th, P_ret, P_perm_out,
                                                   key_index, retained_index)
            else:
                loss, _ = minimum_loss_ideal(x, Q, th, key_index, retained_index)
            if loss is not None:
                out[i, j] = loss
    return out


__all__ = [
    "ConsistencyVerdict",
    "minimum_loss_ideal",
    "minimum_loss_at_pressure",
    "local_permeate_composition",
    "separation_difficulty_ratio",
    "minimum_loss_rule_of_thumb",
    "check_specification_consistency",
    "loss_map",
]
