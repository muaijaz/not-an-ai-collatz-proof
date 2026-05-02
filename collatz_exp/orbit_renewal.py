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
class RenewalExcursionSample:
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    deltas: tuple[float, ...]
    m_values: tuple[int, ...]
    A_values: tuple[int, ...]
    tail_steps: tuple[int, ...]
    tail_delta_log2: tuple[float, ...]
    tail_A: tuple[int, ...]
    post_exit_steps: tuple[int, ...]
    post_exit_delta_log2: tuple[float, ...]
    post_exit_A: tuple[int, ...]
    phase_raw_sums: tuple[float, ...]
    phase_raw_cross_sums: tuple[tuple[float, ...], ...]
    sample_excursions: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class RenewalDriftEstimate:
    estimate: float | None
    ci_low: float | None
    ci_high: float | None

    def to_json_dict(self) -> dict[str, float | None]:
        return asdict(self)


@dataclass(frozen=True)
class RenewalDriftPerStepReport:
    type: str
    status: str
    caveat: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    bootstrap_resamples: int
    bootstrap_ci_method: str
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    mean_delta_log2: float | None
    mean_m_PE: float | None
    mean_A_PE: float | None
    geom2_valuation_target: float
    karp_drift_target: float
    mean_drift_per_step: RenewalDriftEstimate
    mean_valuation_per_step: RenewalDriftEstimate
    structural_drift_prediction_per_step: RenewalDriftEstimate
    structural_identity_residual: RenewalDriftEstimate
    valuation_minus_geom2_mean: RenewalDriftEstimate
    drift_minus_karp_log2_3_over_4: RenewalDriftEstimate
    geom2_mean_consistent: bool
    karp_drift_consistent: bool
    verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "bootstrap_resamples": self.bootstrap_resamples,
            "bootstrap_ci_method": self.bootstrap_ci_method,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "mean_delta_log2": self.mean_delta_log2,
            "mean_m_PE": self.mean_m_PE,
            "mean_A_PE": self.mean_A_PE,
            "geom2_valuation_target": self.geom2_valuation_target,
            "karp_drift_target": self.karp_drift_target,
            "mean_drift_per_step": self.mean_drift_per_step.to_json_dict(),
            "mean_valuation_per_step": (
                self.mean_valuation_per_step.to_json_dict()
            ),
            "structural_drift_prediction_per_step": (
                self.structural_drift_prediction_per_step.to_json_dict()
            ),
            "structural_identity_residual": (
                self.structural_identity_residual.to_json_dict()
            ),
            "valuation_minus_geom2_mean": (
                self.valuation_minus_geom2_mean.to_json_dict()
            ),
            "drift_minus_karp_log2_3_over_4": (
                self.drift_minus_karp_log2_3_over_4.to_json_dict()
            ),
            "geom2_mean_consistent": self.geom2_mean_consistent,
            "karp_drift_consistent": self.karp_drift_consistent,
            "verdict": self.verdict,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class RenewalDriftPhaseDecomposedReport:
    type: str
    status: str
    caveat: str
    sample_count: int
    random_seed: int
    start_min: int
    start_max: int
    bootstrap_resamples: int
    bootstrap_ci_method: str
    completed_orbits: int
    truncated_orbits: int
    total_accelerated_steps: int
    total_excursions: int
    total_excursion_steps: int
    tail_internal_steps: int
    post_exit_steps: int
    tail_drift_target: float
    post_exit_drift_target: float
    post_exit_valuation_target: float
    w_tail: RenewalDriftEstimate
    w_post_exit: RenewalDriftEstimate
    mean_drift_per_step_total: RenewalDriftEstimate
    mean_drift_per_step_tail: RenewalDriftEstimate
    mean_drift_per_step_post_exit: RenewalDriftEstimate
    mean_valuation_per_step_total: RenewalDriftEstimate
    mean_valuation_per_step_tail: RenewalDriftEstimate
    mean_valuation_per_step_post_exit: RenewalDriftEstimate
    reconciliation_residual: RenewalDriftEstimate
    tail_valuation_exact_check: bool
    tail_drift_consistent: bool
    post_exit_drift_consistent: bool
    post_exit_valuation_consistent: bool
    verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "sample_count": self.sample_count,
            "random_seed": self.random_seed,
            "start_min": self.start_min,
            "start_max": self.start_max,
            "bootstrap_resamples": self.bootstrap_resamples,
            "bootstrap_ci_method": self.bootstrap_ci_method,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_accelerated_steps": self.total_accelerated_steps,
            "total_excursions": self.total_excursions,
            "total_excursion_steps": self.total_excursion_steps,
            "tail_internal_steps": self.tail_internal_steps,
            "post_exit_steps": self.post_exit_steps,
            "tail_drift_target": self.tail_drift_target,
            "post_exit_drift_target": self.post_exit_drift_target,
            "post_exit_valuation_target": self.post_exit_valuation_target,
            "w_tail": self.w_tail.to_json_dict(),
            "w_post_exit": self.w_post_exit.to_json_dict(),
            "mean_drift_per_step_total": (
                self.mean_drift_per_step_total.to_json_dict()
            ),
            "mean_drift_per_step_tail": (
                self.mean_drift_per_step_tail.to_json_dict()
            ),
            "mean_drift_per_step_post_exit": (
                self.mean_drift_per_step_post_exit.to_json_dict()
            ),
            "mean_valuation_per_step_total": (
                self.mean_valuation_per_step_total.to_json_dict()
            ),
            "mean_valuation_per_step_tail": (
                self.mean_valuation_per_step_tail.to_json_dict()
            ),
            "mean_valuation_per_step_post_exit": (
                self.mean_valuation_per_step_post_exit.to_json_dict()
            ),
            "reconciliation_residual": self.reconciliation_residual.to_json_dict(),
            "tail_valuation_exact_check": self.tail_valuation_exact_check,
            "tail_drift_consistent": self.tail_drift_consistent,
            "post_exit_drift_consistent": self.post_exit_drift_consistent,
            "post_exit_valuation_consistent": self.post_exit_valuation_consistent,
            "verdict": self.verdict,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class RenewalDriftPhaseN0RangeReport:
    start_min: int
    start_max: int
    midpoint_log10_n: float
    sample_count: int
    completed_orbits: int
    truncated_orbits: int
    total_excursions: int
    total_accelerated_steps: int
    w_tail: float | None
    w_post_exit: float | None
    weights_balanced: bool
    mean_drift_per_step_total: RenewalDriftEstimate
    mean_drift_per_step_tail: RenewalDriftEstimate
    mean_valuation_per_step_tail: RenewalDriftEstimate
    mean_drift_per_step_post_exit: RenewalDriftEstimate
    mean_valuation_per_step_post_exit: RenewalDriftEstimate
    post_exit_valuation_deviation: float | None
    total_drift_deviation: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "start_min": self.start_min,
            "start_max": self.start_max,
            "midpoint_log10_n": self.midpoint_log10_n,
            "sample_count": self.sample_count,
            "completed_orbits": self.completed_orbits,
            "truncated_orbits": self.truncated_orbits,
            "total_excursions": self.total_excursions,
            "total_accelerated_steps": self.total_accelerated_steps,
            "w_tail": self.w_tail,
            "w_post_exit": self.w_post_exit,
            "weights_balanced": self.weights_balanced,
            "mean_drift_per_step_total": (
                self.mean_drift_per_step_total.to_json_dict()
            ),
            "mean_drift_per_step_tail": (
                self.mean_drift_per_step_tail.to_json_dict()
            ),
            "mean_valuation_per_step_tail": (
                self.mean_valuation_per_step_tail.to_json_dict()
            ),
            "mean_drift_per_step_post_exit": (
                self.mean_drift_per_step_post_exit.to_json_dict()
            ),
            "mean_valuation_per_step_post_exit": (
                self.mean_valuation_per_step_post_exit.to_json_dict()
            ),
            "post_exit_valuation_deviation": self.post_exit_valuation_deviation,
            "total_drift_deviation": self.total_drift_deviation,
        }


