"""
Set Trimming cut -- bore-side (permeate) Reynolds number.

PURPOSE
-------
The bore-side pressure drop is described by the Hagen-Poiseuille equation
(friction factor 16/Re), valid only for laminar flow. A candidate whose
bore-side Reynolds number exceeds the laminar limit falls outside the validity
domain of the momentum model and must be discarded.

As on the shell side, the cut requires NO simulation, because the Reynolds
number of a gas written in molar-flow terms carries no pressure dependence:

    Re = rho * v * d_i / mu ,   v = F Z R T /(P A) ,   rho = P M /(Z R T)

       => Re = F * M * d_i / (A * mu)

WHERE THE PERMEATE FLOW COMES FROM
----------------------------------
Unlike the retentate -- whose inlet flow is the feed flow, known exactly -- the
permeate flow is an outcome of the simulation. A trimming cut cannot wait for
it. The separation specification supplies the missing lower bound.

To bring the key component from its feed mole fraction down to the specified
retentate limit Theta, a minimum amount must cross the membrane. Writing the
key-component balance with F_R <= F_feed:

    F_P,key  =  x_key,feed * F_feed - x_key,ret * F_R
             >= (x_key,feed - Theta) * F_feed

and the total permeate is at least its key-component content, so

    F_P >= F_P_min = (x_key,feed - Theta) * F_feed

The permeate flow is largest at the permeate outlet (z = 0), where the whole
permeate stream has accumulated, so the bound applies exactly where the
Reynolds number peaks.

CONDITIONAL VALIDITY -- AND WHY THE CUT IS STILL SAFE
-----------------------------------------------------
The bound above assumes the candidate MEETS the separation specification. That
is sufficient for a safe cut, by cases:

  * If the candidate meets the specification, its permeate flow is at least
    F_P_min, so a Reynolds violation computed from that bound is real.
  * If it does not meet the specification, it is already infeasible through the
    key-component constraint.

Either branch ends in rejection, so trimming on this criterion cannot discard a
viable candidate. (Diagnostically, a specification-failing candidate may show a
bore Reynolds number above its true value -- harmless, but worth knowing when
inspecting the numbers.)

ONE-SIDED ERROR IN THE REMAINING QUANTITIES
-------------------------------------------
A LOWER bound on Re is required, so:

  * Molar flow  -> lower bound  : F_P_min, as derived above.
  * Molar mass  -> lower bound  : the permeate composition is unknown a priori,
    so the smallest pure-component molar mass among the components present in
    the feed is used. This is conservative (the permeate is in practice
    enriched in the fast component), and a tighter bound would strengthen the
    cut.
  * Viscosity   -> UPPER bound  : Re is inversely proportional to mu. For the
    Herning-Zipperer mixing rule the mixture viscosity lies between the
    pure-component extremes, so the largest pure viscosity among the components
    present in the feed is a rigorous upper bound.
  * Geometry    -> exact.

NOTE ON THE LIMIT
-----------------
The default ceiling is Re = 2100, the classical laminar limit for fully
developed flow in a circular pipe. The fiber bore IS a circular pipe, so this
limit applies far more directly here than on the shell side. The value is still
exposed as a parameter for sensitivity studies.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Feed-derived bounds
# ---------------------------------------------------------------------------
def minimum_permeate_flow(feed_flow, feed_composition, theta_key,
                          key_index=0):
    """Return the lower bound of total permeate molar flow [mol/s]."""
    x = np.asarray(feed_composition, dtype=float)
    return float(max(0.0, (x[key_index] - theta_key) * feed_flow))

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def bore_free_area(n_fibers, d_fi):
    """Return the total cross-sectional area of all fiber bores [m²]."""
    n_fibers = np.asarray(n_fibers, dtype=float)
    d_fi = np.asarray(d_fi, dtype=float)
    return n_fibers * np.pi * d_fi**2 / 4.0


# ---------------------------------------------------------------------------
# Reynolds calculation from already prepared quantities
# ---------------------------------------------------------------------------
def bore_reynolds(feed_flow,
                  feed_composition,
                  molar_masses,
                  viscosities,
                  theta_key,
                  d_fi,
                  n_fibers,
                  key_index):
    """Calculate bore-side Reynolds numbers at the permeate outlet.

    Scalar and array candidate geometries are accepted. Impossible geometries
    are represented by ``np.inf`` so they remain immediately identifiable by
    the calling code.
    """
    x = np.asarray(feed_composition, dtype=float)
    M = np.asarray(molar_masses, dtype=float)
    mu = np.asarray(viscosities, dtype=float)

    F_perm_min = minimum_permeate_flow(
        feed_flow=feed_flow,
        feed_composition=x,
        theta_key=theta_key,
        key_index=key_index,
    )

    M_min = float(np.min(M[x > 0]))
    mu_max = float(np.max(mu[x > 0]))

    d_fi = np.asarray(d_fi, dtype=float)
    n_fibers = np.asarray(n_fibers, dtype=float)
    A_bore = bore_free_area(n_fibers, d_fi)

    with np.errstate(divide="ignore", invalid="ignore"):
        Re = F_perm_min * M_min * d_fi / (A_bore * mu_max)

    return Re