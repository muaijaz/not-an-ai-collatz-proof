"""Closed-form stress tests for the renewal Cramer-rate constant."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class JazzTailComparison:
    excursions: int
    exact_binned_empirical_tail: float | None
    empirical_saddlepoint_tail: float
    empirical_saddlepoint_log_tail: float
    empirical_saddlepoint_rate_with_prefactor: float
    closed_crude_tail: float
    closed_gaussian_prefactor_tail: float
    closed_empirical_saddle_prefactor_tail: float
    closed_empirical_saddle_prefactor_log_tail: float
    closed_to_empirical_saddle_ratio: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JazzConstantClosedFormReport:
    type: str
    status: str
    candidate_name: str
    candidate_value: float
    empirical_cramer_rate: float
    bootstrap_q025: float
    bootstrap_q975: float
    candidate_inside_bootstrap_ci: bool
    absolute_difference: float
    relative_difference: float
    sigma_units_from_ci_half_width: float
    variance_delta_log2: float
    empirical_lambda: float
    empirical_tilted_variance: float
    tail_comparisons: tuple[JazzTailComparison, ...]
    verdict: str
    caveat: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "candidate_name": self.candidate_name,
            "candidate_value": self.candidate_value,
            "empirical_cramer_rate": self.empirical_cramer_rate,
            "bootstrap_q025": self.bootstrap_q025,
            "bootstrap_q975": self.bootstrap_q975,
            "candidate_inside_bootstrap_ci": self.candidate_inside_bootstrap_ci,
            "absolute_difference": self.absolute_difference,
            "relative_difference": self.relative_difference,
            "sigma_units_from_ci_half_width": self.sigma_units_from_ci_half_width,
            "variance_delta_log2": self.variance_delta_log2,
            "empirical_lambda": self.empirical_lambda,
            "empirical_tilted_variance": self.empirical_tilted_variance,
            "tail_comparisons": [
                item.to_json_dict() for item in self.tail_comparisons
            ],
            "verdict": self.verdict,
            "caveat": self.caveat,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class JazzSpikeContribution:
    segment: str
    probability: float
    excursions: int
    mean_delta_log2: float
    drift_contribution: float
    interpolated_mgf_at_lambda: float
    weighted_mgf_at_lambda: float
    percent_of_total_mgf: float
    geometric_ratio_from_k4: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JazzClosedFormCandidate:
    name: str
    value: float
    inside_bootstrap_ci: bool
    difference_from_empirical: float
    ci_half_width_units: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JazzConstantDecompositionReport:
    type: str
    status: str
    empirical_cramer_rate: float
    bootstrap_q025: float
    bootstrap_q975: float
    empirical_lambda: float
    interpolated_decomposition_mgf: float
    interpolated_decomposition_rate: float
    interpolation_caveat: str
    gaussian_candidate_name: str
    gaussian_candidate_value: float
    heavy_tail_correction: float
    heavy_tail_relative_multiplier: float
    dominant_segment: str
    dominant_segment_percent_of_mgf: float
    spike_contributions: tuple[JazzSpikeContribution, ...]
    closed_form_candidates: tuple[JazzClosedFormCandidate, ...]
    verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "empirical_cramer_rate": self.empirical_cramer_rate,
            "bootstrap_q025": self.bootstrap_q025,
            "bootstrap_q975": self.bootstrap_q975,
            "empirical_lambda": self.empirical_lambda,
            "interpolated_decomposition_mgf": self.interpolated_decomposition_mgf,
            "interpolated_decomposition_rate": self.interpolated_decomposition_rate,
            "interpolation_caveat": self.interpolation_caveat,
            "gaussian_candidate_name": self.gaussian_candidate_name,
            "gaussian_candidate_value": self.gaussian_candidate_value,
            "heavy_tail_correction": self.heavy_tail_correction,
            "heavy_tail_relative_multiplier": self.heavy_tail_relative_multiplier,
            "dominant_segment": self.dominant_segment,
            "dominant_segment_percent_of_mgf": self.dominant_segment_percent_of_mgf,
            "spike_contributions": [
                item.to_json_dict() for item in self.spike_contributions
            ],
            "closed_form_candidates": [
                item.to_json_dict() for item in self.closed_form_candidates
            ],
            "verdict": self.verdict,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bootstrap_interval(data: dict[str, Any], quantity: str) -> tuple[float, float]:
    for interval in data.get("bootstrap_intervals", []):
        if interval.get("quantity") == quantity:
            return float(interval["q025"]), float(interval["q975"])
    raise ValueError(f"missing bootstrap interval for {quantity}")


def _saddlepoint_tail(
    rate: float,
    lam: float,
    tilted_variance: float,
    horizon: int,
) -> tuple[float, float, float]:
    prefactor = 1.0 / (lam * math.sqrt(2.0 * math.pi * horizon * tilted_variance))
    log_probability = math.log(prefactor) - horizon * rate
    probability = min(1.0, math.exp(log_probability)) if log_probability > -745.0 else 0.0
    log_probability = min(0.0, log_probability)
    rate_with_prefactor = -log_probability / horizon
    return probability, rate_with_prefactor, log_probability


def _exact_binned_tail(
    histogram_bins: list[list[int]],
    horizon: int,
    max_fft_length: int,
) -> float | None:
    if horizon < 1:
        return None
    buckets = [int(bucket) for bucket, _count in histogram_bins]
    counts = [int(count) for _bucket, count in histogram_bins]
    if not buckets:
        return None
    min_bucket = min(buckets)
    max_bucket = max(buckets)
    support = horizon * (max_bucket - min_bucket) + 1
    if support > max_fft_length:
        return None
    try:
        import numpy as np
    except Exception:
        return None
    length = 1
    while length < support:
        length <<= 1
    probabilities = np.zeros(max_bucket - min_bucket + 1, dtype=np.float64)
    total = float(sum(counts))
    for bucket, count in zip(buckets, counts):
        probabilities[bucket - min_bucket] = count / total
    padded = np.zeros(length, dtype=np.float64)
    padded[: len(probabilities)] = probabilities
    transform = np.fft.rfft(padded)
    convolved = np.fft.irfft(transform**horizon, n=length)[:support]
    convolved = np.maximum(convolved, 0.0)
    offset = -horizon * min_bucket
    if offset >= support:
        return 0.0
    tail = float(convolved[offset:].sum())
    return min(1.0, max(0.0, tail))


def _interpolate_log_mgf(mgf_values: dict[str, float], lam: float) -> float:
    points = sorted((float(key), float(value)) for key, value in mgf_values.items())
    if not points:
        raise ValueError("missing MGF values")
    for key, value in points:
        if abs(key - lam) < 1e-15:
            return value
    lower = None
    upper = None
    for point in points:
        if point[0] <= lam:
            lower = point
        if point[0] >= lam and upper is None:
            upper = point
    if lower is None:
        return points[0][1]
    if upper is None:
        return points[-1][1]
    if lower[0] == upper[0]:
        return lower[1]
    weight = (lam - lower[0]) / (upper[0] - lower[0])
    log_value = math.log(lower[1]) + weight * (math.log(upper[1]) - math.log(lower[1]))
    return math.exp(log_value)


def _candidate_report(
    name: str,
    value: float,
    empirical: float,
    q025: float,
    q975: float,
) -> JazzClosedFormCandidate:
    ci_half = (q975 - q025) / 2.0
    difference = value - empirical
    return JazzClosedFormCandidate(
        name=name,
        value=value,
        inside_bootstrap_ci=q025 <= value <= q975,
        difference_from_empirical=difference,
        ci_half_width_units=(
            abs(difference) / ci_half if ci_half > 0.0 else float("inf")
        ),
    )


def jazz_constant_closed_form_report(
    bootstrap_path: str | Path = "docs/reports/renewal_bootstrap_calibration.json",
    horizons: tuple[int, ...] = (10, 100, 1000, 10_000),
    max_exact_fft_length: int = 1_500_000,
) -> JazzConstantClosedFormReport:
    """Stress-test the candidate ``I(0)=log(4/3)^2`` against saved data."""

    data = _read_json(Path(bootstrap_path))
    candidate = math.log(4.0 / 3.0) ** 2
    empirical = float(data["cramer_rate_I0"])
    q025, q975 = _bootstrap_interval(data, "cramer_rate_I0")
    ci_half = (q975 - q025) / 2.0
    difference = empirical - candidate
    variance = float(data["variance_delta_log2"])
    lam = float(data["cramer_lambda"])
    tilted_variance = float(data["tilted_variance_at_lambda"])
    comparisons: list[JazzTailComparison] = []
    for horizon in horizons:
        empirical_tail, empirical_rate_pref, empirical_log_tail = _saddlepoint_tail(
            empirical, lam, tilted_variance, horizon
        )
        closed_crude = math.exp(-candidate * horizon)
        closed_gaussian = closed_crude / math.sqrt(2.0 * math.pi * variance * horizon)
        closed_saddle, _closed_saddle_rate, closed_log_tail = _saddlepoint_tail(
            candidate, lam, tilted_variance, horizon
        )
        log_ratio = closed_log_tail - empirical_log_tail
        ratio = math.exp(log_ratio) if log_ratio < 700.0 else None
        comparisons.append(
            JazzTailComparison(
                excursions=horizon,
                exact_binned_empirical_tail=_exact_binned_tail(
                    data.get("histogram_bins", []),
                    horizon,
                    max_exact_fft_length,
                ),
                empirical_saddlepoint_tail=empirical_tail,
                empirical_saddlepoint_log_tail=empirical_log_tail,
                empirical_saddlepoint_rate_with_prefactor=empirical_rate_pref,
                closed_crude_tail=closed_crude,
                closed_gaussian_prefactor_tail=closed_gaussian,
                closed_empirical_saddle_prefactor_tail=closed_saddle,
                closed_empirical_saddle_prefactor_log_tail=closed_log_tail,
                closed_to_empirical_saddle_ratio=ratio,
            )
        )
    inside = q025 <= candidate <= q975
    verdict = (
        "closed_form_candidate_rejected_by_bootstrap_ci"
        if not inside
        else "closed_form_candidate_consistent_with_bootstrap_ci"
    )
    return JazzConstantClosedFormReport(
        type="jazz_constant_closed_form_test",
        status="closed_form_hypothesis_stress_test_not_collatz_proof",
        candidate_name="log(4/3)^2",
        candidate_value=candidate,
        empirical_cramer_rate=empirical,
        bootstrap_q025=q025,
        bootstrap_q975=q975,
        candidate_inside_bootstrap_ci=inside,
        absolute_difference=abs(difference),
        relative_difference=abs(difference) / empirical,
        sigma_units_from_ci_half_width=(
            abs(difference) / ci_half if ci_half > 0.0 else float("inf")
        ),
        variance_delta_log2=variance,
        empirical_lambda=lam,
        empirical_tilted_variance=tilted_variance,
        tail_comparisons=tuple(comparisons),
        verdict=verdict,
        caveat=(
            "The test uses the saved binned empirical renewal law. Exact binned "
            "convolutions are reported only where FFT support is small enough; "
            "large horizons use saddlepoint calibration. Rejection by bootstrap "
            "CI means the candidate is not the measured empirical-renewal rate, "
            "not that it cannot describe another idealized model."
        ),
    )


def jazz_constant_decomposition_report(
    per_k_path: str | Path = "docs/reports/orbit_renewal_per_k_mgf.json",
    bootstrap_path: str | Path = "docs/reports/renewal_bootstrap_calibration.json",
) -> JazzConstantDecompositionReport:
    """Spike-stratified representation of the empirical renewal Cramer rate."""

    per_k = _read_json(Path(per_k_path))
    bootstrap = _read_json(Path(bootstrap_path))
    empirical = float(bootstrap["cramer_rate_I0"])
    lam = float(bootstrap["cramer_lambda"])
    q025, q975 = _bootstrap_interval(bootstrap, "cramer_rate_I0")
    weighted_values: list[tuple[dict[str, Any], float, float]] = []
    total_mgf = 0.0
    for segment in per_k.get("segments", []):
        mgf = _interpolate_log_mgf(segment["mgf_positive_tail"], lam)
        weighted = float(segment["probability"]) * mgf
        weighted_values.append((segment, mgf, weighted))
        total_mgf += weighted
    contributions = tuple(
        JazzSpikeContribution(
            segment=str(segment["segment"]),
            probability=float(segment["probability"]),
            excursions=int(segment["excursions"]),
            mean_delta_log2=float(segment["mean_delta_log2"]),
            drift_contribution=float(segment["drift_contribution"]),
            interpolated_mgf_at_lambda=mgf,
            weighted_mgf_at_lambda=weighted,
            percent_of_total_mgf=(
                100.0 * weighted / total_mgf if total_mgf > 0.0 else 0.0
            ),
            geometric_ratio_from_k4=(
                None
                if segment.get("geometric_ratio_from_k4") is None
                else float(segment["geometric_ratio_from_k4"])
            ),
        )
        for segment, mgf, weighted in weighted_values
    )
    dominant = max(contributions, key=lambda item: item.percent_of_total_mgf)
    gaussian = math.log(4.0 / 3.0) ** 2
    candidates = (
        _candidate_report("log(4/3)^2", gaussian, empirical, q025, q975),
        _candidate_report("1/12", 1.0 / 12.0, empirical, q025, q975),
        _candidate_report("log2(3)/19", math.log2(3.0) / 19.0, empirical, q025, q975),
        _candidate_report(
            "(log2(3)-1)/7",
            (math.log2(3.0) - 1.0) / 7.0,
            empirical,
            q025,
            q975,
        ),
    )
    return JazzConstantDecompositionReport(
        type="jazz_constant_spike_decomposition",
        status="structural_decomposition_of_empirical_renewal_constant_not_collatz_proof",
        empirical_cramer_rate=empirical,
        bootstrap_q025=q025,
        bootstrap_q975=q975,
        empirical_lambda=lam,
        interpolated_decomposition_mgf=total_mgf,
        interpolated_decomposition_rate=-math.log(total_mgf),
        interpolation_caveat=(
            "Per-spike MGFs are saved on a coarse lambda grid; this report "
            "log-linearly interpolates them to the bootstrap optimizer. The "
            "bootstrap histogram remains the source of the high-precision J value."
        ),
        gaussian_candidate_name="log(4/3)^2",
        gaussian_candidate_value=gaussian,
        heavy_tail_correction=empirical - gaussian,
        heavy_tail_relative_multiplier=empirical / gaussian,
        dominant_segment=dominant.segment,
        dominant_segment_percent_of_mgf=dominant.percent_of_total_mgf,
        spike_contributions=contributions,
        closed_form_candidates=candidates,
        verdict=(
            "Jazz's constant is best treated as a Khinchin-style renewal "
            "constant: the obvious elementary candidates are rejected by the "
            "tight bootstrap interval, while the spike decomposition gives the "
            "useful structural representation."
        ),
    )
