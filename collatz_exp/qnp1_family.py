"""Exact qn+1 accelerated-map primitives for odd q."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .core import AffineWord, accelerated_step, affine_from_word, apply_word, v2
from .cycles import CycleClassification, classify_cycle_word


@dataclass(frozen=True)
class AffineQ:
    """Affine expansion for a fixed q-accelerated valuation word."""

    word: tuple[int, ...]
    q: int
    A: int
    B: int
    m: int


def _validate_q(q: int) -> None:
    if q <= 0 or q % 2 == 0:
        raise ValueError("q must be a positive odd integer")


def _accelerated_step_with_valuation_q(n: int, q: int) -> tuple[int, int]:
    _validate_q(q)
    if n <= 0 or n % 2 == 0:
        raise ValueError("accelerated_step_q expects an odd positive integer")
    a = v2(q * n + 1)
    return (q * n + 1) // (1 << a), a


def accelerated_step_q(n: int, q: int = 3) -> int:
    """Return the accelerated qn+1 image of odd positive ``n``."""

    return _accelerated_step_with_valuation_q(n, q)[0]


def valuation_word_q(n: int, length: int, q: int = 3) -> tuple[int, ...]:
    """Return the first ``length`` q-accelerated valuations for odd ``n``."""

    if length < 0:
        raise ValueError("length must be nonnegative")
    x = n
    word: list[int] = []
    for _ in range(length):
        x, a = _accelerated_step_with_valuation_q(x, q)
        word.append(a)
    return tuple(word)


def apply_word_q(n: int, word: Iterable[int], q: int = 3) -> int:
    """Apply a q-accelerated valuation word, verifying each valuation."""

    x = n
    for expected in word:
        x, actual = _accelerated_step_with_valuation_q(x, q)
        if actual != expected:
            raise ValueError(f"valuation mismatch: expected {expected}, got {actual}")
    return x


def affine_from_word_q(word: Iterable[int], q: int = 3) -> AffineQ:
    """Compute ``S_q^m(n) = (q^m*n + B) / 2^A`` exactly."""

    _validate_q(q)
    values = tuple(word)
    A = 0
    B = 0
    for a in values:
        if a <= 0:
            raise ValueError("valuation words must contain positive integers")
        B = q * B + (1 << A)
        A += a
    return AffineQ(word=values, q=q, A=A, B=B, m=len(values))


def classify_cycle_word_q(
    word: tuple[int, ...],
    q: int = 3,
) -> CycleClassification:
    """Solve ``(2^A - q^m) * n = B`` and classify exactly."""

    if q == 3:
        return classify_cycle_word(word)

    affine = affine_from_word_q(word, q)
    denominator = (1 << affine.A) - q**affine.m
    if denominator == 0:
        return CycleClassification(
            kind="impossible_power_balance",
            value=Fraction(affine.B, 1),
            word=affine.word,
        )

    value = Fraction(affine.B, denominator)
    if affine.B % abs(denominator) != 0:
        return CycleClassification(
            kind="noninteger_2adic_only",
            value=value,
            word=affine.word,
        )

    n = value.numerator
    if denominator < 0:
        return CycleClassification(
            kind="negative_integer_cycle",
            value=value,
            word=affine.word,
        )

    if n > 0 and n % 2 == 1:
        realizes_word = apply_word_q(n, affine.word, q) == n
        return CycleClassification(
            kind=(
                "positive_integer_cycle"
                if realizes_word
                else "positive_integer_nonrealizing_candidate"
            ),
            value=value,
            word=affine.word,
        )
    return CycleClassification(
        kind="integer_but_not_positive_odd",
        value=value,
        word=affine.word,
    )


def q3_regression_tuple(word: tuple[int, ...], n: int) -> tuple[AffineQ, AffineWord, int, int]:
    """Return q=3 sidecar/core values for compact regression tests."""

    return (
        affine_from_word_q(word, 3),
        affine_from_word(word),
        apply_word_q(n, word, 3),
        apply_word(n, word),
    )
