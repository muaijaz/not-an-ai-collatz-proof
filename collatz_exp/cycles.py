"""Exact affine cycle classification for accelerated Collatz words."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from .core import apply_word, affine_from_word


@dataclass(frozen=True)
class CycleClassification:
    kind: str
    value: Fraction
    word: tuple[int, ...]


@dataclass(frozen=True)
class CycleScanReport:
    words_scanned: int
    by_kind: dict[str, int]
    positive_integer_cycles: tuple[CycleClassification, ...]
    nontrivial_positive_integer_cycles: tuple[CycleClassification, ...]
    positive_integer_nonrealizing: tuple[CycleClassification, ...]


def classify_cycle_word(word: tuple[int, ...]) -> CycleClassification:
    """Solve ``(2^A - 3^m) * n = B`` and classify the result exactly."""

    affine = affine_from_word(word)
    denominator = (1 << affine.A) - 3**affine.m
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
        realizes_word = apply_word(n, affine.word) == n
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


def near_balanced_words(
    m_max: int,
    valuation_max: int = 6,
    slack: int = 2,
) -> tuple[tuple[int, ...], ...]:
    """Generate finite near-threshold words for exact cycle experiments.

    This is intentionally not an exhaustive cycle proof. It samples the hard
    region where ``A`` is close to ``m*log2(3)`` by bounding each valuation and
    total excess over the first shrink-favorable total.
    """

    if m_max < 1:
        raise ValueError("m_max must be positive")
    if valuation_max < 1:
        raise ValueError("valuation_max must be positive")
    if slack < 0:
        raise ValueError("slack must be nonnegative")

    words: list[tuple[int, ...]] = []

    def build_words(
        length: int,
        target_min: int,
        target_max: int,
        prefix: tuple[int, ...] = (),
        partial_sum: int = 0,
    ) -> None:
        remaining = length - len(prefix)
        if remaining == 0:
            if target_min <= partial_sum <= target_max:
                words.append(prefix)
            return
        if partial_sum + remaining > target_max:
            return
        if partial_sum + remaining * valuation_max < target_min:
            return
        for valuation in range(1, valuation_max + 1):
            build_words(
                length,
                target_min,
                target_max,
                (*prefix, valuation),
                partial_sum + valuation,
            )

    for m in range(1, m_max + 1):
        min_A = 0
        while (1 << min_A) <= 3**m:
            min_A += 1
        build_words(m, min_A, min_A + slack)
    return tuple(words)


def scan_cycle_words(words: tuple[tuple[int, ...], ...]) -> CycleScanReport:
    """Classify supplied words and summarize possible positive integer cycles."""

    by_kind: dict[str, int] = {}
    positive_cycles: list[CycleClassification] = []
    nontrivial_positive_cycles: list[CycleClassification] = []
    nonrealizing: list[CycleClassification] = []

    for word in words:
        classification = classify_cycle_word(word)
        by_kind[classification.kind] = by_kind.get(classification.kind, 0) + 1
        if classification.kind == "positive_integer_cycle":
            positive_cycles.append(classification)
            if classification.value != 1:
                nontrivial_positive_cycles.append(classification)
        elif classification.kind == "positive_integer_nonrealizing_candidate":
            nonrealizing.append(classification)

    return CycleScanReport(
        words_scanned=len(words),
        by_kind=by_kind,
        positive_integer_cycles=tuple(positive_cycles),
        nontrivial_positive_integer_cycles=tuple(nontrivial_positive_cycles),
        positive_integer_nonrealizing=tuple(nonrealizing),
    )


def scan_near_balanced_cycles(
    m_max: int = 12,
    valuation_max: int = 6,
    slack: int = 2,
) -> CycleScanReport:
    """Generate and classify a bounded near-balanced word family."""

    return scan_cycle_words(
        near_balanced_words(
            m_max=m_max,
            valuation_max=valuation_max,
            slack=slack,
        )
    )