@dataclass(frozen=True)
class RenewalDriftPhaseN0StabilityReport:
    type: str
    status: str
    caveat: str
    sample_count_per_range: int
    random_seed: int
    ranges: tuple[tuple[int, int], ...]
    bootstrap_resamples: int
    bootstrap_ci_method: str
    post_exit_valuation_target: float
    total_drift_target: float
    post_exit_valuation_deviations: tuple[tuple[float, float, float | None], ...]
    total_drift_deviations: tuple[tuple[float, float, float | None], ...]
    post_exit_valuation_monotone: bool
    total_drift_monotone: bool
    post_exit_valuation_log_slope_per_decade: float | None
    total_drift_log_slope_per_decade: float | None
    deepest_window_post_exit_consistent: bool
    deepest_window_total_drift_consistent: bool
    verdict: str
    range_reports: tuple[RenewalDriftPhaseN0RangeReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "sample_count_per_range": self.sample_count_per_range,
            "random_seed": self.random_seed,
            "ranges": [list(item) for item in self.ranges],
            "bootstrap_resamples": self.bootstrap_resamples,
            "bootstrap_ci_method": self.bootstrap_ci_method,
            "post_exit_valuation_target": self.post_exit_valuation_target,
            "total_drift_target": self.total_drift_target,
            "post_exit_valuation_deviations": [
                list(item) for item in self.post_exit_valuation_deviations
            ],
            "total_drift_deviations": [
                list(item) for item in self.total_drift_deviations
            ],
            "post_exit_valuation_monotone": self.post_exit_valuation_monotone,
            "total_drift_monotone": self.total_drift_monotone,
            "post_exit_valuation_log_slope_per_decade": (
                self.post_exit_valuation_log_slope_per_decade
            ),
            "total_drift_log_slope_per_decade": (
                self.total_drift_log_slope_per_decade
            ),
            "deepest_window_post_exit_consistent": (
                self.deepest_window_post_exit_consistent
            ),
            "deepest_window_total_drift_consistent": (
                self.deepest_window_total_drift_consistent
            ),
            "verdict": self.verdict,
            "range_reports": [item.to_json_dict() for item in self.range_reports],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


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


def _collect_renewal_excursions(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    collect_phase_stats: bool = False,
    store_renewal_values: bool = True,
) -> RenewalExcursionSample:
    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    rng = random.Random(random_seed)
    deltas: list[float] = []
    m_values: list[int] = []
    A_values: list[int] = []
    tail_steps_values: list[int] = []
    tail_delta_values: list[float] = []
    tail_A_values: list[int] = []
    post_exit_steps_values: list[int] = []
    post_exit_delta_values: list[float] = []
    post_exit_A_values: list[int] = []
    sample_excursions: list[dict[str, Any]] = []
    phase_raw_sums = [0.0] * 9
    phase_raw_cross_sums = [[0.0] * 9 for _ in range(9)]
    phase_cross_pairs = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (3, 0),
        (6, 0),
        (1, 0),
        (2, 0),
        (4, 3),
        (5, 3),
        (7, 6),
        (8, 6),
    )
    store_phase_excursions = collect_phase_stats and sample_count <= 10_000
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
        excursion_m = 0
        excursion_A = 0
        excursion_tail_steps = 0
        excursion_tail_delta = 0.0
        excursion_tail_A = 0
        excursion_post_exit_steps = 0
        excursion_post_exit_delta = 0.0
        excursion_post_exit_A = 0
        while x != 1 and steps < max_steps_per_orbit:
            pre_step = x
            tail_internal = pre_step % 4 == 3
            x, valuation = accelerated_step(x)
            step_delta = math.log2(x) - math.log2(pre_step)
            steps += 1
            total_steps += 1
            excursion_m += 1
            excursion_A += valuation
            if tail_internal:
                excursion_tail_steps += 1
                excursion_tail_delta += step_delta
                excursion_tail_A += valuation
            else:
                excursion_post_exit_steps += 1
                excursion_post_exit_delta += step_delta
                excursion_post_exit_A += valuation
            if x == 1 or v2(x + 1) >= 2:
                delta = math.log2(x) - math.log2(excursion_start)
                total_excursions += 1
                if store_renewal_values:
                    deltas.append(delta)
                    m_values.append(excursion_m)
                    A_values.append(excursion_A)
                if collect_phase_stats:
                    raw = (
                        float(excursion_m),
                        delta,
                        float(excursion_A),
                        float(excursion_tail_steps),
                        excursion_tail_delta,
                        float(excursion_tail_A),
                        float(excursion_post_exit_steps),
                        excursion_post_exit_delta,
                        float(excursion_post_exit_A),
                    )
                    for i, value_i in enumerate(raw):
                        phase_raw_sums[i] += value_i
                    for i, j in phase_cross_pairs:
                        product = raw[i] * raw[j]
                        phase_raw_cross_sums[i][j] += product
                        if i != j:
                            phase_raw_cross_sums[j][i] += product
                    if store_phase_excursions:
                        tail_steps_values.append(excursion_tail_steps)
                        tail_delta_values.append(excursion_tail_delta)
                        tail_A_values.append(excursion_tail_A)
                        post_exit_steps_values.append(excursion_post_exit_steps)
                        post_exit_delta_values.append(excursion_post_exit_delta)
                        post_exit_A_values.append(excursion_post_exit_A)
                if len(sample_excursions) < 100:
                    sample_excursions.append(
                        {
                            "start": excursion_start,
                            "landing": x,
                            "m_PE": excursion_m,
                            "A_PE": excursion_A,
                            "delta_log2": delta,
                            "tail_internal_steps": excursion_tail_steps,
                            "post_exit_steps": excursion_post_exit_steps,
                            "tail_depth_landing": v2(x + 1) if x > 0 else None,
                        }
                    )
                excursion_start = x
                excursion_m = 0
                excursion_A = 0
                excursion_tail_steps = 0
                excursion_tail_delta = 0.0
                excursion_tail_A = 0
                excursion_post_exit_steps = 0
                excursion_post_exit_delta = 0.0
                excursion_post_exit_A = 0
        if x == 1:
            completed += 1
        else:
            truncated += 1

    return RenewalExcursionSample(
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        completed_orbits=completed,
        truncated_orbits=truncated,
        total_accelerated_steps=total_steps,
        total_excursions=total_excursions,
        deltas=tuple(deltas),
        m_values=tuple(m_values),
        A_values=tuple(A_values),
        tail_steps=tuple(tail_steps_values),
        tail_delta_log2=tuple(tail_delta_values),
        tail_A=tuple(tail_A_values),
        post_exit_steps=tuple(post_exit_steps_values),
        post_exit_delta_log2=tuple(post_exit_delta_values),
        post_exit_A=tuple(post_exit_A_values),
        phase_raw_sums=tuple(phase_raw_sums),
        phase_raw_cross_sums=tuple(tuple(row) for row in phase_raw_cross_sums),
        sample_excursions=tuple(sample_excursions),
    )


