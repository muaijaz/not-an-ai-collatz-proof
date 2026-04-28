"""Constrained matrix-product diagnostics on legal residue transitions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log2
from typing import Any

from .christoffel import (
    is_christoffel_compatible,
    valuation_word_to_parity_bits,
)
from .core import accelerated_step, v2
from .cycles import classify_cycle_word
from .max_plus import _karp_max_cycle_mean


@dataclass(frozen=True)
class LegalResidueEdge:
    source: int
    target: int
    valuation: int
    witness: int
    slope_log2: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstrainedJSRReport:
    type: str
    status: str
    modulus_power: int
    max_valuation: int
    states: int
    edges: int
    max_cycle_mean_log2_slope: float | None
    witness_residue: int | None
    all_one_self_loop_detected: bool
    top_edges: tuple[LegalResidueEdge, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["top_edges"] = [edge.to_json_dict() for edge in self.top_edges]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailFilteredProjectiveJSR:
    tail_depth_cutoff: int
    states: int
    edges: int
    max_cycle_mean_log2_slope: float | None
    affine_quotient_jsr: float | None
    witness_residue: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstrainedProjectiveJSRLevel:
    modulus_power: int
    max_valuation: int
    states: int
    edges: int
    affine_quotient_jsr_lower: float | None
    affine_quotient_jsr_upper: float | None
    max_cycle_mean_log2_slope: float | None
    homogeneous_jsr_lower: float | None
    homogeneous_jsr_upper: float | None
    witness_residue: int | None
    obstruction_word: tuple[int, ...]
    obstruction_kind: str
    obstruction_value: str
    obstruction_note: str
    tail_filtered: tuple[TailFilteredProjectiveJSR, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["tail_filtered"] = [
            item.to_json_dict() for item in self.tail_filtered
        ]
        return data


@dataclass(frozen=True)
class ConstrainedProjectiveJSRReport:
    type: str
    status: str
    levels: tuple[ConstrainedProjectiveJSRLevel, ...]
    scalar_certificate_note: str
    homogeneous_caveat: str
    next_step: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "levels": [level.to_json_dict() for level in self.levels],
            "scalar_certificate_note": self.scalar_certificate_note,
            "homogeneous_caveat": self.homogeneous_caveat,
            "next_step": self.next_step,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailAwareProjectiveEdge:
    source_tail_depth: int
    source_unit_residue: int
    target_tail_depth: int
    target_unit_residue: int
    valuation: int
    accelerated_steps: int
    witness_count: int
    slope_log2: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailAwareProjectiveJSRLevel:
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    states: int
    edges: int
    overflow_edges: int
    closed_overflow_edges: int
    all_one_self_loop_detected: bool
    max_cycle_mean_log2_slope: float | None
    affine_quotient_jsr: float | None
    witness_tail_depth: int | None
    witness_unit_residue: int | None
    top_edges: tuple[TailAwareProjectiveEdge, ...]
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["top_edges"] = [edge.to_json_dict() for edge in self.top_edges]
        return data


@dataclass(frozen=True)
class TailAwareProjectiveJSRReport:
    type: str
    status: str
    coordinate_model: str
    finite_model_caveat: str
    levels: tuple[TailAwareProjectiveJSRLevel, ...]
    next_step: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "coordinate_model": self.coordinate_model,
            "finite_model_caveat": self.finite_model_caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "next_step": self.next_step,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailAwareMarkovComponent:
    component_index: int
    states: int
    average_block_log2_growth: float
    average_accelerated_steps: float
    average_log2_growth_per_accelerated_step: float
    typical_factor_per_accelerated_step: float
    stationary_iterations: int
    stationary_residual_l1: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TailAwareMarkovLyapunovLevel:
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    states: int
    edges: int
    closed_overflow_edges: int
    row_weight_min: int
    row_weight_max: int
    recurrent_components: int
    largest_recurrent_component_states: int
    worst_case_jsr_factor: float | None
    worst_case_log2_slope: float | None
    largest_component_average_block_log2_growth: float
    largest_component_average_accelerated_steps: float
    largest_component_average_log2_growth_per_accelerated_step: float
    largest_component_typical_factor_per_accelerated_step: float
    components: tuple[TailAwareMarkovComponent, ...]
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["components"] = [
            component.to_json_dict() for component in self.components
        ]
        return data


@dataclass(frozen=True)
class TailAwareMarkovLyapunovReport:
    type: str
    status: str
    probability_model: str
    caveat: str
    levels: tuple[TailAwareMarkovLyapunovLevel, ...]
    interpretation: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "probability_model": self.probability_model,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "interpretation": self.interpretation,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ChristoffelFilteredCycle:
    cycle_edges: int
    accelerated_steps: int
    valuation_sum: int
    parity_length: int
    parity_ones: int
    edge_mean_log2_slope: float
    step_mean_log2_slope: float
    edge_factor: float
    step_factor: float
    christoffel_compatible: bool
    start_tail_depth: int
    start_unit_residue: int
    valuation_word: tuple[int, ...]
    parity_word: tuple[int, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChristoffelFilteredJSRLevel:
    tail_unit_power: int
    max_tail_depth: int
    max_valuation: int
    states: int
    edges: int
    closed_overflow_edges: int
    max_cycle_edges: int
    max_cycles_scanned: int
    cycles_scanned: int
    christoffel_compatible_cycles: int
    exact_karp_log2_slope: float | None
    exact_karp_factor: float | None
    enumerated_unfiltered_best_log2_slope: float | None
    enumerated_unfiltered_best_factor: float | None
    christoffel_filtered_best_log2_slope: float | None
    christoffel_filtered_best_factor: float | None
    top_unfiltered_cycles: tuple[ChristoffelFilteredCycle, ...]
    top_christoffel_cycles: tuple[ChristoffelFilteredCycle, ...]
    status: str

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["top_unfiltered_cycles"] = [
            cycle.to_json_dict() for cycle in self.top_unfiltered_cycles
        ]
        data["top_christoffel_cycles"] = [
            cycle.to_json_dict() for cycle in self.top_christoffel_cycles
        ]
        return data


@dataclass(frozen=True)
class ChristoffelFilteredJSRReport:
    type: str
    status: str
    filter_model: str
    caveat: str
    levels: tuple[ChristoffelFilteredJSRLevel, ...]
    interpretation: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "filter_model": self.filter_model,
            "caveat": self.caveat,
            "levels": [level.to_json_dict() for level in self.levels],
            "interpretation": self.interpretation,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def affine_step_matrix(valuation: int) -> tuple[tuple[int, int], tuple[int, int]]:
    if valuation < 1:
        raise ValueError("valuation must be positive")
    return ((3, 1), (0, 1 << valuation))


def legal_residue_edges(
    modulus_power: int,
    max_valuation: int,
) -> tuple[LegalResidueEdge, ...]:
    """Enumerate legal ``(source, valuation, target)`` edges exactly up to a cap."""

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    if max_valuation < 1:
        raise ValueError("max_valuation must be positive")
    modulus = 1 << modulus_power
    edge_map: dict[tuple[int, int, int], LegalResidueEdge] = {}
    for source in range(1, modulus, 2):
        for valuation in range(1, max_valuation + 1):
            for lift in range(1 << valuation):
                witness = source + (lift << modulus_power)
                landing, actual = accelerated_step(witness)
                if actual != valuation:
                    continue
                target = landing % modulus
                key = (source, target, valuation)
                edge_map.setdefault(
                    key,
                    LegalResidueEdge(
                        source=source,
                        target=target,
                        valuation=valuation,
                        witness=witness,
                        slope_log2=log2(3) - valuation,
                    ),
                )
    return tuple(sorted(edge_map.values(), key=lambda edge: (edge.source, edge.target, edge.valuation)))


def legal_word_closes(
    word: tuple[int, ...],
    modulus_power: int,
) -> bool:
    """Return whether a valuation word labels a closed path modulo ``2^k``."""

    if not word:
        return True
    edges = legal_residue_edges(modulus_power, max(word))
    by_source_value: dict[tuple[int, int], set[int]] = {}
    for edge in edges:
        by_source_value.setdefault((edge.source, edge.valuation), set()).add(edge.target)
    modulus = 1 << modulus_power
    for start in range(1, modulus, 2):
        states = {start}
        for valuation in word:
            next_states: set[int] = set()
            for state in states:
                next_states.update(by_source_value.get((state, valuation), ()))
            states = next_states
            if not states:
                break
        if start in states:
            return True
    return False


def constrained_jsr_report(
    modulus_power: int = 6,
    max_valuation: int = 10,
    top_n: int = 8,
) -> ConstrainedJSRReport:
    edges = legal_residue_edges(modulus_power, max_valuation)
    residues = tuple(range(1, 1 << modulus_power, 2))
    index = {residue: i for i, residue in enumerate(residues)}
    weighted_edges = tuple(
        (index[edge.source], index[edge.target], edge.slope_log2)
        for edge in edges
    )
    result = _karp_max_cycle_mean(len(residues), weighted_edges)
    mean = None if result is None else result[0]
    witness = None if result is None else residues[result[1]]
    top_edges = tuple(
        sorted(
            edges,
            key=lambda edge: (edge.slope_log2, -edge.valuation, edge.source),
            reverse=True,
        )[:top_n]
    )
    return ConstrainedJSRReport(
        type="constrained_residue_jsr_cycle_mean",
        status="finite_valuation_truncated_jsr_diagnostic_not_proof",
        modulus_power=modulus_power,
        max_valuation=max_valuation,
        states=len(residues),
        edges=len(edges),
        max_cycle_mean_log2_slope=mean,
        witness_residue=witness,
        all_one_self_loop_detected=any(
            edge.valuation == 1 and edge.source == edge.target for edge in edges
        ),
        top_edges=top_edges,
    )


def _max_cycle_mean_for_edges(
    residues: tuple[int, ...],
    edges: tuple[LegalResidueEdge, ...],
) -> tuple[float | None, int | None]:
    index = {residue: i for i, residue in enumerate(residues)}
    weighted_edges = tuple(
        (index[edge.source], index[edge.target], edge.slope_log2)
        for edge in edges
        if edge.source in index and edge.target in index
    )
    result = _karp_max_cycle_mean(len(residues), weighted_edges)
    if result is None:
        return None, None
    mean, state = result
    return mean, residues[state]


def _projective_jsr_level(
    modulus_power: int,
    max_valuation: int,
    tail_depth_cutoffs: tuple[int, ...],
) -> ConstrainedProjectiveJSRLevel:
    edges = legal_residue_edges(modulus_power, max_valuation)
    residues = tuple(range(1, 1 << modulus_power, 2))
    mean, witness = _max_cycle_mean_for_edges(residues, edges)
    affine_jsr = None if mean is None else 2.0**mean
    homogeneous = None if affine_jsr is None else max(1.0, affine_jsr)
    tail_filtered: list[TailFilteredProjectiveJSR] = []
    for cutoff in tail_depth_cutoffs:
        filtered_residues = tuple(
            residue for residue in residues if v2(residue + 1) < cutoff
        )
        filtered_edges = tuple(
            edge
            for edge in edges
            if edge.source in filtered_residues and edge.target in filtered_residues
        )
        filtered_mean, filtered_witness = _max_cycle_mean_for_edges(
            filtered_residues, filtered_edges
        )
        tail_filtered.append(
            TailFilteredProjectiveJSR(
                tail_depth_cutoff=cutoff,
                states=len(filtered_residues),
                edges=len(filtered_edges),
                max_cycle_mean_log2_slope=filtered_mean,
                affine_quotient_jsr=(
                    None if filtered_mean is None else 2.0**filtered_mean
                ),
                witness_residue=filtered_witness,
            )
        )
    obstruction = classify_cycle_word((1,))
    return ConstrainedProjectiveJSRLevel(
        modulus_power=modulus_power,
        max_valuation=max_valuation,
        states=len(residues),
        edges=len(edges),
        affine_quotient_jsr_lower=affine_jsr,
        affine_quotient_jsr_upper=affine_jsr,
        max_cycle_mean_log2_slope=mean,
        homogeneous_jsr_lower=homogeneous,
        homogeneous_jsr_upper=homogeneous,
        witness_residue=witness,
        obstruction_word=obstruction.word,
        obstruction_kind=obstruction.kind,
        obstruction_value=str(obstruction.value),
        obstruction_note=(
            "The exact finite residue quotient is maximized by the Mersenne-tail "
            "2-adic loop word (1), whose cycle value is n=-1. This is a real "
            "obstruction to naive finite residue JSR, not a positive integer cycle."
        ),
        tail_filtered=tuple(tail_filtered),
    )


def constrained_projective_jsr_report(
    modulus_powers: tuple[int, ...] = (4, 6, 8, 10),
    max_valuation: int = 16,
    tail_depth_cutoffs: tuple[int, ...] = (2, 3, 4, 5, 6, 8),
) -> ConstrainedProjectiveJSRReport:
    """Exact scalar/projective JSR on finite legal-residue quotients.

    The orbit-size quotient of the normalized affine matrices is scalar:
    each edge contributes ``log2(3)-a``.  Therefore the optimal finite
    constrained scalar JSR is exactly the max-plus cycle mean; the lower and
    upper bounds coincide on this finite quotient.  This intentionally does not
    solve the full positive-integer problem because the quotient still contains
    the negative 2-adic Mersenne loop.
    """

    return ConstrainedProjectiveJSRReport(
        type="constrained_projective_jsr",
        status="finite_scalar_quotient_exact_but_tail_obstructed_not_collatz_proof",
        levels=tuple(
            _projective_jsr_level(power, max_valuation, tail_depth_cutoffs)
            for power in modulus_powers
        ),
        scalar_certificate_note=(
            "For the affine-size quotient, the matrix product reduces to the "
            "scalar product of 3/2^a. Karp max-cycle-mean gives matching lower "
            "and upper bounds for each finite legal-residue graph."
        ),
        homogeneous_caveat=(
            "The full homogeneous triangular matrices always have an invariant "
            "constant coordinate, so their JSR is at least 1. Descent-relevant "
            "claims must be made on the affine-size quotient or another "
            "projectivized/renormalized coordinate."
        ),
        next_step=(
            "Replace the naive residue quotient by a tail-aware state space that "
            "tracks v2(n+1) through the Mersenne manifold, so the negative "
            "2-adic n=-1 loop cannot masquerade as a positive orbit cycle."
        ),
    )


def _tail_aware_edges(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
) -> tuple[tuple[TailAwareProjectiveEdge, ...], int, int]:
    """Enumerate witnessed edges in ``n = 2^R u - 1`` coordinates.

    The quotient state is ``(R, u mod 2^q)`` with ``u`` odd.  For ``R >= 2``
    the next valuation is exactly one and ``R`` drops by one.  For ``R = 1``
    the post-exit jump is resolved exactly as long as the resulting tail depth
    is visible below ``2^q``; jumps deeper than ``max_tail_depth`` are counted
    as overflow exits rather than folded into a fake cycle.
    """

    if tail_unit_power < 2:
        raise ValueError("tail_unit_power must be at least two")
    if max_tail_depth < 1:
        raise ValueError("max_tail_depth must be positive")
    if max_tail_depth >= tail_unit_power:
        raise ValueError("max_tail_depth must be smaller than tail_unit_power")
    if max_valuation < 2:
        raise ValueError("max_valuation must be at least two")

    modulus = 1 << tail_unit_power
    odd_units = tuple(range(1, modulus, 2))
    edge_counts: dict[
        tuple[int, int, int, int, int, int, float],
        int,
    ] = {}
    overflow_edges = 0
    closed_overflow_edges = 0

    def add_edge(
        source_tail: int,
        source_unit: int,
        target_tail: int,
        target_unit: int,
        total_valuation: int,
        accelerated_steps: int,
        slope: float,
        count: int = 1,
    ) -> None:
        key = (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            total_valuation,
            accelerated_steps,
            slope,
        )
        edge_counts[key] = edge_counts.get(key, 0) + count

    def add_post_exit_edge(
        source_unit: int,
        landing: int,
        first_valuation: int,
    ) -> None:
        nonlocal overflow_edges, closed_overflow_edges
        target_tail = v2(landing + 1)
        target_unit = ((landing + 1) >> target_tail) % modulus
        accelerated_steps = 1
        total_valuation = first_valuation
        if target_tail > max_tail_depth:
            forced_steps = target_tail - max_tail_depth
            target_unit = (target_unit * pow(3, forced_steps, modulus)) % modulus
            target_tail = max_tail_depth
            accelerated_steps += forced_steps
            total_valuation += forced_steps
            closed_overflow_edges += 1
        slope = accelerated_steps * log2(3) - total_valuation
        add_edge(
            1,
            source_unit,
            target_tail,
            target_unit,
            total_valuation,
            accelerated_steps,
            slope,
        )

    for tail_depth in range(2, max_tail_depth + 1):
        for unit in odd_units:
            add_edge(
                tail_depth,
                unit,
                tail_depth - 1,
                (3 * unit) % modulus,
                1,
                1,
                log2(3) - 1,
            )

    for unit in odd_units:
        base = 3 * unit - 1
        if base % modulus != 0:
            exponent = v2(base)
            if exponent + 1 > max_valuation:
                continue
            for lift in range(1 << exponent):
                lifted_unit = unit + (lift << tail_unit_power)
                landing = (3 * lifted_unit - 1) >> exponent
                add_post_exit_edge(unit, landing, exponent + 1)
            continue

        for exponent in range(tail_unit_power, max_valuation):
            for lift in range(1 << exponent):
                lifted_unit = unit + (lift << tail_unit_power)
                if v2(3 * lifted_unit - 1) != exponent:
                    continue
                landing = (3 * lifted_unit - 1) >> exponent
                add_post_exit_edge(unit, landing, exponent + 1)

    edges = tuple(
        TailAwareProjectiveEdge(
            source_tail_depth=source_tail,
            source_unit_residue=source_unit,
            target_tail_depth=target_tail,
            target_unit_residue=target_unit,
            valuation=valuation,
            accelerated_steps=accelerated_steps,
            witness_count=count,
            slope_log2=slope,
        )
        for (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            valuation,
            accelerated_steps,
            slope,
        ), count in sorted(edge_counts.items())
    )
    return edges, overflow_edges, closed_overflow_edges


def _tail_aware_edges_open(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
) -> tuple[tuple[TailAwareProjectiveEdge, ...], int, int]:
    """Legacy open version: count deeper-tail jumps as exits."""

    if tail_unit_power < 2:
        raise ValueError("tail_unit_power must be at least two")
    if max_tail_depth < 1:
        raise ValueError("max_tail_depth must be positive")
    if max_tail_depth >= tail_unit_power:
        raise ValueError("max_tail_depth must be smaller than tail_unit_power")
    if max_valuation < 2:
        raise ValueError("max_valuation must be at least two")

    modulus = 1 << tail_unit_power
    odd_units = tuple(range(1, modulus, 2))
    edge_counts: dict[tuple[int, int, int, int, int, int, float], int] = {}
    overflow_edges = 0

    def add_edge(
        source_tail: int,
        source_unit: int,
        target_tail: int,
        target_unit: int,
        valuation: int,
        steps: int,
        slope: float,
    ) -> None:
        key = (source_tail, source_unit, target_tail, target_unit, valuation, steps, slope)
        edge_counts[key] = edge_counts.get(key, 0) + 1

    for tail_depth in range(2, max_tail_depth + 1):
        for unit in odd_units:
            add_edge(tail_depth, unit, tail_depth - 1, (3 * unit) % modulus, 1, 1, log2(3) - 1)

    for unit in odd_units:
        base = 3 * unit - 1
        if base % modulus != 0:
            exponent = v2(base)
            if exponent + 1 > max_valuation:
                continue
            for lift in range(1 << exponent):
                lifted_unit = unit + (lift << tail_unit_power)
                landing = (3 * lifted_unit - 1) >> exponent
                target_tail = v2(landing + 1)
                if target_tail > max_tail_depth:
                    overflow_edges += 1
                    continue
                target_unit = ((landing + 1) >> target_tail) % modulus
                add_edge(1, unit, target_tail, target_unit, exponent + 1, 1, log2(3) - (exponent + 1))
            continue

        for exponent in range(tail_unit_power, max_valuation):
            for lift in range(1 << exponent):
                lifted_unit = unit + (lift << tail_unit_power)
                if v2(3 * lifted_unit - 1) != exponent:
                    continue
                landing = (3 * lifted_unit - 1) >> exponent
                target_tail = v2(landing + 1)
                if target_tail > max_tail_depth:
                    overflow_edges += 1
                    continue
                target_unit = ((landing + 1) >> target_tail) % modulus
                add_edge(1, unit, target_tail, target_unit, exponent + 1, 1, log2(3) - (exponent + 1))

    edges = tuple(
        TailAwareProjectiveEdge(
            source_tail_depth=source_tail,
            source_unit_residue=source_unit,
            target_tail_depth=target_tail,
            target_unit_residue=target_unit,
            valuation=valuation,
            accelerated_steps=steps,
            witness_count=count,
            slope_log2=slope,
        )
        for (
            source_tail,
            source_unit,
            target_tail,
            target_unit,
            valuation,
            steps,
            slope,
        ), count in sorted(edge_counts.items())
    )
    return edges, overflow_edges, 0


def _tail_aware_level(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    top_n: int,
    close_overflow: bool,
) -> TailAwareProjectiveJSRLevel:
    edge_builder = _tail_aware_edges if close_overflow else _tail_aware_edges_open
    edges, overflow_edges, closed_overflow_edges = edge_builder(
        tail_unit_power, max_tail_depth, max_valuation
    )
    modulus = 1 << tail_unit_power
    odd_units = tuple(range(1, modulus, 2))
    states = tuple(
        (tail_depth, unit)
        for tail_depth in range(1, max_tail_depth + 1)
        for unit in odd_units
    )
    index = {state: offset for offset, state in enumerate(states)}
    weighted_edges = tuple(
        (
            index[(edge.source_tail_depth, edge.source_unit_residue)],
            index[(edge.target_tail_depth, edge.target_unit_residue)],
            edge.slope_log2,
        )
        for edge in edges
    )
    result = _karp_max_cycle_mean(len(states), weighted_edges)
    mean = None if result is None else result[0]
    witness = None if result is None else states[result[1]]
    top_edges = tuple(
        sorted(
            edges,
            key=lambda edge: (
                edge.slope_log2,
                edge.witness_count,
                -edge.valuation,
            ),
            reverse=True,
        )[:top_n]
    )
    return TailAwareProjectiveJSRLevel(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        states=len(states),
        edges=len(edges),
        overflow_edges=overflow_edges,
        closed_overflow_edges=closed_overflow_edges,
        all_one_self_loop_detected=any(
            edge.valuation == 1
            and edge.source_tail_depth == edge.target_tail_depth
            and edge.source_unit_residue == edge.target_unit_residue
            for edge in edges
        ),
        max_cycle_mean_log2_slope=mean,
        affine_quotient_jsr=None if mean is None else 2.0**mean,
        witness_tail_depth=None if witness is None else witness[0],
        witness_unit_residue=None if witness is None else witness[1],
        top_edges=top_edges,
        status=(
            "closed_lte_overflow_compressed_no_all_one_loop"
            if close_overflow
            else (
                "tracked_subgraph_exact_no_all_one_loop"
                if not overflow_edges
                else "tracked_subgraph_exact_with_deeper_tail_overflow_exits"
            )
        ),
    )


def tail_aware_projective_jsr_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6), (8, 6), (10, 7)),
    max_valuation: int = 12,
    top_n: int = 8,
) -> TailAwareProjectiveJSRReport:
    """Bounded tail-aware constrained product diagnostic.

    This is the first quotient that gives the Mersenne manifold its own
    coordinate instead of collapsing it to the residue ``-1``.  It is still a
    finite diagnostic: transitions that re-enter tail depth beyond ``R_max`` are
    counted as overflow exits and are not used as closed-cycle edges.
    """

    return TailAwareProjectiveJSRReport(
        type="tail_aware_projective_jsr",
        status="bounded_tail_coordinate_diagnostic_not_collatz_proof",
        coordinate_model="odd n represented as n = 2^R u - 1 with state (R, u mod 2^q)",
        finite_model_caveat=(
            "The tracked subgraph is exact for visible target depths, and it "
            "removes the artificial all-a=1 n=-1 self-loop. Edges that jump "
            "to tail depth above R_max are counted as overflow exits, so this "
            "is not yet a global upper bound on positive integer dynamics."
        ),
        levels=tuple(
            _tail_aware_level(q, max_tail_depth, max_valuation, top_n, False)
            for q, max_tail_depth in levels
        ),
        next_step=(
            "Turn overflow exits into a renormalized block transition instead "
            "of dropping them. That would make the tail-aware quotient closed "
            "and suitable for a genuine constrained product upper-bound test."
        ),
    )


def tail_aware_lte_closed_projective_jsr_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6), (8, 6), (10, 7)),
    max_valuation: int = 12,
    top_n: int = 8,
) -> TailAwareProjectiveJSRReport:
    """Tail-aware projective JSR with deeper-tail overflows compressed closed.

    If a post-exit edge lands at depth ``R'>Rmax``, the forced tail-internal
    run back to ``Rmax`` is folded into the same edge.  This uses the identity
    ``S^d(2^R u-1)=2^{R-d} 3^d u-1`` for the forced valuation-one run, with
    the exact lifted landing used to determine ``R'``.
    """

    return TailAwareProjectiveJSRReport(
        type="tail_aware_lte_closed_projective_jsr",
        status="finite_lte_overflow_closed_tail_coordinate_diagnostic_not_collatz_proof",
        coordinate_model="odd n represented as n = 2^R u - 1 with overflow R>Rmax compressed back to Rmax",
        finite_model_caveat=(
            "Overflow closure is exact for the enumerated lifted residues and "
            "valuation cap. It makes the bounded tail-coordinate graph closed "
            "under deeper-tail reentry, but it remains a finite quotient rather "
            "than a proof for all positive integers."
        ),
        levels=tuple(
            _tail_aware_level(q, max_tail_depth, max_valuation, top_n, True)
            for q, max_tail_depth in levels
        ),
        next_step=(
            "Use the closed graph as input to a Markov-weighted Lyapunov or "
            "multiple-potential certificate; worst-case JSR can remain above 1 "
            "while the stochastic/renewal operator contracts."
        ),
    )


def _strongly_connected_components(
    vertex_count: int,
    adjacency: list[list[int]],
) -> tuple[tuple[int, ...], ...]:
    visited = [False] * vertex_count
    order: list[int] = []

    def visit(vertex: int) -> None:
        visited[vertex] = True
        for target in adjacency[vertex]:
            if not visited[target]:
                visit(target)
        order.append(vertex)

    for vertex in range(vertex_count):
        if not visited[vertex]:
            visit(vertex)

    reverse: list[list[int]] = [[] for _ in range(vertex_count)]
    for source, row in enumerate(adjacency):
        for target in row:
            reverse[target].append(source)

    component_of = [-1] * vertex_count
    components: list[list[int]] = []

    def assign(vertex: int, component_index: int) -> None:
        component_of[vertex] = component_index
        components[component_index].append(vertex)
        for source in reverse[vertex]:
            if component_of[source] == -1:
                assign(source, component_index)

    for vertex in reversed(order):
        if component_of[vertex] == -1:
            components.append([])
            assign(vertex, len(components) - 1)
    return tuple(tuple(component) for component in components)


def _stationary_component_growth(
    component_index: int,
    component: tuple[int, ...],
    edges_by_source: list[list[tuple[int, TailAwareProjectiveEdge]]],
    max_iterations: int = 20_000,
    tolerance: float = 1e-14,
) -> TailAwareMarkovComponent:
    local = {state: offset for offset, state in enumerate(component)}
    size = len(component)
    distribution = [1.0 / size for _ in range(size)]
    residual = float("inf")
    iterations = 0
    for iterations in range(1, max_iterations + 1):
        next_distribution = [0.0] * size
        for state, mass in zip(component, distribution):
            outgoing = [
                (target, edge)
                for target, edge in edges_by_source[state]
                if target in local
            ]
            total = sum(edge.witness_count for _target, edge in outgoing)
            if total <= 0:
                next_distribution[local[state]] += mass
                continue
            for target, edge in outgoing:
                next_distribution[local[target]] += mass * edge.witness_count / total
        # Lazy averaging removes harmless periodic oscillations without changing
        # the stationary measure.
        next_distribution = [
            0.5 * old + 0.5 * new
            for old, new in zip(distribution, next_distribution)
        ]
        residual = sum(
            abs(new - old) for old, new in zip(distribution, next_distribution)
        )
        distribution = next_distribution
        if residual < tolerance:
            break

    average_slope = 0.0
    average_steps = 0.0
    for state, mass in zip(component, distribution):
        outgoing = [
            (target, edge)
            for target, edge in edges_by_source[state]
            if target in local
        ]
        total = sum(edge.witness_count for _target, edge in outgoing)
        if total <= 0:
            continue
        for _target, edge in outgoing:
            probability = edge.witness_count / total
            average_slope += mass * probability * edge.slope_log2
            average_steps += mass * probability * edge.accelerated_steps
    per_step = average_slope / average_steps if average_steps > 0.0 else 0.0
    return TailAwareMarkovComponent(
        component_index=component_index,
        states=size,
        average_block_log2_growth=average_slope,
        average_accelerated_steps=average_steps,
        average_log2_growth_per_accelerated_step=per_step,
        typical_factor_per_accelerated_step=2.0**per_step,
        stationary_iterations=iterations,
        stationary_residual_l1=residual,
    )


def _tail_aware_markov_level(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
) -> TailAwareMarkovLyapunovLevel:
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
    index = {state: offset for offset, state in enumerate(states)}
    edges_by_source: list[list[tuple[int, TailAwareProjectiveEdge]]] = [
        [] for _ in states
    ]
    adjacency_sets: list[set[int]] = [set() for _ in states]
    row_weights = [0 for _ in states]
    for edge in edges:
        source = index[(edge.source_tail_depth, edge.source_unit_residue)]
        target = index[(edge.target_tail_depth, edge.target_unit_residue)]
        edges_by_source[source].append((target, edge))
        adjacency_sets[source].add(target)
        row_weights[source] += edge.witness_count
    adjacency = [sorted(row) for row in adjacency_sets]
    components = _strongly_connected_components(len(states), adjacency)
    component_of = {
        vertex: component_index
        for component_index, component in enumerate(components)
        for vertex in component
    }
    recurrent_indices: list[int] = []
    for component_index, component in enumerate(components):
        outgoing = False
        for source in component:
            for target in adjacency[source]:
                if component_of[target] != component_index:
                    outgoing = True
                    break
            if outgoing:
                break
        if not outgoing:
            recurrent_indices.append(component_index)
    recurrent_components = tuple(
        _stationary_component_growth(
            component_index,
            components[component_index],
            edges_by_source,
        )
        for component_index in recurrent_indices
    )
    largest = max(
        recurrent_components,
        key=lambda component: component.states,
        default=TailAwareMarkovComponent(
            component_index=-1,
            states=0,
            average_block_log2_growth=0.0,
            average_accelerated_steps=0.0,
            average_log2_growth_per_accelerated_step=0.0,
            typical_factor_per_accelerated_step=1.0,
            stationary_iterations=0,
            stationary_residual_l1=0.0,
        ),
    )
    jsr_level = _tail_aware_level(
        tail_unit_power,
        max_tail_depth,
        max_valuation,
        top_n=0,
        close_overflow=True,
    )
    return TailAwareMarkovLyapunovLevel(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        states=len(states),
        edges=len(edges),
        closed_overflow_edges=closed_overflow_edges,
        row_weight_min=min(row_weights),
        row_weight_max=max(row_weights),
        recurrent_components=len(recurrent_components),
        largest_recurrent_component_states=largest.states,
        worst_case_jsr_factor=jsr_level.affine_quotient_jsr,
        worst_case_log2_slope=jsr_level.max_cycle_mean_log2_slope,
        largest_component_average_block_log2_growth=largest.average_block_log2_growth,
        largest_component_average_accelerated_steps=largest.average_accelerated_steps,
        largest_component_average_log2_growth_per_accelerated_step=(
            largest.average_log2_growth_per_accelerated_step
        ),
        largest_component_typical_factor_per_accelerated_step=(
            largest.typical_factor_per_accelerated_step
        ),
        components=recurrent_components,
        status="finite_markov_stationary_measure_on_lte_closed_tail_graph",
    )


def tail_aware_markov_lyapunov_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5), (7, 6), (8, 6), (10, 7)),
    max_valuation: int = 12,
) -> TailAwareMarkovLyapunovReport:
    """Markov-weighted Lyapunov diagnostic on the LTE-closed tail graph."""

    return TailAwareMarkovLyapunovReport(
        type="tail_aware_markov_lyapunov",
        status="finite_markov_average_contracts_while_worst_case_jsr_can_grow",
        probability_model=(
            "At each finite state, outgoing LTE-closed edges are weighted by "
            "their enumerated lift counts and normalized to a row-stochastic "
            "Markov chain. Stationary averages are computed on recurrent "
            "components."
        ),
        caveat=(
            "This is a finite quotient and a lift-count model, not a theorem "
            "about all Collatz orbits. Multiple recurrent components are "
            "reported separately; the headline uses the largest component."
        ),
        levels=tuple(
            _tail_aware_markov_level(q, max_tail_depth, max_valuation)
            for q, max_tail_depth in levels
        ),
        interpretation=(
            "Compare largest_component_average_log2_growth_per_accelerated_step "
            "with the worst_case_log2_slope. A negative Markov average alongside "
            "JSR>1 is the expected typical-versus-worst-case split."
        ),
    )


def _edge_valuation_word(edge: TailAwareProjectiveEdge) -> tuple[int, ...]:
    if edge.accelerated_steps <= 1:
        return (edge.valuation,)
    first_valuation = edge.valuation - (edge.accelerated_steps - 1)
    if first_valuation < 1:
        raise ValueError("compressed edge has inconsistent valuation/step data")
    return (first_valuation,) + (1,) * (edge.accelerated_steps - 1)


def _cycle_from_edges(
    start_state: tuple[int, int],
    edges: tuple[TailAwareProjectiveEdge, ...],
) -> ChristoffelFilteredCycle:
    valuation_word = tuple(
        valuation
        for edge in edges
        for valuation in _edge_valuation_word(edge)
    )
    parity_word = valuation_word_to_parity_bits(valuation_word)
    slope = sum(edge.slope_log2 for edge in edges)
    accelerated_steps = sum(edge.accelerated_steps for edge in edges)
    edge_mean = slope / len(edges)
    step_mean = slope / accelerated_steps
    return ChristoffelFilteredCycle(
        cycle_edges=len(edges),
        accelerated_steps=accelerated_steps,
        valuation_sum=sum(valuation_word),
        parity_length=len(parity_word),
        parity_ones=sum(parity_word),
        edge_mean_log2_slope=edge_mean,
        step_mean_log2_slope=step_mean,
        edge_factor=2.0**edge_mean,
        step_factor=2.0**step_mean,
        christoffel_compatible=is_christoffel_compatible(parity_word),
        start_tail_depth=start_state[0],
        start_unit_residue=start_state[1],
        valuation_word=valuation_word,
        parity_word=parity_word,
    )


def _christoffel_filtered_level(
    tail_unit_power: int,
    max_tail_depth: int,
    max_valuation: int,
    max_cycle_edges: int,
    max_cycles_scanned: int,
    top_n: int,
) -> ChristoffelFilteredJSRLevel:
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
    index = {state: offset for offset, state in enumerate(states)}
    adjacency: list[list[tuple[int, int, TailAwareProjectiveEdge]]] = [
        [] for _ in states
    ]
    weighted_edges: list[tuple[int, int, float]] = []
    for edge_id, edge in enumerate(edges):
        source = index[(edge.source_tail_depth, edge.source_unit_residue)]
        target = index[(edge.target_tail_depth, edge.target_unit_residue)]
        adjacency[source].append((edge_id, target, edge))
        weighted_edges.append((source, target, edge.slope_log2))

    exact = _karp_max_cycle_mean(len(states), tuple(weighted_edges))
    exact_mean = None if exact is None else exact[0]
    cycles: list[ChristoffelFilteredCycle] = []
    seen_edge_cycles: set[tuple[int, ...]] = set()
    stopped_early = False

    def canonical(edge_ids: tuple[int, ...]) -> tuple[int, ...]:
        if not edge_ids:
            return edge_ids
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
        path_edges: list[TailAwareProjectiveEdge],
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
                cycle = _cycle_from_edges(states[start], tuple(path_edges + [edge]))
                cycles.append(cycle)
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

    for start in range(len(states)):
        dfs(start, start, {start}, [], [])
        if stopped_early:
            break

    unfiltered = tuple(
        sorted(cycles, key=lambda cycle: cycle.edge_mean_log2_slope, reverse=True)
    )
    filtered = tuple(
        cycle for cycle in unfiltered if cycle.christoffel_compatible
    )
    best_unfiltered = unfiltered[0] if unfiltered else None
    best_filtered = filtered[0] if filtered else None
    return ChristoffelFilteredJSRLevel(
        tail_unit_power=tail_unit_power,
        max_tail_depth=max_tail_depth,
        max_valuation=max_valuation,
        states=len(states),
        edges=len(edges),
        closed_overflow_edges=closed_overflow_edges,
        max_cycle_edges=max_cycle_edges,
        max_cycles_scanned=max_cycles_scanned,
        cycles_scanned=len(cycles),
        christoffel_compatible_cycles=len(filtered),
        exact_karp_log2_slope=exact_mean,
        exact_karp_factor=None if exact_mean is None else 2.0**exact_mean,
        enumerated_unfiltered_best_log2_slope=(
            None if best_unfiltered is None else best_unfiltered.edge_mean_log2_slope
        ),
        enumerated_unfiltered_best_factor=(
            None if best_unfiltered is None else best_unfiltered.edge_factor
        ),
        christoffel_filtered_best_log2_slope=(
            None if best_filtered is None else best_filtered.edge_mean_log2_slope
        ),
        christoffel_filtered_best_factor=(
            None if best_filtered is None else best_filtered.edge_factor
        ),
        top_unfiltered_cycles=unfiltered[:top_n],
        top_christoffel_cycles=filtered[:top_n],
        status=(
            "cycle_scan_hit_cap_bounded_diagnostic"
            if stopped_early
            else "bounded_simple_cycle_scan_complete_for_depth_cap"
        ),
    )


def christoffel_filtered_jsr_report(
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5)),
    max_valuation: int = 12,
    max_cycle_edges: int = 10,
    max_cycles_scanned: int = 50_000,
    top_n: int = 8,
) -> ChristoffelFilteredJSRReport:
    """Bounded Christoffel-compatible cycle filter on the LTE-closed tail graph."""

    return ChristoffelFilteredJSRReport(
        type="christoffel_filtered_tail_jsr",
        status="bounded_finite_cycle_filter_diagnostic_not_full_hercher_theorem",
        filter_model=(
            "Each accelerated valuation a is expanded to the Terras parity "
            "block 1 followed by a-1 zeros. A cycle is retained when this "
            "cyclic parity word is primitive and balanced, the finite "
            "Christoffel/Sturmian compatibility proxy."
        ),
        caveat=(
            "The scan enumerates simple cycles only up to max_cycle_edges and "
            "uses cyclic balance as a local Christoffel proxy. Hercher's full "
            "high-cycle theorem has additional arithmetic hypotheses; this "
            "artifact measures whether the finite high-growth JSR witnesses "
            "survive the Christoffel-style filter."
        ),
        levels=tuple(
            _christoffel_filtered_level(
                q,
                max_tail_depth,
                max_valuation,
                max_cycle_edges,
                max_cycles_scanned,
                top_n,
            )
            for q, max_tail_depth in levels
        ),
        interpretation=(
            "Compare exact_karp_factor and enumerated_unfiltered_best_factor "
            "against christoffel_filtered_best_factor. A drop below one would "
            "mean the bounded high-growth witnesses are filtered by the "
            "Christoffel-compatible parity constraint at that resolution."
        ),
    )
