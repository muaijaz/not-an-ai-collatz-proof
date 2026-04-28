"""Magnitude-style metric invariant for small cover frontiers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp
from typing import Any

from .cover import CertificateCoverReport


@dataclass(frozen=True)
class MagnitudeReport:
    type: str
    status: str
    sampled_points: int
    scale: float
    magnitude: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _prefix_distance(left_residue: int, left_power: int, right_residue: int, right_power: int) -> int:
    limit = min(left_power, right_power)
    common = 0
    for bit in range(limit):
        if ((left_residue >> bit) & 1) != ((right_residue >> bit) & 1):
            break
        common += 1
    return (left_power - common) + (right_power - common)


def _solve_linear(matrix: list[list[float]], rhs: list[float]) -> list[float] | None:
    n = len(rhs)
    rows = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(rows[row][col]))
        if abs(rows[pivot][col]) < 1e-12:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        value = rows[col][col]
        for j in range(col, n + 1):
            rows[col][j] /= value
        for row in range(n):
            if row == col:
                continue
            factor = rows[row][col]
            for j in range(col, n + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][n] for i in range(n)]


def magnitude_report(
    report: CertificateCoverReport,
    max_points: int = 64,
    scale: float = 0.25,
) -> MagnitudeReport:
    frontier = report.frontier[:max_points]
    n = len(frontier)
    if n == 0:
        return MagnitudeReport(
            type="cover_trie_magnitude",
            status="empty_frontier",
            sampled_points=0,
            scale=scale,
            magnitude=0.0,
        )
    matrix = []
    for left in frontier:
        row = []
        for right in frontier:
            distance = _prefix_distance(
                left.residue,
                left.modulus_power,
                right.residue,
                right.modulus_power,
            )
            row.append(exp(-scale * distance))
        matrix.append(row)
    weights = _solve_linear(matrix, [1.0 for _ in range(n)])
    return MagnitudeReport(
        type="cover_trie_magnitude",
        status="finite_metric_magnitude_not_homology_proof",
        sampled_points=n,
        scale=scale,
        magnitude=None if weights is None else sum(weights),
    )
