"""Continued-fraction cycle screens inspired by Eliahou/Hercher methods.

This module does not encode the published Eliahou-Hercher constants. It emits a
machine-readable continued-fraction witness showing which rational ``A/m`` is
closest to ``log2(3)`` in a bounded range. The artifact is useful input for
formal cycle-exclusion work, but is not itself a theorem about all cycles.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import floor, log2
from typing import Any


@dataclass(frozen=True)
class ConvergentWitness:
    numerator_A: int
    denominator_m: int
    approximation: str
    abs_error: float
    power_gap: int
    relation: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CycleLengthScreen:
    type: str
    status: str
    max_m: int
    best_witness: ConvergentWitness
    nearby_convergents: tuple[ConvergentWitness, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["nearby_convergents"] = [
            witness.to_json_dict() for witness in self.nearby_convergents
        ]
        data["best_witness"] = self.best_witness.to_json_dict()
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def continued_fraction_terms(x: float, limit: int) -> tuple[int, ...]:
    if limit < 1:
        raise ValueError("limit must be positive")

    terms: list[int] = []
    y = x
    for _ in range(limit):
        term = floor(y)
        terms.append(term)
        fractional = y - term
        if fractional == 0:
            break
        y = 1 / fractional
    return tuple(terms)


def convergents(terms: tuple[int, ...]) -> tuple[Fraction, ...]:
    if not terms:
        return ()

    values: list[Fraction] = []
    p_minus_2, p_minus_1 = 0, 1
    q_minus_2, q_minus_1 = 1, 0
    for term in terms:
        p = term * p_minus_1 + p_minus_2
        q = term * q_minus_1 + q_minus_2
        values.append(Fraction(p, q))
        p_minus_2, p_minus_1 = p_minus_1, p
        q_minus_2, q_minus_1 = q_minus_1, q
    return tuple(values)


def _witness(fraction: Fraction) -> ConvergentWitness:
    A = fraction.numerator
    m = fraction.denominator
    left = 1 << A
    right = 3**m
    gap = left - right
    relation = "above_descent_threshold" if gap > 0 else "below_descent_threshold"
    return ConvergentWitness(
        numerator_A=A,
        denominator_m=m,
        approximation=f"{A}/{m}",
        abs_error=abs(A / m - log2(3)),
        power_gap=gap,
        relation=relation,
    )


def log2_3_convergents(max_denominator: int, term_limit: int = 24) -> tuple[ConvergentWitness, ...]:
    """Return convergents ``A/m`` to ``log2(3)`` with ``m <= max_denominator``."""

    if max_denominator < 1:
        raise ValueError("max_denominator must be positive")
    terms = continued_fraction_terms(log2(3), term_limit)
    return tuple(
        _witness(fraction)
        for fraction in convergents(terms)
        if fraction.denominator <= max_denominator
    )


def cycle_length_screen(max_m: int = 200) -> CycleLengthScreen:
    """Return a bounded continued-fraction screen for cycle lengths ``m <= max_m``."""

    witnesses = log2_3_convergents(max_m)
    if not witnesses:
        raise RuntimeError("no convergents generated")
    best = min(witnesses, key=lambda witness: witness.abs_error)
    return CycleLengthScreen(
        type="continued_fraction_cycle_screen",
        status=(
            "research_artifact_not_eliahou_hercher_theorem; "
            "published constants are not encoded"
        ),
        max_m=max_m,
        best_witness=best,
        nearby_convergents=witnesses,
    )