def orbit_renewal_descent_report(
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    max_steps_per_orbit: int = 10_000,
    cdf_points: tuple[float, ...] = (-8.0, -4.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0),
) -> RenewalDescentReport:
    """Aggregate actual accelerated orbits into tail-entry renewal excursions."""

    sample = _collect_renewal_excursions(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
    )
    deltas = list(sample.deltas)
    m_values = list(sample.m_values)
    A_values = list(sample.A_values)

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
        completed_orbits=sample.completed_orbits,
        truncated_orbits=sample.truncated_orbits,
        total_accelerated_steps=sample.total_accelerated_steps,
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
        sample_excursions=sample.sample_excursions,
    )


def _renewal_per_step_metrics(
    sum_delta: float,
    sum_m: float,
    sum_A: float,
) -> dict[str, float] | None:
    if sum_m <= 0.0:
        return None
    drift = sum_delta / sum_m
    valuation = sum_A / sum_m
    structural = math.log2(3.0) - valuation
    karp_target = math.log2(3.0 / 4.0)
    return {
        "mean_drift_per_step": drift,
        "mean_valuation_per_step": valuation,
        "structural_drift_prediction_per_step": structural,
        "structural_identity_residual": drift - structural,
        "valuation_minus_geom2_mean": valuation - 2.0,
        "drift_minus_karp_log2_3_over_4": drift - karp_target,
    }


