"""Bootstrap and saddlepoint calibration for renewal-scale descent rates."""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class BootstrapInterval:
    quantity: str
    estimate: float
    q025: float
    q500: float
    q975: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SaddlepointTailEstimate:
    excursions: int
    probability_sum_nonnegative: float
    rate_with_prefactor: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenewalBootstrapCalibrationReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    bootstrap_seed: int
    bootstrap_repetitions: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    histogram_bin_width: float
    histogram_bins: tuple[tuple[int, int], ...]
    mean_delta_log2: float
    variance_delta_log2: float
    cramer_rate_I0: float
    cramer_lambda: float
    tilted_variance_at_lambda: float
    bootstrap_intervals: tuple[BootstrapInterval, ...]
    saddlepoint_tail_estimates: tuple[SaddlepointTailEstimate, ...]
    method_caveat: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "bootstrap_seed": self.bootstrap_seed,
            "bootstrap_repetitions": self.bootstrap_repetitions,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "histogram_bin_width": self.histogram_bin_width,
            "histogram_bins": [list(item) for item in self.histogram_bins],
            "mean_delta_log2": self.mean_delta_log2,
            "variance_delta_log2": self.variance_delta_log2,
            "cramer_rate_I0": self.cramer_rate_I0,
            "cramer_lambda": self.cramer_lambda,
            "tilted_variance_at_lambda": self.tilted_variance_at_lambda,
            "bootstrap_intervals": [
                interval.to_json_dict() for interval in self.bootstrap_intervals
            ],
            "saddlepoint_tail_estimates": [
                item.to_json_dict() for item in self.saddlepoint_tail_estimates
            ],
            "method_caveat": self.method_caveat,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _logsumexp(values: list[float]) -> float:
    if not values:
        return float("-inf")
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    pos = q * (len(ordered) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def _histogram_stats(
    histogram: Counter[int],
    bin_width: float,
) -> tuple[float, float, float, float, float]:
    total = sum(histogram.values())
    if total <= 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    centers = [bucket * bin_width for bucket in histogram]
    counts = [histogram[bucket] for bucket in histogram]
    mean = sum(center * count for center, count in zip(centers, counts)) / total
    second = sum(center * center * count for center, count in zip(centers, counts)) / total
    variance = max(0.0, second - mean * mean)
    rate, lam, tilted_variance = _cramer_rate_from_histogram(histogram, bin_width)
    return mean, variance, rate, lam, tilted_variance


def _cramer_rate_from_histogram(
    histogram: Counter[int],
    bin_width: float,
) -> tuple[float, float, float]:
    total = sum(histogram.values())
    if total <= 0:
        return 0.0, 0.0, 0.0
    centers = [bucket * bin_width for bucket in histogram]
    log_counts = [math.log(histogram[bucket]) for bucket in histogram]
    log_total = math.log(total)

    def log_mgf(lam: float) -> float:
        return _logsumexp(
            [log_count + lam * center for log_count, center in zip(log_counts, centers)]
        ) - log_total

    lo = 0.0
    hi = 20.0
    inv_phi = (math.sqrt(5.0) - 1.0) / 2.0
    inv_phi_sq = (3.0 - math.sqrt(5.0)) / 2.0
    x1 = lo + inv_phi_sq * (hi - lo)
    x2 = lo + inv_phi * (hi - lo)
    f1 = log_mgf(x1)
    f2 = log_mgf(x2)
    for _ in range(80):
        if f1 < f2:
            hi = x2
            x2 = x1
            f2 = f1
            x1 = lo + inv_phi_sq * (hi - lo)
            f1 = log_mgf(x1)
        else:
            lo = x1
            x1 = x2
            f1 = f2
            x2 = lo + inv_phi * (hi - lo)
            f2 = log_mgf(x2)
    lam = (lo + hi) / 2.0
    candidates = [(0.0, log_mgf(0.0)), (lam, log_mgf(lam)), (20.0, log_mgf(20.0))]
    lam, best_log_mgf = min(candidates, key=lambda item: item[1])
    if lam == 0.0:
        return 0.0, 0.0, 0.0
    terms = [log_count + lam * center for log_count, center in zip(log_counts, centers)]
    normalizer = _logsumexp(terms)
    weights = [math.exp(term - normalizer) for term in terms]
    tilted_mean = sum(weight * center for weight, center in zip(weights, centers))
    tilted_second = sum(weight * center * center for weight, center in zip(weights, centers))
    tilted_variance = max(0.0, tilted_second - tilted_mean * tilted_mean)
    return max(0.0, -best_log_mgf), lam, tilted_variance


def _sample_renewal_histogram(
    sample_count: int,
    start_min: int,
    start_max: int,
    random_seed: int,
    max_steps_per_orbit: int,
    histogram_bin_width: float,
) -> tuple[Counter[int], int, int, int, int]:
    rng = random.Random(random_seed)
    histogram: Counter[int] = Counter()
    completed = 0
    truncated = 0
    total_steps = 0
    total_excursions = 0
    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        while x != 1 and steps < max_steps_per_orbit:
            x, _valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                histogram[int(round(delta / histogram_bin_width))] += 1
                total_excursions += 1
                excursion_start = x
        if x == 1:
            completed += 1
        else:
            truncated += 1
    return histogram, completed, truncated, total_steps, total_excursions


def _bootstrap_histogram(
    histogram: Counter[int],
    repetitions: int,
    seed: int,
) -> list[Counter[int]]:
    import numpy as np

    rng = np.random.default_rng(seed)
    buckets = list(histogram)
    counts = np.array([histogram[bucket] for bucket in buckets], dtype=np.int64)
    total = int(counts.sum())
    probabilities = counts / total
    samples: list[Counter[int]] = []
    for _ in range(repetitions):
        resampled = rng.multinomial(total, probabilities)
        samples.append(
            Counter(
                {
                    bucket: int(count)
                    for bucket, count in zip(buckets, resampled)
                    if count
                }
            )
        )
    return samples


def _saddlepoint_tails(
    rate: float,
    lam: float,
    tilted_variance: float,
    horizons: tuple[int, ...],
) -> tuple[SaddlepointTailEstimate, ...]:
    estimates: list[SaddlepointTailEstimate] = []
    for horizon in horizons:
        if lam <= 0.0 or tilted_variance <= 0.0 or horizon <= 0:
            probability = 1.0
            rate_with_prefactor = 0.0
        else:
            prefactor = 1.0 / (
                lam * math.sqrt(2.0 * math.pi * horizon * tilted_variance)
            )
            probability = min(1.0, prefactor * math.exp(-horizon * rate))
            rate_with_prefactor = -math.log(probability) / horizon if probability > 0.0 else float("inf")
        estimates.append(
            SaddlepointTailEstimate(
                excursions=horizon,
                probability_sum_nonnegative=probability,
                rate_with_prefactor=rate_with_prefactor,
            )
        )
    return tuple(estimates)


def renewal_bootstrap_calibration_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    bootstrap_seed: int = 1,
    bootstrap_repetitions: int = 500,
    max_steps_per_orbit: int = 10_000,
    histogram_bin_width: float = 0.005,
    saddlepoint_horizons: tuple[int, ...] = (10, 100, 1000),
) -> RenewalBootstrapCalibrationReport:
    """Bootstrap the renewal increment law and compute a saddlepoint tail model."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    if bootstrap_repetitions < 1:
        raise ValueError("bootstrap_repetitions must be positive")
    histogram, completed, truncated, steps, excursions = _sample_renewal_histogram(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
        histogram_bin_width=histogram_bin_width,
    )
    mean, variance, rate, lam, tilted_variance = _histogram_stats(
        histogram, histogram_bin_width
    )
    boot_means: list[float] = []
    boot_variances: list[float] = []
    boot_rates: list[float] = []
    boot_lambdas: list[float] = []
    for sampled in _bootstrap_histogram(histogram, bootstrap_repetitions, bootstrap_seed):
        boot_mean, boot_variance, boot_rate, boot_lambda, _boot_tilted_variance = (
            _histogram_stats(sampled, histogram_bin_width)
        )
        boot_means.append(boot_mean)
        boot_variances.append(boot_variance)
        boot_rates.append(boot_rate)
        boot_lambdas.append(boot_lambda)

    intervals = (
        BootstrapInterval(
            quantity="mean_delta_log2",
            estimate=mean,
            q025=_quantile(boot_means, 0.025),
            q500=_quantile(boot_means, 0.5),
            q975=_quantile(boot_means, 0.975),
        ),
        BootstrapInterval(
            quantity="variance_delta_log2",
            estimate=variance,
            q025=_quantile(boot_variances, 0.025),
            q500=_quantile(boot_variances, 0.5),
            q975=_quantile(boot_variances, 0.975),
        ),
        BootstrapInterval(
            quantity="cramer_rate_I0",
            estimate=rate,
            q025=_quantile(boot_rates, 0.025),
            q500=_quantile(boot_rates, 0.5),
            q975=_quantile(boot_rates, 0.975),
        ),
        BootstrapInterval(
            quantity="cramer_lambda",
            estimate=lam,
            q025=_quantile(boot_lambdas, 0.025),
            q500=_quantile(boot_lambdas, 0.5),
            q975=_quantile(boot_lambdas, 0.975),
        ),
    )
    return RenewalBootstrapCalibrationReport(
        type="renewal_bootstrap_calibration",
        status="bootstrap_and_saddlepoint_calibration_not_collatz_proof",
        sample_count=sample_count,
        random_seed=random_seed,
        bootstrap_seed=bootstrap_seed,
        bootstrap_repetitions=bootstrap_repetitions,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=steps,
        total_excursions=excursions,
        histogram_bin_width=histogram_bin_width,
        histogram_bins=tuple(sorted(histogram.items())),
        mean_delta_log2=mean,
        variance_delta_log2=variance,
        cramer_rate_I0=rate,
        cramer_lambda=lam,
        tilted_variance_at_lambda=tilted_variance,
        bootstrap_intervals=intervals,
        saddlepoint_tail_estimates=_saddlepoint_tails(
            rate, lam, tilted_variance, saddlepoint_horizons
        ),
        method_caveat=(
            "Bootstrap resamples the observed binned renewal-increment law. "
            "Saddlepoint tails use the empirical law's Cramer tilt and should be "
            "read as calibration/Bahadur-Rao-style approximations, not rigorous "
            "bounds for all Collatz orbits."
        ),
    )
