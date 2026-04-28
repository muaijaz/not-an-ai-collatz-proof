"""Renewal-scale orbit diagnostics between tail-entry events."""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from .core import accelerated_step, v2


@dataclass(frozen=True)
class RenewalDescentReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    mean_delta_log2: float | None
    variance_delta_log2: float | None
    min_delta_log2: float | None
    max_delta_log2: float | None
    fraction_nonnegative_delta_log2: float | None
    mean_m_PE: float | None
    mean_A_PE: float | None
    cdf_delta_log2: tuple[tuple[float, float], ...]
    hoeffding_failure_bounds: dict[str, float | None]
    sample_excursions: tuple[dict[str, Any], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["cdf_delta_log2"] = [list(item) for item in self.cdf_delta_log2]
        data["sample_excursions"] = [dict(item) for item in self.sample_excursions]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class SpikeSegmentReport:
    segment: str
    excursions: int
    probability: float
    mean_delta_log2: float
    drift_contribution: float
    mean_m_PE: float
    mean_A_PE: float
    mgf_positive_tail: dict[str, float]
    mgf_prompt_negative_sign: dict[str, float]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenewalSpikeDecompositionReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    mean_delta_log2: float | None
    variance_delta_log2: float | None
    fraction_nonnegative_delta_log2: float | None
    lambda_values: tuple[float, ...]
    total_mgf_positive_tail: dict[str, float]
    total_mgf_prompt_negative_sign: dict[str, float]
    cramer_rate_I0_grid: float | None
    cramer_rate_lambda: float | None
    cramer_rate_method: str
    bernstein_rate: float | None
    histogram_bin_width: float
    segments: tuple[SpikeSegmentReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "mean_delta_log2": self.mean_delta_log2,
            "variance_delta_log2": self.variance_delta_log2,
            "fraction_nonnegative_delta_log2": self.fraction_nonnegative_delta_log2,
            "lambda_values": list(self.lambda_values),
            "total_mgf_positive_tail": dict(self.total_mgf_positive_tail),
            "total_mgf_prompt_negative_sign": dict(self.total_mgf_prompt_negative_sign),
            "cramer_rate_I0_grid": self.cramer_rate_I0_grid,
            "cramer_rate_lambda": self.cramer_rate_lambda,
            "cramer_rate_method": self.cramer_rate_method,
            "bernstein_rate": self.bernstein_rate,
            "histogram_bin_width": self.histogram_bin_width,
            "segments": [segment.to_json_dict() for segment in self.segments],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class PerKMGFSegmentReport:
    segment: str
    excursions: int
    probability: float
    mean_delta_log2: float
    drift_contribution: float
    mgf_positive_tail: dict[str, float]
    weighted_mgf_positive_tail: dict[str, float]
    grid_optimal_lambda: float | None
    grid_optimal_rate: float | None
    geometric_ratio_from_k4: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrbitRenewalPerKMGFReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    mean_delta_log2: float | None
    variance_delta_log2: float | None
    fraction_nonnegative_delta_log2: float | None
    lambda_values: tuple[float, ...]
    aggregate_mgf_positive_tail: dict[str, float]
    implied_cramer_rate_grid: float | None
    implied_cramer_lambda_grid: float | None
    bottleneck_segment_at_best_lambda: str | None
    bottleneck_weighted_mgf_at_best_lambda: float | None
    geometric_reference_segment: str | None
    segments: tuple[PerKMGFSegmentReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "mean_delta_log2": self.mean_delta_log2,
            "variance_delta_log2": self.variance_delta_log2,
            "fraction_nonnegative_delta_log2": self.fraction_nonnegative_delta_log2,
            "lambda_values": list(self.lambda_values),
            "aggregate_mgf_positive_tail": dict(self.aggregate_mgf_positive_tail),
            "implied_cramer_rate_grid": self.implied_cramer_rate_grid,
            "implied_cramer_lambda_grid": self.implied_cramer_lambda_grid,
            "bottleneck_segment_at_best_lambda": self.bottleneck_segment_at_best_lambda,
            "bottleneck_weighted_mgf_at_best_lambda": (
                self.bottleneck_weighted_mgf_at_best_lambda
            ),
            "geometric_reference_segment": self.geometric_reference_segment,
            "segments": [segment.to_json_dict() for segment in self.segments],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class MarkovCramerLambdaReport:
    lambda_value: float
    spectral_radius: float
    markov_rate: float
    iid_pair_target_mgf: float
    iid_pair_target_rate: float
    iid_all_excursion_mgf: float
    iid_all_excursion_rate: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarkovCramerTransitionReport:
    source_segment: str
    target_segment: str
    transitions: int
    conditional_probability: float
    mean_target_delta_log2: float
    mgf_positive_tail: dict[str, float]
    tilted_entries: dict[str, float]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrbitRenewalMarkovCramerReport:
    type: str
    status: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    markov_pairs: int
    state_labels: tuple[str, ...]
    lambda_values: tuple[float, ...]
    best_markov_rate: float | None
    best_markov_lambda: float | None
    best_iid_pair_target_rate: float | None
    best_iid_all_excursion_rate: float | None
    best_iid_all_excursion_lambda: float | None
    markov_rate_lift_over_iid_at_best: float | None
    markov_rate_lift_over_iid_all_grid: float | None
    mean_pair_target_delta_log2: float | None
    lambda_reports: tuple[MarkovCramerLambdaReport, ...]
    transition_reports: tuple[MarkovCramerTransitionReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "markov_pairs": self.markov_pairs,
            "state_labels": list(self.state_labels),
            "lambda_values": list(self.lambda_values),
            "best_markov_rate": self.best_markov_rate,
            "best_markov_lambda": self.best_markov_lambda,
            "best_iid_pair_target_rate": self.best_iid_pair_target_rate,
            "best_iid_all_excursion_rate": self.best_iid_all_excursion_rate,
            "best_iid_all_excursion_lambda": self.best_iid_all_excursion_lambda,
            "markov_rate_lift_over_iid_at_best": (
                self.markov_rate_lift_over_iid_at_best
            ),
            "markov_rate_lift_over_iid_all_grid": (
                self.markov_rate_lift_over_iid_all_grid
            ),
            "mean_pair_target_delta_log2": self.mean_pair_target_delta_log2,
            "lambda_reports": [
                item.to_json_dict() for item in self.lambda_reports
            ],
            "transition_reports": [
                item.to_json_dict() for item in self.transition_reports
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class N0StabilityRangeReport:
    start_min: int
    start_max: int
    log10_midpoint: float
    sample_count: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    mean_excursions_per_orbit: float
    mean_steps_per_orbit: float
    mean_delta_log2: float | None
    variance_delta_log2: float | None
    fraction_nonnegative_delta_log2: float | None
    cramer_rate_I0: float | None
    cramer_rate_lambda: float | None
    max_a_1_probability: float | None
    max_a_1_mean_delta_log2: float | None
    max_a_1_drift_contribution: float | None
    max_a_1_weighted_mgf_at_lambda_star: float | None
    spike_probabilities: dict[str, float]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrbitRenewalN0StabilityReport:
    type: str
    status: str
    sample_count_per_range: int
    random_seed: int
    ranges: tuple[tuple[int, int], ...]
    max_steps_per_orbit: int
    lambda_source: str
    cramer_rate_slope_per_log10: float | None
    mean_delta_slope_per_log10: float | None
    variance_delta_slope_per_log10: float | None
    cramer_rate_range_width: float | None
    range_reports: tuple[N0StabilityRangeReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "sample_count_per_range": self.sample_count_per_range,
            "random_seed": self.random_seed,
            "ranges": [list(item) for item in self.ranges],
            "max_steps_per_orbit": self.max_steps_per_orbit,
            "lambda_source": self.lambda_source,
            "cramer_rate_slope_per_log10": self.cramer_rate_slope_per_log10,
            "mean_delta_slope_per_log10": self.mean_delta_slope_per_log10,
            "variance_delta_slope_per_log10": self.variance_delta_slope_per_log10,
            "cramer_rate_range_width": self.cramer_rate_range_width,
            "range_reports": [item.to_json_dict() for item in self.range_reports],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _quantile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    if q <= 0.0:
        return sorted_values[0]
    if q >= 1.0:
        return sorted_values[-1]
    index = q * (len(sorted_values) - 1)
    lo = int(math.floor(index))
    hi = int(math.ceil(index))
    if lo == hi:
        return sorted_values[lo]
    weight = index - lo
    return sorted_values[lo] * (1.0 - weight) + sorted_values[hi] * weight


def orbit_renewal_descent_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    cdf_points: tuple[float, ...] = (-8.0, -4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0),
) -> RenewalDescentReport:
    """Aggregate actual accelerated orbits into tail-entry renewal excursions."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    rng = random.Random(random_seed)
    deltas: list[float] = []
    m_values: list[int] = []
    A_values: list[int] = []
    sample_excursions: list[dict[str, Any]] = []
    completed = 0
    truncated = 0
    total_steps = 0

    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        excursion_m = 0
        excursion_A = 0
        while x != 1 and steps < max_steps_per_orbit:
            x, valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            excursion_m += 1
            excursion_A += valuation
            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                deltas.append(delta)
                m_values.append(excursion_m)
                A_values.append(excursion_A)
                if len(sample_excursions) < 100:
                    sample_excursions.append(
                        {
                            "start": excursion_start,
                            "landing": x,
                            "m_PE": excursion_m,
                            "A_PE": excursion_A,
                            "delta_log2": delta,
                            "tail_depth_landing": v2(x + 1) if x > 0 else None,
                        }
                    )
                excursion_start = x
                excursion_m = 0
                excursion_A = 0
        if x == 1:
            completed += 1
        else:
            truncated += 1

    if deltas:
        mean = sum(deltas) / len(deltas)
        variance = sum((value - mean) ** 2 for value in deltas) / len(deltas)
        sorted_deltas = sorted(deltas)
        cdf = tuple(
            (point, sum(value <= point for value in deltas) / len(deltas))
            for point in cdf_points
        )
        nonnegative = sum(value >= 0.0 for value in deltas) / len(deltas)
        span = max(deltas) - min(deltas)
        hoeffding: dict[str, float | None] = {}
        for T in (10, 100, 1000):
            # Bound P(mean_T >= 0) for iid bounded excursion increments.
            if mean < 0.0 and span > 0.0:
                hoeffding[str(T)] = math.exp(-2.0 * T * (0.0 - mean) ** 2 / (span**2))
            else:
                hoeffding[str(T)] = None
        min_delta = sorted_deltas[0]
        max_delta = sorted_deltas[-1]
    else:
        mean = variance = min_delta = max_delta = nonnegative = None
        cdf = ()
        hoeffding = {str(T): None for T in (10, 100, 1000)}

    status = (
        "renewal_excursions_have_negative_mean_delta_log2"
        if mean is not None and mean < 0.0
        else "renewal_excursions_do_not_have_negative_mean_delta_log2"
    )
    return RenewalDescentReport(
        type="orbit_renewal_descent",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        total_excursions=len(deltas),
        mean_delta_log2=mean,
        variance_delta_log2=variance,
        min_delta_log2=min_delta,
        max_delta_log2=max_delta,
        fraction_nonnegative_delta_log2=nonnegative,
        mean_m_PE=None if not m_values else sum(m_values) / len(m_values),
        mean_A_PE=None if not A_values else sum(A_values) / len(A_values),
        cdf_delta_log2=cdf,
        hoeffding_failure_bounds=hoeffding,
        sample_excursions=tuple(sample_excursions),
    )


def _logsumexp(values: list[float]) -> float:
    if not values:
        return float("-inf")
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


def _perron_radius_nonnegative(
    matrix: list[list[float]],
    *,
    iterations: int = 500,
    tolerance: float = 1e-14,
) -> float:
    """Power-method Perron radius for a small nonnegative matrix."""

    n = len(matrix)
    if n == 0 or all(all(value == 0.0 for value in row) for row in matrix):
        return 0.0
    vector = [1.0 / n for _ in range(n)]
    last_rho = 0.0
    rho = 0.0
    for _ in range(iterations):
        next_vector = [
            sum(vector[i] * matrix[i][j] for i in range(n))
            for j in range(n)
        ]
        rho = sum(next_vector)
        if rho == 0.0:
            return 0.0
        next_vector = [value / rho for value in next_vector]
        if abs(rho - last_rho) <= tolerance * max(1.0, abs(rho)):
            return rho
        vector = next_vector
        last_rho = rho
    return rho


def _least_squares_slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    mean_x = sum(point[0] for point in points) / len(points)
    mean_y = sum(point[1] for point in points) / len(points)
    denominator = sum((point[0] - mean_x) ** 2 for point in points)
    if denominator == 0.0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in points) / denominator


def orbit_renewal_spike_decomposition_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    lambda_values: tuple[float, ...] = (0.1, 0.5, 1.0, 2.0, 5.0),
    max_exact_spike: int = 12,
    histogram_bin_width: float = 0.005,
) -> RenewalSpikeDecompositionReport:
    """Decompose renewal increments by maximum valuation spike in the excursion."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    lambdas = tuple(float(value) for value in lambda_values)
    if any(value <= 0.0 for value in lambdas):
        raise ValueError("lambda_values must be positive")
    if histogram_bin_width <= 0.0:
        raise ValueError("histogram_bin_width must be positive")
    rng = random.Random(random_seed)
    segment_data: dict[str, dict[str, Any]] = {}
    histogram: Counter[int] = Counter()
    total = 0
    sum_delta = 0.0
    sum_delta_sq = 0.0
    min_delta = float("inf")
    max_delta = float("-inf")
    nonnegative_count = 0
    total_mgf_pos_sums = {lam: 0.0 for lam in lambdas}
    total_mgf_neg_sums = {lam: 0.0 for lam in lambdas}

    def segment_key(max_valuation: int) -> str:
        return (
            f"{max_valuation}"
            if max_valuation <= max_exact_spike
            else f">{max_exact_spike}"
        )

    def empty_segment() -> dict[str, Any]:
        return {
            "count": 0,
            "sum_delta": 0.0,
            "sum_m": 0.0,
            "sum_A": 0.0,
            "mgf_pos_sums": {lam: 0.0 for lam in lambdas},
            "mgf_neg_sums": {lam: 0.0 for lam in lambdas},
        }

    def record_excursion(
        delta: float,
        excursion_m: int,
        excursion_A: int,
        excursion_max_a: int,
    ) -> None:
        nonlocal total, sum_delta, sum_delta_sq, min_delta, max_delta
        nonlocal nonnegative_count

        total += 1
        sum_delta += delta
        sum_delta_sq += delta * delta
        min_delta = min(min_delta, delta)
        max_delta = max(max_delta, delta)
        if delta >= 0.0:
            nonnegative_count += 1
        histogram[int(round(delta / histogram_bin_width))] += 1
        for lam in lambdas:
            total_mgf_pos_sums[lam] += math.exp(lam * delta)
            total_mgf_neg_sums[lam] += math.exp(-lam * delta)

        key = segment_key(excursion_max_a)
        data = segment_data.setdefault(key, empty_segment())
        data["count"] += 1
        data["sum_delta"] += delta
        data["sum_m"] += excursion_m
        data["sum_A"] += excursion_A
        for lam in lambdas:
            data["mgf_pos_sums"][lam] += math.exp(lam * delta)
            data["mgf_neg_sums"][lam] += math.exp(-lam * delta)

    completed = 0
    truncated = 0
    total_steps = 0
    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        excursion_m = 0
        excursion_A = 0
        excursion_max_a = 0
        while x != 1 and steps < max_steps_per_orbit:
            x, valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            excursion_m += 1
            excursion_A += valuation
            excursion_max_a = max(excursion_max_a, valuation)
            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                record_excursion(
                    delta=delta,
                    excursion_m=excursion_m,
                    excursion_A=excursion_A,
                    excursion_max_a=excursion_max_a,
                )
                excursion_start = x
                excursion_m = 0
                excursion_A = 0
                excursion_max_a = 0
        if x == 1:
            completed += 1
        else:
            truncated += 1

    if total:
        mean = sum_delta / total
        variance = max(0.0, sum_delta_sq / total - mean * mean)
        nonnegative = nonnegative_count / total
        span_upper = max_delta - mean
        bernstein_rate = (
            ((-mean) ** 2) / (2.0 * variance + 2.0 * span_upper * (-mean) / 3.0)
            if mean < 0.0 and variance > 0.0 and span_upper > 0.0
            else None
        )
    else:
        mean = variance = nonnegative = bernstein_rate = None

    total_mgf_positive: dict[str, float] = {}
    total_mgf_negative: dict[str, float] = {}
    for lam in lambdas:
        total_mgf_positive[str(lam)] = total_mgf_pos_sums[lam] / total if total else 0.0
        total_mgf_negative[str(lam)] = total_mgf_neg_sums[lam] / total if total else 0.0

    cramer_rate = None
    cramer_lambda = None
    if total:
        # Cramer's upper-tail rate for E[X] < 0 is
        # I(0) = sup_{lambda >= 0} -log E[exp(lambda X)].
        # Use a binned log-sum-exp objective so the full run stays streaming.
        centers = [
            bucket * histogram_bin_width
            for bucket, _count in histogram.items()
        ]
        log_counts = [
            math.log(count)
            for _bucket, count in histogram.items()
        ]
        log_total = math.log(total)

        def log_mgf(lam: float) -> float:
            terms = [
                log_count + lam * center
                for log_count, center in zip(log_counts, centers)
            ]
            return _logsumexp(terms) - log_total

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
        best_lambda = (lo + hi) / 2.0
        best_log_mgf = min(log_mgf(0.0), log_mgf(best_lambda), log_mgf(20.0))
        if best_log_mgf == log_mgf(0.0):
            best_lambda = 0.0
        cramer_rate = max(0.0, -best_log_mgf)
        cramer_lambda = best_lambda

    segments: list[SpikeSegmentReport] = []
    def segment_sort_key(item: tuple[str, dict[str, Any]]) -> int:
        key, _ = item
        return max_exact_spike + 1 if key.startswith(">") else int(key)

    for key, data in sorted(segment_data.items(), key=segment_sort_key):
        count = data["count"]
        segment_mean = data["sum_delta"] / count
        mgf_positive: dict[str, float] = {}
        mgf_negative: dict[str, float] = {}
        for lam in lambdas:
            mgf_positive[str(lam)] = data["mgf_pos_sums"][lam] / count
            mgf_negative[str(lam)] = data["mgf_neg_sums"][lam] / count
        segments.append(
            SpikeSegmentReport(
                segment=key,
                excursions=count,
                probability=count / total if total else 0.0,
                mean_delta_log2=segment_mean,
                drift_contribution=(count / total) * segment_mean if total else 0.0,
                mean_m_PE=data["sum_m"] / count,
                mean_A_PE=data["sum_A"] / count,
                mgf_positive_tail=mgf_positive,
                mgf_prompt_negative_sign=mgf_negative,
            )
        )

    status = (
        "renewal_spike_decomposition_has_positive_cramer_rate"
        if cramer_rate is not None and cramer_rate > 0.0
        else "renewal_spike_decomposition_no_positive_cramer_rate"
    )
    return RenewalSpikeDecompositionReport(
        type="orbit_renewal_spike_decomposition",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        total_excursions=total,
        mean_delta_log2=mean,
        variance_delta_log2=variance,
        fraction_nonnegative_delta_log2=nonnegative,
        lambda_values=lambdas,
        total_mgf_positive_tail=total_mgf_positive,
        total_mgf_prompt_negative_sign=total_mgf_negative,
        cramer_rate_I0_grid=cramer_rate,
        cramer_rate_lambda=cramer_lambda,
        cramer_rate_method="positive_tail_mgf_histogram_golden_section",
        bernstein_rate=bernstein_rate,
        histogram_bin_width=histogram_bin_width,
        segments=tuple(segments),
    )


def orbit_renewal_per_k_mgf_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    lambda_values: tuple[float, ...] = (0.05, 0.1, 0.2, 0.3, 0.5),
    max_exact_spike: int = 10,
) -> OrbitRenewalPerKMGFReport:
    """Report per-max-valuation conditional MGFs on an audit-friendly lambda grid."""

    base = orbit_renewal_spike_decomposition_report(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
        lambda_values=lambda_values,
        max_exact_spike=max_exact_spike,
    )
    aggregate = dict(base.total_mgf_positive_tail)
    best_lambda: float | None = None
    best_rate: float | None = None
    for lam in base.lambda_values:
        mgf = aggregate[str(lam)]
        rate = -math.log(mgf) if mgf > 0.0 else None
        if rate is not None and (best_rate is None or rate > best_rate):
            best_rate = rate
            best_lambda = lam

    segments: list[PerKMGFSegmentReport] = []
    bottleneck_segment: str | None = None
    bottleneck_weight: float | None = None
    probability_by_segment = {
        segment.segment: segment.probability for segment in base.segments
    }
    geometric_reference_segment = "4" if "4" in probability_by_segment else None
    geometric_reference_probability = (
        probability_by_segment[geometric_reference_segment]
        if geometric_reference_segment is not None
        else None
    )
    for segment in base.segments:
        weighted = {
            key: segment.probability * value
            for key, value in segment.mgf_positive_tail.items()
        }
        segment_best_rate = 0.0
        segment_best_lambda: float | None = 0.0
        for lam in base.lambda_values:
            mgf = segment.mgf_positive_tail[str(lam)]
            rate = -math.log(mgf) if mgf > 0.0 else None
            if rate is not None and rate > segment_best_rate:
                segment_best_rate = rate
                segment_best_lambda = lam
        if best_lambda is not None:
            weight = weighted[str(best_lambda)]
            if bottleneck_weight is None or weight > bottleneck_weight:
                bottleneck_weight = weight
                bottleneck_segment = segment.segment
        geometric_ratio = None
        if (
            geometric_reference_probability is not None
            and not segment.segment.startswith(">")
        ):
            spike = int(segment.segment)
            if spike >= int(geometric_reference_segment):
                predicted = geometric_reference_probability * 2.0 ** (
                    -(spike - int(geometric_reference_segment))
                )
                geometric_ratio = (
                    segment.probability / predicted if predicted > 0.0 else None
                )
        segments.append(
            PerKMGFSegmentReport(
                segment=segment.segment,
                excursions=segment.excursions,
                probability=segment.probability,
                mean_delta_log2=segment.mean_delta_log2,
                drift_contribution=segment.drift_contribution,
                mgf_positive_tail=dict(segment.mgf_positive_tail),
                weighted_mgf_positive_tail=weighted,
                grid_optimal_lambda=segment_best_lambda,
                grid_optimal_rate=segment_best_rate,
                geometric_ratio_from_k4=geometric_ratio,
            )
        )

    status = (
        "per_k_mgf_has_positive_grid_cramer_rate"
        if best_rate is not None and best_rate > 0.0
        else "per_k_mgf_no_positive_grid_cramer_rate"
    )
    return OrbitRenewalPerKMGFReport(
        type="orbit_renewal_per_k_mgf",
        status=status,
        sample_count=base.sample_count,
        random_seed=base.random_seed,
        start_min=base.start_min,
        start_max=base.start_max,
        completed_orbits=base.completed_orbits,
        truncated_orbits=base.truncated_orbits,
        total_accelerated_steps=base.total_accelerated_steps,
        total_excursions=base.total_excursions,
        mean_delta_log2=base.mean_delta_log2,
        variance_delta_log2=base.variance_delta_log2,
        fraction_nonnegative_delta_log2=base.fraction_nonnegative_delta_log2,
        lambda_values=base.lambda_values,
        aggregate_mgf_positive_tail=aggregate,
        implied_cramer_rate_grid=best_rate,
        implied_cramer_lambda_grid=best_lambda,
        bottleneck_segment_at_best_lambda=bottleneck_segment,
        bottleneck_weighted_mgf_at_best_lambda=bottleneck_weight,
        geometric_reference_segment=geometric_reference_segment,
        segments=tuple(segments),
    )


def orbit_renewal_markov_cramer_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    lambda_values: tuple[float, ...] = (
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
    ),
    max_exact_spike: int = 10,
) -> OrbitRenewalMarkovCramerReport:
    """Estimate the Markov-additive Cramer rate on max-valuation classes."""

    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    lambdas = tuple(float(value) for value in lambda_values)
    if any(value <= 0.0 for value in lambdas):
        raise ValueError("lambda_values must be positive")

    labels = tuple(str(value) for value in range(1, max_exact_spike + 1)) + (
        f">{max_exact_spike}",
    )
    label_to_index = {label: index for index, label in enumerate(labels)}
    n_states = len(labels)
    pair_counts = [[0 for _ in range(n_states)] for _ in range(n_states)]
    pair_delta_sums = [[0.0 for _ in range(n_states)] for _ in range(n_states)]
    pair_exp_sums = {
        lam: [[0.0 for _ in range(n_states)] for _ in range(n_states)]
        for lam in lambdas
    }
    row_counts = [0 for _ in range(n_states)]
    all_excursion_exp_sums = {lam: 0.0 for lam in lambdas}
    pair_target_exp_sums = {lam: 0.0 for lam in lambdas}
    pair_target_delta_sum = 0.0

    def segment_key(max_valuation: int) -> str:
        return (
            f"{max_valuation}"
            if max_valuation <= max_exact_spike
            else f">{max_exact_spike}"
        )

    rng = random.Random(random_seed)
    completed = 0
    truncated = 0
    total_steps = 0
    total_excursions = 0
    markov_pairs = 0

    for _ in range(sample_count):
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        excursion_max_a = 0
        previous_segment: str | None = None
        while x != 1 and steps < max_steps_per_orbit:
            x, valuation = accelerated_step(x)
            steps += 1
            total_steps += 1
            excursion_max_a = max(excursion_max_a, valuation)
            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                current_segment = segment_key(excursion_max_a)
                total_excursions += 1
                for lam in lambdas:
                    all_excursion_exp_sums[lam] += math.exp(lam * delta)
                if previous_segment is not None:
                    source = label_to_index[previous_segment]
                    target = label_to_index[current_segment]
                    pair_counts[source][target] += 1
                    pair_delta_sums[source][target] += delta
                    row_counts[source] += 1
                    markov_pairs += 1
                    pair_target_delta_sum += delta
                    for lam in lambdas:
                        value = math.exp(lam * delta)
                        pair_exp_sums[lam][source][target] += value
                        pair_target_exp_sums[lam] += value
                previous_segment = current_segment
                excursion_start = x
                excursion_max_a = 0
        if x == 1:
            completed += 1
        else:
            truncated += 1

    lambda_reports: list[MarkovCramerLambdaReport] = []
    best_markov_rate: float | None = None
    best_markov_lambda: float | None = None
    best_iid_rate_at_best: float | None = None
    best_iid_all_rate: float | None = None
    best_iid_all_lambda: float | None = None
    for lam in lambdas:
        matrix = [[0.0 for _ in range(n_states)] for _ in range(n_states)]
        for source in range(n_states):
            if row_counts[source] == 0:
                continue
            denominator = float(row_counts[source])
            for target in range(n_states):
                matrix[source][target] = pair_exp_sums[lam][source][target] / denominator
        rho = _perron_radius_nonnegative(matrix)
        markov_rate = -math.log(rho) if rho > 0.0 else float("inf")
        iid_mgf = (
            pair_target_exp_sums[lam] / markov_pairs if markov_pairs else 0.0
        )
        iid_rate = -math.log(iid_mgf) if iid_mgf > 0.0 else float("inf")
        iid_all_mgf = (
            all_excursion_exp_sums[lam] / total_excursions
            if total_excursions
            else 0.0
        )
        iid_all_rate = (
            -math.log(iid_all_mgf) if iid_all_mgf > 0.0 else float("inf")
        )
        lambda_reports.append(
            MarkovCramerLambdaReport(
                lambda_value=lam,
                spectral_radius=rho,
                markov_rate=markov_rate,
                iid_pair_target_mgf=iid_mgf,
                iid_pair_target_rate=iid_rate,
                iid_all_excursion_mgf=iid_all_mgf,
                iid_all_excursion_rate=iid_all_rate,
            )
        )
        if best_markov_rate is None or markov_rate > best_markov_rate:
            best_markov_rate = markov_rate
            best_markov_lambda = lam
            best_iid_rate_at_best = iid_rate
        if best_iid_all_rate is None or iid_all_rate > best_iid_all_rate:
            best_iid_all_rate = iid_all_rate
            best_iid_all_lambda = lam

    transition_reports: list[MarkovCramerTransitionReport] = []
    for source_label, source in label_to_index.items():
        if row_counts[source] == 0:
            continue
        for target_label, target in label_to_index.items():
            count = pair_counts[source][target]
            if count == 0:
                continue
            mgf = {
                str(lam): pair_exp_sums[lam][source][target] / count
                for lam in lambdas
            }
            tilted = {
                str(lam): pair_exp_sums[lam][source][target] / row_counts[source]
                for lam in lambdas
            }
            transition_reports.append(
                MarkovCramerTransitionReport(
                    source_segment=source_label,
                    target_segment=target_label,
                    transitions=count,
                    conditional_probability=count / row_counts[source],
                    mean_target_delta_log2=pair_delta_sums[source][target] / count,
                    mgf_positive_tail=mgf,
                    tilted_entries=tilted,
                )
            )

    lift = (
        best_markov_rate - best_iid_rate_at_best
        if best_markov_rate is not None and best_iid_rate_at_best is not None
        else None
    )
    lift_all = (
        best_markov_rate - best_iid_all_rate
        if best_markov_rate is not None and best_iid_all_rate is not None
        else None
    )
    if lift is None or lift_all is None:
        status = "markov_cramer_no_pairs"
    elif lift_all > 0.0:
        status = "markov_cramer_exceeds_all_excursion_iid_grid_rate"
    elif lift > 0.0:
        status = "markov_cramer_exceeds_pair_iid_but_not_all_excursion_iid"
    else:
        status = "markov_cramer_does_not_exceed_iid_grid_rates"
    return OrbitRenewalMarkovCramerReport(
        type="orbit_renewal_markov_cramer",
        status=status,
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        total_excursions=total_excursions,
        markov_pairs=markov_pairs,
        state_labels=labels,
        lambda_values=lambdas,
        best_markov_rate=best_markov_rate,
        best_markov_lambda=best_markov_lambda,
        best_iid_pair_target_rate=best_iid_rate_at_best,
        best_iid_all_excursion_rate=best_iid_all_rate,
        best_iid_all_excursion_lambda=best_iid_all_lambda,
        markov_rate_lift_over_iid_at_best=lift,
        markov_rate_lift_over_iid_all_grid=lift_all,
        mean_pair_target_delta_log2=(
            pair_target_delta_sum / markov_pairs if markov_pairs else None
        ),
        lambda_reports=tuple(lambda_reports),
        transition_reports=tuple(transition_reports),
    )


def orbit_renewal_n0_stability_report(
    sample_count_per_range: int = 200_000,
    ranges: tuple[tuple[int, int], ...] = (
        (10**2, 10**4),
        (10**4, 10**6),
        (10**6, 10**9),
        (10**9, 10**12),
        (10**12, 10**15),
    ),
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    max_exact_spike: int = 12,
) -> OrbitRenewalN0StabilityReport:
    """Run the renewal spike/MGF diagnostic across starting-magnitude ranges."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    if not ranges:
        raise ValueError("ranges must be nonempty")

    range_reports: list[N0StabilityRangeReport] = []
    for index, (start_min, start_max) in enumerate(ranges):
        if start_min < 1 or start_max <= start_min:
            raise ValueError("expected 1 <= start_min < start_max")
        report = orbit_renewal_spike_decomposition_report(
            sample_count=sample_count_per_range,
            start_min=start_min,
            start_max=start_max,
            random_seed=random_seed + index,
            max_steps_per_orbit=max_steps_per_orbit,
            max_exact_spike=max_exact_spike,
        )
        segment_by_key = {segment.segment: segment for segment in report.segments}
        segment_one = segment_by_key.get("1")
        lambda_key = (
            str(report.cramer_rate_lambda)
            if report.cramer_rate_lambda is not None
            else None
        )
        weighted_mgf_one = None
        if segment_one is not None and lambda_key is not None:
            # Floating string keys come from the original lambda tuple. For the
            # continuous Cramer optimum this may not be present, so evaluate the
            # weighted MGF only when it is exactly in the tabulated report.
            weighted_mgf_one = (
                segment_one.probability * segment_one.mgf_positive_tail[lambda_key]
                if lambda_key in segment_one.mgf_positive_tail
                else None
            )
        range_reports.append(
            N0StabilityRangeReport(
                start_min=start_min,
                start_max=start_max,
                log10_midpoint=(math.log10(start_min) + math.log10(start_max)) / 2.0,
                sample_count=sample_count_per_range,
                completed_orbits=report.completed_orbits,
                truncated_orbits=report.truncated_orbits,
                total_accelerated_steps=report.total_accelerated_steps,
                total_excursions=report.total_excursions,
                mean_excursions_per_orbit=(
                    report.total_excursions / sample_count_per_range
                ),
                mean_steps_per_orbit=(
                    report.total_accelerated_steps / sample_count_per_range
                ),
                mean_delta_log2=report.mean_delta_log2,
                variance_delta_log2=report.variance_delta_log2,
                fraction_nonnegative_delta_log2=(
                    report.fraction_nonnegative_delta_log2
                ),
                cramer_rate_I0=report.cramer_rate_I0_grid,
                cramer_rate_lambda=report.cramer_rate_lambda,
                max_a_1_probability=(
                    None if segment_one is None else segment_one.probability
                ),
                max_a_1_mean_delta_log2=(
                    None if segment_one is None else segment_one.mean_delta_log2
                ),
                max_a_1_drift_contribution=(
                    None if segment_one is None else segment_one.drift_contribution
                ),
                max_a_1_weighted_mgf_at_lambda_star=weighted_mgf_one,
                spike_probabilities={
                    segment.segment: segment.probability
                    for segment in report.segments
                },
            )
        )

    rate_points = [
        (item.log10_midpoint, item.cramer_rate_I0)
        for item in range_reports
        if item.cramer_rate_I0 is not None
    ]
    mean_points = [
        (item.log10_midpoint, item.mean_delta_log2)
        for item in range_reports
        if item.mean_delta_log2 is not None
    ]
    variance_points = [
        (item.log10_midpoint, item.variance_delta_log2)
        for item in range_reports
        if item.variance_delta_log2 is not None
    ]
    rates = [item.cramer_rate_I0 for item in range_reports if item.cramer_rate_I0 is not None]
    width = max(rates) - min(rates) if rates else None
    slope = _least_squares_slope(rate_points)
    status = (
        "n0_stability_rate_within_0p005"
        if width is not None and width <= 0.005
        else "n0_stability_rate_within_0p01"
        if width is not None and width <= 0.01
        else "n0_stability_rate_varies_by_more_than_0p01"
        if width is not None
        else "n0_stability_no_rates"
    )
    return OrbitRenewalN0StabilityReport(
        type="orbit_renewal_n0_stability",
        status=status,
        sample_count_per_range=sample_count_per_range,
        random_seed=random_seed,
        ranges=ranges,
        max_steps_per_orbit=max_steps_per_orbit,
        lambda_source="histogram_golden_section_per_range",
        cramer_rate_slope_per_log10=slope,
        mean_delta_slope_per_log10=_least_squares_slope(mean_points),
        variance_delta_slope_per_log10=_least_squares_slope(variance_points),
        cramer_rate_range_width=width,
        range_reports=tuple(range_reports),
    )
