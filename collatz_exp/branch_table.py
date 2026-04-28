"""Branch-table diagnostics for ordinary Collatz trajectories."""

from __future__ import annotations

from dataclasses import dataclass

from .core import accelerated_step
from .tuple_merges import collatz_step


@dataclass(frozen=True)
class BranchRow:
    """One jump plus the following divisions by two."""

    index: int
    odd_start: int
    jump_value: int
    divisions: int
    odd_end: int
    cumulative_divisions: int


@dataclass(frozen=True)
class BranchTableReport:
    """Finite branch-table view of one trajectory."""

    type: str
    status: str
    start: int
    reached_one: bool
    rows: tuple[BranchRow, ...]
    total_divisions: int
    ordinary_steps: int
    terminal_power_exponent: int | None


def terminal_power_exponent_before_one(odd: int) -> int | None:
    """Return ``m`` when ``3*odd + 1 = 2^m``; otherwise ``None``."""

    jump = 3 * odd + 1
    if jump > 0 and jump & (jump - 1) == 0:
        return jump.bit_length() - 1
    return None


def branch_table_report(start: int, max_rows: int = 10_000) -> BranchTableReport:
    """Return the finite jump/division branch table for one start value."""

    if start <= 0:
        raise ValueError("start must be positive")
    if max_rows < 0:
        raise ValueError("max_rows must be nonnegative")

    x = start
    ordinary_steps = 0
    while x % 2 == 0 and x != 1:
        x = collatz_step(x)
        ordinary_steps += 1
    rows: list[BranchRow] = []
    cumulative = ordinary_steps
    terminal_power: int | None = None

    for index in range(1, max_rows + 1):
        if x == 1:
            break
        odd_start = x
        terminal_power = terminal_power_exponent_before_one(odd_start)
        x, divisions = accelerated_step(x)
        jump_value = 3 * odd_start + 1
        cumulative += divisions
        ordinary_steps += 1 + divisions
        rows.append(
            BranchRow(
                index=index,
                odd_start=odd_start,
                jump_value=jump_value,
                divisions=divisions,
                odd_end=x,
                cumulative_divisions=cumulative,
            )
        )
    return BranchTableReport(
        type="branch_table_report",
        status="finite_branch_table_not_collatz_proof",
        start=start,
        reached_one=x == 1,
        rows=tuple(rows),
        total_divisions=cumulative,
        ordinary_steps=ordinary_steps,
        terminal_power_exponent=terminal_power if x == 1 else None,
    )