def _bootstrap_renewal_per_step_metrics(
    deltas: tuple[float, ...],
    m_values: tuple[int, ...],
    A_values: tuple[int, ...],
    *,
    bootstrap_resamples: int,
    random_seed: int,
) -> tuple[dict[str, tuple[float, float]], str]:
    if bootstrap_resamples < 1:
        raise ValueError("bootstrap_resamples must be positive")
    if not deltas:
        return {}, "no_excursions"
    metric_samples: dict[str, list[float]] = {
        "mean_drift_per_step": [],
        "mean_valuation_per_step": [],
        "structural_drift_prediction_per_step": [],
        "structural_identity_residual": [],
        "valuation_minus_geom2_mean": [],
        "drift_minus_karp_log2_3_over_4": [],
    }
    n = len(deltas)
    exact_threshold = 250_000
    if n > exact_threshold:
        sums = _renewal_per_step_metrics(
            sum(deltas),
            float(sum(m_values)),
            float(sum(A_values)),
        )
        if sums is None:
            return {}, "no_accelerated_steps"
        mean_m = sum(m_values) / n
        drift = sums["mean_drift_per_step"]
        valuation = sums["mean_valuation_per_step"]
        ss_drift = 0.0
        ss_valuation = 0.0
        ss_cross = 0.0
        for delta, m_value, A_value in zip(deltas, m_values, A_values):
            drift_influence = (delta - drift * m_value) / mean_m
            valuation_influence = (A_value - valuation * m_value) / mean_m
            ss_drift += drift_influence * drift_influence
            ss_valuation += valuation_influence * valuation_influence
            ss_cross += drift_influence * valuation_influence
        scale = 1.0 / (n * n)
        var_drift = ss_drift * scale
        var_valuation = ss_valuation * scale
        cov = ss_cross * scale
        sd_drift = math.sqrt(max(0.0, var_drift))
        if var_drift > 0.0:
            beta = cov / var_drift
            conditional_var = max(0.0, var_valuation - beta * cov)
        else:
            beta = 0.0
            conditional_var = max(0.0, var_valuation)
        conditional_sd = math.sqrt(conditional_var)
        rng = random.Random(random_seed)
        for _ in range(bootstrap_resamples):
            z1 = rng.gauss(0.0, 1.0)
            z2 = rng.gauss(0.0, 1.0)
            sample_drift = drift + sd_drift * z1
            sample_valuation = valuation + beta * sd_drift * z1 + conditional_sd * z2
            metrics = _renewal_per_step_metrics(
                sample_drift,
                1.0,
                sample_valuation,
            )
            if metrics is None:
                continue
            for key, value in metrics.items():
                metric_samples[key].append(value)
        method = (
            "influence_function_normal_approximation_to_excursion_bootstrap"
        )
    else:
        try:
            import numpy as np
        except Exception:
            rng = random.Random(random_seed)
            for _ in range(bootstrap_resamples):
                sum_delta = 0.0
                sum_m = 0
                sum_A = 0
                for _sample in range(n):
                    index = rng.randrange(n)
                    sum_delta += deltas[index]
                    sum_m += m_values[index]
                    sum_A += A_values[index]
                metrics = _renewal_per_step_metrics(
                    sum_delta,
                    float(sum_m),
                    float(sum_A),
                )
                if metrics is None:
                    continue
                for key, value in metrics.items():
                    metric_samples[key].append(value)
            method = "exact_excursion_resample_percentile"
        else:
            rng = np.random.default_rng(random_seed)
            delta_array = np.asarray(deltas, dtype=np.float64)
            m_array = np.asarray(m_values, dtype=np.float64)
            A_array = np.asarray(A_values, dtype=np.float64)
            completed = 0
            while completed < bootstrap_resamples:
                batch = min(4, bootstrap_resamples - completed)
                indices = rng.integers(0, n, size=(batch, n))
                sum_deltas = delta_array[indices].sum(axis=1)
                sum_ms = m_array[indices].sum(axis=1)
                sum_As = A_array[indices].sum(axis=1)
                for offset in range(batch):
                    metrics = _renewal_per_step_metrics(
                        float(sum_deltas[offset]),
                        float(sum_ms[offset]),
                        float(sum_As[offset]),
                    )
                    if metrics is None:
                        continue
                    for key, value in metrics.items():
                        metric_samples[key].append(value)
                completed += batch
            method = "exact_excursion_resample_percentile"

    intervals: dict[str, tuple[float, float]] = {}
    for key, values in metric_samples.items():
        sorted_values = sorted(values)
        low = _quantile(sorted_values, 0.025)
        high = _quantile(sorted_values, 0.975)
        if low is not None and high is not None:
            intervals[key] = (low, high)
    return intervals, method


