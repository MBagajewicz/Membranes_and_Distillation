# -*- coding: utf-8 -*-
"""
Calculations_HFM_Min_Area_XR_Comp.py

Safe area-floor trimming for multicomponent hollow-fiber membrane candidates.

Main use
--------
    A_floor, info = compute_rayleigh_area_floor(
        Q=Q,
        A_t=A_t,
        Pf=Pf,
        F_f=F_f,
        x_feed=x_feed,
        Key_Comp_index=Key_Comp_index,
        x_key_max=0.03,
        return_all=True,
    )

    cut_mask = info["cut_mask"]

or simply:

    cut_mask, A_floor, info = rayleigh_area_floor_cut_mask(...)

Meaning
-------
The function computes the idealized area required to reduce the retentate mole
fraction of a key component k to x_key_max under the most favorable transport
conditions:

    dF_i/dA = - Q_i * Pf * F_i / F_T

with:
    - retentate-side pressure fixed at Pf;
    - permeate-side partial pressure set to zero for every component;
    - all components permeating with the same constant permeances Q_i used in
      the rigorous model.

If the installed candidate area A_t is smaller than this idealized area floor,
the candidate cannot satisfy the full-model retentate composition constraint
and can be safely discarded.

Safe trimming rule
------------------
    A_t < A_floor  ->  discard candidate

Important assumptions
---------------------
The safety proof assumes:
    1. The key component is the fastest permeating species:
            Q_key >= Q_j for all j != key.
    2. The same constant permeances Q_i are used in this area floor and in the
       rigorous model.
    3. The local retentate pressure/fugacity term in the rigorous model is
       bounded above by Pf.
    4. The permeate-side pressure/fugacity term is nonnegative.
    5. Component fluxes are non-reversing in the operating region.
    6. The permeate composition is the bulk closed-end permeate composition,
       i.e., the stream accumulated from the closed end.
    7. There are no reactions or source terms for the key component.

If require_key_fastest=True, candidates for which the key is not the fastest
component are marked uncertified and assigned A_floor = 0. This prevents unsafe
cuts.

Array convention
----------------
Preferred Q shape:
    Q.shape == (n_comp, n_candidates)

Also accepted:
    Q.shape == (n_comp,)
    Q.shape == (n_candidates, n_comp)

Preferred x_feed shape:
    x_feed.shape == (n_comp,)

Also accepted:
    x_feed.shape == (n_comp, 1)
    x_feed.shape == (n_comp, n_candidates)
    x_feed.shape == (n_candidates, n_comp)

Pf, F_f, and A_t may be scalars or one-dimensional arrays with one value per
candidate.
"""

from __future__ import annotations

import numpy as np


