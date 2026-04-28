"""Tensor-rank diagnostics for mixed 2/3-adic transition structure."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step


@dataclass(frozen=True)
class MixedTensorRankReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    states2: int
    states3: int
    tensor_entries: int
    nonzero_entries: int
    flatten_rank_2_vs_rest: int
    flatten_rank_23_vs_rest: int
    flatten_rank_232_vs_3: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _matrix_rank(matrix: list[list[float]], tolerance: float = 1e-9) -> int:
    rows = [row[:] for row in matrix if any(abs(value) > tolerance for value in row)]
    if not rows:
        return 0
    height = len(rows)
    width = len(rows[0])
    rank = 0
    col = 0
    while rank < height and col < width:
        pivot = max(range(rank, height), key=lambda row: abs(rows[row][col]))
        if abs(rows[pivot][col]) <= tolerance:
            col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][col]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for row in range(height):
            if row == rank:
                continue
            factor = rows[row][col]
            if abs(factor) > tolerance:
                rows[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(rows[row], rows[rank], strict=True)
                ]
        rank += 1
        col += 1
    return rank


def _crt_mod_2_3(residue2: int, power2: int, residue3: int, power3: int) -> int:
    modulus2 = 1 << power2
    modulus3 = 3**power3
    if modulus3 == 1:
        return residue2 % modulus2
    inverse = pow(modulus2, -1, modulus3)
    t = ((residue3 - residue2) * inverse) % modulus3
    return residue2 + modulus2 * t


def mixed_tensor_rank_report(
    mod2_power: int = 5,
    mod3_power: int = 2,
) -> MixedTensorRankReport:
    """Build the mixed transition tensor and report TT-style flattening ranks."""

    if mod2_power < 2:
        raise ValueError("mod2_power must be at least two")
    if mod3_power < 0:
        raise ValueError("mod3_power must be nonnegative")
    residues2 = tuple(range(1, 1 << mod2_power, 2))
    residues3 = tuple(range(3**mod3_power))
    index2 = {residue: i for i, residue in enumerate(residues2)}
    index3 = {residue: i for i, residue in enumerate(residues3)}
    n2 = len(residues2)
    n3 = len(residues3)
    tensor = [[[[0 for _ in range(n3)] for _ in range(n2)] for _ in range(n3)] for _ in range(n2)]
    for residue2 in residues2:
        for residue3 in residues3:
            n = _crt_mod_2_3(residue2, mod2_power, residue3, mod3_power)
            if n == 1:
                n += (1 << mod2_power) * (3**mod3_power)
            landing, _ = accelerated_step(n)
            target2 = landing % (1 << mod2_power)
            target3 = landing % (3**mod3_power) if mod3_power else 0
            tensor[index2[residue2]][index3[residue3]][index2[target2]][index3[target3]] += 1

    nonzero = 0
    flat_2_rest: list[list[float]] = [[0.0 for _ in range(n3 * n2 * n3)] for _ in range(n2)]
    flat_23_rest: list[list[float]] = [[0.0 for _ in range(n2 * n3)] for _ in range(n2 * n3)]
    flat_232_3: list[list[float]] = [[0.0 for _ in range(n3)] for _ in range(n2 * n3 * n2)]
    for i2 in range(n2):
        for i3 in range(n3):
            for j2 in range(n2):
                for j3 in range(n3):
                    value = tensor[i2][i3][j2][j3]
                    if value:
                        nonzero += 1
                    flat_2_rest[i2][(i3 * n2 + j2) * n3 + j3] = float(value)
                    flat_23_rest[i2 * n3 + i3][j2 * n3 + j3] = float(value)
                    flat_232_3[(i2 * n3 + i3) * n2 + j2][j3] = float(value)
    return MixedTensorRankReport(
        type="mixed_2_3_transition_tensor_rank",
        status="finite_tensor_rank_diagnostic_not_decoupling_proof",
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        states2=n2,
        states3=n3,
        tensor_entries=n2 * n3 * n2 * n3,
        nonzero_entries=nonzero,
        flatten_rank_2_vs_rest=_matrix_rank(flat_2_rest),
        flatten_rank_23_vs_rest=_matrix_rank(flat_23_rest),
        flatten_rank_232_vs_3=_matrix_rank(flat_232_3),
    )