def _estimate_from_metrics(
    key: str,
    point_metrics: dict[str, float] | None,
    intervals: dict[str, tuple[float, float]],
) -> RenewalDriftEstimate:
    interval = intervals.get(key)
    return RenewalDriftEstimate(
        estimate=None if point_metrics is None else point_metrics[key],
        ci_low=None if interval is None else interval[0],
        ci_high=None if interval is None else interval[1],
    )


def _interval_contains(estimate: RenewalDriftEstimate, target: float) -> bool:
    return (
        estimate.ci_low is not None
        and estimate.ci_high is not None
        and estimate.ci_low <= target <= estimate.ci_high
    )


def _phase_metrics_from_raw(raw: tuple[float, ...]) -> dict[str, float] | None:
    (
        total_steps,
        total_delta,
        total_A,
        tail_steps,
        tail_delta,
        tail_A,
        post_steps,
        post_delta,
        post_A,
    ) = raw
    if total_steps <= 0.0 or tail_steps <= 0.0 or post_steps <= 0.0:
        return None
    total_drift = total_delta / total_steps
    tail_drift = tail_delta / tail_steps
    post_drift = post_delta / post_steps
    total_valuation = total_A / total_steps
    tail_valuation = tail_A / tail_steps
    post_valuation = post_A / post_steps
    w_tail = tail_steps / total_steps
    w_post = post_steps / total_steps
    return {
        "w_tail": w_tail,
        "w_post_exit": w_post,
        "mean_drift_per_step_total": total_drift,
        "mean_drift_per_step_tail": tail_drift,
        "mean_drift_per_step_post_exit": post_drift,
        "mean_valuation_per_step_total": total_valuation,
        "mean_valuation_per_step_tail": tail_valuation,
        "mean_valuation_per_step_post_exit": post_valuation,
        "reconciliation_residual": (
            total_drift - (w_tail * tail_drift + w_post * post_drift)
        ),
    }


def _phase_ci_from_raw_stats(
    count: int,
    raw_sums: tuple[float, ...],
    raw_cross_sums: tuple[tuple[float, ...], ...],
    *,
    bootstrap_resamples: int,
    random_seed: int,
) -> tuple[dict[str, tuple[float, float]], str]:
    if bootstrap_resamples < 1:
        raise ValueError("bootstrap_resamples must be positive")
    if count <= 1:
        return {}, "insufficient_excursions"
    point_metrics = _phase_metrics_from_raw(raw_sums)
    if point_metrics is None:
        return {}, "no_phase_steps"
    metric_samples: dict[str, list[float]] = {
        "w_tail": [],
        "w_post_exit": [],
        "mean_drift_per_step_total": [],
        "mean_drift_per_step_tail": [],
        "mean_drift_per_step_post_exit": [],
        "mean_valuation_per_step_total": [],
        "mean_valuation_per_step_tail": [],
        "mean_valuation_per_step_post_exit": [],
        "reconciliation_residual": [],
    }
    ratio_specs = {
        "w_tail": (3, 0),
        "w_post_exit": (6, 0),
        "mean_drift_per_step_total": (1, 0),
        "mean_drift_per_step_tail": (4, 3),
        "mean_drift_per_step_post_exit": (7, 6),
        "mean_valuation_per_step_total": (2, 0),
        "mean_valuation_per_step_tail": (5, 3),
        "mean_valuation_per_step_post_exit": (8, 6),
    }
    rng = random.Random(random_seed)
    for key, (numerator_index, denominator_index) in ratio_specs.items():
        estimate = point_metrics[key]
        denominator_mean = raw_sums[denominator_index] / count
        numerator_sq = raw_cross_sums[numerator_index][numerator_index]
        denominator_sq = raw_cross_sums[denominator_index][denominator_index]
        numerator_denominator = raw_cross_sums[numerator_index][denominator_index]
        influence_ss = (
            numerator_sq
            - 2.0 * estimate * numerator_denominator
            + estimate * estimate * denominator_sq
        )
        variance = influence_ss / (count - 1) / (denominator_mean**2) / count
        sd = math.sqrt(max(0.0, variance))
        metric_samples[key] = [
            rng.gauss(estimate, sd) for _ in range(bootstrap_resamples)
        ]
    metric_samples["reconciliation_residual"] = [
        point_metrics["reconciliation_residual"]
        for _ in range(bootstrap_resamples)
    ]

    intervals: dict[str, tuple[float, float]] = {}
    for key, values in metric_samples.items():
        sorted_values = sorted(values)
        low = _quantile(sorted_values, 0.025)
        high = _quantile(sorted_values, 0.975)
        if low is not None and high is not None:
            intervals[key] = (low, high)
    return (
        intervals,
        "influence_function_normal_approximation_to_excursion_bootstrap",
    )


