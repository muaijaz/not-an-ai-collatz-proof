"""Finite Foster-drift diagnostics for the phase-aware Lyapunov candidate."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

from .core import accelerated_step, v2

try:  # pragma: no cover - exercised when scipy is available in the environment.
    from scipy import optimize, stats
except Exception:  # pragma: no cover
    optimize = None
    stats = None


FOSTER_DRIFT_CAVEAT = (
    "This artifact is a finite empirical diagnostic on the accelerated Syracuse "
    "map. It tests whether the candidate Lyapunov V(n) = log_2(n) + v_2(n+1) "
    "satisfies Foster-Lyapunov drift conditions (Meyn & Tweedie, Markov Chains "
    "and Stochastic Stability) on residue quotients of the integers, sampled at "
    "finite n0 windows. The Collatz orbit is deterministic, not a Markov chain; "
    "Foster-type drift on the residue chain gives positive recurrence in "
    "residue space, not deterministic per-orbit descent. The upgrade from "
    "residue-Markov drift to deterministic descent is exactly the open problem "
    "addressed at the distributional level by Tao 2019. This artifact does not "
    "claim, prove, or imply Collatz descent for individual orbits."
)

DEFINITIONS = (
    "Let S be the accelerated odd-to-odd Collatz map: S(n) = (3n+1) / "
    "2^{v_2(3n+1)} for odd n ≥ 1. Let R(n) = v_2(n+1). Let V(n) = log₂(n) "
    "+ R(n). Let ΔV(n) = V(S(n)) − V(n).\n\n"
    "For a probability measure μ on positive odd integers, define the drift "
    "D(μ) = E_{n ∼ μ}[ΔV(n)] and the upper-tail function T(μ; t) = "
    "P_{n ∼ μ}(ΔV(n) > t).\n\n"
    "The structural prediction (from "
    "docs/reports/renewal_drift_phase_decomposed.json and the realizable Karp "
    "finding docs/reports/tail_cycle_realizability_extended.json) is "
    "D(μ_∞) = log₂(3/4) ≈ −0.4150374992788438 where μ_∞ is the "
    "asymptotic residue-uniform measure. Empirically we test convergence at "
    "finite windows."
)

VERDICTS = (
    "foster_drift_supported",
    "drift_supported_tail_inconclusive",
    "drift_residue_obstruction",
    "drift_window_obstruction",
    "drift_finite_window_only",
)

M_STEP_FOSTER_DRIFT_CAVEAT = (
    "This artifact is a finite empirical diagnostic on the accelerated Syracuse "
    "map. It tests whether the candidate Lyapunov V(n) = log_2(n) + v_2(n+1) "
    "satisfies the m-step Foster-Lyapunov drift condition (Meyn & Tweedie, "
    "Markov Chains and Stochastic Stability, ch. 11) on residue quotients of "
    "the integers, sampled at finite n0 windows. The Collatz orbit is "
    "deterministic, not a Markov chain; m-step Foster drift on the residue "
    "chain gives positive recurrence and (with positive margin) geometric "
    "ergodicity in residue space, not deterministic per-orbit descent. The "
    "upgrade from residue-Markov drift to deterministic descent is exactly the "
    "open problem addressed at the distributional level by Tao 2019. This "
    "artifact does not claim, prove, or imply Collatz descent for individual "
    "orbits."
)

M_STEP_DEFINITIONS = (
    "Let S be the accelerated odd-to-odd Collatz map. Let R(n) = v_2(n+1) "
    "and V(n) = log₂(n) + R(n). For m ≥ 1, let S^m denote the m-fold "
    "composition. Let Δ_m V(n) := V(S^m(n)) − V(n).\n\n"
    "For a probability measure μ on positive odd integers, define the m-step "
    "drift D_m(μ) := E_{n ∼ μ}[Δ_m V(n)]. The asymptotic structural "
    "prediction (from docs/reports/renewal_drift_phase_decomposed.json and "
    "docs/reports/tail_cycle_realizability_extended.json) is D_m(μ_∞) = m · "
    "log₂(3/4) where μ_∞ is the asymptotic residue-uniform measure."
)

M_STEP_VERDICTS = (
    "m_step_foster_drift_supported",
    "m_step_foster_drift_supported_strict_only",
    "m_step_foster_drift_marginal_only",
    "m_step_foster_drift_unbounded",
    "m_step_drift_window_obstruction",
)

POINTWISE_DESCENT_CAVEAT = (
    "This artifact is a finite empirical diagnostic on the accelerated Syracuse "
    "map. It tests sampled hitting times T_descent(n) = min{m : "
    "V(S^m(n)) <= V(n) - 1} for the candidate Lyapunov V(n) = log_2(n) + "
    "v_2(n+1), across finite n0 windows and finite truncation depths. It is "
    "not a proof of uniform pointwise descent for all n, not a deterministic "
    "per-orbit Collatz descent theorem, and not a closure of the "
    "residue-Markov-to-deterministic upgrade. The residual upgrade from "
    "finite-window empirical behavior to every integer orbit is exactly the "
    "Tao 2019 distributional-to-pointwise wall."
)

POINTWISE_DESCENT_DEFINITIONS = (
    "Let S be the accelerated odd-to-odd Collatz map. Let R(n) = v_2(n+1) "
    "and V(n) = log_2(n) + R(n). Define T_descent(n) = min{m >= 1 : "
    "V(S^m(n)) <= V(n) - 1}. This report samples odd n in finite windows "
    "and searches for T_descent(n) up to staged truncation depths."
)

POINTWISE_DESCENT_VERDICTS = (
    "pointwise_descent_empirical_uniform_bound_stable",
    "pointwise_descent_empirical_uniform_bound_growing",
    "pointwise_descent_window_depth_growth_or_truncation",
    "pointwise_descent_no_uniform_empirical_bound",
)

CHANG_BIT4_BALANCE_CAVEAT = (
    "This artifact is a finite empirical diagnostic on sampled accelerated "
    "Collatz orbits. It directly tests Chang 2026 arXiv:2603.25753 Eq. 16 "
    "on finite n0 windows by measuring bit-4 balance at burst-ending times "
    "inside the dominant n_t congruent to 1 mod 8 class. It does not prove "
    "Chang's Eq. 16 for all n0, does not compute or certify Chang's delta_max, "
    "and does not close the Tao 2019 distributional-to-pointwise wall."
)

CHANG_BIT4_BALANCE_DEFINITIONS = (
    "Let S be the accelerated odd-to-odd Collatz map and let "
    "X_t = 1[n_t congruent to 1 mod 4]. A burst-ending time is an index t "
    "with X_t = 1 and X_{t+1} = 0. Restrict to burst-ending states with "
    "n_t congruent to 1 mod 8. Chang's bit-4 balance statistic is "
    "r(n0) = #{t_i : n_{t_i} congruent to 9 mod 32} / "
    "#{t_i : n_{t_i} congruent to 9 or 25 mod 32}, and "
    "delta(n0) = |r(n0) - 1/2|."
)

CHANG_BIT4_BALANCE_VERDICTS = (
    "chang_bit4_balance_foster_envelope_supported",
    "chang_bit4_balance_foster_envelope_deep_failure",
    "chang_bit4_balance_foster_envelope_not_supported",
    "chang_bit4_balance_insufficient_burst_endings",
)

DEFAULT_RANGES = (
    (10**2, 10**4),
    (10**4, 10**6),
    (10**6, 10**9),
    (10**9, 10**12),
    (10**12, 10**15),
)
DEFAULT_RESIDUE_POWERS = (2, 3, 4, 5, 6)
DEFAULT_CHANG_RESOLUTION_RESIDUE_POWERS = (2, 3, 4, 5, 6, 7, 8)
DEFAULT_TAIL_THRESHOLDS = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
DEFAULT_M_STEPS_GRID = (1, 2, 4, 8, 16, 32, 64)
DEFAULT_POINTWISE_M_MAX_VALUES = (100, 1000, 10_000, 100_000)
DEFAULT_CHANG_MAX_STEPS_PER_ORBIT = 10_000
STRUCTURAL_DRIFT_TARGET = math.log2(3.0 / 4.0)
Z_975 = 1.959963984540054


def _json_number(value: float | int | None) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    return value


def _log2_int(n: int) -> float:
    if n <= 0:
        raise ValueError("log2_int expects a positive integer")
    exponent = n.bit_length() - 1
    mantissa = n / (1 << exponent)
    return exponent + math.log2(mantissa)


def _V(n: int) -> float:
    return _log2_int(n) + v2(n + 1)


def _delta_V(n: int) -> tuple[float, int, int, int, int]:
    y, valuation = accelerated_step(n)
    R = v2(n + 1)
    R_next = v2(y + 1)
    return _log2_int(y) - _log2_int(n) + (R_next - R), y, valuation, R, R_next


def _estimate(
    value: float | None,
    ci_low: float | None,
    ci_high: float | None,
    *,
    method: str,
) -> dict[str, Any]:
    if value is None or ci_low is None or ci_high is None:
        halfwidth = None
    else:
        halfwidth = max(abs(value - ci_low), abs(ci_high - value))
    return {
        "estimate": _json_number(value),
        "ci_low": _json_number(ci_low),
        "ci_high": _json_number(ci_high),
        "ci_halfwidth": _json_number(halfwidth),
        "ci_method": method,
    }


def _mean_ci_from_values(values: list[float]) -> dict[str, Any]:
    count = len(values)
    if count == 0:
        return _estimate(
            None,
            None,
            None,
            method="influence_function_normal_approximation_to_sample_mean",
        )
    mean = sum(values) / count
    if count == 1:
        return _estimate(
            mean,
            mean,
            mean,
            method="influence_function_normal_approximation_to_sample_mean",
        )
    variance = sum((value - mean) ** 2 for value in values) / (count - 1)
    halfwidth = Z_975 * math.sqrt(max(0.0, variance) / count)
    return _estimate(
        mean,
        mean - halfwidth,
        mean + halfwidth,
        method="influence_function_normal_approximation_to_sample_mean",
    )


def _mean_ci_from_sums(count: int, total: float, total_sq: float) -> dict[str, Any]:
    if count <= 0:
        return _estimate(
            None,
            None,
            None,
            method="influence_function_normal_approximation_to_sample_mean",
        )
    mean = total / count
    if count == 1:
        return _estimate(
            mean,
            mean,
            mean,
            method="influence_function_normal_approximation_to_sample_mean",
        )
    variance = max(0.0, (total_sq - count * mean * mean) / (count - 1))
    halfwidth = Z_975 * math.sqrt(variance / count)
    return _estimate(
        mean,
        mean - halfwidth,
        mean + halfwidth,
        method="influence_function_normal_approximation_to_sample_mean",
    )


def _variance_ci(values: list[float]) -> dict[str, Any]:
    count = len(values)
    if count <= 1:
        value = 0.0 if count == 1 else None
        return _estimate(
            value,
            value,
            value,
            method="normal_approximation_log_variance_delta_method",
        )
    mean = sum(values) / count
    centered2 = [(value - mean) ** 2 for value in values]
    variance = sum(centered2) / (count - 1)
    if variance <= 0.0:
        return _estimate(
            0.0,
            0.0,
            0.0,
            method="normal_approximation_log_variance_delta_method",
        )
    fourth = sum(value * value for value in centered2) / count
    se_log_variance = math.sqrt(max(0.0, fourth / (variance * variance) - 1.0) / count)
    low = math.exp(math.log(variance) - Z_975 * se_log_variance)
    high = math.exp(math.log(variance) + Z_975 * se_log_variance)
    return _estimate(
        variance,
        low,
        high,
        method="normal_approximation_log_variance_delta_method",
    )


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


def _beta_ppf(q: float, a: float, b: float) -> float:
    if stats is not None:
        return float(stats.beta.ppf(q, a, b))
    raise RuntimeError("scipy is required for exact Clopper-Pearson intervals")


def _clopper_pearson(successes: int, trials: int) -> dict[str, Any]:
    if trials <= 0:
        return _estimate(None, None, None, method="clopper_pearson_exact_binomial")
    estimate = successes / trials
    low = 0.0 if successes == 0 else _beta_ppf(0.025, successes, trials - successes + 1)
    high = (
        1.0
        if successes == trials
        else _beta_ppf(0.975, successes + 1, trials - successes)
    )
    return _estimate(
        estimate,
        low,
        high,
        method="clopper_pearson_exact_binomial",
    )


def _odd_sample(
    *,
    n_min: int,
    n_max: int,
    sample_count: int,
    seed: int,
) -> list[int]:
    if n_min < 1 or n_max < n_min:
        raise ValueError("expected 1 <= n_min <= n_max")
    first_odd = n_min if n_min % 2 == 1 else n_min + 1
    last_odd = n_max if n_max % 2 == 1 else n_max - 1
    if first_odd > last_odd:
        raise ValueError("window contains no odd integers")
    odd_count = (last_odd - first_odd) // 2 + 1
    rng = np.random.default_rng(seed)
    offsets = rng.integers(0, odd_count, size=sample_count, dtype=np.int64)
    return [int(first_odd + 2 * int(offset)) for offset in offsets]


def _least_squares_slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    x_mean = sum(point[0] for point in points) / len(points)
    y_mean = sum(point[1] for point in points) / len(points)
    denominator = sum((point[0] - x_mean) ** 2 for point in points)
    if denominator == 0.0:
        return None
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in points)
    return numerator / denominator


def _nonincreasing_abs(values: list[float]) -> bool:
    return all(
        abs(values[index + 1]) <= abs(values[index]) + 1e-15
        for index in range(len(values) - 1)
    )


def _deviation_log_slope(points: list[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    signs = {1 if value > 0.0 else -1 if value < 0.0 else 0 for _x, value in points}
    if 0 in signs or len(signs) != 1:
        return None
    return _least_squares_slope(
        [(x, math.log10(abs(value))) for x, value in points]
    )


def _residue_class_reports(
    deltas: list[float],
    samples: list[int],
    residue_powers: tuple[int, ...],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reports: list[dict[str, Any]] = []
    obstructions: list[dict[str, Any]] = []
    sample_count = len(samples)
    for k in residue_powers:
        modulus = 1 << k
        stats_by_residue = {
            residue: [0, 0.0, 0.0] for residue in range(1, modulus, 2)
        }
        for n, delta in zip(samples, deltas, strict=True):
            residue = n % modulus
            bucket = stats_by_residue[residue]
            bucket[0] += 1
            bucket[1] += delta
            bucket[2] += delta * delta
        expected = sample_count / (1 << (k - 1))
        classes: list[dict[str, Any]] = []
        min_count = min(int(bucket[0]) for bucket in stats_by_residue.values())
        balanced = all(bucket[0] >= 0.5 * expected for bucket in stats_by_residue.values())
        for residue in sorted(stats_by_residue):
            count, total, total_sq = stats_by_residue[residue]
            drift = _mean_ci_from_sums(int(count), float(total), float(total_sq))
            item = {
                "residue": residue,
                "modulus": modulus,
                "count": int(count),
                "drift": drift,
            }
            classes.append(item)
            if (
                drift["ci_low"] is None
                or drift["ci_high"] is None
                or drift["ci_high"] >= 0.0
            ):
                obstructions.append(
                    {
                        "k": k,
                        "residue": residue,
                        "modulus": modulus,
                        "count": int(count),
                        "drift": drift,
                    }
                )
        reports.append(
            {
                "k": k,
                "modulus": modulus,
                "min_count_per_class": int(min_count),
                "residue_count_balanced": balanced,
                "classes": classes,
            }
        )
    return reports, obstructions


def _tail_depth_reports(
    deltas: list[float],
    R_values: list[int],
) -> list[dict[str, Any]]:
    labels = ("1", "2", "3", "4", ">=5")
    buckets = {label: [0, 0.0, 0.0] for label in labels}
    for R, delta in zip(R_values, deltas, strict=True):
        label = str(R) if R <= 4 else ">=5"
        bucket = buckets[label]
        bucket[0] += 1
        bucket[1] += delta
        bucket[2] += delta * delta
    reports: list[dict[str, Any]] = []
    for label in labels:
        count, total, total_sq = buckets[label]
        phase = "post_exit" if label == "1" else "tail_internal"
        reports.append(
            {
                "tail_depth_class": label,
                "phase": phase,
                "count": int(count),
                "drift": _mean_ci_from_sums(int(count), float(total), float(total_sq)),
            }
        )
    return reports


def _upper_tail_reports(
    deltas: list[float],
    thresholds: tuple[float, ...],
) -> list[dict[str, Any]]:
    trials = len(deltas)
    reports: list[dict[str, Any]] = []
    for threshold in thresholds:
        successes = sum(1 for value in deltas if value > threshold)
        reports.append(
            {
                "threshold": threshold,
                "successes": successes,
                "trials": trials,
                "probability": _clopper_pearson(successes, trials),
            }
        )
    return reports


def _truncated_exp_loglik(lambda_value: float, y_values: list[float], L: float) -> float:
    if lambda_value <= 0.0 or L <= 0.0:
        return float("-inf")
    normalizer = -math.expm1(-lambda_value * L)
    if normalizer <= 0.0:
        return float("-inf")
    return (
        len(y_values) * math.log(lambda_value)
        - lambda_value * sum(y_values)
        - len(y_values) * math.log(normalizer)
    )


def _truncated_exp_cdf(y: float, lambda_value: float, L: float) -> float:
    if y <= 0.0:
        return 0.0
    if y >= L:
        return 1.0
    numerator = -math.expm1(-lambda_value * y)
    denominator = -math.expm1(-lambda_value * L)
    return numerator / denominator if denominator > 0.0 else y / L


def _fit_subexponential_tail(
    deltas: list[float],
    *,
    t_min: float = 0.5,
) -> dict[str, Any]:
    tail_values = sorted(value for value in deltas if value > t_min)
    if len(tail_values) < 3:
        return {
            "t_min": t_min,
            "t_max": None,
            "positive_tail_count": len(tail_values),
            "lambda": _estimate(None, None, None, method="truncated_exponential_mle"),
            "ks_statistic": None,
            "ks_p_value": None,
            "tail_subexponential_consistent": False,
            "fit_model": "P(Delta V > t) ~= C exp(-lambda t) on Delta V > t_min",
        }
    t_max = tail_values[-1]
    L = t_max - t_min
    if L <= 0.0:
        return {
            "t_min": t_min,
            "t_max": t_max,
            "positive_tail_count": len(tail_values),
            "lambda": _estimate(None, None, None, method="truncated_exponential_mle"),
            "ks_statistic": None,
            "ks_p_value": None,
            "tail_subexponential_consistent": False,
            "fit_model": "P(Delta V > t) ~= C exp(-lambda t) on Delta V > t_min",
        }
    y_values = [value - t_min for value in tail_values]
    if optimize is not None:
        result = optimize.minimize_scalar(
            lambda log_lambda: -_truncated_exp_loglik(
                math.exp(log_lambda),
                y_values,
                L,
            ),
            bounds=(-20.0, 20.0),
            method="bounded",
        )
        lambda_hat = math.exp(float(result.x))
    else:  # pragma: no cover
        lambda_hat = 1.0 / max(1e-12, sum(y_values) / len(y_values))
    ll_hat = _truncated_exp_loglik(lambda_hat, y_values, L)
    profile_drop = 1.920729410347062

    def root_between(left: float, right: float) -> float:
        for _ in range(80):
            mid = math.sqrt(left * right)
            if _truncated_exp_loglik(mid, y_values, L) >= ll_hat - profile_drop:
                if mid < lambda_hat:
                    right = mid
                else:
                    left = mid
            elif mid < lambda_hat:
                left = mid
            else:
                right = mid
        return math.sqrt(left * right)

    low_floor = 1e-12
    high_ceiling = 1e12
    low = low_floor
    if _truncated_exp_loglik(low_floor, y_values, L) < ll_hat - profile_drop:
        low = root_between(low_floor, lambda_hat)
    high = high_ceiling
    if _truncated_exp_loglik(high_ceiling, y_values, L) < ll_hat - profile_drop:
        high = root_between(lambda_hat, high_ceiling)

    sorted_y = sorted(y_values)
    ks_stat = 0.0
    count = len(sorted_y)
    for index, value in enumerate(sorted_y, start=1):
        cdf = _truncated_exp_cdf(value, lambda_hat, L)
        ks_stat = max(
            ks_stat,
            abs(index / count - cdf),
            abs((index - 1) / count - cdf),
        )
    if stats is not None:
        def fitted_cdf(x):
            if np.isscalar(x):
                return _truncated_exp_cdf(float(x), lambda_hat, L)
            return np.array(
                [_truncated_exp_cdf(float(value), lambda_hat, L) for value in x]
            )

        ks_p_value = float(stats.kstest(sorted_y, fitted_cdf).pvalue)
    else:  # pragma: no cover
        ks_p_value = float(2.0 * math.exp(-2.0 * count * ks_stat * ks_stat))
        ks_p_value = min(1.0, max(0.0, ks_p_value))
    return {
        "t_min": t_min,
        "t_max": t_max,
        "positive_tail_count": count,
        "lambda": _estimate(
            lambda_hat,
            low,
            high,
            method="truncated_exponential_mle_profile_likelihood",
        ),
        "ks_statistic": ks_stat,
        "ks_p_value": ks_p_value,
        "ks_method": "one_sample_ks_against_fitted_truncated_exponential",
        "tail_subexponential_consistent": lambda_hat > 0.0 and ks_p_value > 0.05,
        "fit_model": "P(Delta V > t) ~= C exp(-lambda t) on Delta V > t_min",
    }


def _bootstrap_metric_ci(
    values: list[float],
    *,
    bootstrap_resamples: int,
    seed: int,
    statistic: str,
) -> dict[str, Any]:
    if not values:
        return _estimate(None, None, None, method="bootstrap_percentile")
    array = np.array(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples: list[float] = []
    size = len(array)
    for _ in range(bootstrap_resamples):
        resampled = array[rng.integers(0, size, size=size)]
        if statistic == "mean":
            samples.append(float(np.mean(resampled)))
        elif statistic == "median":
            samples.append(float(np.quantile(resampled, 0.5)))
        elif statistic == "q95":
            samples.append(float(np.quantile(resampled, 0.95)))
        elif statistic == "q99":
            samples.append(float(np.quantile(resampled, 0.99)))
        elif statistic == "fraction":
            samples.append(float(np.mean(resampled)))
        else:
            raise ValueError(f"unknown bootstrap statistic {statistic!r}")
    samples.sort()
    estimate_value = {
        "mean": float(np.mean(array)),
        "median": float(np.quantile(array, 0.5)),
        "q95": float(np.quantile(array, 0.95)),
        "q99": float(np.quantile(array, 0.99)),
        "fraction": float(np.mean(array)),
    }[statistic]
    return _estimate(
        estimate_value,
        _quantile(samples, 0.025),
        _quantile(samples, 0.975),
        method="bootstrap_percentile",
    )


def _hitting_time_report(
    samples: list[int],
    *,
    sample_count_per_range: int,
    max_steps: int,
    threshold: float,
    bootstrap_resamples: int,
    shuffle_seed: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    M = min(sample_count_per_range, 50_000, len(samples))
    rng = np.random.default_rng(shuffle_seed)
    order = rng.permutation(len(samples))
    selected = [samples[int(index)] for index in order[:M]]
    finite_times: list[float] = []
    truncated_flags: list[float] = []
    for start in selected:
        start_V = _V(start)
        x = start
        hit: int | None = None
        for step in range(1, max_steps + 1):
            x, _valuation = accelerated_step(x)
            if _V(x) <= start_V - threshold:
                hit = step
                break
            if x == 1:
                break
        if hit is None:
            truncated_flags.append(1.0)
        else:
            finite_times.append(float(hit))
            truncated_flags.append(0.0)
    truncated_count = int(sum(truncated_flags))
    return {
        "sample_size": M,
        "max_steps": max_steps,
        "threshold": threshold,
        "finite_hitting_count": len(finite_times),
        "hitting_time_truncated_count": truncated_count,
        "mean": _bootstrap_metric_ci(
            finite_times,
            bootstrap_resamples=bootstrap_resamples,
            seed=bootstrap_seed,
            statistic="mean",
        ),
        "median": _bootstrap_metric_ci(
            finite_times,
            bootstrap_resamples=bootstrap_resamples,
            seed=bootstrap_seed + 1,
            statistic="median",
        ),
        "quantile_0_95": _bootstrap_metric_ci(
            finite_times,
            bootstrap_resamples=bootstrap_resamples,
            seed=bootstrap_seed + 2,
            statistic="q95",
        ),
        "quantile_0_99": _bootstrap_metric_ci(
            finite_times,
            bootstrap_resamples=bootstrap_resamples,
            seed=bootstrap_seed + 3,
            statistic="q99",
        ),
        "hitting_time_truncated_fraction": _bootstrap_metric_ci(
            truncated_flags,
            bootstrap_resamples=bootstrap_resamples,
            seed=bootstrap_seed + 4,
            statistic="fraction",
        ),
    }


def _distribution_summary_int(values: list[int]) -> dict[str, Any]:
    if not values:
        return {
            "sample_size": 0,
            "min": None,
            "mean": None,
            "median": None,
            "quantile_0_99": None,
            "quantile_0_999": None,
            "quantile_0_9999": None,
            "quantile_0_99999": None,
            "max": None,
        }
    sorted_values = sorted(values)
    return {
        "sample_size": len(values),
        "min": int(sorted_values[0]),
        "mean": sum(sorted_values) / len(sorted_values),
        "median": _quantile(sorted_values, 0.5),
        "quantile_0_99": _quantile(sorted_values, 0.99),
        "quantile_0_999": _quantile(sorted_values, 0.999),
        "quantile_0_9999": _quantile(sorted_values, 0.9999),
        "quantile_0_99999": _quantile(sorted_values, 0.99999),
        "max": int(sorted_values[-1]),
    }


def _distribution_summary_float(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "sample_size": 0,
            "min": None,
            "mean": None,
            "median": None,
            "quantile_0_99": None,
            "max": None,
        }
    sorted_values = sorted(values)
    return {
        "sample_size": len(values),
        "min": sorted_values[0],
        "mean": sum(sorted_values) / len(sorted_values),
        "median": _quantile(sorted_values, 0.5),
        "quantile_0_99": _quantile(sorted_values, 0.99),
        "max": sorted_values[-1],
    }


def _bootstrap_metric_ci_capped(
    values: list[float],
    *,
    bootstrap_resamples: int,
    seed: int,
    statistic: str,
    max_observations: int = 50_000,
) -> dict[str, Any]:
    if not values:
        return _estimate(None, None, None, method="bootstrap_percentile_capped")
    if bootstrap_resamples < 1:
        sorted_values = sorted(values)
        estimate_value = {
            "mean": sum(values) / len(values),
            "median": _quantile(sorted_values, 0.5),
            "q99": _quantile(sorted_values, 0.99),
        }[statistic]
        return _estimate(
            estimate_value,
            None,
            None,
            method="bootstrap_percentile_capped_no_resamples",
        )

    rng = np.random.default_rng(seed)
    array = np.array(values, dtype=float)
    original_size = len(array)
    if original_size > max_observations:
        array = array[rng.choice(original_size, size=max_observations, replace=False)]
    size = len(array)
    samples: list[float] = []
    for _ in range(bootstrap_resamples):
        resampled = array[rng.integers(0, size, size=size)]
        if statistic == "mean":
            samples.append(float(np.mean(resampled)))
        elif statistic == "median":
            samples.append(float(np.quantile(resampled, 0.5)))
        elif statistic == "q99":
            samples.append(float(np.quantile(resampled, 0.99)))
        else:
            raise ValueError(f"unknown bootstrap statistic {statistic!r}")
    samples.sort()
    estimate_value = {
        "mean": float(np.mean(array)),
        "median": float(np.quantile(array, 0.5)),
        "q99": float(np.quantile(array, 0.99)),
    }[statistic]
    return _estimate(
        estimate_value,
        _quantile(samples, 0.025),
        _quantile(samples, 0.975),
        method=(
            "bootstrap_percentile_capped"
            if original_size > max_observations
            else "bootstrap_percentile"
        ),
    )


def _chang_bit4_orbit_stats(
    start: int,
    *,
    max_steps_per_orbit: int,
    foster_epsilon: float,
    foster_m: int,
) -> dict[str, Any]:
    x = start
    steps = 0
    count_9 = 0
    count_25 = 0
    dominant_burst_endings = 0
    unclassified_dominant_burst_endings = 0

    while x != 1 and steps < max_steps_per_orbit:
        current = x
        current_burst = current % 4 == 1
        x, _valuation = accelerated_step(current)
        next_burst = x % 4 == 1
        if current_burst and not next_burst and current % 8 == 1:
            dominant_burst_endings += 1
            residue = current % 32
            if residue == 9:
                count_9 += 1
            elif residue == 25:
                count_25 += 1
            else:
                unclassified_dominant_burst_endings += 1
        steps += 1

    chang_m = count_9 + count_25
    ratio = None
    delta = None
    foster_rate = None
    sqrt_concentration = None
    envelope = None
    envelope_holds = None
    if chang_m > 0:
        ratio = count_9 / chang_m
        delta = abs(ratio - 0.5)
        foster_rate = (1.0 - foster_epsilon) ** (chang_m / foster_m)
        sqrt_concentration = 1.0 / math.sqrt(chang_m)
        envelope = foster_rate + sqrt_concentration
        envelope_holds = delta <= envelope

    return {
        "start": start,
        "completed": x == 1,
        "truncated": x != 1,
        "orbit_length_T": steps,
        "terminal_value": x if x == 1 else None,
        "chang_m": chang_m,
        "count_mod_9": count_9,
        "count_mod_25": count_25,
        "dominant_burst_endings": dominant_burst_endings,
        "unclassified_dominant_burst_endings": unclassified_dominant_burst_endings,
        "ratio_mod_9": ratio,
        "delta": delta,
        "foster_geometric_rate": foster_rate,
        "sqrt_concentration_term": sqrt_concentration,
        "foster_rate_plus_sqrt_envelope": envelope,
        "foster_rate_envelope_holds": envelope_holds,
    }


def _chang_delta_by_orbit_length_quantile(
    records: list[dict[str, Any]],
    *,
    bins: int = 5,
) -> list[dict[str, Any]]:
    if not records:
        return []
    sorted_records = sorted(records, key=lambda item: item["orbit_length_T"])
    groups: list[dict[str, Any]] = []
    count = len(sorted_records)
    for group_index in range(bins):
        start = (group_index * count) // bins
        stop = ((group_index + 1) * count) // bins
        if start >= stop:
            continue
        group = sorted_records[start:stop]
        deltas = [
            item["delta"]
            for item in group
            if item["delta"] is not None
        ]
        chang_ms = [item["chang_m"] for item in group]
        lengths = [item["orbit_length_T"] for item in group]
        groups.append(
            {
                "bin_index": group_index,
                "quantile_range": [group_index / bins, (group_index + 1) / bins],
                "orbit_count": len(group),
                "defined_delta_count": len(deltas),
                "T_min": min(lengths),
                "T_max": max(lengths),
                "T_mean": sum(lengths) / len(lengths),
                "mean_chang_m": sum(chang_ms) / len(chang_ms),
                "mean_delta": None if not deltas else sum(deltas) / len(deltas),
            }
        )
    return groups


def _chang_foster_rate_parameters() -> dict[str, Any]:
    path = Path("docs/reports/m_step_foster_drift.json")
    params = {
        "source": str(path),
        "source_status": "default_constants_used",
        "foster_epsilon": 0.1,
        "foster_m": 16,
        "rate_formula": "(1 - foster_epsilon)^(m / foster_m)",
    }
    if not path.exists():
        return params
    try:
        data = json.loads(path.read_text())
    except Exception:
        params["source_status"] = "default_constants_used_after_read_failure"
        return params
    epsilon = data.get("foster_epsilon")
    foster_m = data.get("smallest_m_uniform_negative_drift_by_residue_eps_0p1")
    if isinstance(epsilon, (int, float)) and isinstance(foster_m, int) and foster_m > 0:
        params.update(
            {
                "source_status": "loaded_from_m_step_foster_drift_json",
                "foster_epsilon": float(epsilon),
                "foster_m": foster_m,
            }
        )
    return params


def _chang_bit4_window_report(
    *,
    window_index: int,
    n_min: int,
    n_max: int,
    sample_count: int,
    bootstrap_resamples: int,
    seed_base: int,
    max_steps_per_orbit: int,
    foster_epsilon: float,
    foster_m: int,
) -> dict[str, Any]:
    sample_seed = seed_base + 10_000 * window_index + 101
    bootstrap_seed = seed_base + 10_000 * window_index + 404
    samples = _odd_sample(
        n_min=n_min,
        n_max=n_max,
        sample_count=sample_count,
        seed=sample_seed,
    )

    deltas: list[float] = []
    chang_ms: list[int] = []
    records_for_bins: list[dict[str, Any]] = []
    completed = 0
    truncated = 0
    zero_denominator = 0
    envelope_violations = 0
    worst_delta_record: dict[str, Any] | None = None
    worst_envelope_record: dict[str, Any] | None = None
    unclassified_dominant_burst_endings = 0

    for start in samples:
        stats_for_orbit = _chang_bit4_orbit_stats(
            start,
            max_steps_per_orbit=max_steps_per_orbit,
            foster_epsilon=foster_epsilon,
            foster_m=foster_m,
        )
        completed += 1 if stats_for_orbit["completed"] else 0
        truncated += 1 if stats_for_orbit["truncated"] else 0
        unclassified_dominant_burst_endings += stats_for_orbit[
            "unclassified_dominant_burst_endings"
        ]
        records_for_bins.append(stats_for_orbit)
        if stats_for_orbit["delta"] is None:
            zero_denominator += 1
            continue
        deltas.append(stats_for_orbit["delta"])
        chang_ms.append(stats_for_orbit["chang_m"])
        if (
            worst_delta_record is None
            or stats_for_orbit["delta"] > worst_delta_record["delta"]
        ):
            worst_delta_record = stats_for_orbit
        if not stats_for_orbit["foster_rate_envelope_holds"]:
            envelope_violations += 1
            excess = (
                stats_for_orbit["delta"]
                - stats_for_orbit["foster_rate_plus_sqrt_envelope"]
            )
            if (
                worst_envelope_record is None
                or excess > worst_envelope_record["envelope_excess"]
            ):
                worst_envelope_record = dict(stats_for_orbit)
                worst_envelope_record["envelope_excess"] = excess

    delta_summary = _distribution_summary_float(deltas)
    chang_m_distribution = _distribution_summary_int(chang_ms)
    envelope_holds = envelope_violations == 0
    max_delta = delta_summary["max"]
    return {
        "window_index": window_index,
        "start_min": n_min,
        "start_max": n_max,
        "midpoint_log10_n": (math.log10(n_min) + math.log10(n_max)) / 2.0,
        "sample_count": sample_count,
        "distinct_draws": len(set(samples)),
        "seeds": {
            "sample_seed": sample_seed,
            "bootstrap_seed": bootstrap_seed,
        },
        "max_steps_per_orbit": max_steps_per_orbit,
        "completed_orbits": completed,
        "truncated_orbits": truncated,
        "defined_delta_orbits": len(deltas),
        "zero_denominator_orbits": zero_denominator,
        "unclassified_dominant_burst_endings": unclassified_dominant_burst_endings,
        "delta_distribution": {
            **delta_summary,
            "mean_ci": _bootstrap_metric_ci_capped(
                deltas,
                bootstrap_resamples=bootstrap_resamples,
                seed=bootstrap_seed + 1,
                statistic="mean",
            ),
            "median_ci": _bootstrap_metric_ci_capped(
                deltas,
                bootstrap_resamples=bootstrap_resamples,
                seed=bootstrap_seed + 2,
                statistic="median",
            ),
            "quantile_0_99_ci": _bootstrap_metric_ci_capped(
                deltas,
                bootstrap_resamples=bootstrap_resamples,
                seed=bootstrap_seed + 3,
                statistic="q99",
            ),
        },
        "chang_m_distribution": chang_m_distribution,
        "delta_by_orbit_length_T_quantile": _chang_delta_by_orbit_length_quantile(
            records_for_bins
        ),
        "empirical_max_delta_at_window": max_delta,
        "max_delta_witness": (
            None
            if worst_delta_record is None
            else {
                key: worst_delta_record[key]
                for key in (
                    "start",
                    "orbit_length_T",
                    "chang_m",
                    "count_mod_9",
                    "count_mod_25",
                    "ratio_mod_9",
                    "delta",
                    "foster_geometric_rate",
                    "sqrt_concentration_term",
                    "foster_rate_plus_sqrt_envelope",
                )
            }
        ),
        "foster_rate_envelope_holds": envelope_holds,
        "foster_rate_envelope_violation_count": envelope_violations,
        "foster_rate_envelope_worst_violation": worst_envelope_record,
    }


def _pointwise_descent_window_report(
    *,
    window_index: int,
    n_min: int,
    n_max: int,
    sample_count: int,
    m_max_values: tuple[int, ...],
    seed_base: int,
) -> dict[str, Any]:
    sample_seed = seed_base + 10_000 * window_index + 101
    samples = _odd_sample(
        n_min=n_min,
        n_max=n_max,
        sample_count=sample_count,
        seed=sample_seed,
    )
    max_m = max(m_max_values)
    finite_times: list[int] = []
    truncation_counts = {m: 0 for m in m_max_values}
    largest_time: int | None = None
    largest_witness: dict[str, Any] | None = None
    first_truncated_witness: dict[str, Any] | None = None

    for start in samples:
        start_V = _V(start)
        x = start
        hit: int | None = None
        for step in range(1, max_m + 1):
            x, _valuation = accelerated_step(x)
            if _V(x) <= start_V - 1.0:
                hit = step
                break
            if x == 1:
                break

        if hit is None:
            for m in m_max_values:
                truncation_counts[m] += 1
            if first_truncated_witness is None:
                first_truncated_witness = {
                    "n": start,
                    "R": v2(start + 1),
                    "n_mod_64": start % 64,
                    "status": "truncated",
                    "t_descent": None,
                    "searched_to_m_max": max_m,
                    "lower_bound": max_m + 1,
                }
            continue

        finite_times.append(hit)
        for m in m_max_values:
            if hit > m:
                truncation_counts[m] += 1
        if largest_time is None or hit > largest_time:
            largest_time = hit
            largest_witness = {
                "n": start,
                "R": v2(start + 1),
                "n_mod_64": start % 64,
                "status": "finite",
                "t_descent": hit,
                "searched_to_m_max": max_m,
                "lower_bound": None,
            }

    deepest_truncation = truncation_counts[max_m]
    distribution = _distribution_summary_int(finite_times)
    empirical_uniform = (
        deepest_truncation == 0
        and distribution["max"] is not None
        and distribution["max"] < max_m
    )
    worst_witness = (
        first_truncated_witness
        if first_truncated_witness is not None
        else largest_witness
    )
    max_for_scaling = (
        max_m
        if deepest_truncation > 0
        else distribution["max"]
    )
    return {
        "window_index": window_index,
        "start_min": n_min,
        "start_max": n_max,
        "midpoint_log10_n": (math.log10(n_min) + math.log10(n_max)) / 2.0,
        "sample_count": sample_count,
        "distinct_draws": len(set(samples)),
        "seeds": {"sample_seed": sample_seed},
        "m_max_values": list(m_max_values),
        "hitting_time_distribution": distribution,
        "finite_hitting_count": len(finite_times),
        "truncation_counts_by_m_max": {
            str(m): int(truncation_counts[m]) for m in m_max_values
        },
        "truncation_count_at_max_m": int(deepest_truncation),
        "largest_t_descent_observed": largest_time,
        "largest_t_descent_witness": largest_witness,
        "offending_witness": worst_witness,
        "empirical_uniform_bound_at_window": empirical_uniform,
        "max_t_descent_for_scaling": max_for_scaling,
    }


def chang_bit4_balance_audit_report(
    *,
    ranges: tuple[tuple[int, int], ...] = DEFAULT_RANGES,
    sample_count_per_range: int = 1_000_000,
    random_seed: int = 0,
    bootstrap_resamples: int = 200,
    max_steps_per_orbit: int = DEFAULT_CHANG_MAX_STEPS_PER_ORBIT,
) -> dict[str, Any]:
    """Directly audit Chang's bit-4 balance statistic on sampled orbits."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    if not ranges:
        raise ValueError("ranges must be nonempty")
    if bootstrap_resamples < 0:
        raise ValueError("bootstrap_resamples must be nonnegative")
    if max_steps_per_orbit < 1:
        raise ValueError("max_steps_per_orbit must be positive")

    foster_rate = _chang_foster_rate_parameters()
    foster_epsilon = foster_rate["foster_epsilon"]
    foster_m = foster_rate["foster_m"]
    window_reports = [
        _chang_bit4_window_report(
            window_index=index,
            n_min=n_min,
            n_max=n_max,
            sample_count=sample_count_per_range,
            bootstrap_resamples=bootstrap_resamples,
            seed_base=random_seed,
            max_steps_per_orbit=max_steps_per_orbit,
            foster_epsilon=foster_epsilon,
            foster_m=foster_m,
        )
        for index, (n_min, n_max) in enumerate(ranges)
    ]

    max_deltas = [
        report["empirical_max_delta_at_window"]
        for report in window_reports
    ]
    defined_max_deltas = [
        value for value in max_deltas if value is not None
    ]
    decreasing = (
        len(defined_max_deltas) == len(max_deltas)
        and len(defined_max_deltas) >= 2
        and all(
            defined_max_deltas[index] < defined_max_deltas[index - 1]
            for index in range(1, len(defined_max_deltas))
        )
    )
    envelope_by_window = [
        bool(report["foster_rate_envelope_holds"])
        for report in window_reports
    ]
    foster_rate_envelope_holds = all(envelope_by_window)
    any_defined = any(report["defined_delta_orbits"] > 0 for report in window_reports)
    if not any_defined:
        verdict = "chang_bit4_balance_insufficient_burst_endings"
    elif foster_rate_envelope_holds:
        verdict = "chang_bit4_balance_foster_envelope_supported"
    elif envelope_by_window and envelope_by_window[0] and not envelope_by_window[-1]:
        verdict = "chang_bit4_balance_foster_envelope_deep_failure"
    else:
        verdict = "chang_bit4_balance_foster_envelope_not_supported"

    worst_witnesses = [
        report["max_delta_witness"]
        for report in window_reports
        if report["max_delta_witness"] is not None
    ]
    global_worst = (
        max(worst_witnesses, key=lambda item: item["delta"])
        if worst_witnesses
        else None
    )
    total_violations = sum(
        report["foster_rate_envelope_violation_count"]
        for report in window_reports
    )

    return {
        "type": "chang_bit4_balance_audit",
        "status": f"finite_empirical_chang_bit4_balance_diagnostic_{verdict}",
        "verdict": verdict,
        "definitions": CHANG_BIT4_BALANCE_DEFINITIONS,
        "caveat": CHANG_BIT4_BALANCE_CAVEAT,
        "references": [
            "docs/reports/chang_2603_25753_compatibility.md",
            "docs/reports/m_step_foster_drift.json",
            "Chang 2026, arXiv:2603.25753 Eq. 16",
            "Chang 2026, arXiv:2603.11066 Eq. 3 block-TV budget",
            "Tao 2019, arXiv:1909.03562",
        ],
        "numerics": {
            "integer_arithmetic": "S(n), residues, burst indicators, and all iterates use exact Python int arithmetic via collatz_exp.core.",
            "burst_ending_rule": "A burst-ending time is recorded when n_t mod 4 == 1 and S(n_t) mod 4 == 3; the Chang-dominant subclass additionally requires n_t mod 8 == 1.",
            "bit4_classes": "Within the dominant burst-ending subclass, n_t mod 32 == 9 is counted as Chang bit 4 = 0 and n_t mod 32 == 25 is counted as Chang bit 4 = 1.",
            "rng": "All random choices use numpy.random.default_rng with the same per-window sample seeds as the Foster audits.",
            "bootstrap": "Bootstrap CIs for delta summaries are deterministic and cap the resampled empirical population at 50,000 observations for million-orbit runs.",
        },
        "ranges": [list(item) for item in ranges],
        "sample_count_per_range": sample_count_per_range,
        "random_seed": random_seed,
        "bootstrap_resamples": bootstrap_resamples,
        "max_steps_per_orbit": max_steps_per_orbit,
        "foster_rate_reference": foster_rate,
        "window_reports": window_reports,
        "empirical_max_delta_at_window": [
            {
                "start_min": report["start_min"],
                "start_max": report["start_max"],
                "max_delta": report["empirical_max_delta_at_window"],
            }
            for report in window_reports
        ],
        "empirical_max_delta_decreasing_with_window": decreasing,
        "foster_rate_envelope_holds": foster_rate_envelope_holds,
        "foster_rate_envelope_holds_by_window": envelope_by_window,
        "foster_rate_envelope_total_violation_count": total_violations,
        "global_max_delta_witness": global_worst,
        "outcome_interpretation": {
            "chang_bit4_balance_foster_envelope_supported": (
                "The Foster-rate plus sqrt-N envelope holds at every tested "
                "window; this is finite empirical confirmation that the "
                "framework's Foster condition supplies Chang's required delta "
                "rate on the sampled orbit set, not a proof of Eq. 16"
            ),
            "chang_bit4_balance_foster_envelope_deep_failure": (
                "The envelope holds at shallow windows but fails at deeper "
                "windows; the joint argument would need a stronger quantitative "
                "Lyapunov or a sharper concentration term"
            ),
            "chang_bit4_balance_foster_envelope_not_supported": (
                "The envelope fails on the sampled finite windows; this is an "
                "empirical obstruction to the proposed Foster-rate explanation"
            ),
            "chang_bit4_balance_insufficient_burst_endings": (
                "No sampled orbit produced a defined Chang bit-4 denominator, "
                "so this finite run cannot test Eq. 16"
            ),
        },
    }


