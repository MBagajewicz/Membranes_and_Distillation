#region Title: SimulationDeadline
# Nature: Cooperative wall-clock budget for a single simulation
# Methodology: A deadline is armed by SimulatorRunHFM.run() and checked inside
#              the hot loops; exceeding it raises SimulationTimeout.
##################################################################################################################
# VERSION        DATE            AUTHOR                    DESCRIPTION OF CHANGES MADE
#  0.0       27-Jul-2026    Claude / JVT               Proposed: per-candidate time budget
##################################################################################################################
#endregion

"""Per-candidate wall-clock budget for the HFM simulator.

WHY COOPERATIVE. The obvious ways to time-limit a call do not work here:

* `signal.SIGALRM` is POSIX-only -- the runs are on Windows.
* A watchdog thread cannot safely kill the worker thread; Python has no
  interruption primitive for that.
* `multiprocessing` would mean spawning a process per candidate. On Windows that
  is a `spawn` (~0.5 s) plus re-importing CoolProp, for 154 473 candidates --
  far more expensive than the problem being solved.

So the deadline is checked explicitly at the top of every hot loop
(`check()` is one `perf_counter()` comparison, ~50 ns; the loops it guards each
do at least one sparse solve, so the overhead is unmeasurable).

IMPORTANT -- this is a COST cut, not a feasibility proof. A candidate that
exceeds its budget is *unresolved*, not infeasible: it may well be feasible, and
in principle even optimal. Every timeout must therefore be logged and revisited
before any global-optimality claim is made over the enumeration. The simulator
marks such results with `results.timed_out = True` so they can be separated from
genuine `feasible = False` verdicts.
"""

import time

# Module-global rather than passed around: the check has to be reachable from
# deep inside the mass-balance and marching routines, which do not have a
# reference to the simulator instance.
_DEADLINE = None


class SimulationTimeout(RuntimeError):
    """Raised when a single simulation exceeds its wall-clock budget.

    Distinct from SimulationNotConverged: nothing is known about this candidate,
    not even that the solver failed. It is UNRESOLVED.
    """
    pass


def arm(budget_s):
    """Start a budget for the current simulation. `None` disables the deadline."""
    global _DEADLINE
    _DEADLINE = None if not budget_s else time.perf_counter() + float(budget_s)


def clear():
    """Disarm. Always call this in a `finally`, or the deadline leaks into the
    next candidate and makes it look slow."""
    global _DEADLINE
    _DEADLINE = None


def armed():
    return _DEADLINE is not None


def remaining():
    """Seconds left, or None when disarmed."""
    return None if _DEADLINE is None else _DEADLINE - time.perf_counter()


def check():
    """Raise SimulationTimeout if the budget is spent. Cheap enough for any loop."""
    if _DEADLINE is not None and time.perf_counter() > _DEADLINE:
        raise SimulationTimeout("simulation exceeded its wall-clock budget")
