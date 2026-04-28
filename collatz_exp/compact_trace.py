"""Compact Collatz trace invariants.

For an accelerated odd trajectory starting at ``n`` and reaching ``m`` after
``x`` odd steps and ``z`` divisions, the exact affine invariant is

    n * 3^x + y = m * 2^z.

The path code ``y`` is the same numerator offset used by affine words.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import accelerated_step


@dataclass(frozen=True)
class CompactTraceRow:
    index: int
    m: int
    x: int
    y: int
    z: int
    next_divisions: int | None
    invariant_left: int
    invariant_right: int
    invariant_valid: bool


@dataclass(frozen=True)
class CompactTraceReport:
    type: str
    status: str
    start: int
    reached_one: bool
    rows: tuple[CompactTraceRow, ...]
    invariant_valid: bool


def compact_trace_report(start: int, max_steps: int = 10_000) -> CompactTraceReport:
    """Build a finite compact odd-only trace with exact invariant checks."""

    if start <= 0 or start % 2 == 0:
        raise ValueError("start must be an odd positive integer")
    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")

    rows: list[CompactTraceRow] = []
    m = start
    x = 0
    y = 0
    z = 0
    for index in range(max_steps + 1):
        left = start * (3**x) + y
        right = m * (1 << z)
        next_divisions: int | None = None
        if m != 1 and index < max_steps:
            _, next_divisions = accelerated_step(m)
        rows.append(
            CompactTraceRow(
                index=index,
                m=m,
                x=x,
                y=y,
                z=z,
                next_divisions=next_divisions,
                invariant_left=left,
                invariant_right=right,
                invariant_valid=left == right,
            )
        )
        if m == 1 or index == max_steps:
            break
        m, divisions = accelerated_step(m)
        y = 3 * y + (1 << z)
        x += 1
        z += divisions

    return CompactTraceReport(
        type="compact_trace_invariant_report",
        status="finite_compact_trace_not_collatz_proof",
        start=start,
        reached_one=rows[-1].m == 1,
        rows=tuple(rows),
        invariant_valid=all(row.invariant_valid for row in rows),
    )