def renewal_drift_per_step_report(
    *,
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    bootstrap_resamples: int = 1000,
    max_steps_per_orbit: int = 10_000,
) -> RenewalDriftPerStepReport:
    """Bootstrap the per-step renewal drift identity on sampled excursions."""

    sample = _collect_renewal_excursions(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
    )
    total_excursions = len(sample.deltas)
    sum_delta = sum(sample.deltas)
    sum_m = sum(sample.m_values)
    sum_A = sum(sample.A_values)
    point_metrics = _renewal_per_step_metrics(
        sum_delta,
        float(sum_m),
        float(sum_A),
    )
    intervals, bootstrap_ci_method = _bootstrap_renewal_per_step_metrics(
        sample.deltas,
        sample.m_values,
        sample.A_values,
        bootstrap_resamples=bootstrap_resamples,
        random_seed=random_seed + 1,
    )
    mean_drift = _estimate_from_metrics(
        "mean_drift_per_step",
        point_metrics,
        intervals,
    )
    mean_valuation = _estimate_from_metrics(
        "mean_valuation_per_step",
        point_metrics,
        intervals,
    )
    structural_prediction = _estimate_from_metrics(
        "structural_drift_prediction_per_step",
        point_metrics,
        intervals,
    )
    identity_residual = _estimate_from_metrics(
        "structural_identity_residual",
        point_metrics,
        intervals,
    )
    valuation_residual = _estimate_from_metrics(
        "valuation_minus_geom2_mean",
        point_metrics,
        intervals,
    )
    drift_residual = _estimate_from_metrics(
        "drift_minus_karp_log2_3_over_4",
        point_metrics,
        intervals,
    )
    geom2_consistent = _interval_contains(mean_valuation, 2.0)
    karp_target = math.log2(3.0 / 4.0)
    karp_consistent = _interval_contains(mean_drift, karp_target)
    if geom2_consistent and karp_consistent:
        verdict = "both_consistent"
    elif geom2_consistent:
        verdict = "only_valuation_consistent"
    elif karp_consistent:
        verdict = "only_drift_consistent"
    else:
        verdict = "neither_consistent"
    status = f"empirical_per_step_renewal_drift_{verdict}"
    return RenewalDriftPerStepReport(
        type="renewal_drift_per_step",
        status=status,
        caveat=(
            "Empirical bootstrap diagnostic at one start window only. It does "
            "not prove the per-step identity, the Geom(2) valuation law, or "
            "any all-n Collatz descent statement. Large excursion samples use "
            "the recorded influence-function approximation to the excursion "
            "bootstrap distribution."
        ),
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        bootstrap_resamples=bootstrap_resamples,
        bootstrap_ci_method=bootstrap_ci_method,
        completed_orbits=sample.completed_orbits,
        truncated_orbits=sample.truncated_orbits,
        total_accelerated_steps=sample.total_accelerated_steps,
        total_excursions=total_excursions,
        mean_delta_log2=None if total_excursions == 0 else sum_delta / total_excursions,
        mean_m_PE=None if total_excursions == 0 else sum_m / total_excursions,
        mean_A_PE=None if total_excursions == 0 else sum_A / total_excursions,
        geom2_valuation_target=2.0,
        karp_drift_target=karp_target,
        mean_drift_per_step=mean_drift,
        mean_valuation_per_step=mean_valuation,
        structural_drift_prediction_per_step=structural_prediction,
        structural_identity_residual=identity_residual,
        valuation_minus_geom2_mean=valuation_residual,
        drift_minus_karp_log2_3_over_4=drift_residual,
        geom2_mean_consistent=geom2_consistent,
        karp_drift_consistent=karp_consistent,
        verdict=verdict,
    )


