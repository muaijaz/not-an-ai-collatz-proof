"""Diagnostics for single-divider versus multiple-divider odd steps."""

from __future__ import annotations

from dataclasses import dataclass

from .core import accelerated_step


@dataclass(frozen=True)
class DividerTransitionCounts:
    single_to_single: int
    single_to_multiple: int
    multiple_to_single: int
    multiple_to_multiple: int


@dataclass(frozen=True)
class DividerPatternReport:
    type: str
    status: str
    modulus_power: int
    odd_residues: int
    counts: DividerTransitionCounts
    longest_single_run: int
    longest_multiple_run: int


def _divider_kind(valuation: int) -> int:
    return 1 if valuation == 1 else 2


def divider_pattern_report(
    modulus_power: int = 12,
    lookahead: int = 16,
) -> DividerPatternReport:
    """Count finite transitions between valuation ``1`` and valuations ``>=2``."""

    if modulus_power < 2:
        raise ValueError("modulus_power must be at least two")
    if lookahead < 2:
        raise ValueError("lookahead must be at least two")

    counts = {
        (1, 1): 0,
        (1, 2): 0,
        (2, 1): 0,
        (2, 2): 0,
    }
    longest_single = 0
    longest_multiple = 0
    odd_count = 0
    for n in range(1, 1 << modulus_power, 2):
        odd_count += 1
        x = n
        previous: int | None = None
        single_run = 0
        multiple_run = 0
        for _ in range(lookahead):
            x, valuation = accelerated_step(x)
            kind = _divider_kind(valuation)
            if previous is not None:
                counts[(previous, kind)] += 1
            if kind == 1:
                single_run += 1
                multiple_run = 0
            else:
                multiple_run += 1
                single_run = 0
            longest_single = max(longest_single, single_run)
            longest_multiple = max(longest_multiple, multiple_run)
            previous = kind

    return DividerPatternReport(
        type="divider_pattern_report",
        status="finite_single_multiple_divider_census_not_collatz_proof",
        modulus_power=modulus_power,
        odd_residues=odd_count,
        counts=DividerTransitionCounts(
            single_to_single=counts[(1, 1)],
            single_to_multiple=counts[(1, 2)],
            multiple_to_single=counts[(2, 1)],
            multiple_to_multiple=counts[(2, 2)],
        ),
        longest_single_run=longest_single,
        longest_multiple_run=longest_multiple,
    )
