"""Auxiliary-prime valuation diagnostics for affine Collatz words."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .core import affine_from_word, v2
from .cycles import near_balanced_words


@dataclass(frozen=True)
class PrimeValuationSummary:
    prime: int
    max_vp_B: int
    max_vp_power_gap: int

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NewtonPolygonReport:
    type: str
    status: str
    words_scanned: int
    primes: tuple[int, ...]
    summaries: tuple[PrimeValuationSummary, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["summaries"] = [item.to_json_dict() for item in self.summaries]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def vp(value: int, prime: int) -> int:
    if prime == 2:
        return v2(abs(value))
    if prime < 2:
        raise ValueError("prime must be at least two")
    value = abs(value)
    count = 0
    while value and value % prime == 0:
        value //= prime
        count += 1
    return count


def newton_polygon_report(
    m_max: int = 7,
    valuation_max: int = 5,
    slack: int = 1,
    primes: tuple[int, ...] = (5, 7, 11),
) -> NewtonPolygonReport:
    words = near_balanced_words(m_max, valuation_max, slack)
    summaries: list[PrimeValuationSummary] = []
    for prime in primes:
        max_b = 0
        max_gap = 0
        for word in words:
            affine = affine_from_word(word)
            max_b = max(max_b, vp(affine.B, prime))
            max_gap = max(max_gap, vp((1 << affine.A) - 3**affine.m, prime))
        summaries.append(
            PrimeValuationSummary(
                prime=prime,
                max_vp_B=max_b,
                max_vp_power_gap=max_gap,
            )
        )
    return NewtonPolygonReport(
        type="auxiliary_prime_newton_polygon_diagnostic",
        status="finite_padic_valuation_scan_not_cycle_exclusion",
        words_scanned=len(words),
        primes=primes,
        summaries=tuple(summaries),
    )