def renewal_drift_phase_decomposed_report(
    *,
    sample_count: int = 1_000_000,
    start_min: int = 10**6,
    start_max: int = 10**9,
    random_seed: int = 0,
    bootstrap_resamples: int = 1000,
    max_steps_per_orbit: int = 10_000,
) -> RenewalDriftPhaseDecomposedReport:
    """Bootstrap tail-internal vs post-exit renewal drift phases."""

    sample = _collect_renewal_excursions(
        sample_count=sample_count,
        start_min=start_min,
        start_max=start_max,
        random_seed=random_seed,
        max_steps_per_orbit=max_steps_per_orbit,
        collect_phase_stats=True,
        store_renewal_values=False,
    )
    point_metrics = _phase_metrics_from_raw(sample.phase_raw_sums)
    intervals, bootstrap_ci_method = _phase_ci_from_raw_stats(
        sample.total_excursions,
        sample.phase_raw_sums,
        sample.phase_raw_cross_sums,
        bootstrap_resamples=bootstrap_resamples,
        random_seed=random_seed + 2,
    )
    tail_target = math.log2(3.0 / 2.0)
    post_target = math.log2(3.0 / 4.0)
    w_tail = _estimate_from_metrics("w_tail", point_metrics, intervals)
    w_post = _estimate_from_metrics("w_post_exit", point_metrics, intervals)
    total_drift = _estimate_from_metrics(
        "mean_drift_per_step_total",
        point_metrics,
        intervals,
    )
    tail_drift = _estimate_from_metrics(
        "mean_drift_per_step_tail",
        point_metrics,
        intervals,
    )
    post_drift = _estimate_from_metrics(
        "mean_drift_per_step_post_exit",
        point_metrics,
        intervals,
    )
    total_valuation = _estimate_from_metrics(
        "mean_valuation_per_step_total",
        point_metrics,
        intervals,
    )
    tail_valuation = _estimate_from_metrics(
        "mean_valuation_per_step_tail",
        point_metrics,
        intervals,
    )
    post_valuation = _estimate_from_metrics(
        "mean_valuation_per_step_post_exit",
        point_metrics,
        intervals,
    )
    residual = _estimate_from_metrics(
        "reconciliation_residual",
        point_metrics,
        intervals,
    )
    tail_steps = int(sample.phase_raw_sums[3])
    post_steps = int(sample.phase_raw_sums[6])
    tail_A = sample.phase_raw_sums[5]
    tail_valuation_exact = tail_steps > 0 and tail_A == float(tail_steps)
    tail_drift_consistent = _interval_contains(tail_drift, tail_target)
    post_drift_consistent = _interval_contains(post_drift, post_target)
    post_valuation_consistent = _interval_contains(post_valuation, 2.0)
    if post_drift_consistent and post_valuation_consistent:
        verdict = "phase_mixing_explains_deviation"
    elif post_drift_consistent:
        verdict = "post_exit_drift_only_consistent"
    elif post_valuation_consistent:
        verdict = "post_exit_valuation_only_consistent"
    else:
        verdict = "neither_post_exit_consistent"
    return RenewalDriftPhaseDecomposedReport(
        type="renewal_drift_phase_decomposed",
        status=f"empirical_renewal_drift_phase_decomposed_{verdict}",
        caveat=(
            "Empirical phase-decomposed diagnostic at one start window only. "
            "It does not prove a per-step identity for all n. The "
            "tail-internal/post-exit phase classification is a finite "
            "diagnostic based on the sampled pre-step odd integers."
        ),
        sample_count=sample_count,
        random_seed=random_seed,
        start_min=start_min,
        start_max=start_max,
        bootstrap_resamples=bootstrap_resamples,
        bootstrap_ci_method=bootstrap_ci_method,
        completed_orbits=sample.completed_orbits,
        truncated_orbits=sample.truncated_orbits,
        total_accelerated_steps=sample.total_accelerated_steps,
        total_excursions=sample.total_excursions,
        total_excursion_steps=int(sample.phase_raw_sums[0]),
        tail_internal_steps=tail_steps,
        post_exit_steps=post_steps,
        tail_drift_target=tail_target,
        post_exit_drift_target=post_target,
        post_exit_valuation_target=2.0,
        w_tail=w_tail,
        w_post_exit=w_post,
        mean_drift_per_step_total=total_drift,
        mean_drift_per_step_tail=tail_drift,
        mean_drift_per_step_post_exit=post_drift,
        mean_valuation_per_step_total=total_valuation,
        mean_valuation_per_step_tail=tail_valuation,
        mean_valuation_per_step_post_exit=post_valuation,
        reconciliation_residual=residual,
        tail_valuation_exact_check=tail_valuation_exact,
        tail_drift_consistent=tail_drift_consistent,
        post_exit_drift_consistent=post_drift_consistent,
        post_exit_valuation_consistent=post_valuation_consistent,
        verdict=verdict,
    )


def _ci_halfwidth(estimate: RenewalDriftEstimate) -> float | None:
    if estimate.ci_low is None or estimate.ci_high is None:
        return None
    return max(
        abs(estimate.estimate - estimate.ci_low)
        if estimate.estimate is not None
        else 0.0,
        abs(estimate.ci_high - estimate.estimate)
        if estimate.estimate is not None
        else 0.0,
    )


def _nonincreasing_abs(values: list[float]) -> bool:
    return all(
        abs(values[index + 1]) <= abs(values[index]) + 1e-15
        for index in range(len(values) - 1)
    )


def _deviation_log_slope(
    points: list[tuple[float, float]],
) -> float | None:
    if not points:
        return None
    signs = {1 if value > 0.0 else -1 if value < 0.0 else 0 for _x, value in points}
    if 0 in signs or len(signs) != 1:
        return None
    return _least_squares_slope(
        [(x, math.log10(abs(value))) for x, value in points]
    )