def pointwise_descent_audit_report(
    *,
    ranges: tuple[tuple[int, int], ...] = DEFAULT_RANGES,
    sample_count_per_range: int = 1_000_000,
    m_max_values: Iterable[int] = DEFAULT_POINTWISE_M_MAX_VALUES,
    random_seed: int = 0,
) -> dict[str, Any]:
    """Search sampled pointwise hitting times beyond the Foster quantile audit."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    if not ranges:
        raise ValueError("ranges must be nonempty")
    m_values = tuple(sorted({int(value) for value in m_max_values}))
    if not m_values or any(value < 1 for value in m_values):
        raise ValueError("m_max_values must contain positive integers")

    window_reports = [
        _pointwise_descent_window_report(
            window_index=index,
            n_min=n_min,
            n_max=n_max,
            sample_count=sample_count_per_range,
            m_max_values=m_values,
            seed_base=random_seed,
        )
        for index, (n_min, n_max) in enumerate(ranges)
    ]
    scaling_points = [
        (
            report["midpoint_log10_n"],
            math.log10(report["max_t_descent_for_scaling"]),
        )
        for report in window_reports
        if report["max_t_descent_for_scaling"] is not None
        and report["max_t_descent_for_scaling"] > 0
    ]
    slope = _least_squares_slope(scaling_points)
    all_uniform = all(
        report["empirical_uniform_bound_at_window"] for report in window_reports
    )
    any_uniform = any(
        report["empirical_uniform_bound_at_window"] for report in window_reports
    )
    if all_uniform and slope is not None and abs(slope) <= 0.05:
        verdict = "pointwise_descent_empirical_uniform_bound_stable"
    elif all_uniform:
        verdict = "pointwise_descent_empirical_uniform_bound_growing"
    elif any_uniform:
        verdict = "pointwise_descent_window_depth_growth_or_truncation"
    else:
        verdict = "pointwise_descent_no_uniform_empirical_bound"

    finite_witnesses = [
        report["largest_t_descent_witness"]
        for report in window_reports
        if report["largest_t_descent_witness"] is not None
    ]
    largest_finite_witness = (
        max(finite_witnesses, key=lambda item: item["t_descent"])
        if finite_witnesses
        else None
    )
    offending_witnesses = [
        report["offending_witness"]
        for report in window_reports
        if report["offending_witness"] is not None
    ]
    global_offending = None
    if offending_witnesses:
        global_offending = max(
            offending_witnesses,
            key=lambda item: (
                1 if item["status"] == "truncated" else 0,
                item["lower_bound"] or item["t_descent"] or -1,
            ),
        )

    return {
        "type": "pointwise_descent_audit",
        "status": f"finite_empirical_pointwise_descent_diagnostic_{verdict}",
        "verdict": verdict,
        "definitions": POINTWISE_DESCENT_DEFINITIONS,
        "caveat": POINTWISE_DESCENT_CAVEAT,
        "references": [
            "docs/reports/phase_lyapunov_foster_drift.json",
            "docs/reports/m_step_foster_drift.json",
            "Tao 2019, arXiv:1909.03562",
            "Chang 2026, arXiv:2603.25753 Eq. 16 is a related distribution-balance target, not this hitting-time target",
        ],
        "numerics": {
            "integer_arithmetic": "S(n), v_2(3n+1), R(n), and all iterates use exact Python int arithmetic via collatz_exp.core.",
            "log2_precision": (
                "log_2(n) is evaluated as (n.bit_length()-1) + "
                "math.log2(n / (1 << (n.bit_length()-1))); numpy floats are "
                "not used for log_2(n), including in the deepest window."
            ),
            "rng": "All random choices use numpy.random.default_rng with the same per-window sample seeds as the Foster audits.",
            "staged_search": "Each orbit is iterated once up to max(m_max_values), and truncation counts are recorded for each staged cutoff.",
        },
        "ranges": [list(item) for item in ranges],
        "sample_count_per_range": sample_count_per_range,
        "m_max_values": list(m_values),
        "random_seed": random_seed,
        "window_reports": window_reports,
        "all_windows_empirical_uniform_bound": all_uniform,
        "largest_t_descent_observed": (
            None if largest_finite_witness is None else largest_finite_witness["t_descent"]
        ),
        "largest_t_descent_witness": largest_finite_witness,
        "offending_witness": global_offending,
        "cross_window_scaling": {
            "x": "midpoint_log10_n",
            "y": "log10(max_t_descent_for_scaling)",
            "points": [
                [point[0], point[1]]
                for point in scaling_points
            ],
            "slope": slope,
            "interpretation": (
                "slope > 0 indicates hitting-time growth with window depth; "
                "slope approximately 0 indicates stability across tested windows"
            ),
        },
        "outcome_interpretation": {
            "pointwise_descent_empirical_uniform_bound_stable": (
                "empirical_uniform_bound_at_window is true at all tested windows "
                "and cross-window slope is approximately zero; strong empirical "
                "pointwise descent at finite windows, materially stronger than Foster"
            ),
            "pointwise_descent_empirical_uniform_bound_growing": (
                "all tested windows clear the finite cutoff, but max hitting time "
                "grows with depth; document scaling rate"
            ),
            "pointwise_descent_window_depth_growth_or_truncation": (
                "some tested windows clear the cutoff and some do not; document "
                "depth dependence"
            ),
            "pointwise_descent_no_uniform_empirical_bound": (
                "no tested window clears the empirical uniform-bound criterion; "
                "the obstruction class needs separate study"
            ),
        },
    }


def _window_report(
    *,
    window_index: int,
    n_min: int,
    n_max: int,
    sample_count: int,
    residue_powers: tuple[int, ...],
    tail_thresholds: tuple[float, ...],
    hitting_time_max_steps: int,
    hitting_time_threshold: float,
    bootstrap_resamples: int,
    seed_base: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[int]]:
    sample_seed = seed_base + 10_000 * window_index + 101
    hitting_shuffle_seed = seed_base + 10_000 * window_index + 202
    bootstrap_seed = seed_base + 10_000 * window_index + 303
    samples = _odd_sample(
        n_min=n_min,
        n_max=n_max,
        sample_count=sample_count,
        seed=sample_seed,
    )
    deltas: list[float] = []
    R_values: list[int] = []
    for n in samples:
        delta, _target, _valuation, R, _R_next = _delta_V(n)
        deltas.append(delta)
        R_values.append(R)
    marginal = _mean_ci_from_values(deltas)
    residual = _estimate(
        None if marginal["estimate"] is None else marginal["estimate"] - STRUCTURAL_DRIFT_TARGET,
        None if marginal["ci_low"] is None else marginal["ci_low"] - STRUCTURAL_DRIFT_TARGET,
        None if marginal["ci_high"] is None else marginal["ci_high"] - STRUCTURAL_DRIFT_TARGET,
        method=marginal["ci_method"],
    )
    residue_reports, residue_obstructions = _residue_class_reports(
        deltas,
        samples,
        residue_powers,
    )
    report = {
        "window_index": window_index,
        "start_min": n_min,
        "start_max": n_max,
        "midpoint_log10_n": (math.log10(n_min) + math.log10(n_max)) / 2.0,
        "sample_count": sample_count,
        "distinct_draws": len(set(samples)),
        "seeds": {
            "sample_seed": sample_seed,
            "hitting_shuffle_seed": hitting_shuffle_seed,
            "hitting_bootstrap_seed": bootstrap_seed,
        },
        "marginal_drift": marginal,
        "drift_residual_against_log2_3_over_4": residual,
        "variance": _variance_ci(deltas),
        "conditional_drift_by_residue": residue_reports,
        "conditional_drift_by_tail_depth": _tail_depth_reports(deltas, R_values),
        "upper_tail_probabilities": _upper_tail_reports(deltas, tail_thresholds),
        "subexponential_tail_fit": _fit_subexponential_tail(deltas, t_min=0.5),
        "hitting_time_distribution": _hitting_time_report(
            samples,
            sample_count_per_range=sample_count,
            max_steps=hitting_time_max_steps,
            threshold=hitting_time_threshold,
            bootstrap_resamples=bootstrap_resamples,
            shuffle_seed=hitting_shuffle_seed,
            bootstrap_seed=bootstrap_seed,
        ),
    }
    return report, residue_obstructions, samples


def _interval_strictly_negative(estimate: dict[str, Any]) -> bool:
    return (
        estimate.get("ci_low") is not None
        and estimate.get("ci_high") is not None
        and estimate["ci_high"] < 0.0
    )


def foster_drift_report(
    *,
    ranges: tuple[tuple[int, int], ...] = DEFAULT_RANGES,
    sample_count_per_range: int = 200_000,
    residue_powers: Iterable[int] = DEFAULT_RESIDUE_POWERS,
    tail_thresholds: Iterable[float] = DEFAULT_TAIL_THRESHOLDS,
    hitting_time_max_steps: int = 1000,
    hitting_time_threshold: float = 1.0,
    bootstrap_resamples: int = 1000,
    random_seed: int = 0,
) -> dict[str, Any]:
    """Produce the finite Foster-drift diagnostic artifact."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    if bootstrap_resamples < 1:
        raise ValueError("bootstrap_resamples must be positive")
    residue_power_values = tuple(int(value) for value in residue_powers)
    threshold_values = tuple(float(value) for value in tail_thresholds)
    if not ranges:
        raise ValueError("ranges must be nonempty")
    if any(k < 1 for k in residue_power_values):
        raise ValueError("residue powers must be positive")

    window_reports: list[dict[str, Any]] = []
    residue_obstruction_witnesses: list[dict[str, Any]] = []
    window_obstruction_witnesses: list[dict[str, Any]] = []
    for index, (n_min, n_max) in enumerate(ranges):
        report, residue_obstructions, _samples = _window_report(
            window_index=index,
            n_min=n_min,
            n_max=n_max,
            sample_count=sample_count_per_range,
            residue_powers=residue_power_values,
            tail_thresholds=threshold_values,
            hitting_time_max_steps=hitting_time_max_steps,
            hitting_time_threshold=hitting_time_threshold,
            bootstrap_resamples=bootstrap_resamples,
            seed_base=random_seed,
        )
        window_reports.append(report)
        if not _interval_strictly_negative(report["marginal_drift"]):
            window_obstruction_witnesses.append(
                {
                    "window_index": index,
                    "start_min": n_min,
                    "start_max": n_max,
                    "marginal_drift": report["marginal_drift"],
                }
            )
        for obstruction in residue_obstructions:
            enriched = {
                "window_index": index,
                "start_min": n_min,
                "start_max": n_max,
                **obstruction,
            }
            residue_obstruction_witnesses.append(enriched)

    drift_residuals = [
        [
            report["midpoint_log10_n"],
            report["drift_residual_against_log2_3_over_4"]["estimate"],
            report["drift_residual_against_log2_3_over_4"]["ci_halfwidth"],
        ]
        for report in window_reports
    ]
    residual_values = [
        float(item[1])
        for item in drift_residuals
        if item[1] is not None
    ]
    drift_residual_monotone = (
        len(residual_values) >= 2 and _nonincreasing_abs(residual_values)
    )
    drift_slope = _deviation_log_slope(
        [
            (float(item[0]), float(item[1]))
            for item in drift_residuals
            if item[1] is not None
        ]
    )
    deepest = window_reports[-1]
    deepest_drift = deepest["marginal_drift"]
    deepest_window_drift_consistent = (
        deepest_drift["ci_low"] is not None
        and deepest_drift["ci_high"] is not None
        and deepest_drift["ci_low"] <= STRUCTURAL_DRIFT_TARGET <= deepest_drift["ci_high"]
    )
    uniform_negative_drift = not window_obstruction_witnesses
    uniform_negative_drift_by_residue = not residue_obstruction_witnesses
    uniform_subexponential_tail = all(
        report["subexponential_tail_fit"]["tail_subexponential_consistent"]
        for report in window_reports
    )
    converging_condition = deepest_window_drift_consistent or (
        drift_residual_monotone
        and drift_slope is not None
        and drift_slope < 0.0
    )
    if not uniform_negative_drift:
        verdict = "drift_window_obstruction"
    elif not uniform_negative_drift_by_residue:
        verdict = "drift_residue_obstruction"
    elif uniform_subexponential_tail and converging_condition:
        verdict = "foster_drift_supported"
    elif not uniform_subexponential_tail:
        verdict = "drift_supported_tail_inconclusive"
    else:
        verdict = "drift_finite_window_only"

    tao_reference = (
        "docs/references/tao_2019_almost_all_collatz_orbits_arxiv_1909.03562.pdf"
        if Path(
            "docs/references/tao_2019_almost_all_collatz_orbits_arxiv_1909.03562.pdf"
        ).exists()
        else "Tao 2019, arXiv:1909.03562"
    )
    return {
        "type": "phase_lyapunov_foster_drift",
        "status": f"finite_empirical_foster_drift_diagnostic_{verdict}",
        "verdict": verdict,
        "definitions": DEFINITIONS,
        "caveat": FOSTER_DRIFT_CAVEAT,
        "references": [
            "Meyn & Tweedie 2009, Markov Chains and Stochastic Stability, Foster's theorem / chapter 11 drift criteria",
            tao_reference,
            "docs/reports/phase_lyapunov_search.json",
            "docs/reports/tail_cycle_realizability_extended.json",
            "docs/reports/renewal_drift_phase_decomposed_n0_stability.json",
        ],
        "numerics": {
            "integer_arithmetic": "S(n), v_2(3n+1), R(n), and R(S(n)) use exact Python int arithmetic via collatz_exp.core.",
            "log2_precision": (
                "log_2(n) is evaluated as (n.bit_length()-1) + "
                "math.log2(n / 2**(n.bit_length()-1)); numpy floats are not "
                "used for log_2(n), including in the deepest window."
            ),
            "mean_ci_method": "influence_function_normal_approximation_to_sample_mean",
            "variance_ci_method": "normal_approximation_log_variance_delta_method",
            "tail_probability_ci_method": "clopper_pearson_exact_binomial",
            "hitting_time_ci_method": "bootstrap_percentile",
            "rng": "All random choices use numpy.random.default_rng with recorded deterministic per-window seeds.",
        },
        "structural_drift_target": STRUCTURAL_DRIFT_TARGET,
        "ranges": [list(item) for item in ranges],
        "sample_count_per_range": sample_count_per_range,
        "residue_powers": list(residue_power_values),
        "tail_thresholds": list(threshold_values),
        "hitting_time_max_steps": hitting_time_max_steps,
        "hitting_time_threshold": hitting_time_threshold,
        "bootstrap_resamples": bootstrap_resamples,
        "random_seed": random_seed,
        "window_reports": window_reports,
        "drift_residuals": drift_residuals,
        "drift_residual_monotone": drift_residual_monotone,
        "drift_residual_log_slope_per_decade": _json_number(drift_slope),
        "deepest_window_drift_consistent": deepest_window_drift_consistent,
        "uniform_negative_drift": uniform_negative_drift,
        "uniform_negative_drift_by_residue": uniform_negative_drift_by_residue,
        "uniform_subexponential_tail": uniform_subexponential_tail,
        "residue_obstruction_witnesses": residue_obstruction_witnesses,
        "window_obstruction_witnesses": window_obstruction_witnesses,
        "verdict_logic": {
            "foster_drift_supported": (
                "uniform_negative_drift AND uniform_negative_drift_by_residue "
                "AND uniform_subexponential_tail AND "
                "(deepest_window_drift_consistent OR drift_residual_monotone "
                "with negative log-slope)"
            ),
            "drift_supported_tail_inconclusive": (
                "uniform_negative_drift AND uniform_negative_drift_by_residue "
                "AND NOT uniform_subexponential_tail"
            ),
            "drift_residue_obstruction": (
                "uniform_negative_drift AND NOT uniform_negative_drift_by_residue"
            ),
            "drift_window_obstruction": "NOT uniform_negative_drift",
            "drift_finite_window_only": (
                "uniform_negative_drift with no residue obstruction, but neither "
                "deepest-window consistency nor monotone negative-slope residual "
                "convergence is present"
            ),
        },
    }


