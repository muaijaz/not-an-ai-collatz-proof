"""Chang phantom-gain necklace sums versus the renewal Cramer rate."""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from fractions import Fraction
from math import comb, gcd
from pathlib import Path
from typing import Any

from .core import accelerated_step, v2
from .renewal_bootstrap import (
    BootstrapInterval,
    _bootstrap_histogram,
    _cramer_rate_from_histogram,
    _histogram_stats,
    _quantile,
)


CHANG_R_K_IDENTITY_CAVEAT = (
    "This artifact is a finite empirical diagnostic. Chang's R(K) necklace "
    "sum is computed exactly in its rational combinatorial coefficients and "
    "numerically after the log_2(3) weighting. J_renewal and alternate "
    "Cramer rates are finite sampled, binned empirical estimates. The report "
    "does not prove or disprove a symbolic identity."
)

DEFAULT_LAMBDA_VALUES = (0.05, 0.1, 0.2, 0.2630610750809289, 0.3, 0.5)


def _mobius(n: int) -> int:
    if n < 1:
        raise ValueError("mobius expects a positive integer")
    x = n
    prime = 2
    factors = 0
    while prime * prime <= x:
        if x % prime == 0:
            multiplicity = 0
            while x % prime == 0:
                x //= prime
                multiplicity += 1
            if multiplicity > 1:
                return 0
            factors += 1
        prime += 1 if prime == 2 else 2
    if x > 1:
        factors += 1
    return -1 if factors % 2 else 1


