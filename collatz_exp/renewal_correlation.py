"""Long-range correlation audit of renewal excursion series.

Defensive check against Polli et al. (J. Phys. Complex. 5, 2024): they report
long-range power-law correlations in Collatz hailstone sequences, which the
framework's IID renewal model does not predict. This module measures, on long
orbits from large random starts, (a) pooled within-orbit autocorrelation and
(b) detrended fluctuation analysis (DFA) exponents for three series — the
per-excursion log2 drift, the per-excursion step count, and the per-step
2-adic valuation — each against a within-orbit shuffle surrogate as the IID
null. DFA alpha ~= 0.5 and ACF inside the null band mean the IID renewal
assumption survives at the tested scale; alpha substantially above 0.5 with
ACF outside the band would flag Polli-style long-range memory.

Finite empirical diagnostic at tested orbit lengths, not a theorem.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass

from .core import accelerated_step, v2

_STATUS_PRIORITY = (
    "long_range_persistent_candidate",
    "anti_persistent_candidate",
    "short_range_correlations_only",
    "iid_consistent",
)


@dataclass
class SeriesCorrelationResult:
    name: str
    total_values: int
    acf: tuple[float, ...]
    acf_pair_counts: tuple[int, ...]
    acf_null_band: float
    acf_max_abs: float
    acf_max_abs_lag: int
    surrogate_acf_max_abs: float
    dfa_alpha: float | None
    surrogate_dfa_alpha: float | None
    dfa_box_sizes: tuple[int, ...]
    dfa_log2_fluctuations: tuple[float, ...]
    status: str

    def to_json_dict(self) -> dict:
        return {
            "name": self.name,
            "total_values": self.total_values,
            "acf": list(self.acf),
            "acf_pair_counts": list(self.acf_pair_counts),
            "acf_null_band": self.acf_null_band,
            "acf_max_abs": self.acf_max_abs,
            "acf_max_abs_lag": self.acf_max_abs_lag,
            "surrogate_acf_max_abs": self.surrogate_acf_max_abs,
            "dfa_alpha": self.dfa_alpha,
            "surrogate_dfa_alpha": self.surrogate_dfa_alpha,
            "dfa_box_sizes": list(self.dfa_box_sizes),
            "dfa_log2_fluctuations": list(self.dfa_log2_fluctuations),
            "status": self.status,
        }


@dataclass
class RenewalCorrelationReport:
    orbit_count: int
    start_bits: int
    random_seed: int
    max_lag: int
    completed_orbits: int
    truncated_orbits: int
    total_excursions: int
    total_steps: int
    mean_excursions_per_orbit: float
    series: tuple[SeriesCorrelationResult, ...]
    overall_status: str
    note: str

    def to_json_dict(self) -> dict:
        return {
            "orbit_count": self.orbit_count,
            "start_bits": self.start_bits,
            "random_seed": self.random_seed,
            "max_lag": self.max_lag,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_excursions": self.total_excursions,
            "total_steps": self.total_steps,
            "mean_excursions_per_orbit": self.mean_excursions_per_orbit,
            "series": [item.to_json_dict() for item in self.series],
            "overall_status": self.overall_status,
            "note": self.note,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _collect_orbit_series(
    orbit_count: int,
    start_bits: int,
    random_seed: int,
    max_steps_per_orbit: int,
) -> tuple[list[list[float]], list[list[float]], list[list[float]], int, int]:
    """Per-orbit series: excursion deltas, excursion step counts, step valuations."""
    rng = random.Random(random_seed)
    delta_series: list[list[float]] = []
    steps_series: list[list[float]] = []
    valuation_series: list[list[float]] = []
    completed = 0
    truncated = 0
    for _ in range(orbit_count):
        x = rng.getrandbits(start_bits) | (1 << (start_bits - 1)) | 1
        deltas: list[float] = []
        excursion_steps: list[float] = []
        valuations: list[float] = []
        steps = 0
        excursion_start = x
        excursion_m = 0
        while x != 1 and steps < max_steps_per_orbit:
            x, valuation = accelerated_step(x)
            valuations.append(float(valuation))
            steps += 1
            excursion_m += 1
            if x == 1 or v2(x + 1) >= 2:
                deltas.append(math.log2(x) - math.log2(excursion_start))
                excursion_steps.append(float(excursion_m))
                excursion_start = x
                excursion_m = 0
        if x == 1:
            completed += 1
        else:
            truncated += 1
        delta_series.append(deltas)
        steps_series.append(excursion_steps)
        valuation_series.append(valuations)
    return delta_series, steps_series, valuation_series, completed, truncated


def pooled_autocorrelation(
    series_list: list[list[float]],
    max_lag: int,
) -> tuple[list[float], list[int]]:
    """Within-orbit mean-centered ACF, pooled across orbits."""
    if max_lag < 1:
        raise ValueError("max_lag must be positive")
    numerators = [0.0] * max_lag
    pair_counts = [0] * max_lag
    variance_sum = 0.0
    variance_count = 0
    for series in series_list:
        n = len(series)
        if n < 2:
            continue
        mean = sum(series) / n
        centered = [value - mean for value in series]
        variance_sum += sum(value * value for value in centered)
        variance_count += n
        for lag in range(1, min(max_lag, n - 1) + 1):
            total = 0.0
            for index in range(n - lag):
                total += centered[index] * centered[index + lag]
            numerators[lag - 1] += total
            pair_counts[lag - 1] += n - lag
    if variance_count == 0 or variance_sum == 0.0:
        return [0.0] * max_lag, pair_counts
    variance = variance_sum / variance_count
    acf = [
        (numerators[lag] / pair_counts[lag]) / variance if pair_counts[lag] else 0.0
        for lag in range(max_lag)
    ]
    return acf, pair_counts


def _linear_residual_mean_square(segment: list[float]) -> float:
    n = len(segment)
    if n < 2:
        return 0.0
    sum_t = n * (n - 1) / 2.0
    sum_tt = (n - 1) * n * (2 * n - 1) / 6.0
    sum_y = sum(segment)
    sum_ty = sum(index * value for index, value in enumerate(segment))
    denom = n * sum_tt - sum_t * sum_t
    if denom == 0.0:
        return 0.0
    slope = (n * sum_ty - sum_t * sum_y) / denom
    intercept = (sum_y - slope * sum_t) / n
    residual = 0.0
    for index, value in enumerate(segment):
        diff = value - (intercept + slope * index)
        residual += diff * diff
    return residual / n


def dfa_alpha(
    series_list: list[list[float]],
    box_sizes: tuple[int, ...] | None = None,
) -> tuple[float | None, tuple[int, ...], tuple[float, ...]]:
    """Pooled detrended fluctuation exponent across orbits.

    Returns (alpha, box_sizes_used, log2 F(s) per box size); alpha is None
    when fewer than two box sizes have data.
    """
    max_length = max((len(series) for series in series_list), default=0)
    if box_sizes is None:
        sizes = []
        size = 4
        while size <= max(4, max_length // 4):
            sizes.append(size)
            size *= 2
        box_sizes = tuple(sizes)
    residual_sums = {size: 0.0 for size in box_sizes}
    box_counts = {size: 0 for size in box_sizes}
    for series in series_list:
        n = len(series)
        if n < 8:
            continue
        mean = sum(series) / n
        profile = []
        running = 0.0
        for value in series:
            running += value - mean
            profile.append(running)
        for size in box_sizes:
            n_boxes = n // size
            for box in range(n_boxes):
                segment = profile[box * size : (box + 1) * size]
                residual_sums[size] += _linear_residual_mean_square(segment)
                box_counts[size] += 1
    used_sizes = [size for size in box_sizes if box_counts[size] > 0]
    log_points: list[tuple[float, float]] = []
    log_fluctuations: list[float] = []
    for size in used_sizes:
        fluctuation_sq = residual_sums[size] / box_counts[size]
        if fluctuation_sq <= 0.0:
            log_fluctuations.append(float("-inf"))
            continue
        log_f = 0.5 * math.log2(fluctuation_sq)
        log_fluctuations.append(log_f)
        log_points.append((math.log2(size), log_f))
    if len(log_points) < 2:
        return None, tuple(used_sizes), tuple(log_fluctuations)
    n = len(log_points)
    sum_x = sum(point[0] for point in log_points)
    sum_y = sum(point[1] for point in log_points)
    sum_xx = sum(point[0] * point[0] for point in log_points)
    sum_xy = sum(point[0] * point[1] for point in log_points)
    denom = n * sum_xx - sum_x * sum_x
    if denom == 0.0:
        return None, tuple(used_sizes), tuple(log_fluctuations)
    alpha = (n * sum_xy - sum_x * sum_y) / denom
    return alpha, tuple(used_sizes), tuple(log_fluctuations)


def _shuffled_copy(
    series_list: list[list[float]],
    random_seed: int,
) -> list[list[float]]:
    rng = random.Random(random_seed)
    shuffled = []
    for series in series_list:
        copy = list(series)
        rng.shuffle(copy)
        shuffled.append(copy)
    return shuffled


def _series_result(
    name: str,
    series_list: list[list[float]],
    max_lag: int,
    surrogate_seed: int,
) -> SeriesCorrelationResult:
    acf, pair_counts = pooled_autocorrelation(series_list, max_lag)
    total_values = sum(len(series) for series in series_list)
    abs_acf = [abs(value) for value in acf]
    max_abs = max(abs_acf, default=0.0)
    max_abs_lag = abs_acf.index(max_abs) + 1 if acf else 0
    pairs_lag1 = pair_counts[0] if pair_counts else 0
    null_band = 1.96 / math.sqrt(pairs_lag1) if pairs_lag1 else float("inf")
    alpha, box_sizes, log_fluctuations = dfa_alpha(series_list)

    surrogate = _shuffled_copy(series_list, surrogate_seed)
    surrogate_acf, _ = pooled_autocorrelation(surrogate, max_lag)
    surrogate_max_abs = max((abs(value) for value in surrogate_acf), default=0.0)
    surrogate_alpha, _, _ = dfa_alpha(surrogate)

    status = "iid_consistent"
    if alpha is not None and surrogate_alpha is not None:
        threshold = max(0.1, abs(surrogate_alpha - 0.5) + 0.05)
        if alpha - 0.5 > threshold:
            status = "long_range_persistent_candidate"
        elif 0.5 - alpha > threshold:
            status = "anti_persistent_candidate"
    if status == "iid_consistent" and max_abs > max(
        2.0 * null_band, 2.0 * surrogate_max_abs
    ):
        status = "short_range_correlations_only"

    return SeriesCorrelationResult(
        name=name,
        total_values=total_values,
        acf=tuple(acf),
        acf_pair_counts=tuple(pair_counts),
        acf_null_band=null_band,
        acf_max_abs=max_abs,
        acf_max_abs_lag=max_abs_lag,
        surrogate_acf_max_abs=surrogate_max_abs,
        dfa_alpha=alpha,
        surrogate_dfa_alpha=surrogate_alpha,
        dfa_box_sizes=box_sizes,
        dfa_log2_fluctuations=log_fluctuations,
        status=status,
    )


def renewal_correlation_report(
    orbit_count: int = 150,
    start_bits: int = 1000,
    random_seed: int = 0,
    max_lag: int = 50,
    max_steps_per_orbit: int = 200_000,
) -> RenewalCorrelationReport:
    if orbit_count < 1:
        raise ValueError("orbit_count must be positive")
    if start_bits < 8:
        raise ValueError("start_bits must be at least 8")
    delta_series, steps_series, valuation_series, completed, truncated = (
        _collect_orbit_series(
            orbit_count=orbit_count,
            start_bits=start_bits,
            random_seed=random_seed,
            max_steps_per_orbit=max_steps_per_orbit,
        )
    )
    total_excursions = sum(len(series) for series in delta_series)
    total_steps = sum(len(series) for series in valuation_series)
    series = (
        _series_result(
            "excursion_delta_log2", delta_series, max_lag, random_seed + 1
        ),
        _series_result(
            "excursion_step_count", steps_series, max_lag, random_seed + 2
        ),
        _series_result(
            "step_valuation", valuation_series, max_lag, random_seed + 3
        ),
    )
    overall = "iid_consistent"
    for candidate in _STATUS_PRIORITY:
        if any(item.status == candidate for item in series):
            overall = candidate
            break
    note = (
        "Finite diagnostic on {orbits} orbits from random {bits}-bit odd starts; "
        "IID-null via within-orbit shuffles. DFA alpha near 0.5 and ACF inside "
        "the null band support the IID renewal model at this scale; this does "
        "not preclude correlations at longer scales.".format(
            orbits=orbit_count, bits=start_bits
        )
    )
    return RenewalCorrelationReport(
        orbit_count=orbit_count,
        start_bits=start_bits,
        random_seed=random_seed,
        max_lag=max_lag,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_excursions=total_excursions,
        total_steps=total_steps,
        mean_excursions_per_orbit=total_excursions / orbit_count,
        series=series,
        overall_status=overall,
        note=note,
    )


def format_renewal_correlation_report(report: RenewalCorrelationReport) -> str:
    lines = [
        "orbits={orbits} start_bits={bits} seed={seed} "
        "completed={completed} truncated={truncated} "
        "excursions={excursions} steps={steps}".format(
            orbits=report.orbit_count,
            bits=report.start_bits,
            seed=report.random_seed,
            completed=report.completed_orbits,
            truncated=report.truncated_orbits,
            excursions=report.total_excursions,
            steps=report.total_steps,
        )
    ]
    for item in report.series:
        alpha = "None" if item.dfa_alpha is None else f"{item.dfa_alpha:.4f}"
        surrogate_alpha = (
            "None"
            if item.surrogate_dfa_alpha is None
            else f"{item.surrogate_dfa_alpha:.4f}"
        )
        lines.append(
            "  {name}: acf_max|.|={acf_max:.4f}@lag{lag} band={band:.4f} "
            "surrogate_max={surrogate:.4f} dfa_alpha={alpha} "
            "surrogate_alpha={surrogate_alpha} -> {status}".format(
                name=item.name,
                acf_max=item.acf_max_abs,
                lag=item.acf_max_abs_lag,
                band=item.acf_null_band,
                surrogate=item.surrogate_acf_max_abs,
                alpha=alpha,
                surrogate_alpha=surrogate_alpha,
                status=item.status,
            )
        )
    lines.append(f"  overall={report.overall_status}")
    return "\n".join(lines)