def _residue_reports_for_margin(
    deltas: list[float],
    samples: list[int],
    residue_powers: tuple[int, ...],
    *,
    margin: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reports: list[dict[str, Any]] = []
    obstructions: list[dict[str, Any]] = []
    sample_count = len(samples)
    for k in residue_powers:
        modulus = 1 << k
        stats_by_residue = {
            residue: [0, 0.0, 0.0] for residue in range(1, modulus, 2)
        }
        for n, delta in zip(samples, deltas, strict=True):
            bucket = stats_by_residue[n % modulus]
            bucket[0] += 1
            bucket[1] += delta
            bucket[2] += delta * delta
        expected = sample_count / (1 << (k - 1))
        min_count = min(int(bucket[0]) for bucket in stats_by_residue.values())
        balanced = all(bucket[0] >= 0.5 * expected for bucket in stats_by_residue.values())
        classes: list[dict[str, Any]] = []
        for residue in sorted(stats_by_residue):
            count, total, total_sq = stats_by_residue[residue]
            drift = _mean_ci_from_sums(int(count), float(total), float(total_sq))
            item = {
                "residue": residue,
                "modulus": modulus,
                "count": int(count),
                "drift": drift,
            }
            classes.append(item)
            if (
                drift["ci_low"] is None
                or drift["ci_high"] is None
                or drift["ci_high"] >= -margin
            ):
                obstructions.append(
                    {
                        "k": k,
                        "residue": residue,
                        "modulus": modulus,
                        "count": int(count),
                        "drift_estimate": drift["estimate"],
                        "ci_low": drift["ci_low"],
                        "ci_high": drift["ci_high"],
                        "ci_halfwidth": drift["ci_halfwidth"],
                    }
                )
        reports.append(
            {
                "k": k,
                "modulus": modulus,
                "min_count_per_class": int(min_count),
                "residue_count_balanced": balanced,
                "classes": classes,
            }
        )
    return reports, obstructions


def _m_step_deltas(
    samples: list[int],
    m_steps_grid: tuple[int, ...],
) -> dict[int, list[float]]:
    max_m = max(m_steps_grid)
    m_set = set(m_steps_grid)
    deltas = {m: [] for m in m_steps_grid}
    for start in samples:
        start_V = _V(start)
        x = start
        for step in range(1, max_m + 1):
            x, _valuation = accelerated_step(x)
            if step in m_set:
                deltas[step].append(_V(x) - start_V)
    return deltas


def _reference_config_matches(
    reference: dict[str, Any],
    *,
    ranges: tuple[tuple[int, int], ...],
    sample_count_per_range: int,
    residue_powers: tuple[int, ...],
    random_seed: int,
) -> bool:
    return (
        [list(item) for item in ranges] == reference.get("ranges")
        and sample_count_per_range == reference.get("sample_count_per_range")
        and list(residue_powers) == reference.get("residue_powers")
        and random_seed == reference.get("random_seed")
    )


def _m1_cross_check(
    *,
    reference_path: str,
    generated_window_reports: list[dict[str, Any]],
    internal_window_reports: list[dict[str, Any]],
    ranges: tuple[tuple[int, int], ...],
    sample_count_per_range: int,
    residue_powers: tuple[int, ...],
    random_seed: int,
) -> dict[str, Any]:
    path = Path(reference_path)
    reference_source = "internal_same_sample_one_step_projection"
    reference_windows = internal_window_reports
    reference_config_match = False
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict) and _reference_config_matches(
            loaded,
            ranges=ranges,
            sample_count_per_range=sample_count_per_range,
            residue_powers=residue_powers,
            random_seed=random_seed,
        ):
            reference_windows = loaded.get("window_reports", [])
            reference_source = reference_path
            reference_config_match = True
    max_disagreement = 0.0
    comparisons = 0
    passes = True
    for generated, reference in zip(
        generated_window_reports,
        reference_windows,
        strict=False,
    ):
        generated_m1 = next(
            item for item in generated["m_step_reports"] if item["m"] == 1
        )
        gen_residue_reports = generated_m1["conditional_drift_by_residue"]
        ref_residue_reports = reference.get("conditional_drift_by_residue", [])
        for gen_k, ref_k in zip(gen_residue_reports, ref_residue_reports, strict=False):
            for gen_class, ref_class in zip(
                gen_k["classes"],
                ref_k.get("classes", []),
                strict=False,
            ):
                gen_est = gen_class["drift"]["estimate"]
                ref_est = ref_class["drift"]["estimate"]
                if gen_est is None or ref_est is None:
                    passes = False
                    continue
                disagreement = abs(gen_est - ref_est)
                max_disagreement = max(max_disagreement, disagreement)
                comparisons += 1
                gen_halfwidth = gen_class["drift"]["ci_halfwidth"] or 0.0
                ref_halfwidth = ref_class["drift"].get("ci_halfwidth") or 0.0
                if disagreement > gen_halfwidth + ref_halfwidth + 1e-12:
                    passes = False
        gen_marginal = generated_m1["marginal_drift"]
        ref_marginal = reference.get("marginal_drift", {})
        if gen_marginal["estimate"] is not None and ref_marginal.get("estimate") is not None:
            disagreement = abs(gen_marginal["estimate"] - ref_marginal["estimate"])
            max_disagreement = max(max_disagreement, disagreement)
            comparisons += 1
            if disagreement > (
                (gen_marginal["ci_halfwidth"] or 0.0)
                + (ref_marginal.get("ci_halfwidth") or 0.0)
                + 1e-12
            ):
                passes = False
    return {
        "m1_cross_check_passes": passes and comparisons > 0,
        "m1_max_disagreement": max_disagreement,
        "m1_cross_check_comparisons": comparisons,
        "m1_cross_check_reference": reference_source,
        "m1_cross_check_reference_config_match": reference_config_match,
    }


