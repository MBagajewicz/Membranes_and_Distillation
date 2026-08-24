"""Solvers — completely decoupled from Flowsheet."""

from __future__ import annotations

import copy
import time
from collections import deque
from typing import Any, Dict, List, Set, Tuple

from .flowsheet import Flowsheet
from .unit_operation import UnitOperation


class SequentialSolver:
    """Sequential modular solver for acyclic flowsheets."""

    def __init__(self, flowsheet: Flowsheet):
        self.fs = flowsheet

    def before_solve(self, unit: UnitOperation) -> None:
        unit.status = "solving"
        unit.reset_diagnostics()

    def after_solve(self, unit: UnitOperation) -> None:
        unit.status = "converged"

    def on_solve_error(self, unit: UnitOperation, exc: Exception) -> None:
        unit.status = "error"
        unit.warnings.append(str(exc))
        raise

    def solve_unit(self, unit: UnitOperation) -> None:
        """Solve one unit through the common solver pipeline."""
        self.before_solve(unit)
        t0 = time.perf_counter()
        try:
            unit.solve()
        except Exception as exc:
            self.on_solve_error(unit, exc)
        finally:
            unit.solve_time = time.perf_counter() - t0
        self.after_solve(unit)

    def _build_dependency_graph(
        self,
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Dict[str, int]]:
        """Build the unit dependency graph from Stream producer/consumer links."""
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

    @staticmethod
    def _topological_order(
        adj: Dict[str, Set[str]],
        in_degree: Dict[str, int],
    ) -> List[str]:
        """Return a Kahn topological order, or raise if a cycle remains."""
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        order: List[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for downstream in adj[current]:
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        if len(order) != len(in_degree):
            unresolved = [name for name, degree in in_degree.items() if degree > 0]
            raise RuntimeError(f"Cycle detected in units: {unresolved}")

        return order

    def _find_tear_candidates(self, unresolved: List[str]) -> List[str]:
        candidates = []
        unresolved_set = set(unresolved)
        for name in unresolved:
            for port in self.fs.units[name].input_ports:
                if port.stream and port.stream.producer:
                    if port.stream.producer.unit.name in unresolved_set:
                        candidates.append(port.stream.name)
        return list(dict.fromkeys(candidates))

    def solve(self) -> List[str]:
        """Solve the flowsheet in topological order."""
        graph, adj, in_degree = self._build_dependency_graph()
        try:
            order = self._topological_order(adj, in_degree)
        except RuntimeError:
            unresolved = [n for n, d in in_degree.items() if d > 0]
            tear_candidates = self._find_tear_candidates(unresolved)
            raise RuntimeError(
                f"Cycle detected in units: {unresolved}.\n"
                f"  Candidate tear streams: {tear_candidates}\n"
                f"  Use an IterativeSolver (tear + iteration) for this flowsheet."
            )

        print(f"[SequentialSolver] Execution order: {' -> '.join(order)}")
        for unit_name in order:
            unit = self.fs.units[unit_name]
            self.solve_unit(unit)
            print(
                f"[SequentialSolver]  OK  {unit_name}  "
                f"({unit.solve_time * 1e3:.2f} ms)"
            )
        return order


class IterativeSolver(SequentialSolver):
    """
    Generic tear-stream iterative solver for cyclic flowsheets.

    A selected tear stream is treated as a guessed input during each iteration.
    The dependency carried by that stream is removed temporarily, allowing the
    remaining graph to be solved with the same UnitOperation interface used by
    SequentialSolver. The calculated tear state is then compared with the old
    guess and optionally under-relaxed before the next iteration.
    """

    DEFAULT_STATE_VARIABLES = (
        "T",
        "P",
        "mass_flow",
        "composition",
    )

    def __init__(
        self,
        flowsheet: Flowsheet,
        tear_streams: str | List[str] | Tuple[str, ...] | Set[str],
        tolerance: float = 1e-6,
        max_iterations: int = 100,
        relaxation: float = 1.0,
        state_variables: Dict[str, Tuple[str, ...]] | None = None,
        initial_guesses: Dict[str, Dict[str, Any]] | None = None,
    ):
        super().__init__(flowsheet)

        if isinstance(tear_streams, str):
            tear_streams = [tear_streams]
        self.tear_streams = list(tear_streams)

        if not self.tear_streams:
            raise ValueError("At least one tear stream must be specified.")
        if tolerance <= 0:
            raise ValueError("tolerance must be > 0.")
        if max_iterations < 1:
            raise ValueError("max_iterations must be >= 1.")
        if not 0 < relaxation <= 1:
            raise ValueError("relaxation must satisfy 0 < relaxation <= 1.")

        self.tolerance = float(tolerance)
        self.max_iterations = int(max_iterations)
        self.relaxation = float(relaxation)
        self.state_variables = state_variables or {}
        self.initial_guesses = initial_guesses or {}

        self.iterations = 0
        self.converged = False
        self.residual = float("inf")

    def _validate_tear_streams(self) -> None:
        for name in self.tear_streams:
            if name not in self.fs.streams:
                raise ValueError(f"Tear stream '{name}' not found in flowsheet.")
            stream = self.fs.streams[name]
            if stream.producer is None:
                raise ValueError(f"Tear stream '{name}' has no producer.")
            if stream.consumer is None:
                raise ValueError(f"Tear stream '{name}' has no consumer.")

    def _build_iteration_order(self) -> List[str]:
        """Build a topological order after removing tear-stream dependencies."""
        tear_set = set(self.tear_streams)
        graph = {name: set() for name in self.fs.units}
        adj = {name: set() for name in self.fs.units}
        in_degree = {name: 0 for name in self.fs.units}

        for unit_name, unit in self.fs.units.items():
            for port in unit.input_ports:
                if port.stream is None:
                    raise ValueError(
                        f"INPUT port not connected: {unit_name}.{port.name}"
                    )
                stream = port.stream
                if stream.name in tear_set:
                    continue
                producer = stream.producer
                if producer and producer.unit is not unit:
                    upstream = producer.unit.name
                    if upstream not in graph[unit_name]:
                        graph[unit_name].add(upstream)
                        adj[upstream].add(unit_name)
                        in_degree[unit_name] += 1

        try:
            return self._topological_order(adj, in_degree)
        except RuntimeError:
            unresolved = [n for n, d in in_degree.items() if d > 0]
            raise RuntimeError(
                "The selected tear stream(s) did not break all cycles.\n"
                f"  Unresolved units: {unresolved}\n"
                f"  Tear streams: {self.tear_streams}"
            )

    def _variables_for(self, stream_name: str) -> Tuple[str, ...]:
        return self.state_variables.get(stream_name, self.DEFAULT_STATE_VARIABLES)

    @staticmethod
    def _copy(value: Any) -> Any:
        return copy.deepcopy(value)

    def _snapshot(self) -> Dict[str, Dict[str, Any]]:
        snapshot: Dict[str, Dict[str, Any]] = {}
        for name in self.tear_streams:
            stream = self.fs.streams[name]
            values = {}
            for variable in self._variables_for(name):
                if hasattr(stream, variable):
                    values[variable] = self._copy(getattr(stream, variable))
            if not values:
                raise ValueError(
                    f"No valid state variables found on tear stream '{name}'."
                )
            snapshot[name] = values
        return snapshot

    def _restore(self, state: Dict[str, Dict[str, Any]]) -> None:
        """Restore tear-stream state using Stream's public API.

        Stream state properties such as ``T`` and ``P`` are read-only.
        Therefore, the solver must restore the state through ``Stream.update()``
        rather than assigning directly to the properties.
        """
        for name, values in state.items():
            stream = self.fs.streams[name]

            update_values = {
                variable: self._copy(value)
                for variable, value in values.items()
            }

            stream.update(**update_values)

    @classmethod
    def _residual_value(cls, old: Any, new: Any) -> float:
        if isinstance(old, dict) and isinstance(new, dict):
            keys = set(old) | set(new)
            return max(
                (cls._residual_value(old.get(k), new.get(k)) for k in keys),
                default=0.0,
            )
        if isinstance(old, (list, tuple)) and isinstance(new, (list, tuple)):
            if len(old) != len(new):
                return float("inf")
            return max(
                (cls._residual_value(a, b) for a, b in zip(old, new)),
                default=0.0,
            )
        try:
            return abs(float(new) - float(old))
        except (TypeError, ValueError):
            return 0.0 if old == new else float("inf")

    def _residual(self, old: Dict[str, Dict[str, Any]], new: Dict[str, Dict[str, Any]]) -> float:
        value = 0.0
        for name in self.tear_streams:
            for variable, old_value in old[name].items():
                if variable not in new[name]:
                    return float("inf")
                value = max(value, self._residual_value(old_value, new[name][variable]))
        return value

    def _relax(
        self,
        old: Dict[str, Dict[str, Any]],
        new: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Return the next tear guess using simple under-relaxation."""
        result: Dict[str, Dict[str, Any]] = {}
        alpha = self.relaxation

        for name in self.tear_streams:
            result[name] = {}
            for variable, old_value in old[name].items():
                new_value = new[name][variable]

                if isinstance(old_value, dict) and isinstance(new_value, dict):
                    values = {}
                    for key in set(old_value) | set(new_value):
                        if key not in old_value:
                            values[key] = self._copy(new_value[key])
                        elif key not in new_value:
                            values[key] = self._copy(old_value[key])
                        else:
                            try:
                                values[key] = (1 - alpha) * old_value[key] + alpha * new_value[key]
                            except (TypeError, ValueError):
                                values[key] = self._copy(new_value[key])
                    result[name][variable] = values
                    continue

                try:
                    result[name][variable] = (1 - alpha) * old_value + alpha * new_value
                except (TypeError, ValueError):
                    result[name][variable] = self._copy(new_value)

        return result

    def solve(self) -> List[str]:
        """Solve the cyclic flowsheet by tear-stream iteration."""
        self._validate_tear_streams()
        order = self._build_iteration_order()
        current = self._snapshot()

        # Apply optional user-defined initial guesses to the tear states.
        for name, values in self.initial_guesses.items():
            if name not in self.tear_streams:
                raise ValueError(
                    f"Initial guess provided for non-tear stream '{name}'."
                )
            if not isinstance(values, dict):
                raise TypeError(
                    f"Initial guess for tear stream '{name}' must be a dictionary."
                )
            current[name].update(self._copy(values))

        # Make the initial guess effective on the actual Stream objects before
        # the first unit operation is solved.
        self._restore(current)

        self.iterations = 0
        self.converged = False
        self.residual = float("inf")

        print(f"[IterativeSolver] Execution order: {' -> '.join(order)}")
        print(f"[IterativeSolver] Tear streams: {', '.join(self.tear_streams)}")
        print(
            f"[IterativeSolver] tolerance={self.tolerance:.3e}, "
            f"max_iterations={self.max_iterations}, "
            f"relaxation={self.relaxation:.3f}"
        )

        for iteration in range(1, self.max_iterations + 1):
            self.iterations = iteration
            self._restore(current)

            for unit_name in order:
                unit = self.fs.units[unit_name]
                self.solve_unit(unit)

            calculated = self._snapshot()
            self.residual = self._residual(current, calculated)

            print(
                f"[IterativeSolver] Iteration {iteration:03d} | "
                f"residual={self.residual:.6e}"
            )

            if self.residual <= self.tolerance:
                self._restore(calculated)
                self.converged = True
                print(f"[IterativeSolver] CONVERGED in {iteration} iterations.")
                return order

            current = self._relax(current, calculated)

        self._restore(current)
        raise RuntimeError(
            "IterativeSolver did not converge.\n"
            f"  Iterations: {self.max_iterations}\n"
            f"  Final residual: {self.residual:.6e}\n"
            f"  Tolerance: {self.tolerance:.6e}\n"
            f"  Tear streams: {self.tear_streams}\n"
            f"  Relaxation: {self.relaxation:.3f}"
        )
