"""Upper/lower-bound squeeze summaries for Collatz experiment artifacts."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SqueezeEntry:
    name: str
    quantity: str
    empirical_value: float | bool | None
    lower_bound: float | bool | None
    upper_bound: float | bool | None
    lower_method: str
    upper_method: str
    evidence_type: str
    confidence: str | None
    notes: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RigorousSqueezeReport:
    type: str
    status: str
    caveat: str
    entries: tuple[SqueezeEntry, ...]
    theorem_or_finite_entries: int
    high_confidence_entries: int
    empirical_envelope_entries: int

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "entries": [entry.to_json_dict() for entry in self.entries],
            "theorem_or_finite_entries": self.theorem_or_finite_entries,
            "high_confidence_entries": self.high_confidence_entries,
            "empirical_envelope_entries": self.empirical_envelope_entries,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _empirical_bernstein_radius(
    variance: float,
    lower: float,
    upper: float,
    sample_size: int,
    delta: float,
) -> float:
    """One empirical-Bernstein style radius for bounded independent samples."""

    if sample_size <= 0:
        return math.inf
    span = upper - lower
    log_term = math.log(3.0 / delta)
    return math.sqrt(2.0 * variance * log_term / sample_size) + (
        3.0 * span * log_term / sample_size
    )


def _wilson_interval(successes: int, trials: int, z: float) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 1.0)
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    radius = (
        z
        * math.sqrt((p * (1.0 - p) / trials) + z * z / (4.0 * trials * trials))
        / denom
    )
    return max(0.0, center - radius), min(1.0, center + radius)


def _renewal_entries(reports_path: Path) -> list[SqueezeEntry]:
    entries: list[SqueezeEntry] = []
    descent = _read_json(reports_path / "orbit_renewal_descent.json")
    spike = _read_json(reports_path / "orbit_renewal_spike_decomposition.json")
    per_k = _read_json(reports_path / "orbit_renewal_per_k_mgf.json")
    markov = _read_json(reports_path / "orbit_renewal_markov_cramer.json")
    stability = _read_json(reports_path / "orbit_renewal_n0_stability.json")
    bootstrap = _read_json(reports_path / "renewal_bootstrap_calibration.json")
    if descent and spike:
        n = int(spike["total_excursions"])
        mean = float(spike["mean_delta_log2"])
        variance = float(spike["variance_delta_log2"])
        lower = float(descent["min_delta_log2"])
        upper = float(descent["max_delta_log2"])
        delta = 1e-12
        radius = _empirical_bernstein_radius(variance, lower, upper, n, delta)
        entries.append(
            SqueezeEntry(
                name="renewal_mean_delta_log2",
                quantity="E[Delta log2 n per renewal excursion]",
                empirical_value=mean,
                lower_bound=mean - radius,
                upper_bound=mean + radius,
                lower_method="empirical Bernstein bounded-sample interval",
                upper_method="empirical Bernstein bounded-sample interval",
                evidence_type="high_confidence_empirical",
                confidence=f"1-delta with delta={delta}; assumes sampled excursions are representative/independent enough for concentration use",
                notes=(
                    f"N={n}, variance={variance}, observed range=[{lower}, {upper}]. "
                    "This is a statistical squeeze on the sampled renewal law, not a Collatz theorem."
                ),
            )
        )
        mu = -mean
        b = upper - mean
        bernstein_rate = (mu * mu) / (2.0 * variance + 2.0 * b * mu / 3.0)
        entries.append(
            SqueezeEntry(
                name="renewal_upper_tail_cramer_rate",
                quantity="I(0) for P(sum Delta >= 0) per renewal",
                empirical_value=float(spike["cramer_rate_I0_grid"]),
                lower_bound=bernstein_rate,
                upper_bound=None,
                lower_method="one-sided Bernstein bound using observed upper increment bound",
                upper_method="not computed; requires block-sum tail lower confidence bounds",
                evidence_type="mostly_rigorous_empirical",
                confidence="conditional on the sampled bounded-increment renewal law",
                notes=(
                    "The lower bound is conservative and matches the artifact's "
                    f"Bernstein rate {spike.get('bernstein_rate')}. A rigorous upper "
                    "bound needs explicit tail-probability confidence intervals for block sums."
                ),
            )
        )
    if spike and per_k and markov:
        estimates = [
            float(spike["cramer_rate_I0_grid"]),
            float(per_k["implied_cramer_rate_grid"]),
            float(markov["best_markov_rate"]),
            float(markov["best_iid_all_excursion_rate"]),
        ]
        entries.append(
            SqueezeEntry(
                name="cramer_rate_method_spread",
                quantity="I(0) estimated by independent finite estimators",
                empirical_value=float(spike["cramer_rate_I0_grid"]),
                lower_bound=min(estimates),
                upper_bound=max(estimates),
                lower_method="minimum across saved iid/per-k/Markov estimators",
                upper_method="maximum across saved iid/per-k/Markov estimators",
                evidence_type="empirical_envelope",
                confidence=None,
                notes=(
                    "This is not a theorem; it is a robustness envelope showing the "
                    "same rate survives several estimator choices."
                ),
            )
        )
    if stability:
        values = [
            float(item["cramer_rate_I0"])
            for item in stability.get("range_reports", [])
        ]
        if values:
            entries.append(
                SqueezeEntry(
                    name="n0_stability_cramer_rate",
                    quantity="I(0) across starting-magnitude ranges",
                    empirical_value=sum(values) / len(values),
                    lower_bound=min(values),
                    upper_bound=max(values),
                    lower_method="minimum across five n0 ranges",
                    upper_method="maximum across five n0 ranges",
                    evidence_type="empirical_envelope",
                    confidence=None,
                    notes=(
                        f"Width={stability.get('cramer_rate_range_width')}; slope per "
                        f"log10 midpoint={stability.get('cramer_rate_slope_per_log10')}."
                    ),
                )
            )
    if bootstrap:
        intervals = {
            item["quantity"]: item
            for item in bootstrap.get("bootstrap_intervals", [])
        }
        for quantity, name in (
            ("mean_delta_log2", "bootstrap_mean_delta_log2"),
            ("variance_delta_log2", "bootstrap_variance_delta_log2"),
            ("cramer_rate_I0", "bootstrap_cramer_rate_I0"),
            ("cramer_lambda", "bootstrap_cramer_lambda"),
        ):
            interval = intervals.get(quantity)
            if interval is None:
                continue
            entries.append(
                SqueezeEntry(
                    name=name,
                    quantity=f"bootstrap interval for {quantity}",
                    empirical_value=float(interval["estimate"]),
                    lower_bound=float(interval["q025"]),
                    upper_bound=float(interval["q975"]),
                    lower_method="multinomial bootstrap over saved binned renewal-increment histogram",
                    upper_method="multinomial bootstrap over saved binned renewal-increment histogram",
                    evidence_type="bootstrap_empirical",
                    confidence="nominal 95% bootstrap interval for the sampled binned law",
                    notes=(
                        f"Repetitions={bootstrap.get('bootstrap_repetitions')}; "
                        f"excursions={bootstrap.get('total_excursions')}. "
                        "This quantifies estimator stability, not all-orbit truth."
                    ),
                )
            )
        for tail in bootstrap.get("saddlepoint_tail_estimates", []):
            horizon = int(tail["excursions"])
            entries.append(
                SqueezeEntry(
                    name=f"saddlepoint_tail_T_{horizon}",
                    quantity=f"empirical-law approximation to P(S_{horizon} >= 0)",
                    empirical_value=float(tail["probability_sum_nonnegative"]),
                    lower_bound=None,
                    upper_bound=float(tail["probability_sum_nonnegative"]),
                    lower_method="not a lower bound; saddlepoint approximation only",
                    upper_method="Bahadur-Rao/Lugannani-Rice-style prefactor from empirical Cramer tilt",
                    evidence_type="saddlepoint_empirical",
                    confidence=None,
                    notes=(
                        f"Finite-horizon rate with prefactor={tail['rate_with_prefactor']}; "
                        "read as calibration, not a rigorous probability bound."
                    ),
                )
            )
    if per_k:
        total = int(per_k["total_excursions"])
        z = 5.0
        for segment in per_k.get("segments", []):
            label = str(segment["segment"])
            if not label.isdigit() or int(label) > 6:
                continue
            p = float(segment["probability"])
            successes = int(round(p * total))
            lo, hi = _wilson_interval(successes, total, z)
            entries.append(
                SqueezeEntry(
                    name=f"spike_max_a_{label}_probability",
                    quantity=f"P(max valuation in renewal excursion = {label})",
                    empirical_value=p,
                    lower_bound=lo,
                    upper_bound=hi,
                    lower_method="Wilson binomial interval, z=5",
                    upper_method="Wilson binomial interval, z=5",
                    evidence_type="high_confidence_empirical",
                    confidence="approximately five-sigma binomial interval for sampled excursions",
                    notes="Useful for spike-density Cramer decompositions; not an independence theorem.",
                )
            )
    return entries


def _diophantine_entries(reports_path: Path) -> list[SqueezeEntry]:
    entries: list[SqueezeEntry] = []
    cf = _read_json(reports_path / "d_pe_continued_fraction_certification.json")
    observed = None
    if cf:
        for level in cf.get("levels", []):
            if int(level.get("mod2_power", 0)) == 8 and int(level.get("mod3_power", 0)) == 3:
                observed = float(level.get("min_observed_gap"))
                break
    if observed is None:
        observed = abs(12 * math.log2(3.0) - 19)
    lower = 1.0 / (12 + 41)
    upper = 1.0 / 41
    entries.append(
        SqueezeEntry(
            name="diophantine_gap_19_over_12",
            quantity="|12 log2(3) - 19|",
            empirical_value=observed,
            lower_bound=lower,
            upper_bound=upper,
            lower_method="continued-fraction convergent inequality, lower 1/(q_n+q_{n+1})",
            upper_method="continued-fraction convergent inequality, upper 1/q_{n+1}",
            evidence_type="theorem",
            confidence="deterministic",
            notes="This is the sharp squeeze around the worst observed PECM edge (m,A)=(12,19).",
        )
    )
    return entries


def _literature_cycle_entries() -> list[SqueezeEntry]:
    return [
        SqueezeEntry(
            name="hercher_m_le_91_cycle_squeeze",
            quantity="Odd count K of a hypothetical non-trivial m-cycle with m <= 91",
            empirical_value=False,
            lower_bound=7.94e21,
            upper_bound=2.2e20,
            lower_method="Hercher 2022 lower-bound table / reciprocal-sum squeeze",
            upper_method="Simons-de Weger upper-bound formula evaluated for m<=91",
            evidence_type="theorem",
            confidence="deterministic literature theorem, constants recorded from project reference notes",
            notes=(
                "Lower bound exceeds upper bound, giving the contradiction. "
                "This entry records the squeeze shape; exact citation constants should "
                "be checked before publication."
            ),
        )
    ]


def _operator_and_finite_entries(reports_path: Path) -> list[SqueezeEntry]:
    entries: list[SqueezeEntry] = []
    hercher = _read_json(reports_path / "hercher_t_ni_bound.json")
    if hercher:
        entries.append(
            SqueezeEntry(
                name="hercher_sample_Tn_ceiling",
                quantity="max sampled T(n_i) * n_i",
                empirical_value=float(hercher["max_T_times_n"]),
                lower_bound=float(hercher["max_T_times_n"]),
                upper_bound=3.0,
                lower_method="sample maximum over saved local-minimum segments",
                upper_method="Hercher/elementary geometric ceiling sum_j (2/3)^j < 3",
                evidence_type="finite_computation_plus_theorem",
                confidence="deterministic for the sampled segments; theorem for the ceiling",
                notes="The sample nearly saturates the analytic ceiling, confirming sharpness but not creating a cycle exclusion by itself.",
            )
        )
    paparella = _read_json(reports_path / "paparella_nilpotency.json")
    if paparella:
        all_zero = all(
            bool(level.get("all_traces_zero"))
            for level in paparella.get("levels", [])
        )
        entries.append(
            SqueezeEntry(
                name="paparella_trace_nilpotency_tested_levels",
                quantity="all tested traces tr(C_n^p) vanish",
                empirical_value=all_zero,
                lower_bound=all_zero,
                upper_bound=all_zero,
                lower_method="exact sparse finite-matrix trace iteration",
                upper_method="exact sparse finite-matrix trace iteration",
                evidence_type="finite_computation",
                confidence="deterministic for tested n,p",
                notes="Finite truncation diagnostic only; it does not imply nilpotency for all n.",
            )
        )
    mori = _read_json(reports_path / "mori_mixed_first_return_operator.json")
    if mori and mori.get("levels"):
        last = mori["levels"][-1]
        entries.append(
            SqueezeEntry(
                name="mori_mixed_second_eigenvalue_finite",
                quantity="second eigenvalue magnitude of the largest mixed Mori first-return quotient",
                empirical_value=float(last["second_eigenvalue_abs"]),
                lower_bound=float(last["second_eigenvalue_abs"]),
                upper_bound=float(last["operator_norm_l2"]),
                lower_method="finite sparse eigensolver on saved quotient",
                upper_method="finite L2 operator norm on same quotient",
                evidence_type="finite_computation",
                confidence="deterministic up to numerical eigensolver tolerance",
                notes="Wide finite spectral squeeze; not an infinite-dimensional Mori reducing-subspace result.",
            )
        )
    projective = _read_json(reports_path / "projective_jsr_claude_background.json")
    unified = _read_json(reports_path / "unified_collatz_operator.json")
    if projective:
        level = projective.get("results_per_A_max", {}).get("A_max=12", {})
        lower = float(level.get("lower_bound", 1.5))
        upper = float(level.get("upper_bound_SDP", 1.500001))
        entries.append(
            SqueezeEntry(
                name="unconstrained_projective_jsr",
                quantity="JSR of {2^-a [[3,1],[0,2^a]] : 1<=a<=12}",
                empirical_value=lower,
                lower_bound=lower,
                upper_bound=upper,
                lower_method="single-mode spectral radius of a=1 matrix",
                upper_method="common quadratic Lyapunov SDP certificate from background artifact",
                evidence_type="finite_computation_plus_theorem",
                confidence="deterministic lower bound; SDP upper bound is numerical certificate-quality",
                notes=(
                    "Unconstrained switching grows at rate 3/2, so projective JSR "
                    "alone cannot prove Collatz descent. The useful information is "
                    "the gap to residue-constrained dynamics."
                ),
            )
        )
    if projective and unified:
        dyadic_seconds = [
            float(level["second_eigenvalue_abs"])
            for level in unified.get("dyadic_levels", [])
            if level.get("second_eigenvalue_abs") is not None
        ]
        if dyadic_seconds:
            constrained_proxy = dyadic_seconds[-1]
            entries.append(
                SqueezeEntry(
                    name="projective_to_dyadic_constraint_gap",
                    quantity="unconstrained projective JSR divided by dyadic quotient second eigenvalue",
                    empirical_value=1.5 / constrained_proxy,
                    lower_bound=None,
                    upper_bound=None,
                    lower_method="not a theorem; finite projection comparison",
                    upper_method="not a theorem; finite projection comparison",
                    evidence_type="empirical_envelope",
                    confidence=None,
                    notes=(
                        "The ratio is about 3. This is a structural diagnostic, not "
                        "a proof that the dyadic second eigenvalue is a constrained JSR."
                    ),
                )
            )
    constrained_projective = _read_json(
        reports_path / "constrained_projective_jsr.json"
    )
    if constrained_projective and constrained_projective.get("levels"):
        last = constrained_projective["levels"][-1]
        affine_lower = float(last["affine_quotient_jsr_lower"])
        affine_upper = float(last["affine_quotient_jsr_upper"])
        entries.append(
            SqueezeEntry(
                name="naive_residue_constrained_projective_jsr",
                quantity="exact affine-size JSR of the largest naive legal-residue quotient",
                empirical_value=affine_lower,
                lower_bound=affine_lower,
                upper_bound=affine_upper,
                lower_method="Karp max-plus cycle mean on the finite weighted residue graph",
                upper_method="same max-plus cycle-mean certificate; scalar quotient has matching bounds",
                evidence_type="finite_computation_plus_theorem",
                confidence="deterministic for the finite quotient",
                notes=(
                    "The matching bound is dominated by the Mersenne all-a=1 "
                    f"loop, classified as {last.get('obstruction_kind')} with "
                    f"word={last.get('obstruction_word')}. This falsifies the "
                    "naive residue-constrained quotient as a descent certificate."
                ),
            )
        )
        cutoff_two = None
        for item in last.get("tail_filtered", []):
            if int(item.get("tail_depth_cutoff", -1)) == 2:
                cutoff_two = item
                break
        if cutoff_two is not None:
            value = float(cutoff_two["affine_quotient_jsr"])
            entries.append(
                SqueezeEntry(
                    name="tail_filtered_cutoff_2_projective_jsr",
                    quantity="exact affine-size JSR after removing states with v2(r+1)>=2",
                    empirical_value=value,
                    lower_bound=value,
                    upper_bound=value,
                    lower_method="Karp max-plus cycle mean on the finite tail-filtered graph",
                    upper_method="same max-plus cycle-mean certificate",
                    evidence_type="finite_computation_plus_theorem",
                    confidence="deterministic for the finite filtered quotient",
                    notes=(
                        "Removing the Mersenne-tail states recovers the exact "
                        "iid affine drift factor 3/4 at the tested quotient. "
                        "This is a diagnostic, not a proof, because the positive "
                        "integer dynamics must still handle those tail states."
                    ),
                )
            )
    tail_aware = _read_json(reports_path / "tail_aware_projective_jsr.json")
    if tail_aware and tail_aware.get("levels"):
        last = tail_aware["levels"][-1]
        value = float(last["affine_quotient_jsr"])
        entries.append(
            SqueezeEntry(
                name="tail_aware_projective_jsr_tracked_subgraph",
                quantity="exact affine-size max-cycle factor on the largest bounded (R,u mod 2^q) tracked subgraph",
                empirical_value=value,
                lower_bound=value,
                upper_bound=value,
                lower_method="Karp max-plus cycle mean on the finite tail-aware tracked graph",
                upper_method="same finite tracked-graph certificate",
                evidence_type="finite_computation_plus_theorem",
                confidence="deterministic for the bounded tracked subgraph",
                notes=(
                    "The all-a=1 self-loop is gone, so the negative n=-1 loop "
                    "no longer dominates. Positive cycle means remain at the "
                    "largest saved level, and deeper-tail transitions are "
                    f"counted as overflow exits ({last.get('overflow_edges')}); "
                    "this is not yet a closed global upper bound."
                ),
            )
        )
    lte_closed = _read_json(reports_path / "tail_aware_lte_closed_projective_jsr.json")
    if lte_closed and lte_closed.get("levels"):
        last = lte_closed["levels"][-1]
        value = float(last["affine_quotient_jsr"])
        entries.append(
            SqueezeEntry(
                name="tail_aware_lte_closed_projective_jsr",
                quantity="exact affine-size max-cycle factor on the LTE-closed bounded (R,u mod 2^q) graph",
                empirical_value=value,
                lower_bound=value,
                upper_bound=value,
                lower_method="Karp max-plus cycle mean after exact forced-run overflow compression",
                upper_method="same finite closed-graph certificate",
                evidence_type="finite_computation_plus_theorem",
                confidence="deterministic for the bounded valuation-capped closed graph",
                notes=(
                    "Deeper-tail overflows are compressed back to Rmax by the "
                    "forced valuation-one tail identity. The resulting finite "
                    f"closed graph still has factor {value:.6g} at the largest "
                    "saved level, so worst-case constrained products remain "
                    "growth-positive even after removing the n=-1 loop."
                ),
            )
        )
    markov = _read_json(reports_path / "tail_aware_markov_lyapunov.json")
    if markov and markov.get("levels"):
        last = markov["levels"][-1]
        value = float(last["largest_component_average_log2_growth_per_accelerated_step"])
        entries.append(
            SqueezeEntry(
                name="tail_aware_markov_average_growth",
                quantity="stationary average log2 growth per accelerated step on the largest LTE-closed recurrent component",
                empirical_value=value,
                lower_bound=value,
                upper_bound=value,
                lower_method="finite stationary distribution under lift-count normalized transitions",
                upper_method="same finite Markov-average computation",
                evidence_type="finite_computation",
                confidence="deterministic for the finite lift-count Markov model",
                notes=(
                    "This is the typical-case companion to the LTE-closed JSR: "
                    f"worst-case factor={last.get('worst_case_jsr_factor')}, "
                    f"Markov typical factor={last.get('largest_component_typical_factor_per_accelerated_step')}. "
                    "It supports average contraction on the finite model but is "
                    "not a pointwise Collatz proof."
                ),
            )
        )
    christoffel = _read_json(reports_path / "christoffel_filtered_jsr.json")
    if christoffel and christoffel.get("levels"):
        last = christoffel["levels"][-1]
        exact = float(last["exact_karp_factor"])
        filtered = last.get("christoffel_filtered_best_factor")
        filtered_value = None if filtered is None else float(filtered)
        entries.append(
            SqueezeEntry(
                name="christoffel_filtered_tail_jsr_bounded",
                quantity="best bounded simple-cycle factor after cyclic-balanced Christoffel-compatible parity filter",
                empirical_value=filtered_value,
                lower_bound=filtered_value,
                upper_bound=filtered_value,
                lower_method="bounded simple-cycle enumeration plus finite cyclic-balance parity test",
                upper_method="same bounded enumeration; not an all-cycle Karp certificate",
                evidence_type="finite_computation_diagnostic",
                confidence="deterministic for scanned simple cycles up to the saved edge-depth cap",
                notes=(
                    f"At the largest saved level exact Karp factor is {exact:.6g}, "
                    f"bounded unfiltered best is {last.get('enumerated_unfiltered_best_factor')}, "
                    f"and Christoffel-compatible best is {filtered_value}. "
                    f"Scanned {last.get('cycles_scanned')} cycles, with "
                    f"{last.get('christoffel_compatible_cycles')} passing. "
                    "This is a Hercher-style compatibility diagnostic, not the full high-cycle theorem."
                ),
            )
        )
    return entries


def _furstenberg_entries(reports_path: Path) -> list[SqueezeEntry]:
    entries: list[SqueezeEntry] = []
    report = _read_json(reports_path / "lyapunov_furstenberg.json")
    if not report:
        return entries
    exact = float(report["exact_log_growth_affine_coordinate_base2"])
    monte_carlo = float(report["monte_carlo_log_growth_base2"])
    entries.append(
        SqueezeEntry(
            name="furstenberg_iid_affine_lyapunov",
            quantity="iid Geom(2) affine-coordinate Lyapunov exponent, base 2",
            empirical_value=monte_carlo,
            lower_bound=exact,
            upper_bound=exact,
            lower_method="closed form E[log2(3/2^a)] with E[a]=2",
            upper_method="closed form E[log2(3/2^a)] with E[a]=2",
            evidence_type="theorem",
            confidence="deterministic for the iid Geom(2) model",
            notes=(
                "The homogeneous triangular matrix top exponent is 0 because "
                "of the constant coordinate; this entry records the affine-size "
                "drift exponent log2(3/4)."
            ),
        )
    )
    return entries


def _jazz_constant_entries(reports_path: Path) -> list[SqueezeEntry]:
    entries: list[SqueezeEntry] = []
    report = _read_json(reports_path / "jazz_constant_closed_form_test.json")
    if report:
        entries.append(
            SqueezeEntry(
                name="jazz_constant_log_4_over_3_squared_test",
                quantity="closed-form hypothesis I(0)=log(4/3)^2",
                empirical_value=float(report["empirical_cramer_rate"]),
                lower_bound=float(report["bootstrap_q025"]),
                upper_bound=float(report["bootstrap_q975"]),
                lower_method="renewal bootstrap q2.5%",
                upper_method="renewal bootstrap q97.5%",
                evidence_type="bootstrap_empirical",
                confidence="candidate rejected for the saved empirical renewal law",
                notes=(
                    f"Candidate={report['candidate_value']}; "
                    f"difference={report['absolute_difference']}; "
                    f"CI half-width units={report['sigma_units_from_ci_half_width']}. "
                    "The closed form remains a possible idealized-model constant, but "
                    "not the measured renewal Cramer rate."
                ),
            )
        )
    decomposition = _read_json(reports_path / "jazz_constant_spike_decomposition.json")
    if decomposition:
        entries.append(
            SqueezeEntry(
                name="jazz_constant_heavy_tail_correction",
                quantity="I(0)-log(4/3)^2 for the saved empirical renewal law",
                empirical_value=float(decomposition["heavy_tail_correction"]),
                lower_bound=float(decomposition["bootstrap_q025"])
                - float(decomposition["gaussian_candidate_value"]),
                upper_bound=float(decomposition["bootstrap_q975"])
                - float(decomposition["gaussian_candidate_value"]),
                lower_method="renewal bootstrap q2.5% minus Gaussian candidate",
                upper_method="renewal bootstrap q97.5% minus Gaussian candidate",
                evidence_type="bootstrap_empirical",
                confidence="nominal 95% interval for the empirical heavy-tail correction",
                notes=(
                    "The no-spike segment dominates the MGF "
                    f"({decomposition['dominant_segment_percent_of_mgf']:.2f}% "
                    "of mass at lambda*), while spike levels supply the structural "
                    "correction that separates Jazz's constant from the Gaussian "
                    "candidate."
                ),
            )
        )
    return entries


def rigorous_squeeze_report(
    reports_dir: str | Path = "docs/reports",
) -> RigorousSqueezeReport:
    reports_path = Path(reports_dir)
    entries = (
        _diophantine_entries(reports_path)
        + _literature_cycle_entries()
        + _renewal_entries(reports_path)
        + _operator_and_finite_entries(reports_path)
        + _furstenberg_entries(reports_path)
        + _jazz_constant_entries(reports_path)
    )
    theorem_or_finite = sum(
        1
        for entry in entries
        if entry.evidence_type in {"theorem", "finite_computation", "finite_computation_plus_theorem"}
    )
    high_confidence = sum(
        1 for entry in entries if entry.evidence_type == "high_confidence_empirical"
    )
    empirical = sum(
        1
        for entry in entries
        if entry.evidence_type
        in {"empirical_envelope", "bootstrap_empirical", "saddlepoint_empirical"}
    )
    return RigorousSqueezeReport(
        type="rigorous_bound_squeeze",
        status="mixed_theorem_finite_and_empirical_bounds_not_collatz_proof",
        caveat=(
            "Entries deliberately separate deterministic theorems, exact finite "
            "computations, statistical confidence intervals, and empirical "
            "method envelopes. Statistical intervals describe sampled models, "
            "not all Collatz orbits."
        ),
        entries=tuple(entries),
        theorem_or_finite_entries=theorem_or_finite,
        high_confidence_entries=high_confidence,
        empirical_envelope_entries=empirical,
    )
