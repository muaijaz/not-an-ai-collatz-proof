"""LLL-style near-relation artifacts for cycle-search data."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log
from typing import Any

from .core import affine_from_word
from .cycles import near_balanced_words


@dataclass(frozen=True)
class LLLRelation:
    coefficients: tuple[int, ...]
    residual: float
    norm_squared: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CycleLatticeReport:
    type: str
    status: str
    words_scanned: int
    scale: int
    best_word: tuple[int, ...]
    best_m: int
    best_A: int
    best_B_digits: int
    best_power_gap_abs: int
    relations: tuple[LLLRelation, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["relations"] = [item.to_json_dict() for item in self.relations]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def lll_reduce(
    basis: tuple[tuple[int, ...], ...],
    delta: float = 0.75,
) -> tuple[tuple[int, ...], ...]:
    """Return a small LLL-reduced integer basis using floating Gram-Schmidt."""

    if not basis:
        return ()
    rows = [list(row) for row in basis]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("basis rows must have the same width")

    def gram_schmidt() -> tuple[list[list[float]], list[list[float]], list[float]]:
        orthogonal = [[0.0 for _ in range(width)] for _ in rows]
        mu = [[0.0 for _ in rows] for _ in rows]
        norms = [0.0 for _ in rows]
        for i, row in enumerate(rows):
            vector = [float(value) for value in row]
            for j in range(i):
                if norms[j] == 0.0:
                    continue
                mu[i][j] = _dot(vector, orthogonal[j]) / norms[j]
                for col in range(width):
                    vector[col] -= mu[i][j] * orthogonal[j][col]
            orthogonal[i] = vector
            norms[i] = _dot(vector, vector)
        return orthogonal, mu, norms

    k = 1
    _, mu, norms = gram_schmidt()
    while k < len(rows):
        for j in range(k - 1, -1, -1):
            rounded = round(mu[k][j])
            if rounded:
                for col in range(width):
                    rows[k][col] -= rounded * rows[j][col]
                _, mu, norms = gram_schmidt()
        if norms[k] >= (delta - mu[k][k - 1] ** 2) * norms[k - 1]:
            k += 1
        else:
            rows[k], rows[k - 1] = rows[k - 1], rows[k]
            _, mu, norms = gram_schmidt()
            k = max(k - 1, 1)
    return tuple(tuple(row) for row in rows)


def _integer_relation_basis(values: tuple[float, ...], scale: int) -> tuple[tuple[int, ...], ...]:
    rows: list[tuple[int, ...]] = []
    for index, value in enumerate(values):
        row = [0 for _ in range(len(values) + 1)]
        row[index] = 1
        row[-1] = round(scale * value)
        rows.append(tuple(row))
    last = [0 for _ in range(len(values) + 1)]
    last[-1] = scale
    rows.append(tuple(last))
    return tuple(rows)


def cycle_lattice_report(
    m_max: int = 7,
    valuation_max: int = 5,
    slack: int = 1,
    scale: int = 10**8,
    top_relations: int = 4,
) -> CycleLatticeReport:
    """Use LLL as a multi-log near-relation scanner for bounded cycle words."""

    if scale < 1:
        raise ValueError("scale must be positive")
    words = near_balanced_words(
        m_max=m_max,
        valuation_max=valuation_max,
        slack=slack,
    )
    if not words:
        raise RuntimeError("no words generated")
    scored = []
    for word in words:
        affine = affine_from_word(word)
        gap = abs((1 << affine.A) - 3**affine.m)
        scored.append((gap, affine.B, word, affine))
    gap, best_B, best_word, best_affine = min(scored, key=lambda item: item[0])
    values = (log(2), log(3), log(max(best_B, 2)))
    reduced = lll_reduce(_integer_relation_basis(values, scale))
    relations: list[LLLRelation] = []
    for row in reduced:
        coeffs = row[:-1]
        residual = abs(sum(coeff * value for coeff, value in zip(coeffs, values, strict=True)))
        relations.append(
            LLLRelation(
                coefficients=tuple(coeffs),
                residual=residual,
                norm_squared=sum(coeff * coeff for coeff in coeffs),
            )
        )
    relations.sort(key=lambda item: (item.residual, item.norm_squared))
    return CycleLatticeReport(
        type="cycle_lattice_lll_near_relation",
        status="finite_lll_near_relation_not_cycle_proof",
        words_scanned=len(words),
        scale=scale,
        best_word=best_word,
        best_m=best_affine.m,
        best_A=best_affine.A,
        best_B_digits=len(str(best_affine.B)),
        best_power_gap_abs=gap,
        relations=tuple(relations[:top_relations]),
    )
