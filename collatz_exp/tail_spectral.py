"""Spectral diagnostics for tail-prefixed residue subautomata."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class TailSubautomatonSpectrumReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    prefix_ones: int
    tail_states: int
    row_denominator: int
    survival_mass_num: int
    survival_mass_den: int
    perron_eigenvalue: float | None
    top_tail_residue: int | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TailPointwiseRatioReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    prefix_ones: int
    tail_states: int
    row_denominator: int
    zero_survival_rows: int
    full_survival_rows: int
    max_row_survival_num: int
    max_row_survival_den: int
    perron_eigenvalue_estimate: float | None
    finite_ratio_min: float | None
    finite_ratio_max: float | None
    infinite_ratio_rows: int
    zero_weight_rows: int
    worst_residue: int | None
    constant_weight_rho_max: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def is_tail_prefixed_residue(residue: int, prefix_ones: int) -> bool:
    if prefix_ones < 0:
        raise ValueError("prefix_ones must be nonnegative")
    modulus = 1 << (prefix_ones + 1)
    return residue % modulus == modulus - 1


@dataclass(frozen=True)
class TailSpectralLadderReport:
    type: str
    status: str
    prefix_ones: int
    sample_lift_power: int
    max_perron_eigenvalue: float | None
    max_survival_mass_num: int
    max_survival_mass_den: int
    levels: tuple[TailSubautomatonSpectrumReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "prefix_ones": self.prefix_ones,
            "sample_lift_power": self.sample_lift_power,
            "max_perron_eigenvalue": self.max_perron_eigenvalue,
            "max_survival_mass_num": self.max_survival_mass_num,
            "max_survival_mass_den": self.max_survival_mass_den,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _sparse_perron(rows: tuple[dict[int, int], ...], denominator: int) -> tuple[float, int] | None:
    n = len(rows)
    if n == 0:
        return None
    vector = [1.0 / n for _ in range(n)]
    eigenvalue = 0.0
    for _ in range(100):
        nxt = [0.0 for _ in range(n)]
        for i, value in enumerate(vector):
            for j, count in rows[i].items():
                nxt[j] += value * count / denominator
        mass = sum(nxt)
        if mass == 0.0:
            return 0.0, 0
        eigenvalue = mass / sum(vector)
        vector = [value / mass for value in nxt]
    return eigenvalue, max(range(n), key=lambda i: vector[i])


def _tail_subautomaton_rows(
    modulus_power: int,
    prefix_ones: int,
    sample_lift_power: int,
) -> tuple[tuple[int, ...], tuple[dict[int, int], ...], int, Fraction]:
    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    if prefix_ones < 1:
        raise ValueError("prefix_ones must be positive")
    if prefix_ones + 1 > modulus_power:
        raise ValueError("prefix_ones must leave at least one free residue bit")

    tail_residues = tuple(
        residue
        for residue in range(
            (1 << (prefix_ones + 1)) - 1,
            1 << modulus_power,
            1 << (prefix_ones + 1),
        )
    )
    local_index = {residue: local for local, residue in enumerate(tail_residues)}
    row_denominator = 1 << sample_lift_power
    rows: list[dict[int, int]] = []
    survival = Fraction(0, 1)
    for residue in tail_residues:
        row: dict[int, int] = {}
        row_survival = 0
        for lift in range(row_denominator):
            n = residue + (lift << modulus_power)
            landing, _ = accelerated_step(n)
            target = landing % (1 << modulus_power)
            if is_tail_prefixed_residue(target, prefix_ones):
                row[local_index[target]] = row.get(local_index[target], 0) + 1
                row_survival += 1
        survival += Fraction(row_survival, row_denominator)
        rows.append(row)
    if tail_residues:
        survival /= len(tail_residues)
    return tail_residues, tuple(rows), row_denominator, survival


def _right_perron_vector(
    rows: tuple[dict[int, int], ...],
    denominator: int,
    iterations: int = 200,
) -> tuple[float, tuple[float, ...]]:
    n = len(rows)
    if n == 0:
        return 0.0, ()
    vector = [1.0 for _ in range(n)]
    eigenvalue = 0.0
    for _ in range(iterations):
        nxt = [
            sum(count * vector[j] / denominator for j, count in row.items())
            for row in rows
        ]
        scale = max(nxt, default=0.0)
        if scale == 0.0:
            return 0.0, tuple(nxt)
        eigenvalue = scale
        vector = [value / scale for value in nxt]
    return eigenvalue, tuple(vector)


def tail_subautomaton_spectrum(
    modulus_power: int = 12,
    prefix_ones: int = 8,
    sample_lift_power: int = 4,
) -> TailSubautomatonSpectrumReport:
    """Restrict the sampled transfer operator to tail-prefixed residues."""

    tail_residues, rows, row_denominator, survival = _tail_subautomaton_rows(
        modulus_power=modulus_power,
        prefix_ones=prefix_ones,
        sample_lift_power=sample_lift_power,
    )
    spectral = _sparse_perron(rows, row_denominator)
    perron = None if spectral is None else spectral[0]
    top = None if spectral is None else tail_residues[spectral[1]]
    return TailSubautomatonSpectrumReport(
        type="tail_prefixed_subautomaton_spectrum",
        status="finite_tail_subblock_spectrum_not_tail_exclusion_proof",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        prefix_ones=prefix_ones,
        tail_states=len(tail_residues),
        row_denominator=row_denominator,
        survival_mass_num=survival.numerator,
        survival_mass_den=survival.denominator,
        perron_eigenvalue=perron,
        top_tail_residue=top,
    )


def tail_pointwise_ratio_scan(
    modulus_power: int = 12,
    prefix_ones: int = 8,
    sample_lift_power: int = 6,
    iterations: int = 200,
) -> TailPointwiseRatioReport:
    """Scan pointwise ``(P omega)(r)/omega(r)`` on the tail subblock.

    A Perron eigenvalue below one is an average mass-decay certificate. A
    pointwise Lyapunov certificate needs a positive super-eigenvector. This
    report intentionally exposes zero-weight rows and full-survival rows, since
    either one blocks a direct pointwise certificate from the current subblock.
    """

    tail_residues, rows, row_denominator, _ = _tail_subautomaton_rows(
        modulus_power=modulus_power,
        prefix_ones=prefix_ones,
        sample_lift_power=sample_lift_power,
    )
    if not rows:
        return TailPointwiseRatioReport(
            type="tail_pointwise_ratio_scan",
            status="empty_tail_subblock",
            modulus_power=modulus_power,
            sample_lift_power=sample_lift_power,
            prefix_ones=prefix_ones,
            tail_states=0,
            row_denominator=1 << sample_lift_power,
            zero_survival_rows=0,
            full_survival_rows=0,
            max_row_survival_num=0,
            max_row_survival_den=1 << sample_lift_power,
            perron_eigenvalue_estimate=None,
            finite_ratio_min=None,
            finite_ratio_max=None,
            infinite_ratio_rows=0,
            zero_weight_rows=0,
            worst_residue=None,
            constant_weight_rho_max=None,
        )

    perron, omega = _right_perron_vector(rows, row_denominator, iterations=iterations)
    row_sums = [sum(row.values()) for row in rows]
    zero_survival_rows = sum(1 for total in row_sums if total == 0)
    full_survival_rows = sum(1 for total in row_sums if total == row_denominator)
    max_survival = max(row_sums, default=0)
    ratios: list[float] = []
    infinite_ratio_rows = 0
    worst_index: int | None = None
    worst_ratio = float("-inf")
    for i, row in enumerate(rows):
        image = sum(count * omega[j] / row_denominator for j, count in row.items())
        if omega[i] == 0.0:
            if image > 0.0:
                infinite_ratio_rows += 1
                worst_index = i
            continue
        ratio = image / omega[i]
        ratios.append(ratio)
        if ratio > worst_ratio:
            worst_ratio = ratio
            worst_index = i
    finite_ratio_min = min(ratios, default=None)
    finite_ratio_max = max(ratios, default=None)
    zero_weight_rows = sum(1 for value in omega if value == 0.0)
    constant_weight_rho_max = max_survival / row_denominator
    if infinite_ratio_rows:
        status = "right_perron_vector_has_zero_weight_blockers_not_pointwise"
    elif constant_weight_rho_max >= 1.0:
        status = "full_survival_rows_block_uniform_pointwise_contraction"
    elif finite_ratio_max is not None and finite_ratio_max < 1.0:
        status = "finite_pointwise_contraction_candidate_not_global_proof"
    else:
        status = "finite_pointwise_scan_inconclusive_not_global_proof"
    return TailPointwiseRatioReport(
        type="tail_pointwise_ratio_scan",
        status=status,
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        prefix_ones=prefix_ones,
        tail_states=len(rows),
        row_denominator=row_denominator,
        zero_survival_rows=zero_survival_rows,
        full_survival_rows=full_survival_rows,
        max_row_survival_num=max_survival,
        max_row_survival_den=row_denominator,
        perron_eigenvalue_estimate=perron,
        finite_ratio_min=finite_ratio_min,
        finite_ratio_max=finite_ratio_max,
        infinite_ratio_rows=infinite_ratio_rows,
        zero_weight_rows=zero_weight_rows,
        worst_residue=None if worst_index is None else tail_residues[worst_index],
        constant_weight_rho_max=constant_weight_rho_max,
    )


def tail_spectral_ladder(
    k_values: tuple[int, ...] = (12, 14, 16, 18, 20),
    prefix_ones: int = 8,
    sample_lift_power: int = 6,
) -> TailSpectralLadderReport:
    """Check tail-subblock Perron values across several depths."""

    levels = tuple(
        tail_subautomaton_spectrum(
            modulus_power=k,
            prefix_ones=prefix_ones,
            sample_lift_power=sample_lift_power,
        )
        for k in k_values
    )
    perrons = [
        level.perron_eigenvalue
        for level in levels
        if level.perron_eigenvalue is not None
    ]
    survivals = [
        Fraction(level.survival_mass_num, level.survival_mass_den)
        for level in levels
    ]
    max_survival = max(survivals, default=Fraction(0, 1))
    return TailSpectralLadderReport(
        type="tail_subautomaton_spectral_ladder",
        status="finite_uniform_tail_spectral_check_not_global_proof",
        prefix_ones=prefix_ones,
        sample_lift_power=sample_lift_power,
        max_perron_eigenvalue=max(perrons, default=None),
        max_survival_mass_num=max_survival.numerator,
        max_survival_mass_den=max_survival.denominator,
        levels=levels,
    )