def _max_numeric_disagreement(
    generated: Any,
    reference: Any,
) -> tuple[bool, float, int]:
    if isinstance(generated, bool) or isinstance(reference, bool):
        return generated == reference, 0.0, 1
    if isinstance(generated, (int, float)) and isinstance(reference, (int, float)):
        disagreement = abs(float(generated) - float(reference))
        return disagreement <= 1e-12, disagreement, 1
    if generated is None or reference is None:
        return generated is reference, 0.0, 1
    if isinstance(generated, str) or isinstance(reference, str):
        return generated == reference, 0.0, 1
    if isinstance(generated, list) and isinstance(reference, list):
        passes = len(generated) == len(reference)
        max_disagreement = 0.0
        comparisons = 1
        for gen_item, ref_item in zip(generated, reference, strict=False):
            item_passes, item_disagreement, item_comparisons = (
                _max_numeric_disagreement(gen_item, ref_item)
            )
            passes = passes and item_passes
            max_disagreement = max(max_disagreement, item_disagreement)
            comparisons += item_comparisons
        return passes, max_disagreement, comparisons
    if isinstance(generated, dict) and isinstance(reference, dict):
        passes = set(generated) == set(reference)
        max_disagreement = 0.0
        comparisons = 1
        for key in sorted(set(generated) & set(reference)):
            item_passes, item_disagreement, item_comparisons = (
                _max_numeric_disagreement(generated[key], reference[key])
            )
            passes = passes and item_passes
            max_disagreement = max(max_disagreement, item_disagreement)
            comparisons += item_comparisons
        return passes, max_disagreement, comparisons
    return generated == reference, 0.0, 1


