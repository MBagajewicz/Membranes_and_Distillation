"""
Set Trimming cut -- maximum membrane area from the component-loss constraint.

PURPOSE
-------
The companion cut A >= A_LB (minimum-area proxy) discards candidates too small
to reach the key-component specification. This module supplies the opposite
bound: candidates whose membrane area is so large that the constrained
component -- methane, in natural gas sweetening -- is necessarily lost beyond
the allowed fraction Psi (Eq. 28).

Oversized candidates are exactly the ones that make the simulator suffer: they
drive very high stage cuts, which push the permeate through the fiber bores at
velocities where the momentum model loses validity, and they make the
pressure/flow coupling stiff and slow to converge. Removing them before the
simulation is both a correctness gain and a large computational saving.

DERIVATION
----------
For the constrained component m, the local balance along the membrane area is

    dF_R,m / dA = -Q_m ( P_R x_R,m - P_P x_P,m )

To CERTIFY that the loss is exceeded, a LOWER bound on the amount permeated is
required, i.e. the least-transfer trajectory. Two rigorous ingredients:

  * Retentate pressure. A candidate that satisfies the pressure-drop constraint
    (Eq. 30) has P_R >= P_R_min = P_R_feed - dP_R_max everywhere.

  * Permeate pressure. Bounded above by a design limit P_P_max (see the note on
    assumptions below), and x_P,m <= 1, so P_P x_P,m <= P_P_max.

The mole fraction is eliminated WITHOUT any assumption on how the composition
evolves, by noting that the retentate total flow never exceeds the feed:

    x_R,m = F_R,m / F_R >= F_R,m / F_feed

Substituting gives a linear differential inequality,

    dF_R,m / dA  <=  -a F_R,m + b ,
        a = Q_m P_R_min / F_feed ,      b = Q_m P_P_max

whose integration yields a rigorous upper bound on the retained flow:

    F_R,m(A)  <=  (F_R,m_feed - b/a) exp(-a A) + b/a

and therefore a rigorous LOWER bound on the loss,

    L(A)  >=  1 - F_R,m(A) / F_R,m_feed

Imposing L = Psi and inverting gives the maximum admissible area:

    A_UB = -(1/a) * ln[ ( (1 - Psi) F_R,m_feed - b/a ) / ( F_R,m_feed - b/a ) ]

Any candidate with A_M > A_UB loses more than Psi of component m and is
infeasible by Eq. 28.

CONSERVATISM
------------
The bound x_R,m >= F_R,m / F_feed is rigorous but loose: the retentate shrinks
along the module, so the true mole fraction is larger, the true flux is larger,
and the true loss is larger than the bound. The error is therefore always on
the safe side -- the cut under-trims rather than over-trims.

ASSUMPTION ON THE PERMEATE PRESSURE -- THE ONE NON-RIGOROUS INGREDIENT
---------------------------------------------------------------------
Everything above is rigorous except the ceiling P_P_max, which is a DESIGN
CONSTRAINT rather than a derived bound. No a priori upper bound on the permeate
pressure exists: the pressure at the closed end is an outcome of the simulation,
and the only assumption-free limit (P_P <= P_R) empties the bound by zeroing the
driving force -- taking P_P_max = P_R_min returns A_UB = +inf and cuts nothing.

Adopted here: P_P_max = 10 bar (P_PERM_MAX_DEFAULT). This value must be reported
in the parameter table alongside dP_R_max and Psi, because the strength of the
cut depends on it and a reader cannot audit the result without it.

Direction of the risk if the value is set too low: the real permeate pressure
would then exceed it, the real back-permeation would be larger, the real flux
smaller and the real loss SMALLER than the bound -- so a viable candidate could
be rejected. On the stiff reference candidate the bound reports a guaranteed
loss of 65.2% at P_P_max = 1 bar and 55.2% at 5 bar, both ABOVE the true value
of 53.7%, i.e. invalid; at 10 bar it reports 42.7%, safely below. This is why
the ceiling cannot be set optimistically.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not apply the cut. Following the convention of the constraint layer,
the functions here return the QUANTITY being evaluated -- the membrane area --
and the limit against which it is compared. The comparison and the trimming
decision belong outside, e.g.

    A_M   = membrane_area(dfo, L, Ntf)
    A_UB  = max_area_from_loss(Q_m, f_total, x_m_feed, psi, P_ret_min)
    fun_val = A_M - A_UB

A_UB depends only on the feed, the specifications and the material -- never on
the geometry -- so it is a scalar per material and can be computed once and
reused across the whole candidate set.

For several constrained components (the set M of Eq. 28), evaluate A_UB for each
and keep the smallest.

FUGACITY
--------
The derivation is written in partial pressures. Adopting phi = 1 is conservative
for the key component in CO2/hydrocarbon mixtures, but the same argument does
NOT automatically transfer to the constrained component, and should be checked
before the cut is quoted as rigorous under the fugacity-based model.
"""

from __future__ import annotations


import numpy as np


# Design ceiling on the permeate pressure [Pa]. See the module docstring: this
# is a DESIGN CONSTRAINT, not a derived bound, and the cut is rigorous only
# given it. Report it alongside dP_R_max and Psi.
P_PERM_MAX_DEFAULT = 10.0e5