def compute_rayleigh_area_floor(
    Q,
    Pf,
    F_f,
    x_feed,
    Key_Comp_index,
    Material=None,
    x_key_max=0.03,
    A_t=None,
    require_key_fastest=True,
    fastest_tol=1e-12,
    r_zero_tol=1e-14,
    root_tol=1e-13,
    max_bisect=200,
    eps=1e-16,
    return_all=False,
):
    """
    Compute the idealized multicomponent area floor for safe trimming.

    Parameters
    ----------
    Q : array_like
        Component permeances. Accepted shapes:
            (n_comp,), (n_comp, n_candidates), or (n_candidates, n_comp).
        Use the real constant permeances used in the rigorous model.

    Pf : float or array_like
        Feed/retentate pressure, or an upper bound on the local retentate-side
        pressure/fugacity term. Scalar or one value per candidate.

    F_f : float or array_like
        Feed molar flow rate. Scalar or one value per candidate.

    x_feed : array_like
        Feed composition. Accepted shapes:
            (n_comp,), (n_comp, 1), (n_comp, n_candidates),
            or (n_candidates, n_comp).

    Key_Comp_index : int
        Index of the component constrained in the retentate.

    x_key_max : float, default 0.03
        Maximum allowed retentate mole fraction of the key component.

    A_t : None, float, or array_like, optional
        Installed candidate membrane area. If supplied, a cut_mask is returned
        in the diagnostics.

    require_key_fastest : bool, default True
        If True, the function performs a safe no-cut fallback when the key
        component is not the fastest species. In that case A_floor = 0 and
        certified = False.

    fastest_tol : float, default 1e-12
        Numerical tolerance used in the key-fastest check.

    r_zero_tol : float, default 1e-14
        If Q_j/Q_k <= r_zero_tol, the logarithmic limiting term is used.

    root_tol : float, default 1e-13
        Bisection tolerance for the scalar target solve.

    max_bisect : int, default 200
        Maximum number of bisection iterations.

    eps : float, default 1e-16
        Numerical floor.

    return_all : bool, default False
        If False, returns A_floor only.
        If True, returns (A_floor, info).

    Returns
    -------
    A_floor : np.ndarray
        Area floor for each candidate. Shape (n_candidates,).

    info : dict, optional
        Returned when return_all=True. Main keys:
            "A_floor"
            "s_star"
            "cut_mask" if A_t is provided
            "certified"
            "key_is_fastest"
            "already_satisfies"
            "target_reachable_in_ideal_model"
            "reason"
    """

    if not (0.0 <= x_key_max < 1.0):
        raise ValueError("x_key_max must satisfy 0 <= x_key_max < 1.")

    if max_bisect < 1:
        raise ValueError("max_bisect must be at least 1.")

    # ------------------------------------------------------------------
    # Shape preparation
    # ------------------------------------------------------------------
    x_raw = np.asarray(x_feed, dtype=float)

    n_comp = _infer_n_comp(Q, x_raw)
    n_cases = _infer_n_cases(Q, Material, A_t, Pf, F_f, x_raw, n_comp)

    Q_mat, material_vec = _prepare_q_matrix(Q, n_comp, n_cases, Material)

    x_mat = _prepare_component_case_matrix(x_raw, n_comp, "x_feed")
    if x_mat.shape[1] == 1 and n_cases > 1:
        x_mat = np.repeat(x_mat, n_cases, axis=1)
    elif x_mat.shape[1] != n_cases:
        raise ValueError(
            "x_feed must provide either one composition vector or one "
            "composition vector per candidate."
        )

    Pf_vec = _as_case_vector(Pf, n_cases, "Pf")
    F_vec = _as_case_vector(F_f, n_cases, "F_f")
    A_vec = None if A_t is None else _as_case_vector(A_t, n_cases, "A_t")

    k = int(Key_Comp_index)
    if k < 0 or k >= n_comp:
        raise ValueError("Key_Comp_index is outside the component range.")

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    if np.any(Q_mat < 0.0):
        raise ValueError("All permeances Q must be nonnegative.")
    if np.any(Pf_vec <= 0.0):
        raise ValueError("Pf must be positive.")
    if np.any(F_vec <= 0.0):
        raise ValueError("F_f must be positive.")
    if np.any(x_mat < 0.0):
        raise ValueError("x_feed must be nonnegative.")
    if A_vec is not None and np.any(A_vec < 0.0):
        raise ValueError("A_t must be nonnegative.")

    col_sums = np.sum(x_mat, axis=0)
    if not np.allclose(col_sums, 1.0, rtol=1e-8, atol=1e-12):
        raise ValueError(
            "Each x_feed column must sum to one. "
            f"Current sums: {col_sums}"
        )

    # ------------------------------------------------------------------
    # Allocate outputs
    # ------------------------------------------------------------------
    A_floor = np.zeros(n_cases, dtype=float)
    s_star = np.full(n_cases, np.nan, dtype=float)
    certified = np.zeros(n_cases, dtype=bool)
    key_is_fastest = np.zeros(n_cases, dtype=bool)
    already_satisfies = np.zeros(n_cases, dtype=bool)
    target_reachable = np.zeros(n_cases, dtype=bool)
    reason = np.empty(n_cases, dtype=object)
    x_key_feed = x_mat[k, :].copy()

    # ------------------------------------------------------------------
    # Candidate loop
    # ------------------------------------------------------------------
    for c in range(n_cases):
        Qc = Q_mat[:, c]
        xc = x_mat[:, c]
        Qk = Qc[k]
        xk0 = xc[k]

        non_idx = np.array([i for i in range(n_comp) if i != k], dtype=int)

        already_satisfies[c] = xk0 <= x_key_max + 1e-15
        if already_satisfies[c]:
            A_floor[c] = 0.0
            s_star[c] = 1.0
            certified[c] = True
            target_reachable[c] = True
            key_is_fastest[c] = _is_key_fastest(Qc, k, non_idx, fastest_tol)
            reason[c] = "feed_already_satisfies_spec"
            continue

        if Qk <= eps:
            # With zero key permeance, an above-spec key component cannot be
            # depleted by membrane permeation. This is a safe infinite floor
            # under the same constant-Q model.
            A_floor[c] = np.inf
            s_star[c] = np.nan
            certified[c] = True
            target_reachable[c] = False
            key_is_fastest[c] = _is_key_fastest(Qc, k, non_idx, fastest_tol)
            reason[c] = "key_permeance_zero_above_spec"
            continue

        key_is_fastest[c] = _is_key_fastest(Qc, k, non_idx, fastest_tol)
        if require_key_fastest and not key_is_fastest[c]:
            # Safe no-cut fallback.
            A_floor[c] = 0.0
            s_star[c] = np.nan
            certified[c] = False
            target_reachable[c] = False
            reason[c] = "uncertified_key_not_fastest_no_cut"
            continue

        F0 = F_vec[c] * xc
        Fk0 = F0[k]
        Fj0 = F0[non_idx]
        Qj = Qc[non_idx]

        positive_nonkey = Fj0 > eps

        if not np.any(positive_nonkey):
            # A retentate containing only the key component cannot have a
            # key mole fraction below x_key_max < 1 while retaining nonzero
            # retentate product. Treat as unreachable.
            A_floor[c] = np.inf
            s_star[c] = np.nan
            certified[c] = True
            target_reachable[c] = False
            reason[c] = "pure_key_feed_spec_unreachable"
            continue

        r = np.divide(Qj, Qk, out=np.zeros_like(Qj), where=Qk > eps)

        # If all positive non-key species have r == 1, all components decay
        # proportionally and x_key remains constant. Since feed is above spec,
        # the target is unreachable even in the ideal model.
        has_selective_nonkey = np.any((r[positive_nonkey] < 1.0 - fastest_tol))
        if not has_selective_nonkey:
            A_floor[c] = np.inf
            s_star[c] = np.nan
            certified[c] = True
            target_reachable[c] = False
            reason[c] = "ideal_model_cannot_reduce_key_fraction_equal_permeance"
            continue

        # Solve x_key(s) = x_key_max.
        s = _solve_s_star(
            Fk0=Fk0,
            Fj0=Fj0,
            r=r,
            x_target=x_key_max,
            eps=eps,
            root_tol=root_tol,
            max_bisect=max_bisect,
        )

        s_star[c] = s

        # Compute area.
        bracket = 1.0 - s
        infinite = False

        for Fj, rj in zip(Fj0, r):
            if Fj <= eps:
                continue

            term = _rayleigh_integral_term(s, rj, r_zero_tol)
            if not np.isfinite(term):
                infinite = True
                break

            bracket += (Fj / Fk0) * term

        if infinite:
            A_floor[c] = np.inf
            target_reachable[c] = False
            reason[c] = "infinite_area_due_to_zero_permeance_limit"
        else:
            A_floor[c] = Fk0 / (Qk * Pf_vec[c]) * bracket
            target_reachable[c] = True
            reason[c] = "ok"

        certified[c] = True

    if return_all:
        info = {
            "A_floor": A_floor,
            "s_star": s_star,
            "certified": certified,
            "key_is_fastest": key_is_fastest,
            "already_satisfies": already_satisfies,
            "target_reachable_in_ideal_model": target_reachable,
            "x_key_feed": x_key_feed,
            "x_key_max": x_key_max,
            "reason": reason,
            "assumptions": (
                "Safe if key is fastest, Q are the real constant permeances, "
                "retentate pressure/fugacity is bounded by Pf, permeate "
                "pressure/fugacity is nonnegative, fluxes are non-reversing, "
                "and permeate composition is bulk closed-end permeate."
            ),
        }

        if material_vec is not None:
            info["Material"] = material_vec

        if A_vec is not None:
            info["A_t"] = A_vec
            info["cut_mask"] = A_vec < A_floor

        return A_floor, info

    return A_floor


