# The module docstring below is preserved unchanged.
# It provides a high-level description of the iterative NoNTU / F-correction algorithm.
"""
Iterative LMTD-correction calculation for the NoNTU formulation.
The iteration is deliberately kept separate from both:
- Calculations_STHE_NoNTU.py
- Calculations_STHE_correction_factor.py
The existing correction-factor calculation is used unchanged.
Algorithm
F^(k)
-> NoNTU(F^(k))
-> outlet temperatures
-> check P-R applicability
-> existing STHE_correction_factor (if applicable)
-> F_calculated
-> convergence / relaxation
-> F^(k+1)
If the initial F=1 state is outside the applicable P-R region, F is
automatically reduced until an admissible state is found. The same
applicability check is performed at every subsequent iteration.
"""

# Import NumPy, used for numerical helpers such as finite checks, arrays,
# square roots, linspace scans, and floating-point tolerances.
import numpy as np

# Import the existing NoNTU solver from the sibling module.
# This routine is called repeatedly with different trial correction factors.
from .Calculations_STHE_NoNTU import STHE_NoNTU

# Import the existing correction-factor routine from the sibling module.
# This routine is used unchanged to compute F_calculated from outlet temperatures.
from .Calculations_STHE_correction_factor import STHE_correction_factor

# Set of tube-pass counts that this iterative solver explicitly supports.
_VALID_TUBE_PASSES = {1, 2, 4, 6, 8}

# The existing correction-factor implementation returns a value of this
# order when the state is outside its P-R applicability region.
# This threshold is used to detect invalid / effectively-zero F values.
_INVALID_F_THRESHOLD = 1.0e-12


def _calculate_P_R_Pmax(  # Define a private helper that calculates P, R, and the theoretical maximum P.
    Tin_hot,  # Hot-stream inlet temperature.
    Tout_hot,  # Hot-stream outlet temperature.
    Tin_cold,  # Cold-stream inlet temperature.
    Tout_cold,  # Cold-stream outlet temperature.
    m_hot,  # Hot-stream mass flow rate.
    cp_hot,  # Hot-stream specific heat capacity.
    m_cold,  # Cold-stream mass flow rate.
    cp_cold,  # Cold-stream specific heat capacity.
):  # End of the function signature; the body starts next.
    """Calculate the P-R state and the theoretical P limit."""  # Docstring preserved; explains helper purpose.

    # Calculate the inlet temperature difference used as the denominator of P.
    delta_T_in = Tin_hot - Tin_cold

    # If the hot and cold inlet temperatures are numerically equal, P would divide by zero.
    if abs(delta_T_in) <= np.finfo(float).eps:  # Compare against machine epsilon for floats.
        raise ValueError(  # Raise a clear error because the correction factor cannot be defined.
            "Cannot calculate the correction factor when hot and cold "  # First part of the error message.
            "inlet temperatures are equal."  # Second part of the error message.
        )  # Close the ValueError call.

    # Calculate P, the cold-side temperature effectiveness-like ratio.
    P = (Tout_cold - Tin_cold) / delta_T_in

    # Hot-side heat-capacity rate C_h = m_dot_hot * cp_hot.
    Ch = m_hot * cp_hot

    # Cold-side heat-capacity rate C_c = m_dot_cold * cp_cold.
    Cc = m_cold * cp_cold

    # Both heat-capacity rates must be strictly positive for a physically meaningful exchanger.
    if Ch <= 0.0 or Cc <= 0.0:  # If either capacity rate is zero or negative...
        raise ValueError(  # ...raise an error because R and the thermal solution would be invalid.
            "Hot and cold heat-capacity rates must both be positive."  # Error message text.
        )  # Close the ValueError call.

    # Capacity-rate ratio R used by the correction-factor correlation.
    R = Cc / Ch

    # Theoretical maximum P for the given R.
    Pmax = 2.0 / (  # Start the analytical expression for Pmax.
        R + 1.0 + np.sqrt(R**2 + 1.0)  # Denominator of the Pmax expression.
    )  # Close the Pmax calculation.

    # Return the calculated P, R, and theoretical Pmax.
    return P, R, Pmax