def renewal_drift_phase_decomposed_n0_stability_report(
    *,
    ranges: tuple[tuple[int, int], ...] = (
        (10**2, 10**4),
        (10**4, 10**6),
        (10**6, 10**9),
        (10**9, 10**12),
        (10**12, 10**15),
    ),
    sample_count_per_range: int = 200_000,
    random_seed: int = 0,
    bootstrap_resamples: int = 1000,
    max_steps_per_orbit: int = 10_000,
) -> RenewalDriftPhaseN0StabilityReport:
    """Run the phase-decomposed renewal-drift audit across n0 windows."""

    if sample_count_per_range < 1:
        raise ValueError("sample_count_per_range must be positive")
    if not ranges:
        raise ValueError("ranges must be nonempty")

    total_drift_target = math.log2(3.0 / 4.0)
    post_exit_target = 3.0
    range_reports: list[RenewalDriftPhaseN0RangeReport] = []
    ci_method = "influence_function_normal_approximation_to_excursion_bootstrap"
    for index, (start_min, start_max) in enumerate(ranges):
        if start_min < 1 or start_max <= start_min:
            raise ValueError("expected 1 <= start_min < start_max")
        sample = _collect_renewal_excursions(
            sample_count=sample_count_per_range,
            start_min=start_min,
            start_max=start_max,
            random_seed=random_seed + index,
            max_steps_per_orbit=max_steps_per_orbit,
            collect_phase_stats=True,
            store_renewal_values=False,
        )
        point_metrics = _phase_metrics_from_raw(sample.phase_raw_sums)
        intervals, method = _phase_ci_from_raw_stats(
            sample.total_excursions,
            sample.phase_raw_sums,
            sample.phase_raw_cross_sums,
            bootstrap_resamples=bootstrap_resamples,
            random_seed=random_seed + 1000 + index,
        )
        ci_method = method
        total_drift = _estimate_from_metrics(
            "mean_drift_per_step_total",
            point_metrics,
            intervals,
        )
        tail_drift = _estimate_from_metrics(
            "mean_drift_per_step_tail",
            point_metrics,
            intervals,
        )
        tail_valuation = _estimate_from_metrics(
            "mean_valuation_per_step_tail",
            point_metrics,
            intervals,
        )
        post_drift = _estimate_from_metrics(
            "mean_drift_per_step_post_exit",
            point_metrics,
            intervals,
        )
        post_valuation = _estimate_from_metrics(
            "mean_valuation_per_step_post_exit",
            point_metrics,
            intervals,
        )
        w_tail = None if point_metrics is None else point_metrics["w_tail"]
        w_post = None if point_metrics is None else point_metrics["w_post_exit"]
        weights_balanced = (
            w_tail is not None
            and w_post is not None
            and 0.495 <= w_tail <= 0.505
            and 0.495 <= w_post <= 0.505
        )
        range_reports.append(
            RenewalDriftPhaseN0RangeReport(
                start_min=start_min,
                start_max=start_max,
                midpoint_log10_n=(
                    math.log10(start_min) + math.log10(start_max)
                )
                / 2.0,
                sample_count=sample_count_per_range,
                completed_orbits=sample.completed_orbits,
                truncated_orbits=sample.truncated_orbits,
                total_excursions=sample.total_excursions,
                total_accelerated_steps=sample.total_accelerated_steps,
                w_tail=w_tail,
                w_post_exit=w_post,
                weights_balanced=weights_balanced,
                mean_drift_per_step_total=total_drift,
                mean_drift_per_step_tail=tail_drift,
                mean_valuation_per_step_tail=tail_valuation,
                mean_drift_per_step_post_exit=post_drift,
                mean_valuation_per_step_post_exit=post_valuation,
                post_exit_valuation_deviation=(
                    None
                    if post_valuation.estimate is None
                    else post_valuation.estimate - post_exit_target
                ),
                total_drift_deviation=(
                    None
                    if total_drift.estimate is None
                    else total_drift.estimate - total_drift_target
                ),
            )
        )

    post_points = [
        (
            item.midpoint_log10_n,
            item.post_exit_valuation_deviation,
            _ci_halfwidth(item.mean_valuation_per_step_post_exit),
        )
        for item in range_reports
        if item.post_exit_valuation_deviation is not None
    ]
    drift_points = [
        (
            item.midpoint_log10_n,
            item.total_drift_deviation,
            _ci_halfwidth(item.mean_drift_per_step_total),
        )
        for item in range_reports
        if item.total_drift_deviation is not None
    ]
    post_values = [value for _x, value, _halfwidth in post_points]
    drift_values = [value for _x, value, _halfwidth in drift_points]
    post_monotone = len(post_values) >= 2 and _nonincreasing_abs(post_values)
    drift_monotone = len(drift_values) >= 2 and _nonincreasing_abs(drift_values)
    post_slope = _deviation_log_slope(
        [(x, value) for x, value, _halfwidth in post_points]
    )
    drift_slope = _deviation_log_slope(
        [(x, value) for x, value, _halfwidth in drift_points]
    )
    deepest = range_reports[-1]
    deepest_post = _interval_contains(
        deepest.mean_valuation_per_step_post_exit,
        post_exit_target,
    )
    deepest_drift = _interval_contains(
        deepest.mean_drift_per_step_total,
        total_drift_target,
    )
    slopes_negative = (
        post_slope is not None
        and drift_slope is not None
        and post_slope < 0.0
        and drift_slope < 0.0
    )
    if deepest_post and deepest_drift:
        verdict = "asymptotic_identity_supported"
    elif post_monotone and drift_monotone and slopes_negative:
        verdict = "converging_but_not_yet_at_target"
    elif len(post_values) >= 2 and len(drift_values) >= 2 and (
        abs(post_values[-1]) > abs(post_values[0])
        and abs(drift_values[-1]) > abs(drift_values[0])
    ):
        verdict = "diverging"
    else:
        verdict = "non_monotone_or_flat"
    return RenewalDriftPhaseN0StabilityReport(
        type="renewal_drift_phase_decomposed_n0_stability",
        status=f"empirical_phase_decomposed_n0_stability_{verdict}",
        caveat=(
            "Empirical finite-sample n0 sweep over phase-decomposed renewal "
            "drift. It does not prove an asymptotic identity or all-n "
            "Collatz descent."
        ),
        sample_count_per_range=sample_count_per_range,
        random_seed=random_seed,
        ranges=ranges,
        bootstrap_resamples=bootstrap_resamples,
        bootstrap_ci_method=ci_method,
        post_exit_valuation_target=post_exit_target,
        total_drift_target=total_drift_target,
        post_exit_valuation_deviations=tuple(post_points),
        total_drift_deviations=tuple(drift_points),
        post_exit_valuation_monotone=post_monotone,
        total_drift_monotone=drift_monotone,
        post_exit_valuation_log_slope_per_decade=post_slope,
        total_drift_log_slope_per_decade=drift_slope,
        deepest_window_post_exit_consistent=deepest_post,
        deepest_window_total_drift_consistent=deepest_drift,
        verdict=verdict,
        range_reports=tuple(range_reports),
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