def rayleigh_area_floor_cut_mask(
    Q,
    A_t,
    Pf,
    F_f,
    x_feed,
    Key_Comp_index,
    Material=None,
    x_key_max=0.03,
    require_key_fastest=True,
    **kwargs,
):
    """
    Convenience wrapper returning the cut mask directly.

    Returns
    -------
    cut_mask : np.ndarray
        True for candidates safely discarded by A_t < A_floor.

    A_floor : np.ndarray
        Area floor for each candidate.

    info : dict
        Diagnostics from compute_rayleigh_area_floor.
    """
    A_floor, info = compute_rayleigh_area_floor(
        Q=Q,
        Pf=Pf,
        F_f=F_f,
        x_feed=x_feed,
        Key_Comp_index=Key_Comp_index,
        Material=Material,
        x_key_max=x_key_max,
        A_t=A_t,
        require_key_fastest=require_key_fastest,
        return_all=True,
        **kwargs,
    )

    return info["cut_mask"], A_floor, info


# ----------------------------------------------------------------------
# Internal helper functions
# ----------------------------------------------------------------------
def _infer_n_comp(Q, x_raw):
    if x_raw.ndim == 1:
        return x_raw.size

    if x_raw.ndim != 2:
        raise ValueError("x_feed must be one- or two-dimensional.")

    if isinstance(Q, dict):
        if not Q:
            raise ValueError("Q dictionary must not be empty.")

        q_sizes = [np.asarray(v, dtype=float).reshape(-1).size for v in Q.values()]
        candidates = [d for d in x_raw.shape if d in q_sizes]
        return candidates[0] if candidates else x_raw.shape[0]

    Q_raw = np.asarray(Q, dtype=float)
    if Q_raw.ndim == 1:
        return Q_raw.size

    if Q_raw.ndim == 2:
        # Prefer a dimension shared by Q and x_feed.
        candidates = [d for d in x_raw.shape if d in Q_raw.shape]
        return candidates[0] if candidates else x_raw.shape[0]

    raise ValueError("Q must be one- or two-dimensional, or a material dictionary.")