def _solve_noNTU_at_F(  # Define a helper that solves the NoNTU problem for a specified trial F.
    F,  # Trial correction factor supplied to NoNTU.
    U,  # Overall heat-transfer coefficient.
    InstalledArea,  # Installed heat-transfer area.
    m_hot,  # Hot-stream mass flow rate.
    cp_hot,  # Hot-stream specific heat capacity.
    Tin_hot,  # Hot-stream inlet temperature.
    m_cold,  # Cold-stream mass flow rate.
    cp_cold,  # Cold-stream specific heat capacity.
    Tin_cold,  # Cold-stream inlet temperature.
):  # End of the function signature; the body starts next.
    """Solve NoNTU for a specified correction factor."""  # Docstring preserved; explains helper purpose.

    # Call the existing NoNTU calculation using the trial correction factor F_T.
    result = STHE_NoNTU(
        U=U,  # Pass overall heat-transfer coefficient.
        InstalledArea=InstalledArea,  # Pass installed area.
        m_hot=m_hot,  # Pass hot mass flow rate.
        cp_hot=cp_hot,  # Pass hot specific heat capacity.
        Tin_hot=Tin_hot,  # Pass hot inlet temperature.
        m_cold=m_cold,  # Pass cold mass flow rate.
        cp_cold=cp_cold,  # Pass cold specific heat capacity.
        Tin_cold=Tin_cold,  # Pass cold inlet temperature.
        F_T=F,  # Pass the trial correction factor.
    )  # Close the NoNTU call.

    # From the NoNTU outlet temperatures, calculate the resulting P, R, and Pmax.
    P, R, Pmax = _calculate_P_R_Pmax(
        Tin_hot=Tin_hot,  # Hot inlet temperature used for P calculation.
        Tout_hot=result["ToutHot"],  # Hot outlet temperature returned by NoNTU.
        Tin_cold=Tin_cold,  # Cold inlet temperature used for P calculation.
        Tout_cold=result["ToutCold"],  # Cold outlet temperature returned by NoNTU.
        m_hot=m_hot,  # Hot mass flow rate used for capacity rates.
        cp_hot=cp_hot,  # Hot specific heat used for capacity rates.
        m_cold=m_cold,  # Cold mass flow rate used for capacity rates.
        cp_cold=cp_cold,  # Cold specific heat used for capacity rates.
    )  # Close the P/R/Pmax calculation call.

    # Return the full NoNTU result and the associated P-R state.
    return result, P, R, Pmax


def _is_P_region_admissible(  # Define a helper that checks whether the P-R state is usable.
    P,  # Calculated P value.
    Pmax,  # Theoretical maximum P.
    Xp,  # Applicability scaling factor used by the existing correlation domain.
):  # End of the function signature; the body starts next.
    """Return whether the state is inside the existing correlation domain."""  # Docstring preserved.

    # Return True only if every condition below is satisfied.
    return (
        np.isfinite(P)  # P must be a finite number.
        and np.isfinite(Pmax)  # Pmax must be a finite number.
        and P >= 0.0  # P must be non-negative.
        and P < Xp * Pmax  # P must be strictly below the scaled theoretical limit.
    )  # Close the Boolean return expression.


