"""Integer-rank and Bowen-Franks-style invariants for finite quotients."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import gcd
from typing import Any

from .density_lp import transition_matrix_artifact


@dataclass(frozen=True)
class SNFInvariantReport:
    type: str
    status: str
    modulus_power: int
    sample_lift_power: int
    vertices: int
    support_edges: int
    integer_rank_i_minus_a_t: int
    cokernel_free_rank: int
    entry_gcd: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def integer_rank(matrix: tuple[tuple[int, ...], ...]) -> int:
    rows = [[float(value) for value in row] for row in matrix if any(row)]
    if not rows:
        return 0
    height = len(rows)
    width = len(rows[0])
    rank = 0
    col = 0
    while rank < height and col < width:
        pivot = max(range(rank, height), key=lambda row: abs(rows[row][col]))
        if abs(rows[pivot][col]) < 1e-9:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][col]
        for c in range(col, width):
            rows[rank][c] /= pivot_value
        for row in range(height):
            if row == rank:
                continue
            factor = rows[row][col]
            for c in range(col, width):
                rows[row][c] -= factor * rows[rank][c]
        rank += 1
        col += 1
    return rank


def snf_invariant_report(
    modulus_power: int = 6,
    sample_lift_power: int = 4,
) -> SNFInvariantReport:
    """Report first integer invariants for ``coker(I - A^T)``."""

    artifact = transition_matrix_artifact(modulus_power, sample_lift_power)
    dimension = len(artifact.residues)
    support = [
        [1 if artifact.row_counts[i][j] else 0 for j in range(dimension)]
        for i in range(dimension)
    ]
    matrix = []
    entry_gcd = 0
    for i in range(dimension):
        row = []
        for j in range(dimension):
            value = (1 if i == j else 0) - support[j][i]
            row.append(value)
            entry_gcd = gcd(entry_gcd, abs(value))
        matrix.append(tuple(row))
    rank = integer_rank(tuple(matrix))
    return SNFInvariantReport(
        type="bowen_franks_style_integer_invariant",
        status="finite_integer_rank_not_full_smith_normal_form",
        modulus_power=modulus_power,
        sample_lift_power=sample_lift_power,
        vertices=dimension,
        support_edges=sum(sum(row) for row in support),
        integer_rank_i_minus_a_t=rank,
        cokernel_free_rank=dimension - rank,
        entry_gcd=entry_gcd,
    )