def _divisors(n: int) -> list[int]:
    small: list[int] = []
    large: list[int] = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d * d != n:
                large.append(n // d)
        d += 1
    return small + large[::-1]


def primitive_binary_necklace_count(length: int, ones: int) -> int:
    """Primitive binary necklaces of length ``length`` with ``ones`` one-bits."""

    if length < 1 or ones < 0 or ones > length:
        return 0
    numerator = 0
    for d in _divisors(gcd(length, ones)):
        numerator += _mobius(d) * comb(length // d, ones // d)
    return numerator // length


def _chang_R_K_components(K: int) -> tuple[Fraction, Fraction, list[dict[str, Any]]]:
    log_coefficient = Fraction(0, 1)
    rational_subtrahend = Fraction(0, 1)
    terms: list[dict[str, Any]] = []
    log2_3 = math.log2(3.0)
    for ell in range(1, K + 1):
        if log2_3 <= K / ell:
            continue
        necklace_count = primitive_binary_necklace_count(K, ell)
        if necklace_count == 0:
            continue
        probability = Fraction(necklace_count, 2**K)
        log_coefficient += probability
        rational_subtrahend += probability * Fraction(K, ell)
        terms.append(
            {
                "ell": ell,
                "primitive_necklaces": necklace_count,
                "probability_num": probability.numerator,
                "probability_den": probability.denominator,
                "gain_without_log2_3_subtrahend": K / ell,
            }
        )
    return log_coefficient, rational_subtrahend, terms


def chang_R_K_entry(K: int) -> dict[str, Any]:
    log_coefficient, rational_subtrahend, terms = _chang_R_K_components(K)
    value = float(log_coefficient) * math.log2(3.0) - float(rational_subtrahend)
    return {
        "K": K,
        "R_K": value,
        "log2_3_coefficient": str(log_coefficient),
        "rational_subtrahend": str(rational_subtrahend),
        "term_count": len(terms),
        "terms": terms,
    }


def compute_chang_R_K(K_max: int = 50) -> dict[int, float]:
    """Compute Chang's R(K) values for K=3..K_max.

    The primitive-necklace counts and their 2^{-K} weights are exact rational
    arithmetic; only the final multiplication by log_2(3) is floating-point.
    """

    if K_max < 3:
        raise ValueError("K_max must be at least 3")
    return {K: chang_R_K_entry(K)["R_K"] for K in range(3, K_max + 1)}


def _sample_identity_histograms(
    *,
    target_renewal_excursions: int,
    start_min: int,
    start_max: int,
    random_seed: int,
    max_steps_per_orbit: int,
    histogram_bin_width: float,
) -> dict[str, Any]:
    rng = random.Random(random_seed)
    renewal_histogram: Counter[int] = Counter()
    step_histogram: Counter[int] = Counter()
    two_step_histogram: Counter[int] = Counter()
    burst_end_histogram: Counter[int] = Counter()
    completed = 0
    truncated = 0
    sampled_orbits = 0
    total_steps = 0
    total_renewal_excursions = 0
    total_step_increments = 0
    total_two_step_increments = 0
    total_burst_end_increments = 0

    def bucket(value: float) -> int:
        return int(round(value / histogram_bin_width))

    while total_renewal_excursions < target_renewal_excursions:
        sampled_orbits += 1
        x = rng.randrange(start_min, start_max)
        if x % 2 == 0:
            x += 1
            if x >= start_max:
                x -= 2
        steps = 0
        excursion_start = x
        pair_delta = 0.0
        pair_length = 0
        last_dominant_burst_end: int | None = None
        while x != 1 and steps < max_steps_per_orbit:
            pre_step = x
            current_burst = pre_step % 4 == 1
            x, _valuation = accelerated_step(x)
            next_burst = x % 4 == 1
            step_delta = math.log2(x) - math.log2(pre_step)
            steps += 1
            total_steps += 1
            step_histogram[bucket(step_delta)] += 1
            total_step_increments += 1

            pair_delta += step_delta
            pair_length += 1
            if pair_length == 2:
                two_step_histogram[bucket(pair_delta)] += 1
                total_two_step_increments += 1
                pair_delta = 0.0
                pair_length = 0

            if current_burst and not next_burst and pre_step % 8 == 1:
                if last_dominant_burst_end is not None:
                    burst_delta = math.log2(pre_step) - math.log2(last_dominant_burst_end)
                    burst_end_histogram[bucket(burst_delta)] += 1
                    total_burst_end_increments += 1
                last_dominant_burst_end = pre_step

            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                renewal_histogram[bucket(delta)] += 1
                total_renewal_excursions += 1
                excursion_start = x
        if x == 1:
            completed += 1
        else:
            truncated += 1

    return {
        "sampled_orbits": sampled_orbits,
        "completed_orbits": completed,
        "truncated_orbits": truncated,
        "total_accelerated_steps": total_steps,
        "histograms": {
            "J_renewal": renewal_histogram,
            "J_step": step_histogram,
            "J_per_2_step": two_step_histogram,
            "J_per_burst_end": burst_end_histogram,
        },
        "counts": {
            "J_renewal": total_renewal_excursions,
            "J_step": total_step_increments,
            "J_per_2_step": total_two_step_increments,
            "J_per_burst_end": total_burst_end_increments,
        },
    }


def _bootstrap_cramer_report(
    histogram: Counter[int],
    *,
    histogram_bin_width: float,
    bootstrap_resamples: int,
    bootstrap_seed: int,
    target_value: float,
) -> dict[str, Any]:
    mean, variance, rate, lam, tilted_variance = _histogram_stats(
        histogram,
        histogram_bin_width,
    )
    boot_rates: list[float] = []
    boot_lambdas: list[float] = []
    boot_means: list[float] = []
    boot_variances: list[float] = []
    if histogram and bootstrap_resamples > 0:
        for sampled in _bootstrap_histogram(histogram, bootstrap_resamples, bootstrap_seed):
            boot_mean, boot_variance, boot_rate, boot_lambda, _tilted = (
                _histogram_stats(sampled, histogram_bin_width)
            )
            boot_means.append(boot_mean)
            boot_variances.append(boot_variance)
            boot_rates.append(boot_rate)
            boot_lambdas.append(boot_lambda)

    def interval(quantity: str, estimate: float, values: list[float]) -> dict[str, Any]:
        if not values:
            return BootstrapInterval(
                quantity=quantity,
                estimate=estimate,
                q025=estimate,
                q500=estimate,
                q975=estimate,
            ).to_json_dict()
        return BootstrapInterval(
            quantity=quantity,
            estimate=estimate,
            q025=_quantile(values, 0.025),
            q500=_quantile(values, 0.5),
            q975=_quantile(values, 0.975),
        ).to_json_dict()

    rate_interval = interval("cramer_rate_I0", rate, boot_rates)
    return {
        "estimate": rate,
        "bootstrap_ci": rate_interval,
        "inside_ci_of_chang_sigma_R_K": (
            rate_interval["q025"] <= target_value <= rate_interval["q975"]
        ),
        "cramer_lambda": lam,
        "mean_delta_log2": mean,
        "variance_delta_log2": variance,
        "tilted_variance_at_lambda": tilted_variance,
        "bootstrap_intervals": [
            interval("mean_delta_log2", mean, boot_means),
            interval("variance_delta_log2", variance, boot_variances),
            rate_interval,
            interval("cramer_lambda", lam, boot_lambdas),
        ],
    }


def chang_R_K_identity_report(
    *,
    K_max: int = 200,
    comparison_K_max: int = 500,
    target_renewal_excursions: int = 5_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    bootstrap_seed: int = 1,
    bootstrap_resamples: int = 500,
    max_steps_per_orbit: int = 10_000,
    histogram_bin_width: float = 0.005,
) -> dict[str, Any]:
    """Test whether Chang's necklace sum matches this framework's J_renewal."""

    if K_max < 3:
        raise ValueError("K_max must be at least 3")
    if comparison_K_max < K_max:
        raise ValueError("comparison_K_max must be at least K_max")
    if target_renewal_excursions < 1:
        raise ValueError("target_renewal_excursions must be positive")
    if bootstrap_resamples < 0:
        raise ValueError("bootstrap_resamples must be nonnegative")

    entries = {K: chang_R_K_entry(K) for K in range(3, comparison_K_max + 1)}
    values = {K: entries[K]["R_K"] for K in range(3, K_max + 1)}
    sigma_K_max = sum(values.values())
    sigma_comparison = sum(entries[K]["R_K"] for K in range(3, comparison_K_max + 1))
    finite_tail_to_comparison = sigma_comparison - sigma_K_max
    chang_reported_sigma_3_500 = 0.08823625
    chang_reported_tail_bound_after_500 = 6.22e-7

    sampled = _sample_identity_histograms(
        target_renewal_excursions=target_renewal_excursions,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
        histogram_bin_width=histogram_bin_width,
    )
    j_renewal = _bootstrap_cramer_report(
        sampled["histograms"]["J_renewal"],
        histogram_bin_width=histogram_bin_width,
        bootstrap_resamples=bootstrap_resamples,
        bootstrap_seed=bootstrap_seed,
        target_value=sigma_comparison,
    )
    alternates: dict[str, Any] = {}
    for index, name in enumerate(("J_step", "J_per_2_step", "J_per_burst_end"), start=1):
        alternates[name] = _bootstrap_cramer_report(
            sampled["histograms"][name],
            histogram_bin_width=histogram_bin_width,
            bootstrap_resamples=bootstrap_resamples,
            bootstrap_seed=bootstrap_seed + 100 * index,
            target_value=sigma_comparison,
        )
        alternates[name]["sample_count"] = sampled["counts"][name]
    alternates["J_renewal_weighted_by_Chang_h_K"] = {
        "estimate": None,
        "bootstrap_ci": None,
        "matches_chang_sigma_R_K": False,
        "status": "not_computed_requires_explicit_Chang_h_K_gain_function_from_2603_11066_sections_9_7_to_9_9",
    }

    identity_supported = j_renewal["bootstrap_ci"]["q025"] <= sigma_comparison <= j_renewal[
        "bootstrap_ci"
    ]["q975"]
    alternate_matches = [
        name
        for name, report in alternates.items()
        if report.get("bootstrap_ci") is not None
        and report["bootstrap_ci"]["q025"] <= sigma_comparison <= report["bootstrap_ci"]["q975"]
    ]
    if identity_supported:
        verdict = "identity_supported"
    elif alternate_matches:
        verdict = "identity_supported_under_alternate_definition"
    else:
        verdict = "distinct_quantities_5_percent_gap_structural"

    ratios = {
        str(K): entries[K]["R_K"] / entries[K - 1]["R_K"]
        for K in range(4, min(comparison_K_max, 50) + 1)
        if entries[K - 1]["R_K"] != 0.0
    }
    return {
        "type": "jazz_constant_chang_R_K_identity",
        "status": f"finite_empirical_identity_diagnostic_{verdict}",
        "verdict": verdict,
        "caveat": CHANG_R_K_IDENTITY_CAVEAT,
        "references": [
            "docs/reports/delta_max_quantitative.md",
            "docs/reports/jazz_constant_closed_form_test.json",
            "docs/reports/renewal_bootstrap_calibration.json",
            "Chang 2026, arXiv:2603.11066 Eq. 34 and Table 1",
        ],
        "numerics": {
            "necklace_counts": "M(K,ell) uses the standard primitive binary necklace Mobius-inversion formula.",
            "exact_arithmetic": "Primitive-necklace counts and 2^{-K} weights are exact Python integers/Fractions until the final log_2(3) weighting.",
            "renewal_sampling": "Cramer-rate estimates use binned empirical histograms of sampled Collatz increments and multinomial bootstrap resampling of those histograms.",
            "chang_h_K_weighted_candidate": "Not computed because the explicit h_K gain function from Chang sections 9.7-9.9 is not encoded in this repository.",
        },
        "K_max": K_max,
        "comparison_K_max": comparison_K_max,
        "chang_R_K_values": {str(K): values[K] for K in values},
        "chang_R_K_detailed_values": {
            str(K): {
                key: value
                for key, value in entries[K].items()
                if key != "terms" or K <= 10
            }
            for K in range(3, K_max + 1)
        },
        "chang_R_K_ratio_diagnostics": {
            "R_K_over_R_K_minus_1": ratios,
            "note": "The K=3 value matches Chang's stated Table 1 scale; finite ratios are oscillatory rather than a clean geometric sequence at small K.",
        },
        "chang_sigma_R_K": {
            "sum_3_to_K_max": sigma_K_max,
            "finite_tail_K_max_plus_1_to_comparison_K_max": finite_tail_to_comparison,
            "sum_3_to_comparison_K_max": sigma_comparison,
            "chang_reported_sum_3_to_500": chang_reported_sigma_3_500,
            "absolute_difference_from_chang_reported_sum_3_to_500": abs(
                sigma_comparison - chang_reported_sigma_3_500
            ),
            "chang_reported_tail_bound_after_500": chang_reported_tail_bound_after_500,
            "comparison_value_used": sigma_comparison,
        },
        "sampling_config": {
            "target_renewal_excursions": target_renewal_excursions,
            "sampled_orbits": sampled["sampled_orbits"],
            "completed_orbits": sampled["completed_orbits"],
            "truncated_orbits": sampled["truncated_orbits"],
            "total_accelerated_steps": sampled["total_accelerated_steps"],
            "histogram_bin_width": histogram_bin_width,
            "random_seed": random_seed,
            "bootstrap_seed": bootstrap_seed,
            "bootstrap_resamples": bootstrap_resamples,
            "max_steps_per_orbit": max_steps_per_orbit,
        },
        "j_renewal_high_precision": {
            **j_renewal,
            "sample_count": sampled["counts"]["J_renewal"],
        },
        "identity_supported_at_high_precision": identity_supported,
        "alternate_definitions": alternates,
        "alternate_definition_matches": alternate_matches,
        "outcome_interpretation": {
            "identity_supported": (
                "The Chang necklace sum falls inside the high-precision "
                "J_renewal bootstrap interval; this is empirical support for "
                "a shared structural quantity, not a proof"
            ),
            "identity_supported_under_alternate_definition": (
                "The original J_renewal misses the Chang sum but an alternate "
                "partition-dependent Cramer rate matches within bootstrap CI"
            ),
            "distinct_quantities_5_percent_gap_structural": (
                "The Chang necklace sum lies outside the high-precision "
                "J_renewal CI and outside the tested alternate CIs; the 5% gap "
                "is treated as structural in this finite diagnostic"
            ),
            "no_alternate_definition_matches": (
                "No tested definition matches, but the h_K-weighted candidate "
                "still requires a separate structural implementation"
            ),
        },
    }


def jazz_constant_high_precision_from_identity_report(report: dict[str, Any]) -> dict[str, Any]:
    """Extract the standalone high-precision J report requested by Prompt B."""

    return {
        "type": "jazz_constant_high_precision",
        "status": "finite_empirical_high_precision_renewal_cramer_diagnostic_not_collatz_proof",
        "caveat": CHANG_R_K_IDENTITY_CAVEAT,
        "sampling_config": report["sampling_config"],
        "j_renewal_high_precision": report["j_renewal_high_precision"],
        "chang_sigma_R_K_comparison_value": report["chang_sigma_R_K"][
            "comparison_value_used"
        ],
        "identity_supported_at_high_precision": report[
            "identity_supported_at_high_precision"
        ],
    }