def _infer_n_cases(Q, Material, A_t, Pf, F_f, x_raw, n_comp):
    if A_t is not None:
        return np.asarray(A_t).reshape(-1).size

    if Material is not None:
        material_size = np.asarray(Material, dtype=object).reshape(-1).size
        if material_size > 1:
            return material_size

    if not isinstance(Q, dict):
        Q_mat = _prepare_component_case_matrix(np.asarray(Q, dtype=float), n_comp, "Q")
        if Q_mat.shape[1] > 1:
            return Q_mat.shape[1]

    if x_raw.ndim == 2:
        if x_raw.shape[0] == n_comp:
            x_cases = x_raw.shape[1]
        elif x_raw.shape[1] == n_comp:
            x_cases = x_raw.shape[0]
        else:
            x_cases = 1

        if x_cases > 1:
            return x_cases

    for value in (Pf, F_f):
        value_size = np.asarray(value).reshape(-1).size
        if value_size > 1:
            return value_size

    return 1


def _prepare_q_matrix(Q, n_comp, n_cases, Material):
    if isinstance(Q, dict):
        return _prepare_q_from_material_dict(Q, Material, n_comp, n_cases)

    Q_mat = _prepare_component_case_matrix(np.asarray(Q, dtype=float), n_comp, "Q")

    if Q_mat.shape[1] == 1 and n_cases > 1:
        Q_mat = np.repeat(Q_mat, n_cases, axis=1)
    elif Q_mat.shape[1] != n_cases:
        raise ValueError(
            "Q must provide either one permeance vector or one permeance "
            "vector per candidate."
        )

    return Q_mat, None


def _prepare_q_from_material_dict(Q, Material, n_comp, n_cases):
    if Material is None:
        raise ValueError(
            "Material must be provided when Q is a dictionary of material permeances."
        )

    material_vec = np.asarray(Material, dtype=object).reshape(-1)

    if material_vec.size == 1 and n_cases > 1:
        material_vec = np.full(n_cases, material_vec[0], dtype=object)
    elif material_vec.size != n_cases:
        raise ValueError(
            "Material must be scalar or have one entry per candidate. "
            f"Received size {material_vec.size}, expected {n_cases}."
        )

    q_by_material = {}
    for material_name, q_values in Q.items():
        q_vec = np.asarray(q_values, dtype=float).reshape(-1)

        if q_vec.size != n_comp:
            raise ValueError(
                f"Q[{material_name!r}] must have n_comp={n_comp} values. "
                f"Received size {q_vec.size}."
            )

        q_by_material[str(material_name)] = q_vec

    Q_mat = np.empty((n_comp, n_cases), dtype=float)
    missing = []

    for c, material_name in enumerate(material_vec):
        key = str(material_name)
        q_vec = q_by_material.get(key)

        if q_vec is None:
            missing.append(material_name)
            continue

        Q_mat[:, c] = q_vec

    if missing:
        available = sorted(q_by_material.keys())
        missing_unique = sorted({str(m) for m in missing})
        raise ValueError(
            "Material contains entries that are not keys in Q. "
            f"Missing: {missing_unique}. Available: {available}."
        )

    return Q_mat, material_vec.copy()


