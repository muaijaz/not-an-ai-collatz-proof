"""Substochastic survival spectra for unresolved certificate-cover frontiers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .core import accelerated_step
from .cover import CertificateCoverReport, CoverFrontierNode


@dataclass(frozen=True)
class SurvivalRowSummary:
    state_index: int
    residue: int
    modulus_power: int
    survival_count: int
    escape_count: int
    row_denominator: int

    @property
    def survival_fraction(self) -> Fraction:
        return Fraction(self.survival_count, self.row_denominator)

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverSurvivalSpectrumReport:
    type: str
    status: str
    frontier_classes: int
    sample_lift_power: int
    row_denominator: int
    matrix_dimension: int
    weighted_survival_num: int
    weighted_survival_den: int
    min_row_survival_num: int
    min_row_survival_den: int
    max_row_survival_num: int
    max_row_survival_den: int
    perron_eigenvalue: float | None
    slowest_state_index: int | None
    slowest_state_residue: int | None
    slowest_state_modulus_power: int | None
    top_survival_rows: tuple[SurvivalRowSummary, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["top_survival_rows"] = [
            row.to_json_dict() for row in self.top_survival_rows
        ]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _frontier_index(
    frontier: tuple[CoverFrontierNode, ...],
) -> dict[int, dict[int, int]]:
    by_power: dict[int, dict[int, int]] = {}
    for index, node in enumerate(frontier):
        by_power.setdefault(node.modulus_power, {})[
            node.residue % (1 << node.modulus_power)
        ] = index
    return by_power


def _locate_frontier_state(
    n: int,
    by_power: dict[int, dict[int, int]],
) -> int | None:
    for power, residues in by_power.items():
        index = residues.get(n % (1 << power))
        if index is not None:
            return index
    return None


def _weighted_survival(
    frontier: tuple[CoverFrontierNode, ...],
    rows: tuple[SurvivalRowSummary, ...],
) -> Fraction:
    total = Fraction(0, 1)
    for node, row in zip(frontier, rows, strict=True):
        state_mass = Fraction(1, 1 << (node.modulus_power - 1))
        total += state_mass * row.survival_fraction
    return total


def _perron_with_numpy(
    row_counts: tuple[tuple[int, ...], ...],
    row_denominator: int,
) -> tuple[float, int] | None:
    try:
        import numpy as np
    except ImportError:
        return None

    matrix = np.array(row_counts, dtype=float) / row_denominator
    eigenvalues, eigenvectors = np.linalg.eig(matrix.T)
    index = int(np.argmax(np.abs(eigenvalues)))
    vector = np.real(eigenvectors[:, index])
    slowest = int(np.argmax(np.abs(vector)))
    return float(abs(eigenvalues[index])), slowest


def _perron_by_power_iteration(
    row_counts: tuple[tuple[int, ...], ...],
    row_denominator: int,
    iterations: int = 80,
) -> tuple[float, int] | None:
    dimension = len(row_counts)
    if dimension == 0:
        return None
    vector = [1.0 / dimension for _ in range(dimension)]
    eigenvalue = 0.0
    for _ in range(iterations):
        next_vector = [0.0 for _ in range(dimension)]
        for source, value in enumerate(vector):
            if value == 0.0:
                continue
            row = row_counts[source]
            for target, count in enumerate(row):
                if count:
                    next_vector[target] += value * count / row_denominator
        mass = sum(next_vector)
        if mass == 0.0:
            return 0.0, 0
        eigenvalue = mass / sum(vector)
        vector = [value / mass for value in next_vector]
    return eigenvalue, max(range(dimension), key=lambda index: vector[index])


def _perron_sparse_power_iteration(
    sparse_rows: tuple[dict[int, int], ...],
    row_denominator: int,
    iterations: int = 120,
) -> tuple[float, int] | None:
    dimension = len(sparse_rows)
    if dimension == 0:
        return None
    vector = [1.0 / dimension for _ in range(dimension)]
    eigenvalue = 0.0
    for _ in range(iterations):
        next_vector = [0.0 for _ in range(dimension)]
        for source, value in enumerate(vector):
            if value == 0.0:
                continue
            for target, count in sparse_rows[source].items():
                next_vector[target] += value * count / row_denominator
        old_mass = sum(vector)
        mass = sum(next_vector)
        if mass == 0.0 or old_mass == 0.0:
            return 0.0, 0
        eigenvalue = mass / old_mass
        vector = [value / mass for value in next_vector]
    return eigenvalue, max(range(dimension), key=lambda index: vector[index])


def cover_survival_spectrum(
    report: CertificateCoverReport,
    sample_lift_power: int = 4,
    max_states: int = 2_048,
    top_n: int = 10,
) -> CoverSurvivalSpectrumReport:
    """Build a finite substochastic matrix on unresolved frontier cylinders.

    Each row enumerates ``2^sample_lift_power`` binary lifts inside one frontier
    cylinder, applies one accelerated odd step, and counts whether the landing
    remains in an unresolved frontier cylinder. Missing mass is treated as
    escape into the already-certified side of the finite cover.
    """

    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")
    if max_states < 1:
        raise ValueError("max_states must be positive")
    if top_n < 1:
        raise ValueError("top_n must be positive")

    frontier = report.frontier
    dimension = len(frontier)
    row_denominator = 1 << sample_lift_power
    dense_allowed = dimension <= max_states
    if not dense_allowed and dimension > max_states * 32:
        zero = Fraction(0, 1)
        return CoverSurvivalSpectrumReport(
            type="cover_frontier_substochastic_spectrum",
            status="frontier_too_large_matrix_not_built",
            frontier_classes=dimension,
            sample_lift_power=sample_lift_power,
            row_denominator=row_denominator,
            matrix_dimension=0,
            weighted_survival_num=zero.numerator,
            weighted_survival_den=zero.denominator,
            min_row_survival_num=zero.numerator,
            min_row_survival_den=zero.denominator,
            max_row_survival_num=zero.numerator,
            max_row_survival_den=zero.denominator,
            perron_eigenvalue=None,
            slowest_state_index=None,
            slowest_state_residue=None,
            slowest_state_modulus_power=None,
            top_survival_rows=(),
        )

    by_power = _frontier_index(frontier)
    sparse_rows: list[dict[int, int]] = []
    summaries: list[SurvivalRowSummary] = []
    for source_index, node in enumerate(frontier):
        counts: dict[int, int] = {}
        for lift in range(row_denominator):
            n = node.residue + (lift << node.modulus_power)
            landing, _ = accelerated_step(n)
            target = _locate_frontier_state(landing, by_power)
            if target is not None:
                counts[target] = counts.get(target, 0) + 1
        survival_count = sum(counts.values())
        summaries.append(
            SurvivalRowSummary(
                state_index=source_index,
                residue=node.residue,
                modulus_power=node.modulus_power,
                survival_count=survival_count,
                escape_count=row_denominator - survival_count,
                row_denominator=row_denominator,
            )
        )
        sparse_rows.append(counts)

    rows = tuple(summaries)
    sparse_tuple = tuple(sparse_rows)
    spectral = None
    if dense_allowed:
        row_count_tuple = tuple(
            tuple(row.get(target, 0) for target in range(dimension))
            for row in sparse_tuple
        )
        spectral = _perron_with_numpy(row_count_tuple, row_denominator)
        if spectral is None:
            spectral = _perron_by_power_iteration(row_count_tuple, row_denominator)
    if spectral is None:
        spectral = _perron_sparse_power_iteration(sparse_tuple, row_denominator)
    perron, slowest = (None, None) if spectral is None else spectral
    weighted = _weighted_survival(frontier, rows)
    row_fractions = [row.survival_fraction for row in rows]
    min_row = min(row_fractions, default=Fraction(0, 1))
    max_row = max(row_fractions, default=Fraction(0, 1))
    top_rows = tuple(
        sorted(
            rows,
            key=lambda row: (
                row.survival_fraction,
                row.modulus_power,
                row.residue,
            ),
            reverse=True,
        )[:top_n]
    )
    slowest_node = None if slowest is None else frontier[slowest]
    return CoverSurvivalSpectrumReport(
        type="cover_frontier_substochastic_spectrum",
        status="finite_frontier_survival_spectrum_not_collatz_proof",
        frontier_classes=dimension,
        sample_lift_power=sample_lift_power,
        row_denominator=row_denominator,
        matrix_dimension=dimension,
        weighted_survival_num=weighted.numerator,
        weighted_survival_den=weighted.denominator,
        min_row_survival_num=min_row.numerator,
        min_row_survival_den=min_row.denominator,
        max_row_survival_num=max_row.numerator,
        max_row_survival_den=max_row.denominator,
        perron_eigenvalue=perron,
        slowest_state_index=slowest,
        slowest_state_residue=None if slowest_node is None else slowest_node.residue,
        slowest_state_modulus_power=None
        if slowest_node is None
        else slowest_node.modulus_power,
        top_survival_rows=top_rows,
    )
