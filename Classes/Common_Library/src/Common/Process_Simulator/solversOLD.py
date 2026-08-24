"""Solvers — completely decoupled from Flowsheet."""

from __future__ import annotations

import time
from collections import deque
from typing import Dict, List, Set, Tuple

from .flowsheet import Flowsheet
from .unit_operation import UnitOperation


class SequentialSolver:
    """
    A sequential modular solver.
    It reads the implicit graph from Stream.producer / Stream.consumer,
    computes a topological order (Kahn's algorithm), and solves units one by one.

    solve_unit(unit) wraps unit.solve() with before/after hooks so that
    logging, timing, profiling, and convergence checks can be added later
    without modifying any equipment code.
    """

    def __init__(self, flowsheet: Flowsheet):
        self.fs = flowsheet

    # -------------------------------------------------------------------------
    # Hooks (override in subclasses for custom behavior)
    # -------------------------------------------------------------------------

    def before_solve(self, unit: UnitOperation) -> None:
        """Called immediately before unit.solve()."""
        unit.status = "solving"
        unit.reset_diagnostics()

    def after_solve(self, unit: UnitOperation) -> None:
        """Called immediately after unit.solve() succeeds."""
        unit.status = "converged"

    def on_solve_error(self, unit: UnitOperation, exc: Exception) -> None:
        """Called if unit.solve() raises an exception."""
        unit.status = "error"
        unit.warnings.append(str(exc))
        raise

    # -------------------------------------------------------------------------
    # Unit solving (the wrapper)
    # -------------------------------------------------------------------------

    def solve_unit(self, unit: UnitOperation) -> None:
        """
        Solve a single unit through the solver's pipeline.
        This is the ONLY place where unit.solve() should be called.
        """
        self.before_solve(unit)
        t0 = time.perf_counter()
        try:
            unit.solve()
        except Exception as exc:
            self.on_solve_error(unit, exc)
        finally:
            unit.solve_time = time.perf_counter() - t0
        self.after_solve(unit)

    # -------------------------------------------------------------------------
    # Topological sort
    # -------------------------------------------------------------------------

    def _build_dependency_graph(self) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Dict[str, int]]:
        """
        Build the dependency graph from the stream connections.

        Returns:
            graph    : {unit_name: {upstream_units_it_depends_on}}
            adj      : {unit_name: {downstream_units_that_depend_on_it}}
            in_degree: {unit_name: number_of_unresolved_dependencies}
        """
        graph = {name: set() for name in self.fs.units}
        adj = {name: set() for name in self.fs.units}
        in_degree = {name: 0 for name in self.fs.units}

        for unit_name, unit in self.fs.units.items():
            for port in unit.input_ports:
                if port.stream is None:
                    raise ValueError(
                        f"INPUT port not connected: {unit_name}.{port.name}"
                    )

                producer = port.stream.producer
                if producer and producer.unit is not unit:
                    upstream = producer.unit.name
                    if upstream not in graph[unit_name]:
                        graph[unit_name].add(upstream)
                        adj[upstream].add(unit_name)
                        in_degree[unit_name] += 1

        return graph, adj, in_degree

    # -------------------------------------------------------------------------
    # Main solve entry point
    # -------------------------------------------------------------------------

    def solve(self) -> List[str]:
        """
        Solve the flowsheet.
        1. Compute topological order.
        2. Solve each unit in that order via solve_unit().
        3. Return the execution order.
        Raises RuntimeError if a recycle loop is detected.
        """
        graph, adj, in_degree = self._build_dependency_graph()

        # Kahn's algorithm: start with units that have zero dependencies
        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for downstream in adj[current]:
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        # If we didn't visit all units, there is a cycle (recycle loop)
        if len(order) != len(self.fs.units):
            unresolved = [n for n, d in in_degree.items() if d > 0]

            tear_candidates = []
            for name in unresolved:
                unit = self.fs.units[name]
                for port in unit.input_ports:
                    if port.stream and port.stream.producer:
                        if port.stream.producer.unit.name in unresolved:
                            tear_candidates.append(port.stream.name)

            raise RuntimeError(
                f"Cycle detected in units: {unresolved}.\n"
                f"  Candidate tear streams: {tear_candidates}\n"
                f"  Use a RecycleSolver (tear + iteration) for this flowsheet."
            )

        # Execute units in topological order
        print(f"[SequentialSolver] Execution order: {' -> '.join(order)}")
        for unit_name in order:
            unit = self.fs.units[unit_name]
            self.solve_unit(unit)
            print(f"[SequentialSolver]  OK  {unit_name}  ({unit.solve_time*1e3:.2f} ms)")

        return order