# ---------------------------------------------------------------------------
# Core bound
# ---------------------------------------------------------------------------
def loss_lower_bound(area,
                     permeance_m: float,
                     feed_flow: float,
                     x_m_feed: float,
                     P_ret_min: float,
                     P_perm_max: float = P_PERM_MAX_DEFAULT):
    """Rigorous LOWER bound of the fractional loss of component m at area `area`.

        L(A) >= 1 - [ (F0 - b/a) exp(-a A) + b/a ] / F0

    Returns 0.0 where no removal can be guaranteed (b/a >= F0), which is the
    safe value: claiming zero guaranteed loss never trims anything.
    """
    A = np.asarray(area, dtype=float)
    F0 = x_m_feed * feed_flow
    a = permeance_m * P_ret_min / feed_flow
    b = permeance_m * P_perm_max
    if a <= 0.0 or F0 <= 0.0:
        return np.zeros_like(A)
    floor = b / a                      # asymptotic retained flow as A -> inf
    span = F0 - floor
    if span <= 0.0:
        return np.zeros_like(A)
    F = span * np.exp(-a * A) + floor
    return 1.0 - F / F0


def max_area_from_loss(permeance_m: float,
                       feed_flow: float,
                       x_m_feed: float,
                       psi_max: float,
                       P_ret_min: float,
                       P_perm_max: float = P_PERM_MAX_DEFAULT) -> float:
    """Maximum membrane area compatible with the loss constraint [m^2].

        A_UB = -(1/a) ln[ ((1 - Psi) F0 - b/a) / (F0 - b/a) ]

    Returns +inf whenever the loss bound can never reach Psi -- either because
    no net removal is guaranteed (b/a >= F0) or because the asymptotic
    guaranteed loss, 1 - (b/a)/F0, is itself below Psi. Returning +inf means
    "this cut proves nothing here", which is the only safe behaviour: returning
    a finite (let alone zero) value in those cases would trim viable candidates.
    """
    F0 = x_m_feed * feed_flow
    if feed_flow <= 0.0 or F0 <= 0.0 or permeance_m <= 0.0 or P_ret_min <= 0.0:
        return float("inf")

    a = permeance_m * P_ret_min / feed_flow
    b = permeance_m * P_perm_max
    floor = b / a

    den = F0 - floor                    # guaranteed removable flow
    if den <= 0.0:
        return float("inf")             # driving force not guaranteed positive

    num = (1.0 - psi_max) * F0 - floor  # retained flow at the loss limit
    if num <= 0.0:
        return float("inf")             # asymptotic guaranteed loss <= Psi

    return float(-np.log(num / den) / a)


# ---------------------------------------------------------------------------
# Per-material dispatch
# ---------------------------------------------------------------------------
def max_area_by_material(permeance_by_material: dict,
                         materials,
                         retained_index: int,
                         feed_flow: float,
                         x_m_feed: float,
                         psi_max: float,
                         P_ret_min: float,
                         P_perm_max: float = P_PERM_MAX_DEFAULT):
    """Maximum admissible area for each candidate, dispatched by its material.

    A_UB depends on the material ONLY through the permeance of the constrained
    component, and not at all on the geometry. It is therefore a single scalar
    per material: with two materials over a million candidates, exactly two
    evaluations are needed. This function computes one value per distinct entry
    of `materials` and broadcasts it back onto the candidate array.

    Parameters
    ----------
    permeance_by_material : dict mapping material name -> array of component
        permeances, e.g. {'PI': array([...]), 'CA': array([...])}. All materials
        must share the same component ordering.
    materials : array of material names, one per candidate.
    retained_index : index of the constrained component (the one whose loss is
        limited by Psi -- methane in sweetening, NOT the key component).
    feed_flow, x_m_feed, psi_max, P_ret_min, P_perm_max
        As in `max_area_from_loss`.

    Returns
    -------
    Array of A_UB values [m^2], aligned with `materials`. Entries are +inf where
    the bound proves nothing for that material.
    """
    mats = np.asarray(materials)
    scalar_input = mats.ndim == 0
    if scalar_input:
        mats = mats.reshape(1)

    out = np.empty(mats.shape, dtype=float)
    for name in np.unique(mats):
        key = name.item() if hasattr(name, "item") else name
        if key not in permeance_by_material:
            raise KeyError(f"Material '{key}' ausente em permeance_by_material.")
        Q = np.asarray(permeance_by_material[key], dtype=float)
        out[mats == name] = max_area_from_loss(
            permeance_m=float(Q[retained_index]),
            feed_flow=feed_flow,
            x_m_feed=x_m_feed,
            psi_max=psi_max,
            P_ret_min=P_ret_min,
            P_perm_max=P_perm_max,
        )
    return float(out[0]) if scalar_input else out


# ---------------------------------------------------------------------------
# Geometry -- the quantity being evaluated
# ---------------------------------------------------------------------------
def membrane_area(d_fo, length, n_fibers):
    """Outer membrane area of the bundle [m^2],

        A_M = pi d_fo L N

    This is the value the constraint is written on. The number of fibers is
    taken as an argument rather than recomputed here, so the caller keeps a
    single definition of it.

    Accepts scalars or equal-shaped NumPy arrays.
    """
    d_fo = np.asarray(d_fo, dtype=float)
    length = np.asarray(length, dtype=float)
    n_fibers = np.asarray(n_fibers, dtype=float)
    return np.pi * d_fo * length * n_fibers


__all__ = [
    "P_PERM_MAX_DEFAULT",
    "loss_lower_bound",
    "max_area_from_loss",
    "max_area_by_material",
    "membrane_area",
]