def _filter_m_step_report_to_residue_powers(
    report: dict[str, Any],
    residue_powers: set[int],
) -> dict[str, Any]:
    filtered_windows: list[dict[str, Any]] = []
    for window in report.get("window_reports", []):
        filtered_m_reports: list[dict[str, Any]] = []
        for m_report in window.get("m_step_reports", []):
            filtered_m_report = {
                "m": m_report["m"],
                "structural_prediction": m_report["structural_prediction"],
                "marginal_drift": m_report["marginal_drift"],
                "drift_residual_against_m_log2_3_over_4": m_report[
                    "drift_residual_against_m_log2_3_over_4"
                ],
                "conditional_drift_by_residue": [
                    residue_report
                    for residue_report in m_report["conditional_drift_by_residue"]
                    if residue_report["k"] in residue_powers
                ],
            }
            filtered_m_reports.append(filtered_m_report)
        filtered_windows.append(
            {
                "window_index": window["window_index"],
                "start_min": window["start_min"],
                "start_max": window["start_max"],
                "midpoint_log10_n": window["midpoint_log10_n"],
                "sample_count": window["sample_count"],
                "distinct_draws": window["distinct_draws"],
                "seeds": window["seeds"],
                "m_step_reports": filtered_m_reports,
            }
        )
    return {
        "ranges": report.get("ranges"),
        "sample_count_per_range": report.get("sample_count_per_range"),
        "random_seed": report.get("random_seed"),
        "m_steps_grid": report.get("m_steps_grid"),
        "window_reports": filtered_windows,
        "m_step_drift_residual_table": report.get("m_step_drift_residual_table"),
    }


