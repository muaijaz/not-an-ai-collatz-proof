"""Interval champion diagnostics for ordinary Collatz trajectories."""

from __future__ import annotations

from dataclasses import dataclass

from .tuple_merges import collatz_step


@dataclass(frozen=True)
class OrbitStats:
    start: int
    steps_to_one: int
    max_value: int
    reached_one: bool


@dataclass(frozen=True)
class ChampionReport:
    type: str
    status: str
    start: int
    stop: int
    checked: int
    max_height_champion: OrbitStats
    longest_stopping_champion: OrbitStats


def orbit_stats(start: int, max_steps: int = 100_000) -> OrbitStats:
    """Return ordinary Collatz stopping time and max height for one start."""

    if start <= 0:
        raise ValueError("start must be positive")
    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    x = start
    max_value = x
    for step in range(1, max_steps + 1):
        if x == 1:
            return OrbitStats(
                start=start,
                steps_to_one=step - 1,
                max_value=max_value,
                reached_one=True,
            )
        x = collatz_step(x)
        max_value = max(max_value, x)
    return OrbitStats(
        start=start,
        steps_to_one=max_steps,
        max_value=max_value,
        reached_one=x == 1,
    )


def champion_report(
    start: int = 1,
    stop: int = 10_000,
    max_steps: int = 100_000,
) -> ChampionReport:
    """Scan ``start <= n <= stop`` for max-height and longest-time champions."""

    if start < 1:
        raise ValueError("start must be positive")
    if stop < start:
        raise ValueError("stop must be at least start")
    stats = tuple(orbit_stats(n, max_steps=max_steps) for n in range(start, stop + 1))
    height = max(stats, key=lambda item: (item.max_value, -item.start))
    stopping = max(stats, key=lambda item: (item.steps_to_one, -item.start))
    return ChampionReport(
        type="interval_champion_report",
        status="finite_interval_scan_not_collatz_proof",
        start=start,
        stop=stop,
        checked=len(stats),
        max_height_champion=height,
        longest_stopping_champion=stopping,
    )
