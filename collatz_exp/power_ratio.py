"""Proportional-power-ratio diagnostics for Collatz orbits."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, log

from .tuple_merges import collatz_step


@dataclass(frozen=True)
class PowerRatioPoint:
    """One orbit point mapped between consecutive powers of ``base``."""

    index: int
    value: int
    base: float
    exponent: int
    ratio: float


@dataclass(frozen=True)
class BasePowerRatioSummary:
    """Summary statistics for one base."""

    base: float
    points: tuple[PowerRatioPoint, ...]
    mean_ratio: float
    max_ratio: float
    period44_mean_abs_delta: float | None
    period44_max_abs_delta: float | None


@dataclass(frozen=True)
class PowerRatioReport:
    """Finite proportional-power-ratio orbit diagnostic."""

    type: str
    status: str
    start: int
    orbit_length: int
    reached_one: bool
    summaries: tuple[BasePowerRatioSummary, ...]


def collatz_orbit(start: int, max_steps: int = 10_000) -> tuple[int, ...]:
    """Return an ordinary Collatz orbit prefix, stopping at 1 if reached."""

    if start <= 0:
        raise ValueError("start must be positive")
    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    values = [start]
    x = start
    for _ in range(max_steps):
        if x == 1:
            break
        x = collatz_step(x)
        values.append(x)
    return tuple(values)


def power_ratio(value: int, base: float) -> tuple[int, float]:
    """Return ``(k, r)`` with ``base^k <= value < base^(k+1)`` and ``r in [0,1)``."""

    if value <= 0:
        raise ValueError("value must be positive")
    if base <= 1:
        raise ValueError("base must be greater than one")
    exponent = max(0, floor(log(value, base)))
    lower = base**exponent
    upper = lower * base
    while upper <= value:
        exponent += 1
        lower = upper
        upper *= base
    while lower > value and exponent > 0:
        exponent -= 1
        upper = lower
        lower /= base
    return exponent, (value - lower) / (upper - lower)


def power_ratio_points(
    orbit: tuple[int, ...],
    base: float,
) -> tuple[PowerRatioPoint, ...]:
    """Map an orbit to proportional-power-ratio points for one base."""

    points: list[PowerRatioPoint] = []
    for index, value in enumerate(orbit):
        exponent, ratio = power_ratio(value, base)
        points.append(
            PowerRatioPoint(
                index=index,
                value=value,
                base=base,
                exponent=exponent,
                ratio=ratio,
            )
        )
    return tuple(points)


def _period_delta(points: tuple[PowerRatioPoint, ...], period: int) -> tuple[float, float] | None:
    if len(points) <= period:
        return None
    deltas = [
        abs(points[index + period].ratio - points[index].ratio)
        for index in range(len(points) - period)
    ]
    return sum(deltas) / len(deltas), max(deltas)


def base_power_ratio_summary(
    orbit: tuple[int, ...],
    base: float,
    period: int = 44,
) -> BasePowerRatioSummary:
    """Summarize proportional-power-ratio points for one base."""

    points = power_ratio_points(orbit, base)
    ratios = [point.ratio for point in points]
    period_stats = _period_delta(points, period)
    return BasePowerRatioSummary(
        base=base,
        points=points,
        mean_ratio=sum(ratios) / len(ratios),
        max_ratio=max(ratios),
        period44_mean_abs_delta=None if period_stats is None else period_stats[0],
        period44_max_abs_delta=None if period_stats is None else period_stats[1],
    )


def power_ratio_report(
    start: int = 27,
    bases: tuple[float, ...] = (2.0, 3.0, 6.0),
    max_steps: int = 10_000,
) -> PowerRatioReport:
    """Build a finite graph-feature report for one ordinary Collatz orbit."""

    orbit = collatz_orbit(start, max_steps=max_steps)
    summaries = tuple(base_power_ratio_summary(orbit, base) for base in bases)
    return PowerRatioReport(
        type="power_ratio_orbit_report",
        status="finite_visual_diagnostic_not_collatz_proof",
        start=start,
        orbit_length=len(orbit) - 1,
        reached_one=orbit[-1] == 1,
        summaries=summaries,
    )
