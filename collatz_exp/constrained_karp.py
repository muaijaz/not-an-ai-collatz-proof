"""Automaton-constrained Karp diagnostics on the LTE-closed tail graph."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import gcd, log2
from typing import Any

from .christoffel import (
    LOG2_3,
    christoffel_slope,
    is_christoffel_compatible,
    is_upper_christoffel_conjugate,
    valuation_word_to_parity_bits,
)
from .constrained_jsr import (
    TailAwareProjectiveEdge,
    _christoffel_filtered_level,
    _tail_aware_edges,
)
from .cycles import classify_cycle_word
from .lift_realizability import exact_word_closures_mod_power, word_cylinder_residues
from .max_plus import _karp_max_cycle_mean


def _canonical_rotation(bits: tuple[int, ...]) -> tuple[int, ...]:
    return min(bits[offset:] + bits[:offset] for offset in range(len(bits)))


def _mechanical_word(ones: int, length: int) -> tuple[int, ...]:
    return tuple(
        ((index + 1) * ones) // length - (index * ones) // length
        for index in range(length)
    )


@dataclass(frozen=True)
class BalancedAutomatonState:
    pattern_index: int
    offset: int

    def to_json_dict(self) -> dict[str, int]:
        return asdict(self)


class BalancedWordAutomaton:
    """Finite acceptor for bounded primitive cyclically balanced patterns.

    The automaton is a finite union of phase cycles.  Each phase cycle is a
    primitive cyclically balanced binary word up to ``max_period``; consuming a
    bit advances the phase only when the bit agrees with that periodic word.
    """

    def __init__(self, max_imbalance: int = 1, max_period: int = 4) -> None:
        if max_imbalance < 1:
            raise ValueError("max_imbalance must be positive")
        if max_period < 2:
            raise ValueError("max_period must be at least two")
        patterns: list[tuple[int, ...]] = []
        seen: set[tuple[int, ...]] = set()
        for length in range(2, max_period + 1):
            for ones in range(1, length):
                zeros = length - ones
                if gcd(ones, zeros) != 1:
                    continue
                word = _canonical_rotation(_mechanical_word(ones, length))
                if word in seen:
                    continue
                if not is_christoffel_compatible(word):
                    continue
                if _cyclic_factor_imbalance(word) > max_imbalance:
                    continue
                seen.add(word)
                patterns.append(word)
        self.max_imbalance = max_imbalance
        self.max_period = max_period
        self.patterns = tuple(patterns)
        self.states = tuple(
            BalancedAutomatonState(pattern_index, offset)
            for pattern_index, pattern in enumerate(self.patterns)
            for offset in range(len(pattern))
        )
        self._state_index = {
            state: index for index, state in enumerate(self.states)
        }

    @property
    def state_count(self) -> int:
        return len(self.states)

    @property
    def pattern_count(self) -> int:
        return len(self.patterns)

    def transition(self, state_index: int, bits: tuple[int, ...]) -> int | None:
        state = self.states[state_index]
        pattern = self.patterns[state.pattern_index]
        offset = state.offset
        for bit in bits:
            if bit not in (0, 1):
                raise ValueError("automaton labels must be binary")
            if bit != pattern[offset]:
                return None
            offset = (offset + 1) % len(pattern)
        return self._state_index[BalancedAutomatonState(state.pattern_index, offset)]

    def accepts_cyclic_word(self, bits: tuple[int, ...]) -> bool:
        if len(bits) > self.max_period:
            return False
        return (
            _cyclic_factor_imbalance(bits) <= self.max_imbalance
            and is_christoffel_compatible(bits)
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "max_imbalance": self.max_imbalance,
            "max_period": self.max_period,
            "pattern_count": self.pattern_count,
            "state_count": self.state_count,
            "patterns": [list(pattern) for pattern in self.patterns],
        }


def _cyclic_factor_imbalance(bits: tuple[int, ...]) -> int:
    length = len(bits)
    if length <= 1:
        return 0
    doubled = bits + bits
    worst = 0
    for window in range(1, length + 1):
        counts = [
            sum(doubled[start : start + window])
            for start in range(length)
        ]
        worst = max(worst, max(counts) - min(counts))
    return worst


@dataclass(frozen=True)
class TailGraph:
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    states: tuple[tuple[int, int], ...]
    edges: tuple[TailAwareProjectiveEdge, ...]
    closed_overflow_edges: int


@dataclass(frozen=True)
class ProductEdge:
    source: int
    target: int
    tail_edge_index: int
    automaton_source: int
    automaton_target: int
    numerator: int
    denominator: int
    log2_weight: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProductGraph:
    tail_graph: TailGraph
    automaton: BalancedWordAutomaton
    states: int
    edges: tuple[ProductEdge, ...]


@dataclass(frozen=True)
class ConstrainedKarpResult:
    max_cycle_mean_log2_slope: float | None
    constrained_factor: float | None
    exact_rational_factor: str | None
    witness_product_state: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstrainedKarpLevel:
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    max_imbalance: int
    automaton_max_period: int
    tail_states: int
    tail_edges: int
    closed_overflow_edges: int
    automaton_patterns: int
    automaton_states: int
    product_states: int
    product_edges: int
    constrained_karp_log2_slope: float | None
    constrained_karp_factor: float | None
    exact_rational_factor: str | None
    christoffel_cycle_filter_bound: float | None
    within_cycle_filter_bound: bool | None
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstrainedKarpReport:
    type: str
    status: str
    construction: str
    caveat: str
    levels: tuple[ConstrainedKarpLevel, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "construction": self.construction,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class KarpSlopeSweepSurvivor:
    cycle_edges: int
    accelerated_steps: int
    edge_factor: float
    edge_mean_log2_slope: float
    christoffel_slope: str
    slope_distance: float
    non_elementary: bool
    valuation_word: tuple[int, ...]
    parity_word: tuple[int, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KarpSlopeSweepObstruction:
    level_index: int
    tail_unit_power: int
    max_tail_depth: int
    automaton_max_period: int
    slope_tolerance: float
    survivor: KarpSlopeSweepSurvivor

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["survivor"] = self.survivor.to_json_dict()
        return data


@dataclass(frozen=True)
class KarpSlopeJointSweepLevel:
    level_index: int
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    max_imbalance: int
    automaton_max_period: int
    slope_target: float
    slope_tolerance: float
    tail_states: int
    tail_edges: int
    closed_overflow_edges: int
    automaton_patterns: int
    automaton_states: int
    product_states: int
    product_edges: int
    constrained_karp_factor: float | None
    exact_rational_factor: str | None
    cycles_scanned: int
    max_cycle_edges: int
    max_cycles_scanned: int
    survivor_count: int
    non_elementary_survivor_count: int
    non_elementary_factor_ge_one: bool
    survivors: tuple[KarpSlopeSweepSurvivor, ...]
    status: str
    cycle_cap_reached: bool = False
    scan_completion_status: str = "bounded_simple_cycle_scan_complete_for_depth_cap"

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["survivors"] = [
            survivor.to_json_dict() for survivor in self.survivors
        ]
        return data


@dataclass(frozen=True)
class KarpSlopeJointSweepReport:
    type: str
    status: str
    construction: str
    caveat: str
    levels: tuple[KarpSlopeJointSweepLevel, ...]
    obstruction: KarpSlopeSweepObstruction | None
    next_step: str
    deferred_levels: tuple[dict[str, Any], ...] = ()
    scan_policy: dict[str, Any] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "construction": self.construction,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "obstruction": (
                None if self.obstruction is None else self.obstruction.to_json_dict()
            ),
            "next_step": self.next_step,
            "deferred_levels": list(self.deferred_levels),
            "scan_policy": self.scan_policy,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailCycleRealizabilityCycle:
    valuation_word: tuple[int, ...]
    parity_word: tuple[int, ...]
    edge_factor: float
    edge_mean_log2_slope: float
    graph_cycle_edges: int
    period: int
    christoffel_slope: str
    slope_distance: float
    in_slope_window: bool
    lift_classification: str
    cycle_value: str | None
    cylinder_power: int
    closure_precision_power: int
    cylinder_residue_count: int | None
    closes_mod_power_count: int | None
    lift_audit_status: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailCycleRealizabilityObstruction:
    level_index: int
    tail_unit_power: int
    max_tail_depth: int
    cycle: TailCycleRealizabilityCycle

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cycle"] = self.cycle.to_json_dict()
        return data


@dataclass(frozen=True)
class TailCycleRealizabilityLevel:
    level_index: int
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    tail_states: int
    tail_edges: int
    closed_overflow_edges: int
    max_cycle_edges: int
    max_cycles_scanned: int
    cycles_scanned: int
    audited_cycles: int
    recorded_cycles: int
    factor_threshold: float
    slope_target: float
    slope_tolerance: float
    high_growth_cycles: int
    classification_counts: dict[str, int]
    in_slope_window_count: int
    closure_skipped_count: int
    realizable_karp_factor: float | None
    realizable_karp_cycle: TailCycleRealizabilityCycle | None
    cycles: tuple[TailCycleRealizabilityCycle, ...]
    status: str
    cycle_cap_reached: bool = False
    scan_completion_status: str = "bounded_simple_cycle_scan_complete_for_depth_cap"

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cycles"] = [cycle.to_json_dict() for cycle in self.cycles]
        data["realizable_karp_cycle"] = (
            None
            if self.realizable_karp_cycle is None
            else self.realizable_karp_cycle.to_json_dict()
        )
        return data


@dataclass(frozen=True)
class TailCycleRealizabilityReport:
    type: str
    status: str
    construction: str
    caveat: str
    levels: tuple[TailCycleRealizabilityLevel, ...]
    classification_counts: dict[str, int]
    realizable_karp_factor: float | None
    realizable_karp_cycle: TailCycleRealizabilityObstruction | None
    obstruction: TailCycleRealizabilityObstruction | None
    deferred_levels: tuple[dict[str, Any], ...] = ()
    scan_policy: dict[str, Any] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "construction": self.construction,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "classification_counts": dict(self.classification_counts),
            "realizable_karp_factor": self.realizable_karp_factor,
            "realizable_karp_cycle": (
                None
                if self.realizable_karp_cycle is None
                else self.realizable_karp_cycle.to_json_dict()
            ),
            "obstruction": (
                None if self.obstruction is None else self.obstruction.to_json_dict()
            ),
            "deferred_levels": list(self.deferred_levels),
            "scan_policy": self.scan_policy,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def lte_closed_tail_graph(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
) -> TailGraph:
    edges, _overflow_edges, closed_overflow_edges = _tail_aware_edges(
        tail_unit_power,
        max_tail_depth,
        max_valuation,
    )
    modulus = 1 << tail_unit_power
    states = tuple(
        (tail_depth, unit)
        for tail_depth in range(1, max_tail_depth + 1)
        for unit in range(1, modulus, 2)
    )
    return TailGraph(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        states=states,
        edges=edges,
        closed_overflow_edges=closed_overflow_edges,
    )


def _edge_valuation_word(edge: TailAwareProjectiveEdge) -> tuple[int, ...]:
    if edge.accelerated_steps <= 1:
        return (edge.valuation,)
    first_valuation = edge.valuation - (edge.accelerated_steps - 1)
    if first_valuation < 1:
        raise ValueError("compressed edge has inconsistent valuation/step data")
    return (first_valuation,) + (1,) * (edge.accelerated_steps - 1)


def product_graph(
    tail_graph: TailGraph,
    automaton: BalancedWordAutomaton,
) -> ProductGraph:
    """Build the exact integer-index product graph."""

    tail_index = {state: index for index, state in enumerate(tail_graph.states)}
    product_edges: list[ProductEdge] = []
    for tail_edge_index, edge in enumerate(tail_graph.edges):
        source_tail = tail_index[(edge.source_tail_depth, edge.source_unit_residue)]
        target_tail = tail_index[(edge.target_tail_depth, edge.target_unit_residue)]
        bits = valuation_word_to_parity_bits(_edge_valuation_word(edge))
        numerator = 3 ** edge.accelerated_steps
        denominator = 1 << edge.valuation
        for automaton_source in range(automaton.state_count):
            automaton_target = automaton.transition(automaton_source, bits)
            if automaton_target is None:
                continue
            source = source_tail * automaton.state_count + automaton_source
            target = target_tail * automaton.state_count + automaton_target
            product_edges.append(
                ProductEdge(
                    source=source,
                    target=target,
                    tail_edge_index=tail_edge_index,
                    automaton_source=automaton_source,
                    automaton_target=automaton_target,
                    numerator=numerator,
                    denominator=denominator,
                    log2_weight=edge.slope_log2,
                )
            )
    return ProductGraph(
        tail_graph=tail_graph,
        automaton=automaton,
        states=len(tail_graph.states) * automaton.state_count,
        edges=tuple(product_edges),
    )


def constrained_karp_jsr(graph: ProductGraph) -> ConstrainedKarpResult:
    weighted_edges = tuple(
        (edge.source, edge.target, edge.log2_weight)
        for edge in graph.edges
    )
    result = _karp_max_cycle_mean(graph.states, weighted_edges)
    if result is None:
        return ConstrainedKarpResult(
            max_cycle_mean_log2_slope=None,
            constrained_factor=None,
            exact_rational_factor=None,
            witness_product_state=None,
        )
    mean, witness = result
    factor = 2.0**mean
    rational = Fraction(factor).limit_denominator(1_000_000)
    exact = None
    if abs(float(rational) - factor) <= 1e-12:
        exact = f"{rational.numerator}/{rational.denominator}"
    return ConstrainedKarpResult(
        max_cycle_mean_log2_slope=mean,
        constrained_factor=factor,
        exact_rational_factor=exact,
        witness_product_state=witness,
    )


def constrained_karp_jsr_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5)),
    max_valuation: int = 12,
    max_imbalance: int = 1,
    max_period: int = 4,
    christoffel_cycle_filter_bounds: dict[tuple[int, int], float] | None = None,
) -> ConstrainedKarpReport:
    from .constrained_jsr import christoffel_filtered_jsr_report

    automaton = BalancedWordAutomaton(
        max_imbalance=max_imbalance,
        max_period=max_period,
    )
    bounds = dict(christoffel_cycle_filter_bounds or {})
    missing = tuple(level for level in levels if level not in bounds)
    if missing:
        comparison = christoffel_filtered_jsr_report(
            levels=missing,
            max_valuation=max_valuation,
            max_cycle_edges=12,
            max_cycles_scanned=200_000,
        )
        for level, comparison_level in zip(missing, comparison.levels):
            bounds[level] = comparison_level.christoffel_filtered_best_factor

    report_levels: list[ConstrainedKarpLevel] = []
    for q, max_tail_depth in levels:
        tail_graph = lte_closed_tail_graph(q, max_tail_depth, max_valuation)
        graph = product_graph(tail_graph, automaton)
        result = constrained_karp_jsr(graph)
        bound = bounds.get((q, max_tail_depth))
        within = None
        if result.constrained_factor is not None and bound is not None:
            within = result.constrained_factor <= bound + 1e-12
        report_levels.append(
            ConstrainedKarpLevel(
                tail_unit_power=q,
                max_tail_depth=max_tail_depth,
                max_valuation=max_valuation,
                max_imbalance=max_imbalance,
                automaton_max_period=max_period,
                tail_states=len(tail_graph.states),
                tail_edges=len(tail_graph.edges),
                closed_overflow_edges=tail_graph.closed_overflow_edges,
                automaton_patterns=automaton.pattern_count,
                automaton_states=automaton.state_count,
                product_states=graph.states,
                product_edges=len(graph.edges),
                constrained_karp_log2_slope=result.max_cycle_mean_log2_slope,
                constrained_karp_factor=result.constrained_factor,
                exact_rational_factor=result.exact_rational_factor,
                christoffel_cycle_filter_bound=bound,
                within_cycle_filter_bound=within,
                status="finite_product_graph_karp_diagnostic",
            )
        )

    return ConstrainedKarpReport(
        type="constrained_karp_tail_jsr",
        status="finite_automaton_constrained_karp_diagnostic",
        construction=(
            "Product graph equals the LTE-closed tail graph crossed with a "
            "finite balanced-word phase automaton. Edge labels are exact "
            "integer numerator/denominator growth factors, and Karp is run on "
            "their log2 weights."
        ),
        caveat=(
            "The balanced-word automaton is period-capped, so this is a bounded "
            "finite diagnostic rather than a global statement."
        ),
        levels=tuple(report_levels),
    )


def _expand_sweep_values[T](
    values: tuple[T, ...] | None,
    default_factory,
    count: int,
    name: str,
) -> tuple[T, ...]:
    if values is None:
        return tuple(default_factory(index) for index in range(count))
    if len(values) == 1:
        return values * count
    if len(values) != count:
        raise ValueError(f"{name} must have length 1 or match levels")
    return values


def _karp_slope_sweep_survivor(
    cycle,
    target_slope: float,
) -> KarpSlopeSweepSurvivor:
    slope = christoffel_slope(cycle.parity_word)
    slope_value = float(slope)
    return KarpSlopeSweepSurvivor(
        cycle_edges=cycle.cycle_edges,
        accelerated_steps=cycle.accelerated_steps,
        edge_factor=cycle.edge_factor,
        edge_mean_log2_slope=cycle.edge_mean_log2_slope,
        christoffel_slope=f"{slope.numerator}/{slope.denominator}",
        slope_distance=abs(slope_value - target_slope),
        non_elementary=cycle.cycle_edges > 1,
        valuation_word=cycle.valuation_word,
        parity_word=cycle.parity_word,
    )


def karp_slope_joint_sweep_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6)),
    max_valuation: int = 12,
    max_imbalance: int = 1,
    automaton_max_periods: tuple[int, ...] | None = None,
    slope_tolerances: tuple[float, ...] | None = None,
    max_cycle_edges: int = 10,
    max_cycles_scanned: int = 200_000,
    target_slope: float = LOG2_3,
    deferred_levels: tuple[dict[str, Any], ...] = (),
) -> KarpSlopeJointSweepReport:
    """Jointly widen the balanced automaton and scan the slope window.

    The sweep stops after the first bounded upper-Christoffel survivor whose
    product-graph period is non-elementary and whose cycle-mean factor is at
    least one.  The triggering level is retained in the report.
    """

    periods = _expand_sweep_values(
        automaton_max_periods,
        lambda index: 4 + index,
        len(levels),
        "automaton_max_periods",
    )
    tolerances = _expand_sweep_values(
        slope_tolerances,
        lambda _index: 0.5,
        len(levels),
        "slope_tolerances",
    )
    report_levels: list[KarpSlopeJointSweepLevel] = []
    obstruction: KarpSlopeSweepObstruction | None = None

    for level_index, ((q, max_tail_depth), period, tolerance) in enumerate(
        zip(levels, periods, tolerances, strict=True)
    ):
        automaton = BalancedWordAutomaton(
            max_imbalance=max_imbalance,
            max_period=period,
        )
        tail_graph = lte_closed_tail_graph(q, max_tail_depth, max_valuation)
        graph = product_graph(tail_graph, automaton)
        karp = constrained_karp_jsr(graph)
        slope_level = _christoffel_filtered_level(
            tail_unit_power=q,
            max_tail_depth=max_tail_depth,
            max_valuation=max_valuation,
            max_cycle_edges=max_cycle_edges,
            max_cycles_scanned=max_cycles_scanned,
            top_n=max_cycles_scanned,
        )
        survivors = tuple(
            _karp_slope_sweep_survivor(cycle, target_slope)
            for cycle in slope_level.top_unfiltered_cycles
            if is_upper_christoffel_conjugate(cycle.parity_word)
            and abs(float(christoffel_slope(cycle.parity_word)) - target_slope)
            <= tolerance
        )
        non_elementary_bad = tuple(
            survivor
            for survivor in survivors
            if survivor.non_elementary and survivor.edge_factor >= 1.0
        )
        cycle_cap_reached = slope_level.status == "cycle_scan_hit_cap_bounded_diagnostic"
        scan_completion_status = (
            "cycle_cap_reached"
            if cycle_cap_reached
            else "bounded_simple_cycle_scan_complete_for_depth_cap"
        )
        if non_elementary_bad and obstruction is None:
            obstruction = KarpSlopeSweepObstruction(
                level_index=level_index,
                tail_unit_power=q,
                max_tail_depth=max_tail_depth,
                automaton_max_period=period,
                slope_tolerance=tolerance,
                survivor=non_elementary_bad[0],
            )

        report_levels.append(
            KarpSlopeJointSweepLevel(
                level_index=level_index,
                tail_unit_power=q,
                max_tail_depth=max_tail_depth,
                max_valuation=max_valuation,
                max_imbalance=max_imbalance,
                automaton_max_period=period,
                slope_target=target_slope,
                slope_tolerance=tolerance,
                tail_states=len(tail_graph.states),
                tail_edges=len(tail_graph.edges),
                closed_overflow_edges=tail_graph.closed_overflow_edges,
                automaton_patterns=automaton.pattern_count,
                automaton_states=automaton.state_count,
                product_states=graph.states,
                product_edges=len(graph.edges),
                constrained_karp_factor=karp.constrained_factor,
                exact_rational_factor=karp.exact_rational_factor,
                cycles_scanned=slope_level.cycles_scanned,
                max_cycle_edges=max_cycle_edges,
                max_cycles_scanned=max_cycles_scanned,
                survivor_count=len(survivors),
                non_elementary_survivor_count=sum(
                    1 for survivor in survivors if survivor.non_elementary
                ),
                non_elementary_factor_ge_one=bool(non_elementary_bad),
                survivors=survivors,
                status=(
                    "obstruction_found_non_elementary_factor_ge_one"
                    if non_elementary_bad
                    else scan_completion_status
                ),
                cycle_cap_reached=cycle_cap_reached,
                scan_completion_status=scan_completion_status,
            )
        )
        if obstruction is not None:
            break

    return KarpSlopeJointSweepReport(
        type="karp_slope_joint_sweep",
        status=(
            "obstruction_found_non_elementary_factor_ge_one"
            if obstruction is not None
            else "no_non_elementary_factor_ge_one_survivor_found"
        ),
        construction=(
            "For each (q,Rmax), Karp is run on the LTE-closed tail graph "
            "crossed with a period-capped balanced-word automaton, while the "
            "same tail graph is scanned for bounded upper-Christoffel cycles "
            "inside the configured slope window."
        ),
        caveat=(
            "Cycle survivors are complete only for the bounded simple-cycle "
            "scan up to max_cycle_edges and max_cycles_scanned. The slope "
            "window is a finite diagnostic; it is not a full Hercher "
            "parity-vector theorem."
        ),
        levels=tuple(report_levels),
        obstruction=obstruction,
        next_step=(
            "If obstruction is null, widen both the automaton period cap and "
            "cycle-edge cap. If obstruction is present, inspect that survivor "
            "as the new finite-to-infinite bridge obstruction."
        ),
        deferred_levels=deferred_levels,
        scan_policy={
            "max_cycle_edges": max_cycle_edges,
            "max_cycles_scanned": max_cycles_scanned,
            "max_valuation": max_valuation,
            "cycle_cap_status_values": [
                "bounded_simple_cycle_scan_complete_for_depth_cap",
                "cycle_cap_reached",
            ],
        },
    )


def _merge_counts(
    left: dict[str, int],
    right: dict[str, int],
) -> dict[str, int]:
    merged = dict(left)
    for key, value in right.items():
        merged[key] = merged.get(key, 0) + value
    return merged


def _cycle_value_when_integer(value) -> str | None:
    if value.denominator != 1:
        return None
    return str(value.numerator)


def _tail_cycle_realizability_cycle(
    cycle,
    tail_unit_power: int,
    target_slope: float,
    slope_tolerance: float,
    lift_max_scan_power: int,
    check_closure: bool = True,
    classification=None,
) -> TailCycleRealizabilityCycle:
    slope = christoffel_slope(cycle.parity_word)
    slope_value = float(slope)
    if classification is None:
        classification = classify_cycle_word(cycle.valuation_word)
    cylinder_power = sum(cycle.valuation_word) + 1
    closure_precision_power = max(
        cylinder_power,
        tail_unit_power + sum(cycle.valuation_word) + 1,
    )
    cylinder_residue_count: int | None = None
    closes_mod_power_count: int | None = None
    lift_audit_status = "cylinder_closure_not_requested"
    if check_closure:
        lift_audit_status = "cylinder_closure_counted"
        try:
            cylinder_residue_count = len(
                word_cylinder_residues(
                    cycle.valuation_word,
                    precision_power=cylinder_power,
                    max_scan_power=lift_max_scan_power,
                )
            )
            closes_mod_power_count = len(
                exact_word_closures_mod_power(
                    cycle.valuation_word,
                    modulus_power=tail_unit_power,
                    precision_power=closure_precision_power,
                    max_scan_power=lift_max_scan_power,
                )
            )
        except ValueError as exc:
            lift_audit_status = f"cylinder_closure_skipped: {exc}"

    in_slope_window = (
        is_upper_christoffel_conjugate(cycle.parity_word)
        and abs(slope_value - target_slope) <= slope_tolerance
    )
    return TailCycleRealizabilityCycle(
        valuation_word=cycle.valuation_word,
        parity_word=cycle.parity_word,
        edge_factor=cycle.edge_factor,
        edge_mean_log2_slope=cycle.edge_mean_log2_slope,
        graph_cycle_edges=cycle.cycle_edges,
        period=len(cycle.valuation_word),
        christoffel_slope=f"{slope.numerator}/{slope.denominator}",
        slope_distance=abs(slope_value - target_slope),
        in_slope_window=in_slope_window,
        lift_classification=classification.kind,
        cycle_value=_cycle_value_when_integer(classification.value),
        cylinder_power=cylinder_power,
        closure_precision_power=closure_precision_power,
        cylinder_residue_count=cylinder_residue_count,
        closes_mod_power_count=closes_mod_power_count,
        lift_audit_status=lift_audit_status,
    )


def _tail_cycle_realizability_level(
    level_index: int,
    q: int,
    max_tail_depth: int,
    max_valuation: int,
    max_cycle_edges: int,
    max_cycles_scanned: int,
    factor_threshold: float,
    target_slope: float,
    slope_tolerance: float,
    lift_max_scan_power: int,
    audit_all_cycles: bool,
) -> TailCycleRealizabilityLevel:
    tail_graph = lte_closed_tail_graph(q, max_tail_depth, max_valuation)
    scanned = _christoffel_filtered_level(
        tail_unit_power=q,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
        top_n=max_cycles_scanned,
    )
    source_cycles = (
        scanned.top_unfiltered_cycles
        if audit_all_cycles
        else tuple(
            cycle
            for cycle in scanned.top_unfiltered_cycles
            if cycle.edge_factor >= factor_threshold
        )
    )
    counts: dict[str, int] = {}
    recorded: list[TailCycleRealizabilityCycle] = []
    realizable_karp_cycle: TailCycleRealizabilityCycle | None = None
    high_growth_cycles = 0
    in_slope_window_count = 0
    closure_skipped_count = 0
    for cycle in source_cycles:
        classification = classify_cycle_word(cycle.valuation_word)
        counts[classification.kind] = counts.get(classification.kind, 0) + 1
        high_growth = cycle.edge_factor >= factor_threshold
        if high_growth:
            high_growth_cycles += 1
        should_record = high_growth or classification.kind == "positive_integer_cycle"
        if not should_record and audit_all_cycles:
            continue
        audited = _tail_cycle_realizability_cycle(
            cycle,
            q,
            target_slope,
            slope_tolerance,
            lift_max_scan_power,
            check_closure=should_record,
            classification=classification,
        )
        if audited.in_slope_window:
            in_slope_window_count += 1
        if audited.lift_audit_status.startswith("cylinder_closure_skipped"):
            closure_skipped_count += 1
        if classification.kind == "positive_integer_cycle" and (
            realizable_karp_cycle is None
            or audited.edge_factor > realizable_karp_cycle.edge_factor
        ):
            realizable_karp_cycle = audited
        recorded.append(audited)
    cycle_cap_reached = scanned.status == "cycle_scan_hit_cap_bounded_diagnostic"
    scan_completion_status = (
        "cycle_cap_reached"
        if cycle_cap_reached
        else "bounded_simple_cycle_scan_complete_for_depth_cap"
    )
    return TailCycleRealizabilityLevel(
        level_index=level_index,
        tail_unit_power=q,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        tail_states=len(tail_graph.states),
        tail_edges=len(tail_graph.edges),
        closed_overflow_edges=tail_graph.closed_overflow_edges,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
        cycles_scanned=scanned.cycles_scanned,
        audited_cycles=len(source_cycles),
        recorded_cycles=len(recorded),
        factor_threshold=factor_threshold,
        slope_target=target_slope,
        slope_tolerance=slope_tolerance,
        high_growth_cycles=high_growth_cycles,
        classification_counts=counts,
        in_slope_window_count=in_slope_window_count,
        closure_skipped_count=closure_skipped_count,
        realizable_karp_factor=(
            None if realizable_karp_cycle is None else realizable_karp_cycle.edge_factor
        ),
        realizable_karp_cycle=realizable_karp_cycle,
        cycles=tuple(recorded),
        status=scan_completion_status,
        cycle_cap_reached=cycle_cap_reached,
        scan_completion_status=scan_completion_status,
    )


def tail_cycle_realizability_report(
    q: int,
    Rmax: int,
    *,
    max_cycle_edges: int,
    max_cycles_scanned: int,
    factor_threshold: float = 1.0,
    max_valuation: int = 12,
    target_slope: float = LOG2_3,
    slope_tolerance: float = 0.5,
    lift_max_scan_power: int = 24,
    audit_all_cycles: bool = False,
    deferred_levels: tuple[dict[str, Any], ...] = (),
) -> TailCycleRealizabilityReport:
    """Audit high-growth LTE-closed tail cycles against exact word lifting."""

    return tail_cycle_realizability_sweep_report(
        levels=((q, Rmax),),
        max_valuation=max_valuation,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
        factor_threshold=factor_threshold,
        target_slope=target_slope,
        slope_tolerance=slope_tolerance,
        lift_max_scan_power=lift_max_scan_power,
        audit_all_cycles=audit_all_cycles,
        deferred_levels=deferred_levels,
    )


def tail_cycle_realizability_sweep_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6)),
    max_valuation: int = 12,
    max_cycle_edges: int = 10,
    max_cycles_scanned: int = 200_000,
    factor_threshold: float = 1.0,
    target_slope: float = LOG2_3,
    slope_tolerance: float = 0.5,
    lift_max_scan_power: int = 24,
    audit_all_cycles: bool = False,
    deferred_levels: tuple[dict[str, Any], ...] = (),
) -> TailCycleRealizabilityReport:
    """Finite audit of whether high-growth tail cycles lift to integer cycles."""

    report_levels: list[TailCycleRealizabilityLevel] = []
    classification_counts: dict[str, int] = {}
    obstruction: TailCycleRealizabilityObstruction | None = None
    for level_index, (q, max_tail_depth) in enumerate(levels):
        level = _tail_cycle_realizability_level(
            level_index=level_index,
            q=q,
            max_tail_depth=max_tail_depth,
            max_valuation=max_valuation,
            max_cycle_edges=max_cycle_edges,
            max_cycles_scanned=max_cycles_scanned,
            factor_threshold=factor_threshold,
            target_slope=target_slope,
            slope_tolerance=slope_tolerance,
            lift_max_scan_power=lift_max_scan_power,
            audit_all_cycles=audit_all_cycles,
        )
        report_levels.append(level)
        classification_counts = _merge_counts(
            classification_counts,
            level.classification_counts,
        )
        if obstruction is None:
            for cycle in level.cycles:
                if (
                    cycle.lift_classification == "positive_integer_cycle"
                    and cycle.edge_factor >= factor_threshold
                ):
                    obstruction = TailCycleRealizabilityObstruction(
                        level_index=level_index,
                        tail_unit_power=q,
                        max_tail_depth=max_tail_depth,
                        cycle=cycle,
                    )
                    break
    realizable_karp_cycle: TailCycleRealizabilityObstruction | None = None
    for level in report_levels:
        if level.realizable_karp_cycle is None:
            continue
        if (
            realizable_karp_cycle is None
            or level.realizable_karp_cycle.edge_factor
            > realizable_karp_cycle.cycle.edge_factor
        ):
            realizable_karp_cycle = TailCycleRealizabilityObstruction(
                level_index=level.level_index,
                tail_unit_power=level.tail_unit_power,
                max_tail_depth=level.max_tail_depth,
                cycle=level.realizable_karp_cycle,
            )

    return TailCycleRealizabilityReport(
        type="tail_cycle_realizability",
        status=(
            "positive_integer_high_growth_obstruction_found"
            if obstruction is not None
            else "no_positive_integer_high_growth_cycle_found"
        ),
        construction=(
            "Simple cycles are enumerated in the LTE-closed tail graph. Cycles "
            "with edge factor at least factor_threshold are classified by the "
            "exact accelerated-word lift equation and, when feasible, checked "
            "against finite word-cylinder closure counts."
        ),
        caveat=(
            "This is a finite diagnostic bounded by max_cycle_edges, "
            "max_cycles_scanned, max_valuation, and the lift scan precision. "
            "It does not prove Collatz descent or general realizability of the "
            "slope filter."
        ),
        levels=tuple(report_levels),
        classification_counts=classification_counts,
        realizable_karp_factor=(
            None
            if realizable_karp_cycle is None
            else realizable_karp_cycle.cycle.edge_factor
        ),
        realizable_karp_cycle=realizable_karp_cycle,
        obstruction=obstruction,
        deferred_levels=deferred_levels,
        scan_policy={
            "max_cycle_edges": max_cycle_edges,
            "max_cycles_scanned": max_cycles_scanned,
            "max_valuation": max_valuation,
            "factor_threshold": factor_threshold,
            "lift_max_scan_power": lift_max_scan_power,
            "audit_all_cycles": audit_all_cycles,
            "cycle_cap_status_values": [
                "bounded_simple_cycle_scan_complete_for_depth_cap",
                "cycle_cap_reached",
            ],
        },
    )
