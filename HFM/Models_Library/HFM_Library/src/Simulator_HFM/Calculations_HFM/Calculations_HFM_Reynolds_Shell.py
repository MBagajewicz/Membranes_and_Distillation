"""
Set Trimming cut -- shell-side (retentate) Reynolds number.

PURPOSE
-------
The momentum balance adopted for the shell side is a Hagen-Poiseuille-type
laminar correlation (friction factor 24/Re for a square fiber arrangement).
That correlation is only defined for laminar flow, so a candidate whose
shell-side Reynolds number exceeds the laminar limit is outside the validity
domain of the model and must be discarded.

This cut requires NO simulation. The Reynolds number of a gas, written in
molar-flow terms, is independent of pressure:

    Re = rho * v * d_h / mu ,   v = F Z R T /(P A) ,   rho = P M /(Z R T)

       => Re = F * M * d_h / (A * mu)

The pressure (and Z, and T) cancel between density and velocity. Therefore the
shell Reynolds number depends only on the molar flow, the mixture molar mass,
the geometry and the viscosity -- all known before any simulation.

WHY THE CUT IS SAFE (one-sided error)
-------------------------------------
Trimming may only discard a candidate that is certainly infeasible. False
negatives (discarding a viable candidate) are forbidden; false positives
(keeping an infeasible one) are tolerated. The cut must therefore be built on a
LOWER bound of Re, so that exceeding the limit is certain:

  * Molar flow. The retentate flow is largest at the feed inlet, where it equals
    the feed flow exactly. Since the criterion asks whether ANY point of the
    module is non-laminar, and the maximum along the module is at least the
    inlet value, evaluating at the inlet is exact -- not a bound.

  * Viscosity. Re is inversely proportional to mu, so a LOWER bound on Re
    requires an UPPER bound on mu. For the Herning-Zipperer mixing rule the
    mixture viscosity is a weighted average of the pure-component viscosities
    with positive weights summing to one, hence it lies between the minimum and
    the maximum pure value. The maximum pure-component viscosity is therefore a
    rigorous upper bound. Only components actually present in the feed
    (non-zero mole fraction) are considered.

  * Geometry. Exact.

Using the minimum pure viscosity instead would give an UPPER bound on Re, which
cannot certify a violation and would trim viable candidates.

NOTE ON THE LIMIT
-----------------
The default ceiling is Re = 2100, the classical laminar limit for fully
developed flow in a circular pipe. This is a conservative, citable choice, but
the reader should be aware that the shell side is axial flow through a fiber
bundle, not pipe flow. Transition values reported for rod bundles vary (values
around 2500 and above 4000 appear in the literature for the same bundle
depending on the correlation adopted), and recent high-fidelity simulations
indicate transition can begin at considerably lower Reynolds numbers through
gap instabilities. There is no established consensus value for fiber bundles,
and hollow-fiber packing is typically irregular rather than a regular lattice.
The limit is exposed as a parameter so the sensitivity of the results to this
choice can be reported.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def shell_free_area(D_shell, n_fibers, d_fo):
    """Cross-sectional area available to shell-side flow [m^2],

        A = pi (D^2 - N d_fo^2) / 4
    """
    D_shell = np.asarray(D_shell, dtype=float)
    n_fibers = np.asarray(n_fibers, dtype=float)
    d_fo = np.asarray(d_fo, dtype=float)
    return np.pi * (D_shell ** 2 - n_fibers * d_fo ** 2) / 4.0


def shell_hydraulic_diameter(D_shell, n_fibers, d_fo):
    """Hydraulic diameter for axial flow through the bundle [m],

        d_h = 4 A_free / wetted perimeter
            = (D^2 - N d_fo^2) / (D + N d_fo)

    The wetted perimeter includes the shell wall (pi D) and every fiber
    (N pi d_fo).
    """
    D_shell = np.asarray(D_shell, dtype=float)
    n_fibers = np.asarray(n_fibers, dtype=float)
    d_fo = np.asarray(d_fo, dtype=float)
    perimeter = D_shell + n_fibers * d_fo
    with np.errstate(divide="ignore", invalid="ignore"):
        d_h = (D_shell ** 2 - n_fibers * d_fo ** 2) / perimeter
    return d_h


# ---------------------------------------------------------------------------
# Reynolds number
# ---------------------------------------------------------------------------
def shell_reynolds(feed_flow: float,
                   feed_composition,
                   molar_masses,
                   viscosities,
                   D_shell,
                   d_fo,
                   n_fibers):
    """Shell-side Reynolds number, evaluated at the feed inlet.

        Re = F_feed * M_feed * d_h / (A_free * mu_max)

    Computed explicitly from d_h and A_free (no algebraic simplification), so
    every geometric quantity remains inspectable.

    All geometric arguments may be scalars or NumPy arrays of equal shape,
    allowing the whole candidate set to be evaluated in one call.

    Returns +inf where the geometry is impossible (fibers do not fit in the
    shell), so that such candidates are trimmed by the same comparison.
    """
    x = np.asarray(feed_composition, dtype=float)
    M = np.asarray(molar_masses, dtype=float)
    mu = np.asarray(viscosities, dtype=float)

    M_feed = float(np.dot(x, M))
    mu_max = float(np.max(mu[x > 0]))

    A_free = shell_free_area(D_shell, n_fibers, d_fo)
    d_h = shell_hydraulic_diameter(D_shell, n_fibers, d_fo)

    with np.errstate(divide="ignore", invalid="ignore"):
        Re = feed_flow * M_feed * d_h / (A_free * mu_max)

    return Re