def STHE_NoNTU_iteration(  # Define the main iterative solver function.
    U,  # Overall heat-transfer coefficient.
    InstalledArea,  # Installed heat-transfer area.
    m_hot,  # Hot-side mass flow rate.
    cp_hot,  # Hot-side specific heat capacity.
    Tin_hot,  # Hot-side inlet temperature.
    m_cold,  # Cold-side mass flow rate.
    cp_cold,  # Cold-side specific heat capacity.
    Tin_cold,  # Cold-side inlet temperature.
    Npt,  # Number of tube passes.
    Xp,  # Parameter used by the correction-factor correlation domain.
    tolerance=1.0e-6,  # Absolute convergence tolerance for F residual.
    maximum_iterations=50,  # Maximum number of bisection iterations.
    relaxation=1.0,  # Kept for compatibility; not used by bisection.
    F_initial=1.0,  # Initial trial correction factor for admissibility search.
):  # End of the function signature; the main body starts next.
    # The public docstring below is preserved unchanged.
    # It documents the purpose, parameters, and return value of this function.
    """
    Solve the NoNTU thermal problem with an iterative correction factor.

    For Npt > 1, the correction factor is obtained as the root of:

         g(F) = F_calculated(F) - F = 0

     where F_calculated is obtained from the existing
     STHE_correction_factor() using the outlet temperatures generated by
     STHE_NoNTU() at the trial F.

     The existing Calculations_STHE_correction_factor.py is not modified.

     Parameters
     ----------
     U : float
         Overall heat-transfer coefficient [W/(m² K)].
     InstalledArea : float
         Installed heat-transfer area [m²].
     m_hot, m_cold : float
         Hot and cold mass flow rates [kg/s].
     cp_hot, cp_cold : float
         Hot and cold heat capacities [J/(kg K)].
     Tin_hot, Tin_cold : float
         Inlet temperatures [K].
     Npt : int
         Number of tube passes. Supported values: 1, 2, 4, 6, 8.
     Xp : float
         Parameter used by the existing correction-factor correlation.
     tolerance : float
         Absolute tolerance for the F root.
     maximum_iterations : int
         Maximum number of bisection iterations.
     relaxation : float
         Retained for API compatibility. Not used by bisection.
     F_initial : float
         Initial F used when searching for an admissible upper point.

     Returns
     -------
     dict
         Final NoNTU results plus correction-factor diagnostics.
     """

    # --------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------

    # Try to convert the supplied Npt into a plain Python integer.
    try:
        # Use np.asarray(...).item() to extract a scalar value, then cast to int.
        Npt_int = int(np.asarray(Npt).item())
    except Exception as exc:  # Catch any failure during scalar conversion.
        # Raise a clear ValueError and preserve the original exception context.
        raise ValueError("Npt must be a scalar integer.") from exc

    # Reject unsupported tube-pass counts.
    if Npt_int not in _VALID_TUBE_PASSES:
        raise ValueError(
            f"Unsupported number of tube passes: {Npt_int}. "  # Show invalid Npt value.
            "Supported values are 1, 2, 4, 6 and 8."  # List allowed values.
        )  # Close the ValueError call.

    # Convert numerical solver settings to the expected Python types.
    tolerance = float(tolerance)  # Ensure tolerance is float.
    maximum_iterations = int(maximum_iterations)  # Ensure maximum_iterations is int.
    F_initial = float(F_initial)  # Ensure F_initial is float.

    # Xp is intentionally fixed to 1.0 for this calculation.
    # Any externally supplied value is ignored.
    Xp = 1.0  # Force the applicability scaling factor to 1.0.

    # Kept for compatibility with Options_STHE. The root solver does not
    # need relaxation because it uses a bracketed bisection method.
    _ = relaxation  # Explicitly ignore the relaxation argument.

    # The tolerance must be strictly positive; otherwise convergence checks are invalid.
    if tolerance <= 0.0:
        raise ValueError("F tolerance must be positive.")  # Error message for invalid tolerance.

    # At least one iteration must be allowed.
    if maximum_iterations < 1:
        raise ValueError("Maximum F iterations must be at least 1.")  # Error message.

    # The initial correction factor must be physically meaningful: 0 < F <= 1.
    if not 0.0 < F_initial <= 1.0:
        raise ValueError("Initial F must satisfy 0 < F <= 1.")  # Error message.

    # Xp must be positive, even though it is fixed to 1.0 above.
    if Xp <= 0.0:
        raise ValueError("Xp must be positive.")  # Error message.

    # Lower numerical bound used when reducing F during searches.
    minimum_F = 1.0e-8

    # Multiplicative reduction factor used when searching for admissible states.
    admissibility_factor = 0.9

    # Maximum number of geometric reduction steps before giving up.
    maximum_admissibility_steps = 100

    # Store the sequence of F values tried during the root search.
    F_history = []

    # Store detailed diagnostic dictionaries for every evaluated F.
    F_evaluation_history = []

    # Reserved for admissibility-history information; kept for output compatibility.
    F_admissibility_history = []

    def evaluate_F(  # Define a local helper that evaluates one trial F.
        F,  # Trial correction factor to evaluate.
        stage,  # Text label identifying why this evaluation is being performed.
    ):  # End of nested-function signature.
        # The nested-function docstring below is preserved unchanged.
        """
        Evaluate NoNTU and the existing correction factor at a trial F.

        Returns a dictionary even when the P-R state is outside the
        correlation domain. This is essential for robust bracketing.
        """

        # Solve the NoNTU problem using the trial F and obtain the resulting P-R state.
        result, P, R, Pmax = _solve_noNTU_at_F(
            F=F,  # Trial correction factor.
            U=U,  # Overall heat-transfer coefficient.
            InstalledArea=InstalledArea,  # Installed heat-transfer area.
            m_hot=m_hot,  # Hot mass flow rate.
            cp_hot=cp_hot,  # Hot specific heat capacity.
            Tin_hot=Tin_hot,  # Hot inlet temperature.
            m_cold=m_cold,  # Cold mass flow rate.
            cp_cold=cp_cold,  # Cold specific heat capacity.
            Tin_cold=Tin_cold,  # Cold inlet temperature.
        )  # Close the NoNTU-at-F call.

        # Determine whether this state is inside the correction-factor applicability region.
        admissible = _is_P_region_admissible(P, Pmax, Xp)

        # Create a diagnostic record for this evaluation.
        item = {
            "stage": stage,  # Label such as admissibility_search, bracket_search, or bisection.
            "F": float(F),  # Trial F value as a Python float.
            "P": float(P),  # Calculated P value.
            "R": float(R),  # Calculated R value.
            "Pmax": float(Pmax),  # Calculated theoretical Pmax.
            "Xp_Pmax": float(Xp * Pmax),  # Scaled Pmax limit used for admissibility.
            "admissible": bool(admissible),  # Whether this state can use STHE_correction_factor.
            "result": result,  # Full NoNTU result dictionary for this trial F.
            "F_calculated": None,  # Will be filled if the state is admissible.
            "g": None,  # Will be filled with F_calculated - F if admissible.
        }  # Close the diagnostic dictionary.

        # Only call the existing correction-factor routine when the P-R state is admissible.
        if admissible:
            # Call the unchanged existing correction-factor implementation.
            F_calculated = STHE_correction_factor(
                Thi=Tin_hot,  # Hot inlet temperature.
                Tho=result["ToutHot"],  # Hot outlet temperature from NoNTU.
                Tci=Tin_cold,  # Cold inlet temperature.
                Tco=result["ToutCold"],  # Cold outlet temperature from NoNTU.
                Npt=Npt_int,  # Number of tube passes as integer.
                Xp=Xp,  # Applicability scaling factor, fixed to 1.0.
            )  # Close the correction-factor call.

            # Convert the returned value to a plain scalar float.
            F_calculated = float(
                np.asarray(F_calculated).reshape(-1)[0]  # Flatten and take the first element.
            )  # Close float conversion.

            # If the returned F is non-finite or effectively zero, something is wrong.
            if (
                not np.isfinite(F_calculated)  # F_calculated must be finite.
                or F_calculated <= _INVALID_F_THRESHOLD  # F_calculated must not be invalidly small.
            ):  # If either invalid condition is true...
                raise ValueError(  # Raise an error because this should not happen inside the valid region.
                    "The existing STHE_correction_factor returned an "  # Message part 1.
                    "invalid correction factor inside its explicit P-R "  # Message part 2.
                    "applicability region. "  # Message part 3.
                    f"F={F:.12g}, P={P:.12g}, R={R:.12g}, "  # Diagnostic values.
                    f"Xp*Pmax={Xp * Pmax:.12g}."  # Additional diagnostic limit.
                )  # Close the ValueError call.

            # Clamp F_calculated to the physically meaningful numerical range.
            F_calculated = min(1.0, max(F_calculated, minimum_F))

            # Store the computed correction factor in the diagnostic record.
            item["F_calculated"] = F_calculated

            # Store the residual g(F) = F_calculated - F.
            item["g"] = F_calculated - F

        # Append the diagnostic record to the global evaluation history.
        F_evaluation_history.append(item)

        # Return the diagnostic record for use by bracketing and bisection logic.
        return item

    # --------------------------------------------------------------
    # One tube pass: ideal countercurrent case.
    # --------------------------------------------------------------

    # If there is only one tube pass, the exchanger is treated as ideal counterflow.
    if Npt_int == 1:
        # Solve NoNTU once with F_T = 1.0.
        result = STHE_NoNTU(
            U=U,  # Overall heat-transfer coefficient.
            InstalledArea=InstalledArea,  # Installed area.
            m_hot=m_hot,  # Hot mass flow rate.
            cp_hot=cp_hot,  # Hot specific heat capacity.
            Tin_hot=Tin_hot,  # Hot inlet temperature.
            m_cold=m_cold,  # Cold mass flow rate.
            cp_cold=cp_cold,  # Cold specific heat capacity.
            Tin_cold=Tin_cold,  # Cold inlet temperature.
            F_T=1.0,  # Correction factor is exactly 1 for ideal counterflow.
        )  # Close the NoNTU call.

        # Calculate the final P, R, and Pmax for the single-pass result.
        P, R, Pmax = _calculate_P_R_Pmax(
            Tin_hot=Tin_hot,  # Hot inlet temperature.
            Tout_hot=result["ToutHot"],  # Hot outlet temperature.
            Tin_cold=Tin_cold,  # Cold inlet temperature.
            Tout_cold=result["ToutCold"],  # Cold outlet temperature.
            m_hot=m_hot,  # Hot mass flow rate.
            cp_hot=cp_hot,  # Hot specific heat capacity.
            m_cold=m_cold,  # Cold mass flow rate.
            cp_cold=cp_cold,  # Cold specific heat capacity.
        )  # Close P/R/Pmax calculation.

        # Add diagnostic fields expected by callers of the iterative solver.
        result.update(
            {
                "P": P,  # Calculated P.
                "R": R,  # Calculated R.
                "Pmax": Pmax,  # Theoretical Pmax.
                "F_T": 1.0,  # Final correction factor.
                "F_method": "STHE_correction_factor",  # Method label.
                "F_converged": True,  # Single-pass case is trivially converged.
                "F_iterations": 0,  # No iteration was required.
                "F_error": 0.0,  # No residual error.
                "F_history": [1.0],  # History contains only F=1.
                "F_evaluation_history": [],  # No iterative evaluations were needed.
                "F_admissibility_history": [],  # No admissibility search was needed.
            }
        )  # Close result.update(...).

        # Return the completed single-pass result.
        return result

    # --------------------------------------------------------------
    # Step 1: find an admissible state starting from F_initial.
    #
    # This is NOT the root search yet. It only finds a point where the
    # existing P-R correlation can be evaluated.
    # --------------------------------------------------------------

    # Start from F_initial, but never allow a starting value above 1.
    F_upper = min(1.0, F_initial)

    # Try up to a fixed number of geometric reductions to find an admissible state.
    for step in range(1, maximum_admissibility_steps + 1):
        # Evaluate the current upper trial F and record it as an admissibility search.
        trial = evaluate_F(F_upper, "admissibility_search")

        # Print diagnostic information for the admissibility search.
        print("\n--- NoNTU F admissibility search ---")  # Section header.
        print(f"Step      = {step}")  # Current admissibility-search step.
        print(f"F         = {trial['F']}")  # Trial F value.
        print(f"P         = {trial['P']}")  # Resulting P.
        print(f"R         = {trial['R']}")  # Resulting R.
        print(f"Pmax      = {trial['Pmax']}")  # Theoretical Pmax.
        print(f"Xp        = {Xp}")  # Applicability scaling factor.
        print(f"Xp*Pmax   = {trial['Xp_Pmax']}")  # Scaled Pmax limit.
        print(
            "Status    = "  # Label before status.
            + ("VALID" if trial["admissible"] else "OUTSIDE P-R REGION")  # Status text.
        )  # Close status print.

        # If this trial is admissible, stop looking for an admissible upper point.
        if trial["admissible"]:
            break  # Exit the admissibility-search loop.

        # Otherwise, reduce F and try again.
        F_upper *= admissibility_factor

        # If F has been reduced below the minimum allowed value, fail.
        if F_upper < minimum_F:
            raise ValueError(
                "Could not find an admissible F state for the existing "  # Message part 1.
                "STHE_correction_factor. "  # Message part 2.
                f"Last trial F={trial['F']:.12g}, "  # Diagnostic last F.
                f"P={trial['P']:.12g}, "  # Diagnostic last P.
                f"Xp*Pmax={trial['Xp_Pmax']:.12g}."  # Diagnostic last scaled Pmax.
            )  # Close the ValueError call.
    else:
        # If the loop finished without break, no admissible state was found.
        raise ValueError(
            "Could not find an admissible F state within the allowed "  # Message part 1.
            "search range."  # Message part 2.
        )  # Close the ValueError call.

    # --------------------------------------------------------------
    # Step 2: find a bracket [F_low, F_high] such that:
    #
    #     g(F_low) * g(F_high) <= 0
    #
    # and both endpoints are admissible.
    #
    # We first search downward from the admissible upper point. If the
    # sign does not change, we continue with a finer scan over (0,F_upper].
    # --------------------------------------------------------------

    # Evaluate the admissible upper point again and label it as bracket_upper.
    upper_eval = evaluate_F(F_upper, "bracket_upper")

    # Safety check: the upper point must have a residual g because it is admissible.
    if upper_eval["g"] is None:
        raise RuntimeError(
            "Internal error: the selected upper F is not admissible."  # Error message.
        )  # Close RuntimeError.

    # If the upper endpoint already satisfies the root tolerance, use it as the final root.
    if abs(upper_eval["g"]) <= tolerance:
        F_root = F_upper  # Final correction factor.
        final_eval = upper_eval  # Store final evaluation record.
        converged = True  # Mark as converged.
        iteration_count = 0  # No bisection iterations were needed.
        F_error = abs(upper_eval["g"])  # Final residual error.
        F_history.append(F_root)  # Record the final F.
    else:
        # Search downward geometrically first.
        lower_eval = None  # No previous lower/probe evaluation yet.
        F_probe = F_upper  # Start probing downward from the admissible upper F.

        # Try a geometric sequence of decreasing F values.
        for step in range(1, maximum_admissibility_steps + 1):
            # Reduce the probe F by the admissibility factor.
            F_probe *= admissibility_factor

            # Stop probing if below the minimum numerical F.
            if F_probe < minimum_F:
                break  # Exit geometric bracket search.

            # Evaluate this probe point.
            trial = evaluate_F(F_probe, "bracket_search")

            # Print diagnostic information for the bracket search.
            print("\n--- NoNTU F bracket search ---")  # Section header.
            print(f"Step      = {step}")  # Current bracket-search step.
            print(f"F         = {trial['F']}")  # Probe F.
            print(f"P         = {trial['P']}")  # Resulting P.
            print(f"Pmax      = {trial['Pmax']}")  # Resulting Pmax.
            print(f"Xp*Pmax   = {trial['Xp_Pmax']}")  # Scaled Pmax limit.
            print(f"Status    = {'VALID' if trial['admissible'] else 'OUTSIDE'}")  # Admissibility status.
            # print(f"Xp*Pmax   = {trial['Xp_Pmax']}")
            # print(f"F_calc    = {trial['F_calculated']}")
            # print(f"g(F)      = {trial['g']}")
            # print(f"Status    = {'VALID' if trial['admissible'] else 'OUTSIDE'}")


            # If this probe is not admissible, it cannot be used for bracketing.
            if not trial["admissible"]:
                continue  # Skip to the next smaller F.

            # If there is already a previous admissible lower/probe evaluation...
            if lower_eval is not None:
                # Check whether the residual changed sign between lower_eval and trial.
                if (
                    lower_eval["g"] * trial["g"] <= 0.0  # Sign change or exact zero.
                ):
                    # Keep the two points ordered in F.
                    if lower_eval["F"] < trial["F"]:
                        bracket_low = lower_eval  # Lower F endpoint.
                        bracket_high = trial  # Higher F endpoint.
                    else:
                        bracket_low = trial  # Lower F endpoint.
                        bracket_high = lower_eval  # Higher F endpoint.
                    break  # A bracket has been found.

            # Store the current admissible trial as the previous probe evaluation.
            lower_eval = trial

            # Also check whether the trial brackets the root together with the upper endpoint.
            if upper_eval["g"] * trial["g"] <= 0.0:
                bracket_low = trial  # Lower endpoint is the trial.
                bracket_high = upper_eval  # Upper endpoint is upper_eval.
                break  # A bracket has been found.
        else:
            # If the geometric search finished without break, no bracket was found yet.
            bracket_low = None  # Explicitly mark missing lower bracket.
            bracket_high = None  # Explicitly mark missing upper bracket.

        # If the geometric search did not find a sign change, perform a
        # systematic scan over the admissible interval. This is important
        # because g(F) can change rapidly near the P-R boundary.
        if (
            "bracket_low" not in locals()  # True if bracket_low was never created.
            or bracket_low is None  # True if bracket_low is explicitly missing.
            or bracket_high is None  # True if bracket_high is explicitly missing.
        ):
            # Create a uniform grid of candidate F values from minimum_F to F_upper.
            scan_F = np.linspace(
                minimum_F,  # Lower bound of the scan.
                F_upper,  # Upper bound of the scan.
                101,  # Number of scan points.
            )  # Close linspace call.

            # Previous admissible scan point, used to detect sign changes.
            previous = None

            # Scan systematically across the interval.
            for F_probe in scan_F:
                # Evaluate this scan point.
                trial = evaluate_F(F_probe, "bracket_scan")

                # Inadmissible points cannot contribute to a bracket.
                if not trial["admissible"]:
                    continue  # Skip inadmissible point.

                # If this point is already within tolerance, treat it as an exact bracket.
                if abs(trial["g"]) <= tolerance:
                    bracket_low = trial  # Lower endpoint.
                    bracket_high = trial  # Upper endpoint; same point.
                    break  # Stop scanning.

                # If a previous admissible point exists, check for a sign change.
                if previous is not None and previous["g"] * trial["g"] < 0.0:
                    bracket_low = previous  # Previous point becomes lower endpoint.
                    bracket_high = trial  # Current point becomes upper endpoint.
                    break  # Stop scanning.

                # Remember this admissible point for the next sign-change test.
                previous = trial
            else:
                # If the scan finished without break, no bracket was found.
                bracket_low = None  # Mark missing lower bracket.
                bracket_high = None  # Mark missing upper bracket.

        # If after all bracketing attempts no bracket exists, raise an error.
        if bracket_low is None or bracket_high is None:
            raise RuntimeError(
                "NoNTU/STHE_correction_factor: no sign change was found "  # Message part 1.
                "for g(F)=F_calculated(F)-F inside the applicable "  # Message part 2.
                "P-R region. A consistent correction-factor root could "  # Message part 3.
                "not be bracketed. "  # Message part 4.
                f"Upper admissible F={F_upper:.12g}, "  # Diagnostic upper F.
                f"g(upper)={upper_eval['g']:.12g}."  # Diagnostic upper residual.
            )  # Close RuntimeError.

        # Exact root at a bracket endpoint.
        if bracket_low["F"] == bracket_high["F"]:
            F_root = bracket_low["F"]  # Final correction factor.
            final_eval = bracket_low  # Store final evaluation record.
            converged = True  # Mark as converged.
            iteration_count = 0  # No bisection iterations were needed.
            F_error = abs(bracket_low["g"])  # Final residual error.
            F_history.append(F_root)  # Record final F.
        else:
            # ----------------------------------------------------------
            # Step 3: bisection on g(F)=0.
            # ----------------------------------------------------------

            # Extract the lower endpoint F.
            a = float(bracket_low["F"])

            # Extract the upper endpoint F.
            b = float(bracket_high["F"])

            # Extract the residual at the lower endpoint.
            ga = float(bracket_low["g"])

            # Extract the residual at the upper endpoint.
            gb = float(bracket_high["g"])

            # The bracket must contain a sign change.
            if ga * gb > 0.0:
                raise RuntimeError(
                    "Internal bracketing error: the root interval does "  # Message part 1.
                    "not contain a sign change."  # Message part 2.
                )  # Close RuntimeError.

            # Initialize convergence flags.
            converged = False
            final_eval = None
            F_root = None
            F_error = np.inf  # Start with infinite error.

            # Perform bisection iterations.
            for iteration_count in range(
                1,  # Start counting at iteration 1.
                maximum_iterations + 1,  # Stop after maximum_iterations.
            ):
                # Midpoint of the current bracket.
                c = 0.5 * (a + b)

                # Evaluate the midpoint.
                mid = evaluate_F(c, "bisection")

                # The midpoint can lie outside the P-R domain if the
                # admissible region is bounded above. Move the upper
                # endpoint toward the midpoint and continue.
                if not mid["admissible"]:
                    b = c  # Shrink upper bound to midpoint.
                    gb = np.nan  # Residual at upper bound is now unknown/invalid.
                    F_history.append(c)  # Record the midpoint trial.
                    continue  # Skip residual-based bisection update.

                # Extract the midpoint residual.
                gc = float(mid["g"])

                # Record the midpoint trial.
                F_history.append(c)

                # Print bisection diagnostics.
                print("\n--- NoNTU F bisection ---")  # Section header.
                print(f"Iteration = {iteration_count}")  # Current bisection iteration.
                print(f"F_low     = {a}")  # Lower bracket endpoint.
                print(f"F_mid     = {c}")  # Midpoint trial F.
                print(f"F_high    = {b}")  # Upper bracket endpoint.
                print(f"g(F_mid)  = {gc}")  # Residual at midpoint.
                print(f"P         = {mid['P']}")  # P at midpoint.
                print(f"R         = {mid['R']}")  # R at midpoint.
                print(f"Pmax      = {mid['Pmax']}")  # Pmax at midpoint.
                print(f"F_calc    = {mid['F_calculated']}")  # F_calculated at midpoint.

                # Update the absolute residual error.
                F_error = abs(gc)

                # If the residual is within tolerance, the midpoint is the root.
                if F_error <= tolerance:
                    F_root = c  # Final correction factor.
                    final_eval = mid  # Store final evaluation record.
                    converged = True  # Mark convergence.
                    break  # Exit bisection loop.

                # Choose the subinterval that contains the sign change.
                if ga * gc <= 0.0:
                    b = c  # Move upper bound to midpoint.
                    gb = gc  # Update upper residual.
                else:
                    a = c  # Move lower bound to midpoint.
                    ga = gc  # Update lower residual.

                # If the bracket itself has become sufficiently small...
                if abs(b - a) <= tolerance:
                    # Use the midpoint of the final tiny interval as the root estimate.
                    F_root = 0.5 * (a + b)

                    # Evaluate the final interval midpoint one more time.
                    final_eval = evaluate_F(
                        F_root,  # Final candidate F.
                        "bisection_final_interval",  # Stage label.
                    )  # Close final evaluation call.

                    # Accept the result if it is admissible and sufficiently accurate.
                    if (
                        final_eval["admissible"]  # Must be inside P-R domain.
                        and abs(final_eval["g"]) <= max(  # Residual must be small enough.
                            tolerance,  # User tolerance.
                            1.0e-8,  # Absolute floor tolerance.
                        )  # Close max(...).
                    ):
                        F_error = abs(final_eval["g"])  # Store final residual error.
                        converged = True  # Mark convergence.
                        break  # Exit bisection loop.

            # If the bisection loop finished without convergence, raise an error.
            if not converged:
                raise RuntimeError(
                    "NoNTU correction-factor root search did not converge "  # Message part 1.
                    f"within {maximum_iterations} bisection iterations. "  # Message part 2.
                    f"Last bracket=[{a:.12g}, {b:.12g}], "  # Diagnostic final bracket.
                    f"last error={F_error:.6g}."  # Diagnostic final error.
                )  # Close RuntimeError.

    # --------------------------------------------------------------
    # Step 4: final NoNTU solve at the converged F.
    # --------------------------------------------------------------

    # Convert the converged correction factor to float.
    F_final = float(F_root)

    # Run the final NoNTU calculation using the converged correction factor.
    final_result = STHE_NoNTU(
        U=U,  # Overall heat-transfer coefficient.
        InstalledArea=InstalledArea,  # Installed heat-transfer area.
        m_hot=m_hot,  # Hot mass flow rate.
        cp_hot=cp_hot,  # Hot specific heat capacity.
        Tin_hot=Tin_hot,  # Hot inlet temperature.
        m_cold=m_cold,  # Cold mass flow rate.
        cp_cold=cp_cold,  # Cold specific heat capacity.
        Tin_cold=Tin_cold,  # Cold inlet temperature.
        F_T=F_final,  # Final converged correction factor.
    )  # Close final NoNTU call.

    # Calculate the final P, R, and Pmax from the final outlet temperatures.
    P_final, R_final, Pmax_final = _calculate_P_R_Pmax(
        Tin_hot=Tin_hot,  # Hot inlet temperature.
        Tout_hot=final_result["ToutHot"],  # Final hot outlet temperature.
        Tin_cold=Tin_cold,  # Cold inlet temperature.
        Tout_cold=final_result["ToutCold"],  # Final cold outlet temperature.
        m_hot=m_hot,  # Hot mass flow rate.
        cp_hot=cp_hot,  # Hot specific heat capacity.
        m_cold=m_cold,  # Cold mass flow rate.
        cp_cold=cp_cold,  # Cold specific heat capacity.
    )  # Close final P/R/Pmax calculation.

    # Add correction-factor diagnostics to the final NoNTU result dictionary.
    final_result.update(
        {
            "P": P_final,  # Final P.
            "R": R_final,  # Final R.
            "Pmax": Pmax_final,  # Final theoretical Pmax.
            "F_T": F_final,  # Final correction factor.
            "F_method": "STHE_correction_factor",  # Method label.
            "F_converged": True,  # At this point the solver has converged or raised.
            "F_iterations": iteration_count,  # Number of bisection iterations used.
            "F_error": float(  # Final residual error as float.
                abs(final_eval["g"])  # Use final residual if available.
                if final_eval is not None  # Check that final_eval exists.
                and final_eval["g"] is not None  # Check that residual exists.
                else F_error  # Otherwise use the last stored F_error.
            ),  # Close F_error value.
            "F_history": F_history,  # Full history of trial F values.
            "F_evaluation_history": F_evaluation_history,  # Detailed evaluation records.
            "F_admissibility_history": F_admissibility_history,  # Reserved admissibility history.
        }
    )  # Close final_result.update(...).

    # Return the final NoNTU result enriched with iterative correction-factor diagnostics.
    return final_result