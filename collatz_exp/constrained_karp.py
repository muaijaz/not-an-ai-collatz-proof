"""Automaton-constrained Karp diagnostics on the LTE-closed tail graph."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import gcd, log2
from typing import Any

from .christoffel import (
    is_christoffel_compatible,
    valuation_word_to_parity_bits,
)
from .constrained_jsr import TailAwareProjectiveEdge, _tail_aware_edges
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