def _m_step_k_le_6_cross_check(
    generated: dict[str, Any],
    *,
    reference_path: str,
) -> dict[str, Any]:
    path = Path(reference_path)
    if not path.exists():
        return {
            "cross_check_against_k_le_6_passes": False,
            "cross_check_max_disagreement": None,
            "cross_check_comparisons": 0,
            "cross_check_reference": reference_path,
            "cross_check_status": "reference_missing",
        }
    try:
        reference = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "cross_check_against_k_le_6_passes": False,
            "cross_check_max_disagreement": None,
            "cross_check_comparisons": 0,
            "cross_check_reference": reference_path,
            "cross_check_status": "reference_json_decode_failed",
        }
    generated_filtered = _filter_m_step_report_to_residue_powers(
        generated,
        residue_powers={2, 3, 4, 5, 6},
    )
    reference_filtered = _filter_m_step_report_to_residue_powers(
        reference,
        residue_powers={2, 3, 4, 5, 6},
    )
    passes, max_disagreement, comparisons = _max_numeric_disagreement(
        generated_filtered,
        reference_filtered,
    )
    return {
        "cross_check_against_k_le_6_passes": passes,
        "cross_check_max_disagreement": max_disagreement,
        "cross_check_comparisons": comparisons,
        "cross_check_reference": reference_path,
        "cross_check_status": "compared_filtered_k_le_6_subreport",
    }


