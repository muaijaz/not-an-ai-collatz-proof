"""Finite density artifacts for residue covers and truncated transitions.

The exact unresolved-density calculation is rigorous for the finite residue
cover supplied to it. The optional LP hook is deliberately marked experimental;
it is a scaffold for a Krasikov-Lagarias style relaxation, not a port of their
published LP yet.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

from .core import accelerated_step
from .search import CoverSearchResult, adaptive_cover


@dataclass(frozen=True)
class DensityBound:
    type: str
    status: str
    max_depth: int
    nodes_processed: int
    certified_classes: int
    unresolved_classes: int
    unresolved_odd_density_num: int
    unresolved_odd_density_den: int

    @property
    def unresolved_odd_density(self) -> Fraction:
        return Fraction(self.unresolved_odd_density_num, self.unresolved_odd_density_den)

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class TransitionMatrixArtifact:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    residues: tuple[int, ...]
    row_counts: tuple[tuple[int, ...], ...]
    row_denominator: int

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["residues"] = list(self.residues)
        data["row_counts"] = [list(row) for row in self.row_counts]
        return data


def unresolved_odd_density(unresolved: tuple[tuple[int, int], ...]) -> Fraction:
    """Return the relative density of unresolved odd residue cylinders."""

    density = Fraction(0, 1)
    for _, modulus_power in unresolved:
        density += Fraction(1, 1 << (modulus_power - 1))
    return density


def density_bound_from_cover(result: CoverSearchResult) -> DensityBound:
    density = unresolved_odd_density(result.unresolved)
    max_depth = max((power for _, power in result.unresolved), default=0)
    return DensityBound(
        type="finite_residue_cover_density_bound",
        status="rigorous_for_reported_finite_cover_not_KL_LP",
        max_depth=max_depth,
        nodes_processed=result.nodes_processed,
        certified_classes=len(result.certificates),
        unresolved_classes=len(result.unresolved),
        unresolved_odd_density_num=density.numerator,
        unresolved_odd_density_den=density.denominator,
    )


def density_bound(
    max_depth: int = 16,
    max_nodes: int = 20_000,
) -> DensityBound:
    return density_bound_from_cover(adaptive_cover(max_depth=max_depth, max_nodes=max_nodes))


def transition_matrix_artifact(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
) -> TransitionMatrixArtifact:
    """Build exact transition counts by sampling all finer binary lifts."""

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least 2")
    if sample_lift_power < 0:
        raise ValueError("sample_lift_power must be nonnegative")

    residues = tuple(range(1, 1 << modulus_power, 2))
    index = {residue: i for i, residue in enumerate(residues)}
    row_denominator = 1 << sample_lift_power
    rows: list[list[int]] = []
    for residue in residues:
        counts = [0 for _ in residues]
        for lift in range(row_denominator):
            n = residue + (lift << modulus_power)
            landing, _ = accelerated_step(n)
            target = landing % (1 << modulus_power)
            counts[index[target]] += 1
        rows.append(counts)

    return TransitionMatrixArtifact(
        type="truncated_accelerated_transition_counts",
        status="exact_for_sampled_lifts_not_full_KL_LP",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        residues=residues,
        row_counts=tuple(tuple(row) for row in rows),
        row_denominator=row_denominator,
    )