def _as_case_vector(value, n_cases, name):
    arr = np.asarray(value, dtype=float).reshape(-1)

    if arr.size == 1:
        return np.full(n_cases, float(arr[0]), dtype=float)

    if arr.size != n_cases:
        raise ValueError(
            f"{name} must be scalar or have one value per candidate. "
            f"Received size {arr.size}, expected {n_cases}."
        )

    return arr.astype(float, copy=False)


def _prepare_component_case_matrix(arr, n_comp, name):
    arr = np.asarray(arr, dtype=float)

    if arr.ndim == 1:
        if arr.size != n_comp:
            raise ValueError(
                f"For one-dimensional {name}, size must be n_comp={n_comp}."
            )
        return arr[:, None].copy()

    if arr.ndim != 2:
        raise ValueError(f"{name} must be one- or two-dimensional.")

    if arr.shape[0] == n_comp:
        return arr.copy()

    if arr.shape[1] == n_comp:
        return arr.T.copy()

    raise ValueError(
        f"{name} shape is incompatible with n_comp={n_comp}. "
        f"Received shape {arr.shape}."
    )


def _is_key_fastest(Qc, k, non_idx, tol):
    if non_idx.size == 0:
        return True

    max_nonkey = np.max(Qc[non_idx])
    return Qc[k] >= max_nonkey - tol * max(1.0, abs(max_nonkey))


def _x_key_ideal(s, Fk0, Fj0, r, eps):
    """Ideal key mole fraction as a function of s=Fk/Fk0."""
    if s <= 0.0:
        # Limit as s -> 0. If at least one positive non-key has r < 1, the
        # key fraction tends to zero. Otherwise it is not reduced.
        positive = Fj0 > eps
        if np.any(positive & (r < 1.0 - 1e-14)):
            return 0.0
        denom = Fk0 + np.sum(Fj0[positive])
        return Fk0 / max(denom, eps)

    log_s = np.log(s)
    denom = Fk0 * s

    for Fj, rj in zip(Fj0, r):
        if Fj <= eps:
            continue
        if rj <= 0.0:
            denom += Fj
        else:
            denom += Fj * np.exp(rj * log_s)

    return (Fk0 * s) / max(denom, eps)


def _solve_s_star(Fk0, Fj0, r, x_target, eps, root_tol, max_bisect):
    """Solve x_key_ideal(s)=x_target on s in [0,1]."""
    if x_target <= eps:
        return 0.0

    lo = 0.0
    hi = 1.0

    f_hi = _x_key_ideal(hi, Fk0, Fj0, r, eps) - x_target
    f_lo = _x_key_ideal(lo, Fk0, Fj0, r, eps) - x_target

    if f_hi <= 0.0:
        return 1.0

    if f_lo > 0.0:
        # Unreachable. Caller usually checks this earlier, but keep safe.
        return np.nan

    for _ in range(max_bisect):
        mid = 0.5 * (lo + hi)
        f_mid = _x_key_ideal(mid, Fk0, Fj0, r, eps) - x_target

        if abs(f_mid) <= root_tol or (hi - lo) <= root_tol:
            return mid

        if f_mid > 0.0:
            hi = mid
        else:
            lo = mid

    return 0.5 * (lo + hi)


def _rayleigh_integral_term(s, r, r_zero_tol):
    """Return (1 - s**r)/r, with the logarithmic limit for r -> 0."""
    if r <= r_zero_tol:
        if s <= 0.0:
            return np.inf
        return -np.log(s)

    if s <= 0.0:
        return 1.0 / r

    return (1.0 - s**r) / r


if __name__ == "__main__":
    # Smoke test with a 3-component system:
    # component 0 is the key and fastest component.
    Q_demo = np.array([
        [4.00875e-9, 4.00875e-9, 4.00875e-9],
        [1.66250e-10, 1.66250e-10, 1.66250e-10],
        [2.67250e-9, 2.67250e-9, 2.67250e-9],
    ])

    A_t_demo = np.array([5.0, 25.0, 100.0])
    Pf_demo = 15.0e5
    F_f_demo = 0.35
    x_feed_demo = np.array([0.10, 0.90, 0.0])

    cut_mask, A_floor, info = rayleigh_area_floor_cut_mask(
        Q=Q_demo,
        A_t=A_t_demo,
        Pf=Pf_demo,
        F_f=F_f_demo,
        x_feed=x_feed_demo,
        Key_Comp_index=0,
        x_key_max=0.03,
    )

    print("A_floor:", A_floor)
    print("cut_mask:", cut_mask)
    print("s_star:", info["s_star"])
    print("certified:", info["certified"])
    print("reason:", info["reason"])