def m_step_foster_drift_report(
    *,
    ranges: tuple[tuple[int, int], ...] = DEFAULT_RANGES,
    sample_count_per_range: int = 200_000,
    residue_powers: Iterable[int] = DEFAULT_RESIDUE_POWERS,
    m_steps_grid: Iterable[int] = DEFAULT_M_STEPS_GRID,
    foster_epsilon: float = 0.1,
    random_seed: int = 0,
) -> dict[str, Any]:
    """Produce the finite m-step Foster-drift diagnostic artifact."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    residue_power_values = tuple(int(value) for value in residue_powers)
    m_values = tuple(sorted(int(value) for value in m_steps_grid))
    if not m_values or m_values[0] != 1:
        raise ValueError("m_steps_grid must be nonempty and have smallest entry 1")
    if any(m < 1 for m in m_values):
        raise ValueError("m_steps_grid must contain positive integers")
    if foster_epsilon < 0.0:
        raise ValueError("foster_epsilon must be nonnegative")

    window_reports: list[dict[str, Any]] = []
    internal_1step_windows: list[dict[str, Any]] = []
    strict_success_by_m = {m: True for m in m_values}
    eps_success_by_m = {m: True for m in m_values}
    marginal_success_by_m = {m: True for m in m_values}
    obstructions_by_m: dict[int, list[dict[str, Any]]] = {m: [] for m in m_values}
    marginal_window_failures: list[dict[str, Any]] = []

    for window_index, (n_min, n_max) in enumerate(ranges):
        sample_seed = random_seed + 10_000 * window_index + 101
        samples = _odd_sample(
            n_min=n_min,
            n_max=n_max,
            sample_count=sample_count_per_range,
            seed=sample_seed,
        )
        deltas_by_m = _m_step_deltas(samples, m_values)
        m_reports: list[dict[str, Any]] = []
        one_step_residue_reports: list[dict[str, Any]] | None = None
        for m in m_values:
            deltas = deltas_by_m[m]
            marginal = _mean_ci_from_values(deltas)
            target = m * STRUCTURAL_DRIFT_TARGET
            residual = _estimate(
                None if marginal["estimate"] is None else marginal["estimate"] - target,
                None if marginal["ci_low"] is None else marginal["ci_low"] - target,
                None if marginal["ci_high"] is None else marginal["ci_high"] - target,
                method=marginal["ci_method"],
            )
            residue_reports, strict_obstructions = _residue_reports_for_margin(
                deltas,
                samples,
                residue_power_values,
                margin=0.0,
            )
            _eps_reports, eps_obstructions = _residue_reports_for_margin(
                deltas,
                samples,
                residue_power_values,
                margin=foster_epsilon,
            )
            strict_uniform = not strict_obstructions
            eps_uniform = not eps_obstructions
            marginal_negative = _interval_strictly_negative(marginal)
            strict_success_by_m[m] = strict_success_by_m[m] and strict_uniform
            eps_success_by_m[m] = eps_success_by_m[m] and eps_uniform
            marginal_success_by_m[m] = marginal_success_by_m[m] and marginal_negative
            if not marginal_negative:
                marginal_window_failures.append(
                    {
                        "m": m,
                        "window_index": window_index,
                        "start_min": n_min,
                        "start_max": n_max,
                        "marginal_drift": marginal,
                    }
                )
            for obstruction in strict_obstructions:
                obstructions_by_m[m].append(
                    {
                        "m": m,
                        "window_index": window_index,
                        "start_min": n_min,
                        "start_max": n_max,
                        **obstruction,
                    }
                )
            if m == 1:
                one_step_residue_reports = residue_reports
            m_reports.append(
                {
                    "m": m,
                    "structural_prediction": target,
                    "marginal_drift": marginal,
                    "drift_residual_against_m_log2_3_over_4": residual,
                    "conditional_drift_by_residue": residue_reports,
                    "uniform_negative_marginal_drift_at_m": marginal_negative,
                    "uniform_negative_drift_by_residue_at_m": strict_uniform,
                    "uniform_negative_drift_by_residue_at_m_eps_0p1": eps_uniform,
                    "strict_residue_obstruction_count": len(strict_obstructions),
                    "eps_0p1_residue_obstruction_count": len(eps_obstructions),
                }
            )
        window_reports.append(
            {
                "window_index": window_index,
                "start_min": n_min,
                "start_max": n_max,
                "midpoint_log10_n": (math.log10(n_min) + math.log10(n_max)) / 2.0,
                "sample_count": sample_count_per_range,
                "distinct_draws": len(set(samples)),
                "seeds": {"sample_seed": sample_seed},
                "m_step_reports": m_reports,
            }
        )
        m1_deltas = deltas_by_m[1]
        internal_1step_windows.append(
            {
                "marginal_drift": _mean_ci_from_values(m1_deltas),
                "conditional_drift_by_residue": one_step_residue_reports or [],
            }
        )

    smallest_strict = next((m for m in m_values if strict_success_by_m[m]), None)
    smallest_eps = next((m for m in m_values if eps_success_by_m[m]), None)
    smallest_marginal = next((m for m in m_values if marginal_success_by_m[m]), None)
    residual_table: list[dict[str, Any]] = []
    for m in m_values:
        residual_entries = [
            next(item for item in window["m_step_reports"] if item["m"] == m)[
                "drift_residual_against_m_log2_3_over_4"
            ]
            for window in window_reports
        ]
        max_entry = max(
            residual_entries,
            key=lambda item: abs(item["estimate"]) if item["estimate"] is not None else -1.0,
        )
        residual_table.append(
            {
                "m": m,
                "max_window_residual": max_entry["estimate"],
                "max_window_residual_ci_halfwidth": max_entry["ci_halfwidth"],
            }
        )

    first_failing_m = next(
        (m for m in m_values if not strict_success_by_m[m]),
        None,
    )
    witness_m = first_failing_m if first_failing_m is not None else m_values[-1]
    obstruction_witnesses = obstructions_by_m[witness_m]
    max_m = m_values[-1]
    obstruction_count_at_max = len(obstructions_by_m[max_m])
    max_obstruction_drift_at_max = (
        max(
            witness["drift_estimate"]
            for witness in obstructions_by_m[max_m]
            if witness["drift_estimate"] is not None
        )
        if obstructions_by_m[max_m]
        else None
    )
    if marginal_window_failures:
        verdict = "m_step_drift_window_obstruction"
    elif smallest_eps is not None:
        verdict = "m_step_foster_drift_supported"
    elif smallest_strict is not None:
        verdict = "m_step_foster_drift_supported_strict_only"
    elif smallest_marginal is not None and obstruction_count_at_max > 0:
        verdict = "m_step_foster_drift_unbounded"
    elif smallest_marginal is not None:
        verdict = "m_step_foster_drift_marginal_only"
    else:
        verdict = "m_step_drift_window_obstruction"

    cross_check = _m1_cross_check(
        reference_path="docs/reports/phase_lyapunov_foster_drift.json",
        generated_window_reports=window_reports,
        internal_window_reports=internal_1step_windows,
        ranges=ranges,
        sample_count_per_range=sample_count_per_range,
        residue_powers=residue_power_values,
        random_seed=random_seed,
    )
    tao_reference = (
        "docs/references/tao_2019_almost_all_collatz_orbits_arxiv_1909.03562.pdf"
        if Path(
            "docs/references/tao_2019_almost_all_collatz_orbits_arxiv_1909.03562.pdf"
        ).exists()
        else "Tao 2019, arXiv:1909.03562"
    )
    return {
        "type": "m_step_foster_drift",
        "status": f"finite_empirical_m_step_foster_drift_diagnostic_{verdict}",
        "verdict": verdict,
        "definitions": M_STEP_DEFINITIONS,
        "caveat": M_STEP_FOSTER_DRIFT_CAVEAT,
        "references": [
            "Meyn & Tweedie 2009, Markov Chains and Stochastic Stability, ch. 11 m-step Foster drift criteria",
            tao_reference,
            "docs/reports/phase_lyapunov_foster_drift.json",
            "docs/reports/tail_cycle_realizability_extended.json",
            "docs/reports/renewal_drift_phase_decomposed_n0_stability.json",
        ],
        "numerics": {
            "integer_arithmetic": "S(n), v_2(3n+1), R(n), and all iterates use exact Python int arithmetic via collatz_exp.core.",
            "log2_precision": (
                "log_2(n) is evaluated as (n.bit_length()-1) + "
                "math.log2(n / (1 << (n.bit_length()-1))); numpy floats are "
                "not used for log_2(n), including in the deepest window."
            ),
            "ci_method": "influence_function_normal_approximation_to_sample_mean",
            "rng": "All random choices use numpy.random.default_rng with the same per-window sample seeds as the 1-step audit.",
        },
        "structural_drift_target_per_step": STRUCTURAL_DRIFT_TARGET,
        "ranges": [list(item) for item in ranges],
        "sample_count_per_range": sample_count_per_range,
        "residue_powers": list(residue_power_values),
        "m_steps_grid": list(m_values),
        "foster_epsilon": foster_epsilon,
        "random_seed": random_seed,
        "window_reports": window_reports,
        "smallest_m_uniform_negative_drift_by_residue": smallest_strict,
        "smallest_m_uniform_negative_drift_by_residue_eps_0p1": smallest_eps,
        "smallest_m_uniform_negative_marginal_drift": smallest_marginal,
        "m_step_drift_residual_table": residual_table,
        "residue_obstruction_witnesses_at_smallest_m": obstruction_witnesses,
        "residue_obstruction_witness_m": witness_m,
        "obstruction_count_at_smallest_failing_m": len(obstruction_witnesses),
        "obstruction_count_at_max_m": obstruction_count_at_max,
        "max_obstruction_drift_at_max_m": _json_number(max_obstruction_drift_at_max),
        "marginal_window_failure_witnesses": marginal_window_failures,
        "m1_cross_check_passes": cross_check["m1_cross_check_passes"],
        "m1_max_disagreement": cross_check["m1_max_disagreement"],
        "m1_cross_check": cross_check,
        "verdict_logic": {
            "m_step_foster_drift_supported": (
                "smallest_m_uniform_negative_drift_by_residue_eps_0p1 is not null"
            ),
            "m_step_foster_drift_supported_strict_only": (
                "smallest_m_uniform_negative_drift_by_residue is not null but "
                "smallest_m_uniform_negative_drift_by_residue_eps_0p1 is null"
            ),
            "m_step_foster_drift_marginal_only": (
                "smallest_m_uniform_negative_marginal_drift is not null but no "
                "m in the grid achieves residue-uniform negativity"
            ),
            "m_step_foster_drift_unbounded": (
                "even at max(m_steps_grid), residue obstructions persist"
            ),
            "m_step_drift_window_obstruction": (
                "some tested m and window has marginal drift CI not strictly "
                "excluding zero"
            ),
        },
    }


def m_step_foster_drift_k8_report(
    *,
    ranges: tuple[tuple[int, int], ...] = DEFAULT_RANGES,
    sample_count_per_range: int = 200_000,
    residue_powers: Iterable[int] = DEFAULT_CHANG_RESOLUTION_RESIDUE_POWERS,
    m_steps_grid: Iterable[int] = DEFAULT_M_STEPS_GRID,
    foster_epsilon: float = 0.1,
    random_seed: int = 0,
    cross_check_reference_path: str = "docs/reports/m_step_foster_drift.json",
) -> dict[str, Any]:
    """Run the m-step Foster audit at Chang's mod-256 fiber resolution."""

    report = m_step_foster_drift_report(
        ranges=ranges,
        sample_count_per_range=sample_count_per_range,
        residue_powers=residue_powers,
        m_steps_grid=m_steps_grid,
        foster_epsilon=foster_epsilon,
        random_seed=random_seed,
    )
    cross_check = _m_step_k_le_6_cross_check(
        report,
        reference_path=cross_check_reference_path,
    )
    report["status"] = report["status"].replace(
        "finite_empirical_m_step_foster_drift_diagnostic_",
        "finite_empirical_m_step_foster_drift_k8_diagnostic_",
    )
    report["type"] = "m_step_foster_drift_k8"
    report["references"] = [
        *report["references"],
        "Chang 2026, arXiv:2603.25753 mod 32 with mod 256 fiber refinement",
        cross_check_reference_path,
    ]
    report["chang_resolution"] = {
        "description": (
            "Chang 2603.25753 works at modulus 32 with mod 256 fiber "
            "refinement; this audit extends residue powers through k=8 "
            "(odd classes modulo 256)."
        ),
        "modulus_power_32": 5,
        "fiber_refinement_power_256": 8,
        "extra_residue_powers_checked": [
            k for k in report["residue_powers"] if k in (7, 8)
        ],
    }
    report.update(cross_check)
    report["outcome_interpretation_k8"] = {
        "foster_matches_chang_resolution": (
            "m=16 with epsilon=0.1 clears all tested residue powers through "
            "k=8; this closes the joint argument's third technical "
            "verification empirically at finite sampled windows, not as a "
            "proof claim"
        ),
        "foster_fails_at_chang_resolution": (
            "some k=7 or k=8 residue class fails the configured Foster "
            "condition; the residue-Markov framework would only be verified "
            "at coarser resolution in this finite diagnostic"
        ),
    }
    report["foster_holds_at_chang_resolution_m16_eps_0p1"] = (
        report["smallest_m_uniform_negative_drift_by_residue_eps_0p1"] is not None
        and report["smallest_m_uniform_negative_drift_by_residue_eps_0p1"] <= 16
        and 7 in report["residue_powers"]
        and 8 in report["residue_powers"]
    )
    return report


def foster_drift_report_json(**kwargs: Any) -> str:
    return json.dumps(foster_drift_report(**kwargs), indent=2, sort_keys=True)
