"""Finite realizability audits for qn+1 accelerated maps."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from math import ceil, log2
from pathlib import Path
from typing import Any

from .core import v2
from .max_plus import _karp_max_cycle_mean
from .qnp1_family import (
    _accelerated_step_with_valuation_q,
    apply_word_q,
    classify_cycle_word_q,
    valuation_word_q,
)


_CLASSIFICATION_KINDS = (
    "noninteger_2adic_only",
    "positive_integer_cycle",
    "negative_integer_cycle",
    "integer_but_not_positive_odd",
    "positive_integer_nonrealizing_candidate",
    "impossible_power_balance",
)


@dataclass(frozen=True)
class QTailEdge:
    source_tail_depth: int
    source_unit_residue: int
    target_tail_depth: int
    target_unit_residue: int
    valuation: int
    accelerated_steps: int
    valuation_word: tuple[int, ...]
    witness_count: int
    slope_log2: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QTailGraph:
    q_param: int
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    tail_drop: int
    states: tuple[tuple[int, int], ...]
    edges: tuple[QTailEdge, ...]
    closed_overflow_edges: int


@dataclass(frozen=True)
class QCycleCandidate:
    valuation_word: tuple[int, ...]
    edge_factor: float
    log2_growth: float
    graph_cycle_edges: int
    accelerated_steps: int
    start_tail_depth: int
    start_unit_residue: int


@dataclass(frozen=True)
class QPositiveCycle:
    word: tuple[int, ...]
    cycle_value: str
    orbit: tuple[int, ...]
    edge_factor: float
    log2_growth: float
    graph_cycle_edges: int
    accelerated_steps: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QNP1RealizabilityLevel:
    level_index: int
    q_param: int
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    tail_drop: int
    tail_states: int
    tail_edges: int
    closed_overflow_edges: int
    max_cycle_edges: int
    max_cycles_scanned: int
    cycles_scanned: int
    audited_cycles: int
    classification_counts: dict[str, int]
    positive_integer_cycle_count: int
    negative_integer_cycle_count: int
    realizable_karp_factor_positive: float | None
    realizable_karp_factor_integer: float | None
    exact_karp_factor_unclassified: float | None
    positive_integer_cycles: tuple[QPositiveCycle, ...]
    elapsed_seconds: float
    status: str
    cycle_cap_reached: bool = False
    scan_completion_status: str = "bounded_simple_cycle_scan_complete_for_depth_cap"

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["positive_integer_cycles"] = [
            cycle.to_json_dict() for cycle in self.positive_integer_cycles
        ]
        return data


@dataclass(frozen=True)
class QSmallSearchCycle:
    orbit: tuple[int, ...]
    word: tuple[int, ...]
    edge_factor: float
    recovered_in_bounded_scan: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QNP1RealizabilityReport:
    type: str
    status: str
    q_param: int
    construction: str
    caveat: str
    levels: tuple[QNP1RealizabilityLevel, ...]
    known_cycles_recovered: tuple[QSmallSearchCycle, ...]
    small_search_cycles: tuple[QSmallSearchCycle, ...]
    realizable_karp_factor_q5_max: float | None
    realizable_karp_factor_q5_positive_max: float | None
    comparison_to_q3: dict[str, float | int | str | None]
    timing_and_memory: dict[str, Any]
    scan_policy: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "q_param": self.q_param,
            "construction": self.construction,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "known_cycles_recovered": [
                cycle.to_json_dict() for cycle in self.known_cycles_recovered
            ],
            "small_search_cycles": [
                cycle.to_json_dict() for cycle in self.small_search_cycles
            ],
            "realizable_karp_factor_q5_max": self.realizable_karp_factor_q5_max,
            "realizable_karp_factor_q5_positive_max": (
                self.realizable_karp_factor_q5_positive_max
            ),
            "comparison_to_q3": dict(self.comparison_to_q3),
            "timing_and_memory": dict(self.timing_and_memory),
            "scan_policy": dict(self.scan_policy),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json() + "\n")


def _is_power_of_two(value: int) -> bool:
    return value > 0 and value & (value - 1) == 0


def _tail_drop(q_param: int) -> int:
    if q_param <= 1 or q_param % 2 == 0:
        raise ValueError("q_param must be an odd integer greater than one")
    return v2(q_param - 1)


def _qnp1_power_tail_graph(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    q_param: int = 5,
) -> QTailGraph:
    """Enumerate witnessed edges in ``n = 2^R u - 1`` coordinates for qn+1."""

    tail_drop = _tail_drop(q_param)
    if tail_unit_power < 2:
        raise ValueError("tail_unit_power must be at least two")
    if max_tail_depth < 1:
        raise ValueError("max_tail_depth must be positive")
    if max_tail_depth >= tail_unit_power:
        raise ValueError("max_tail_depth must be smaller than tail_unit_power")
    if max_valuation < tail_drop:
        raise ValueError("max_valuation must be at least the forced tail drop")

    modulus = 1 << tail_unit_power
    odd_units = tuple(range(1, modulus, 2))
    edge_counts: dict[tuple[int, int, int, int, tuple[int, ...], float], int] = {}
    closed_overflow_edges = 0

    def add_edge(
        source_tail: int,
        source_unit: int,
        target_tail: int,
        target_unit: int,
        word: tuple[int, ...],
        count: int = 1,
    ) -> None:
        slope = len(word) * log2(q_param) - sum(word)
        key = (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            word,
            slope,
        )
        edge_counts[key] = edge_counts.get(key, 0) + count

    def add_post_exit_edge(
        source_tail: int,
        source_unit: int,
        landing: int,
        first_valuation: int,
    ) -> None:
        nonlocal closed_overflow_edges
        target_tail = v2(landing + 1)
        target_unit = ((landing + 1) >> target_tail) % modulus
        word = (first_valuation,)
        if target_tail > max_tail_depth:
            forced_steps = ceil((target_tail - max_tail_depth) / tail_drop)
            target_unit = (
                target_unit * pow(q_param, forced_steps, modulus)
            ) % modulus
            target_tail -= forced_steps * tail_drop
            word = word + (tail_drop,) * forced_steps
            closed_overflow_edges += 1
        add_edge(
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            word,
        )

    for tail_depth in range(tail_drop + 1, max_tail_depth + 1):
        for unit in odd_units:
            add_edge(
                tail_depth,
                unit,
                tail_depth - tail_drop,
                (q_param * unit) % modulus,
                (tail_drop,),
            )

    for tail_depth in range(1, min(tail_drop, max_tail_depth) + 1):
        constant = (q_param - 1) >> tail_depth
        for unit in odd_units:
            base = q_param * unit - constant
            if base % modulus != 0:
                exponent = v2(base)
                total_valuation = tail_depth + exponent
                if total_valuation > max_valuation:
                    continue
                for lift in range(1 << exponent):
                    lifted_unit = unit + (lift << tail_unit_power)
                    landing = (q_param * lifted_unit - constant) >> exponent
                    add_post_exit_edge(
                        tail_depth,
                        unit,
                        landing,
                        total_valuation,
                    )
                continue

            for exponent in range(tail_unit_power, max_valuation - tail_depth + 1):
                for lift in range(1 << exponent):
                    lifted_unit = unit + (lift << tail_unit_power)
                    lifted_base = q_param * lifted_unit - constant
                    if v2(lifted_base) != exponent:
                        continue
                    landing = lifted_base >> exponent
                    add_post_exit_edge(
                        tail_depth,
                        unit,
                        landing,
                        tail_depth + exponent,
                    )

    states = tuple(
        (tail_depth, unit)
        for tail_depth in range(1, max_tail_depth + 1)
        for unit in odd_units
    )
    edges = tuple(
        QTailEdge(
            source_tail_depth=source_tail,
            source_unit_residue=source_unit,
            target_tail_depth=target_tail,
            target_unit_residue=target_unit,
            valuation=sum(word),
            accelerated_steps=len(word),
            valuation_word=word,
            witness_count=count,
            slope_log2=slope,
        )
        for (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            word,
            slope,
        ), count in sorted(edge_counts.items())
    )
    return QTailGraph(
        q_param=q_param,
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        tail_drop=tail_drop,
        states=states,
        edges=edges,
        closed_overflow_edges=closed_overflow_edges,
    )


def _qnp1_sampled_tail_graph(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    q_param: int,
    sample_lift_power: int | None = None,
) -> QTailGraph:
    """Sample witnessed tail transitions when q-1 is not a pure power of two.

    The q=3 and q=5 publication-facing audits use the exact LTE closure above.
    For general odd q, the Mersenne tail no longer has a deterministic forced
    drop, so this fallback records a finite witnessed graph over lifted unit
    residues. It is deliberately empirical.
    """

    tail_drop = _tail_drop(q_param)
    if tail_unit_power < 2:
        raise ValueError("tail_unit_power must be at least two")
    if max_tail_depth < 1:
        raise ValueError("max_tail_depth must be positive")
    if max_tail_depth >= tail_unit_power:
        raise ValueError("max_tail_depth must be smaller than tail_unit_power")
    if max_valuation < 1:
        raise ValueError("max_valuation must be positive")

    lift_power = min(max_valuation, 8) if sample_lift_power is None else sample_lift_power
    if lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")

    modulus = 1 << tail_unit_power
    odd_units = tuple(range(1, modulus, 2))
    edge_counts: dict[tuple[int, int, int, int, tuple[int, ...], float], int] = {}
    closed_overflow_edges = 0

    def add_edge(
        source_tail: int,
        source_unit: int,
        target_tail: int,
        target_unit: int,
        word: tuple[int, ...],
    ) -> None:
        slope = len(word) * log2(q_param) - sum(word)
        key = (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            word,
            slope,
        )
        edge_counts[key] = edge_counts.get(key, 0) + 1

    for source_tail in range(1, max_tail_depth + 1):
        for source_unit in odd_units:
            for lift in range(1 << lift_power):
                unit = source_unit + (lift << tail_unit_power)
                x = (1 << source_tail) * unit - 1
                word: list[int] = []
                overflow_seen = False
                for _step in range(max_valuation):
                    x, valuation = _accelerated_step_with_valuation_q(x, q_param)
                    word.append(valuation)
                    if sum(word) > max_valuation:
                        break
                    target_tail = v2(x + 1)
                    if target_tail > max_tail_depth:
                        overflow_seen = True
                        continue
                    target_unit = ((x + 1) >> target_tail) % modulus
                    if overflow_seen:
                        closed_overflow_edges += 1
                    add_edge(
                        source_tail,
                        source_unit,
                        target_tail,
                        target_unit,
                        tuple(word),
                    )
                    break

    states = tuple(
        (tail_depth, unit)
        for tail_depth in range(1, max_tail_depth + 1)
        for unit in odd_units
    )
    edges = tuple(
        QTailEdge(
            source_tail_depth=source_tail,
            source_unit_residue=source_unit,
            target_tail_depth=target_tail,
            target_unit_residue=target_unit,
            valuation=sum(word),
            accelerated_steps=len(word),
            valuation_word=word,
            witness_count=count,
            slope_log2=slope,
        )
        for (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            word,
            slope,
        ), count in sorted(edge_counts.items())
    )
    return QTailGraph(
        q_param=q_param,
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        tail_drop=tail_drop,
        states=states,
        edges=edges,
        closed_overflow_edges=closed_overflow_edges,
    )


def qnp1_lte_closed_tail_graph(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    q_param: int = 5,
) -> QTailGraph:
    """Enumerate a q-aware bounded tail graph.

    When ``q - 1`` is a power of two this is the exact LTE-closed Mersenne-tail
    graph used by the q=3 and q=5 audits. Otherwise it falls back to a finite
    witnessed residue-lift graph.
    """

    if _is_power_of_two(q_param - 1):
        return _qnp1_power_tail_graph(
            tail_unit_power=tail_unit_power,
            max_tail_depth=max_tail_depth,
            max_valuation=max_valuation,
            q_param=q_param,
        )
    return _qnp1_sampled_tail_graph(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        q_param=q_param,
    )


def _cycle_from_edges(
    start_state: tuple[int, int],
    edges: tuple[QTailEdge, ...],
    q_param: int,
) -> QCycleCandidate:
    word = tuple(valuation for edge in edges for valuation in edge.valuation_word)
    slope = len(word) * log2(q_param) - sum(word)
    return QCycleCandidate(
        valuation_word=word,
        edge_factor=(q_param ** len(word)) / (1 << sum(word)),
        log2_growth=slope,
        graph_cycle_edges=len(edges),
        accelerated_steps=len(word),
        start_tail_depth=start_state[0],
        start_unit_residue=start_state[1],
    )


def enumerate_qnp1_tail_cycles(
    graph: QTailGraph,
    max_cycle_edges: int,
    max_cycles_scanned: int,
) -> tuple[tuple[QCycleCandidate, ...], bool, float | None]:
    """Enumerate bounded simple cycles in a q-aware LTE-closed tail graph."""

    index = {state: offset for offset, state in enumerate(graph.states)}
    adjacency: list[list[tuple[int, int, QTailEdge]]] = [[] for _ in graph.states]
    weighted_edges: list[tuple[int, int, float]] = []
    for edge_id, edge in enumerate(graph.edges):
        source = index[(edge.source_tail_depth, edge.source_unit_residue)]
        target = index[(edge.target_tail_depth, edge.target_unit_residue)]
        adjacency[source].append((edge_id, target, edge))
        weighted_edges.append((source, target, edge.slope_log2))

    exact = _karp_max_cycle_mean(len(graph.states), tuple(weighted_edges))
    exact_factor = None if exact is None else 2.0 ** exact[0]
    cycles: list[QCycleCandidate] = []
    seen_edge_cycles: set[tuple[int, ...]] = set()
    stopped_early = False

    def canonical(edge_ids: tuple[int, ...]) -> tuple[int, ...]:
        rotations = [
            edge_ids[offset:] + edge_ids[:offset]
            for offset in range(len(edge_ids))
        ]
        return min(rotations)

    def dfs(
        start: int,
        current: int,
        visited: set[int],
        path_ids: list[int],
        path_edges: list[QTailEdge],
    ) -> None:
        nonlocal stopped_early
        if stopped_early or len(path_ids) >= max_cycle_edges:
            return
        for edge_id, target, edge in adjacency[current]:
            if target < start:
                continue
            if target == start:
                cycle_key = canonical(tuple(path_ids + [edge_id]))
                if cycle_key in seen_edge_cycles:
                    continue
                seen_edge_cycles.add(cycle_key)
                cycles.append(
                    _cycle_from_edges(
                        graph.states[start],
                        tuple(path_edges + [edge]),
                        graph.q_param,
                    )
                )
                if len(cycles) >= max_cycles_scanned:
                    stopped_early = True
                    return
                continue
            if target in visited:
                continue
            visited.add(target)
            path_ids.append(edge_id)
            path_edges.append(edge)
            dfs(start, target, visited, path_ids, path_edges)
            path_edges.pop()
            path_ids.pop()
            visited.remove(target)
            if stopped_early:
                return

    for start in range(len(graph.states)):
        dfs(start, start, {start}, [], [])
        if stopped_early:
            break

    return (
        tuple(sorted(cycles, key=lambda cycle: cycle.log2_growth, reverse=True)),
        stopped_early,
        exact_factor,
    )


def _orbit_for_word(n: int, word: tuple[int, ...], q_param: int) -> tuple[int, ...]:
    values = [n]
    x = n
    for expected in word[:-1]:
        x, actual = _accelerated_step_with_valuation_q(x, q_param)
        if actual != expected:
            raise ValueError(f"valuation mismatch: expected {expected}, got {actual}")
        values.append(x)
    apply_word_q(n, word, q_param)
    return tuple(values)


def _cycle_key(values: tuple[int, ...]) -> tuple[int, ...]:
    rotations = [values[offset:] + values[:offset] for offset in range(len(values))]
    return min(rotations)


def _word_rotation_key(word: tuple[int, ...]) -> tuple[int, ...]:
    rotations = [word[offset:] + word[:offset] for offset in range(len(word))]
    return min(rotations)


def direct_small_qnp1_cycles(
    q_param: int,
    n_max: int = 100,
    max_steps: int = 2_000,
    max_bits: int = 20_000,
) -> tuple[QSmallSearchCycle, ...]:
    """Find accelerated positive cycles reached by odd starts ``1 <= n <= n_max``."""

    cycles: dict[tuple[int, ...], QSmallSearchCycle] = {}
    for start in range(1, n_max + 1, 2):
        x = start
        seen: dict[int, int] = {}
        orbit: list[int] = []
        for _step in range(max_steps):
            if x in seen:
                offset = seen[x]
                cycle_values = tuple(orbit[offset:])
                word = valuation_word_q(cycle_values[0], len(cycle_values), q_param)
                key = _cycle_key(cycle_values)
                cycles[key] = QSmallSearchCycle(
                    orbit=key,
                    word=_word_rotation_key(word),
                    edge_factor=(q_param ** len(word)) / (1 << sum(word)),
                    recovered_in_bounded_scan=False,
                )
                break
            if x.bit_length() > max_bits:
                break
            seen[x] = len(orbit)
            orbit.append(x)
            x = _accelerated_step_with_valuation_q(x, q_param)[0]
    return tuple(sorted(cycles.values(), key=lambda cycle: cycle.orbit))


def _empty_counts() -> dict[str, int]:
    return {kind: 0 for kind in _CLASSIFICATION_KINDS}


def _positive_cycle_from_candidate(
    cycle: QCycleCandidate,
    q_param: int,
) -> QPositiveCycle | None:
    classification = classify_cycle_word_q(cycle.valuation_word, q_param)
    if classification.kind != "positive_integer_cycle":
        return None
    n = classification.value.numerator
    return QPositiveCycle(
        word=cycle.valuation_word,
        cycle_value=str(n),
        orbit=_orbit_for_word(n, cycle.valuation_word, q_param),
        edge_factor=cycle.edge_factor,
        log2_growth=cycle.log2_growth,
        graph_cycle_edges=cycle.graph_cycle_edges,
        accelerated_steps=cycle.accelerated_steps,
    )


def _level_report(
    level_index: int,
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    max_cycle_edges: int,
    max_cycles_scanned: int,
    q_param: int,
) -> QNP1RealizabilityLevel:
    started = time.perf_counter()
    graph = qnp1_lte_closed_tail_graph(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        q_param=q_param,
    )
    cycles, stopped_early, exact_factor = enumerate_qnp1_tail_cycles(
        graph,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
    )
    counts = _empty_counts()
    positive_cycles: list[QPositiveCycle] = []
    realizable_positive: float | None = None
    realizable_integer: float | None = None
    for cycle in cycles:
        classification = classify_cycle_word_q(cycle.valuation_word, q_param)
        counts[classification.kind] = counts.get(classification.kind, 0) + 1
        if classification.kind in {
            "positive_integer_cycle",
            "negative_integer_cycle",
            "integer_but_not_positive_odd",
        }:
            if realizable_integer is None or cycle.edge_factor > realizable_integer:
                realizable_integer = cycle.edge_factor
        if classification.kind == "positive_integer_cycle":
            if realizable_positive is None or cycle.edge_factor > realizable_positive:
                realizable_positive = cycle.edge_factor
            positive = _positive_cycle_from_candidate(cycle, q_param)
            if positive is not None:
                positive_cycles.append(positive)

    scan_status = (
        "cycle_cap_reached"
        if stopped_early
        else "bounded_simple_cycle_scan_complete_for_depth_cap"
    )
    return QNP1RealizabilityLevel(
        level_index=level_index,
        q_param=q_param,
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        tail_drop=graph.tail_drop,
        tail_states=len(graph.states),
        tail_edges=len(graph.edges),
        closed_overflow_edges=graph.closed_overflow_edges,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
        cycles_scanned=len(cycles),
        audited_cycles=len(cycles),
        classification_counts=counts,
        positive_integer_cycle_count=counts["positive_integer_cycle"],
        negative_integer_cycle_count=counts["negative_integer_cycle"],
        realizable_karp_factor_positive=realizable_positive,
        realizable_karp_factor_integer=realizable_integer,
        exact_karp_factor_unclassified=exact_factor,
        positive_integer_cycles=tuple(positive_cycles),
        elapsed_seconds=time.perf_counter() - started,
        status=scan_status,
        cycle_cap_reached=stopped_early,
        scan_completion_status=scan_status,
    )


def _max_or_none(values: list[float]) -> float | None:
    return None if not values else max(values)


def _ru_maxrss_kb() -> int | None:
    try:
        import resource
    except ImportError:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def qnp1_realizability_report(
    q_param: int = 5,
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6)),
    max_valuation: int = 12,
    max_cycle_edges: int = 12,
    max_cycles_scanned: int = 200_000,
    small_search_n_max: int = 100,
) -> QNP1RealizabilityReport:
    """Run the qn+1 bounded simple-cycle realizability audit."""

    started = time.perf_counter()
    rss_before = _ru_maxrss_kb()
    report_levels = tuple(
        _level_report(
            level_index=index,
            tail_unit_power=tail_unit_power,
            max_tail_depth=max_tail_depth,
            max_valuation=max_valuation,
            max_cycle_edges=max_cycle_edges,
            max_cycles_scanned=max_cycles_scanned,
            q_param=q_param,
        )
        for index, (tail_unit_power, max_tail_depth) in enumerate(levels)
    )
    positive_keys = {
        _cycle_key(cycle.orbit)
        for level in report_levels
        for cycle in level.positive_integer_cycles
    }
    small_cycles = tuple(
        QSmallSearchCycle(
            orbit=cycle.orbit,
            word=cycle.word,
            edge_factor=cycle.edge_factor,
            recovered_in_bounded_scan=_cycle_key(cycle.orbit) in positive_keys,
        )
        for cycle in direct_small_qnp1_cycles(
            q_param=q_param,
            n_max=small_search_n_max,
        )
    )
    known_recovered = tuple(
        cycle for cycle in small_cycles if cycle.recovered_in_bounded_scan
    )
    integer_factors = [
        factor
        for level in report_levels
        for factor in [level.realizable_karp_factor_integer]
        if factor is not None
    ]
    positive_factors = [
        factor
        for level in report_levels
        for factor in [level.realizable_karp_factor_positive]
        if factor is not None
    ]
    q5_integer = _max_or_none(integer_factors)
    q5_positive = _max_or_none(positive_factors)
    elapsed = time.perf_counter() - started
    rss_after = _ru_maxrss_kb()
    return QNP1RealizabilityReport(
        type="qnp1_tail_cycle_realizability",
        status=(
            "positive_integer_cycles_found"
            if positive_factors
            else "no_positive_integer_cycles_found_in_bounded_scan"
        ),
        q_param=q_param,
        construction=(
            "Simple cycles are enumerated in a q-aware LTE-closed Mersenne-tail "
            "graph. Each valuation word is classified by the exact qn+1 affine "
            "cycle equation, and small positive cycles reached from n0 <= 100 "
            "are checked by direct accelerated simulation."
        ),
        caveat=(
            "This is a finite empirical diagnostic bounded by levels, "
            "max_cycle_edges, max_cycles_scanned, and max_valuation; it is not "
            "a proof of global qn+1 dynamics or a proof of cycle absence."
        ),
        levels=report_levels,
        known_cycles_recovered=known_recovered,
        small_search_cycles=small_cycles,
        realizable_karp_factor_q5_max=q5_integer,
        realizable_karp_factor_q5_positive_max=q5_positive,
        comparison_to_q3={
            "q3_realizable_karp_factor": 0.75,
            "q5_realizable_karp_factor": q5_integer,
            "q5_positive_realizable_karp_factor": q5_positive,
            "predicted_q5_drift": log2(5) - 2,
            "q5_minus_q3_drift": log2(5 / 3),
            "q3_tail_forced_drop": 1,
            "q5_tail_forced_drop": _tail_drop(5),
            "factor_scope_note": (
                "q5_realizable_karp_factor is over integer-realizable bounded "
                "tail-cycle words; the positive-only maximum is reported "
                "separately because positive cycles require 2^A > q^m."
            ),
        },
        timing_and_memory={
            "elapsed_seconds": elapsed,
            "ru_maxrss_kb_before": rss_before,
            "ru_maxrss_kb_after": rss_after,
            "timing_note": (
                "q=5 uses forced tail drops of two valuations, changing both "
                "edge compression and overflow closure relative to q=3."
            ),
        },
        scan_policy={
            "levels": [list(level) for level in levels],
            "max_valuation": max_valuation,
            "max_cycle_edges": max_cycle_edges,
            "max_cycles_scanned": max_cycles_scanned,
            "small_search_n_max": small_search_n_max,
        },
    )
