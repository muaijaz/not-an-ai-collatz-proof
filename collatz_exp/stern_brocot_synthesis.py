"""Stern-Brocot megasynthesis diagnostics across Collatz reductions."""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from statistics import median
from typing import Any

from sympy import factorint

from .cf_convergent_slope import (
    _collect_cycles,
    _intermediate_fractions,
    continued_fraction_convergents_log2_3,
)
from .chang_phantom_gain import chang_R_K_entry
from .qnp1_phase_transition import continued_fraction_convergents_log2
from .rozier_abc_audit import mu_from_factorization


DEFAULT_Q_VALUES = (3, 5, 7, 9)
DEFAULT_SLOPE_ARTIFACT_PATHS = (
    "docs/reports/karp_slope_joint_sweep.json",
    "docs/reports/karp_slope_joint_sweep_extended.json",
    "docs/reports/tail_cycle_realizability.json",
    "docs/reports/tail_cycle_realizability_extended.json",
    "docs/reports/tail_cycle_realizability_extended_deep.json",
)

MEGASYNTHESIS_CAVEAT = (
    "This is a finite empirical synthesis attempt across multiple recent "
    "Collatz frameworks. The unification claim is a structural hypothesis, "
    "not a theorem."
)


@dataclass(frozen=True)
class SternBrocotMegasynthesisReport:
    type: str
    status: str
    caveat: str
    cf_convergents_log_2_3: tuple[dict[str, Any], ...]
    cf_convergents_log_2_5: tuple[dict[str, Any], ...]
    cf_convergents_log_2_7: tuple[dict[str, Any], ...]
    cf_convergents_log_2_9: tuple[dict[str, Any], ...]
    stern_brocot_alignment_table: tuple[dict[str, Any], ...]
    tao_tier_test_results: dict[str, Any]
    six_reduction_table: dict[str, Any]
    verdict: dict[str, Any]
    scan_policy: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "cf_convergents_log_2_3": list(self.cf_convergents_log_2_3),
            "cf_convergents_log_2_5": list(self.cf_convergents_log_2_5),
            "cf_convergents_log_2_7": list(self.cf_convergents_log_2_7),
            "cf_convergents_log_2_9": list(self.cf_convergents_log_2_9),
            "stern_brocot_alignment_table": list(self.stern_brocot_alignment_table),
            "tao_tier_test_results": self.tao_tier_test_results,
            "six_reduction_table": self.six_reduction_table,
            "verdict": self.verdict,
            "scan_policy": self.scan_policy,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json() + "\n")


def _fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _normalize_cf_rows(
    q: int,
    rows: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    target = math.log2(q)
    normalized: list[dict[str, Any]] = []
    for row in rows:
        numerator = int(row.get("p", row.get("numerator")))
        denominator = int(row.get("q", row.get("denominator")))
        frac = Fraction(numerator, denominator)
        residual = float(frac) - target
        normalized.append(
            {
                "index": int(row["index"]),
                "partial_quotient": int(row["partial_quotient"]),
                "p": numerator,
                "q": denominator,
                "fraction": _fraction_text(frac),
                "residual": residual,
                "side": "above" if residual > 0 else "below" if residual < 0 else "exact",
            }
        )
    return tuple(normalized)


def cf_convergents_log2(q: int, depth: int = 20) -> tuple[dict[str, Any], ...]:
    """Return normalized continued-fraction convergents of ``log2(q)``."""

    if q == 3:
        return _normalize_cf_rows(q, continued_fraction_convergents_log2_3(depth))
    return _normalize_cf_rows(q, continued_fraction_convergents_log2(q, depth))


def chang_oscillation_window(
    K: int,
    radius: int = 2,
    *,
    max_K: int = 80,
) -> dict[str, Any]:
    """Compute a local Chang ``R(K)`` oscillation proxy around ``K``."""

    if K < 3:
        return {
            "K": K,
            "theta_proxy": None,
            "neighbor_values": [],
            "local_maximum_at_K": None,
            "status": "K_below_chang_R_K_domain",
        }
    if K > max_K:
        return {
            "K": K,
            "theta_proxy": None,
            "neighbor_values": [],
            "local_maximum_at_K": None,
            "status": "skipped_above_finite_chang_K_cap",
            "max_K": max_K,
            "note": (
                "Chang R(K) uses primitive-necklace sums that become expensive "
                "at large K; the megasynthesis records high convergents but "
                "bounds this local oscillation proxy."
            ),
        }
    values: list[dict[str, Any]] = []
    for item in range(max(3, K - radius), K + radius + 1):
        entry = chang_R_K_entry(item)
        theta = abs(float(entry["R_K"]))
        values.append({"K": item, "R_K": float(entry["R_K"]), "theta_proxy": theta})
    center = next(item for item in values if item["K"] == K)
    local_max = all(center["theta_proxy"] >= item["theta_proxy"] for item in values)
    return {
        "K": K,
        "theta_proxy": center["theta_proxy"],
        "neighbor_values": values,
        "local_maximum_at_K": local_max,
        "status": "computed_abs_chang_R_K_proxy",
        "note": (
            "Theta_K is represented by |R(K)| from the local Chang phantom-gain "
            "module; this is a finite proxy for local oscillation, not a "
            "claim about Chang's full asymptotic difficulty profile."
        ),
    }


def _cycle_slope_matches(
    slope: Fraction,
    artifact_paths: tuple[str, ...],
) -> tuple[dict[str, Any], ...]:
    matches: list[dict[str, Any]] = []
    for cycle in _collect_cycles(artifact_paths):
        if Fraction(int(cycle["slope_A"]), int(cycle["slope_m"])) != slope:
            continue
        matches.append(
            {
                "level": list(cycle["level"]),
                "valuation_word": list(cycle["valuation_word"]),
                "classification": cycle["classification"],
                "edge_factor": cycle["edge_factor"],
                "edge_mean_log2_slope": cycle["edge_mean_log2_slope"],
                "slope_A_over_m": cycle["slope_A_over_m"],
                "slope_filter_survivor": cycle["slope_filter_survivor"],
                "source_files": list(cycle["source_files"]),
            }
        )
    return tuple(matches)


def _cycle_slope_match_map(
    artifact_paths: tuple[str, ...],
) -> dict[Fraction, tuple[dict[str, Any], ...]]:
    grouped: dict[Fraction, list[dict[str, Any]]] = {}
    for cycle in _collect_cycles(artifact_paths):
        slope = Fraction(int(cycle["slope_A"]), int(cycle["slope_m"]))
        grouped.setdefault(slope, []).append(
            {
                "level": list(cycle["level"]),
                "valuation_word": list(cycle["valuation_word"]),
                "classification": cycle["classification"],
                "edge_factor": cycle["edge_factor"],
                "edge_mean_log2_slope": cycle["edge_mean_log2_slope"],
                "slope_A_over_m": cycle["slope_A_over_m"],
                "slope_filter_survivor": cycle["slope_filter_survivor"],
                "source_files": list(cycle["source_files"]),
            }
        )
    return {slope: tuple(rows) for slope, rows in grouped.items()}


def _best_rozier_candidate_for_denominator(
    denominator: int,
    *,
    n_max: int = 500,
    k_max: int = 20,
) -> dict[str, Any]:
    """Search small ``n`` whose ``n^2+1`` factorization has Rozier-style shape."""

    if denominator < 1:
        raise ValueError("denominator must be positive")
    best: dict[str, Any] | None = None
    for n in range(3, n_max + 1, 2):
        factors = factorint(n * n + 1)
        mu_value = mu_from_factorization(factors)
        low_mu_score = math.log(n * n + 1) - mu_value
        prime, exponent = max(factors.items(), key=lambda item: (item[1], item[0]))
        predicted_gains = [
            math.log(2 * (prime**3) / n) - math.log(k + 4)
            for k in range(2, k_max + 1)
        ]
        best_gain = max(predicted_gains)
        alignment_score = min(
            abs(denominator - prime),
            denominator % prime if prime else denominator,
            prime % denominator if denominator else prime,
        )
        aligned = (
            denominator == prime
            or denominator == exponent
            or prime % denominator == 0
            or denominator % prime == 0
        )
        score = (int(aligned), best_gain, low_mu_score, -alignment_score)
        if best is None or score > best["_score"]:
            best = {
                "_score": score,
                "n": n,
                "n_squared_plus_1_factors": {
                    str(base): int(power)
                    for base, power in sorted(factors.items())
                },
                "mu_n_squared_plus_1": mu_value,
                "low_mu_score_log_minus_mu": low_mu_score,
                "dominant_prime_power_base": int(prime),
                "dominant_prime_power_exponent": int(exponent),
                "best_predicted_gain_k_2_to_20": best_gain,
                "aligned_to_convergent_denominator": aligned,
                "alignment_rule": (
                    "denominator equals/divides/is-divided-by dominant prime "
                    "or equals its exponent"
                ),
                "denominator_distance_proxy": alignment_score,
            }
    assert best is not None
    best.pop("_score", None)
    if denominator in (12, 13, 41, 53):
        # Keep Rozier's documented n=239 family visible near the first large
        # denominators even when it is not the best small-n score.
        factors_239 = factorint(239 * 239 + 1)
        best["rozier_239_reference"] = {
            "n": 239,
            "n_squared_plus_1_factors": {
                str(base): int(power) for base, power in sorted(factors_239.items())
            },
            "dominant_prime_power_base": 13,
            "alignment_to_denominator": (
                denominator == 13
                or denominator % 13 == 0
                or 13 % denominator == 0
            ),
            "note": (
                "Rozier's n=239 family is retained as a reference family; "
                "the denominator relation is recorded without claiming a theorem."
            ),
        }
    return best


def stern_brocot_alignment_table(
    *,
    cf_depth: int = 20,
    artifact_paths: tuple[str, ...] = DEFAULT_SLOPE_ARTIFACT_PATHS,
    rozier_n_max: int = 500,
    chang_max_K: int = 80,
) -> tuple[dict[str, Any], ...]:
    """Join Chang, slope-realizability, and Rozier diagnostics by convergent."""

    rows: list[dict[str, Any]] = []
    slope_match_map = _cycle_slope_match_map(artifact_paths)
    for convergent in cf_convergents_log2(3, cf_depth):
        slope = Fraction(convergent["p"], convergent["q"])
        K = convergent["p"]
        chang = chang_oscillation_window(K, max_K=chang_max_K)
        slope_matches = slope_match_map.get(slope, ())
        rozier = _best_rozier_candidate_for_denominator(
            convergent["q"],
            n_max=rozier_n_max,
        )
        triple_alignment = bool(
            chang["local_maximum_at_K"]
            and slope_matches
            and rozier["aligned_to_convergent_denominator"]
            and rozier["best_predicted_gain_k_2_to_20"] > 0
        )
        rows.append(
            {
                "convergent_index": convergent["index"],
                "p": convergent["p"],
                "q": convergent["q"],
                "fraction": convergent["fraction"],
                "side": convergent["side"],
                "residual": convergent["residual"],
                "chang_link": chang,
                "slope_realizability_matches": list(slope_matches),
                "rozier_link": rozier,
                "triple_alignment_detected": triple_alignment,
            }
        )
    return tuple(rows)


def tao_discrepancy(a: int, m: int, *, max_admissible: int = 500_000) -> dict[str, Any]:
    """Compute Tao-style finite congruence discrepancy for one ``a/m`` tier."""

    if a < 1 or m < 1:
        raise ValueError("a and m must be positive")
    if a < m:
        return {
            "a": a,
            "m": m,
            "fraction": f"{a}/{m}",
            "status": "skipped_no_admissible_sigma",
            "admissible_count": 0,
            "hit_count": 0,
            "discrepancy": None,
        }
    admissible_count = math.comb(a - 1, m - 1)
    if admissible_count > max_admissible:
        return {
            "a": a,
            "m": m,
            "fraction": f"{a}/{m}",
            "status": "skipped_admissible_count_cap",
            "admissible_count": admissible_count,
            "hit_count": None,
            "discrepancy": None,
            "max_admissible": max_admissible,
        }
    modulus = abs((1 << a) - 3**m)
    if modulus <= 1:
        return {
            "a": a,
            "m": m,
            "fraction": f"{a}/{m}",
            "status": "skipped_degenerate_modulus",
            "admissible_count": admissible_count,
            "hit_count": None,
            "discrepancy": None,
            "modulus": modulus,
        }
    hit_count = 0
    for tail in combinations(range(1, a), m - 1):
        sigmas = (0, *tail)
        total = 0
        for i, sigma in enumerate(sigmas):
            total += (3 ** (m - 1 - i)) * (1 << sigma)
        if total % modulus == 0:
            hit_count += 1
    return {
        "a": a,
        "m": m,
        "fraction": f"{a}/{m}",
        "status": "computed_exact",
        "admissible_count": admissible_count,
        "hit_count": hit_count,
        "discrepancy": hit_count / admissible_count if admissible_count else None,
        "modulus": modulus,
    }


def _dedupe_pairs(pairs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    rows: list[tuple[int, int]] = []
    for pair in pairs:
        if pair in seen:
            continue
        seen.add(pair)
        rows.append(pair)
    return rows


def _tier_pairs(
    *,
    max_m: int,
    random_count: int,
    random_seed: int,
    max_a: int,
    max_admissible: int,
) -> dict[str, list[tuple[int, int]]]:
    convergents = continued_fraction_convergents_log2_3(20)
    cf_pairs = [
        (int(item["p"]), int(item["q"]))
        for item in convergents
        if 2 <= int(item["q"]) <= max_m and int(item["p"]) <= max_a
    ]
    intermediate_pairs = [
        (int(item["p"]), int(item["q"]))
        for item in _intermediate_fractions(convergents)
        if 2 <= int(item["q"]) <= max_m and int(item["p"]) <= max_a
    ]
    rng = random.Random(random_seed)
    random_pairs: list[tuple[int, int]] = []
    attempts = 0
    while len(random_pairs) < random_count and attempts < random_count * 200:
        attempts += 1
        m = rng.randint(2, max_m)
        a = rng.randint(m, max_a)
        pair = (a, m)
        if (
            pair in cf_pairs
            or pair in intermediate_pairs
            or math.comb(a - 1, m - 1) > max_admissible
        ):
            continue
        random_pairs.append(pair)
    return {
        "cf_convergent": _dedupe_pairs(cf_pairs),
        "intermediate_fraction": _dedupe_pairs(intermediate_pairs),
        "random_rational": _dedupe_pairs(random_pairs),
    }


def _bootstrap_order_p_value(
    cf_values: list[float],
    intermediate_values: list[float],
    random_values: list[float],
    *,
    samples: int,
    seed: int,
) -> float | None:
    if not cf_values or not intermediate_values or not random_values:
        return None
    rng = random.Random(seed)
    failures = 0
    for _ in range(samples):
        cf_sample = [rng.choice(cf_values) for _ in cf_values]
        intermediate_sample = [
            rng.choice(intermediate_values) for _ in intermediate_values
        ]
        random_sample = [rng.choice(random_values) for _ in random_values]
        if not (
            median(cf_sample)
            < median(intermediate_sample)
            < median(random_sample)
        ):
            failures += 1
    return failures / samples if samples > 0 else None


def _bootstrap_median_interval(
    values: list[float],
    *,
    samples: int,
    seed: int,
) -> dict[str, float | None]:
    if not values:
        return {"q025": None, "q500": None, "q975": None}
    if samples <= 0:
        value = median(values)
        return {"q025": value, "q500": value, "q975": value}
    rng = random.Random(seed)
    boot: list[float] = []
    for _ in range(samples):
        boot.append(median([rng.choice(values) for _ in values]))
    boot.sort()

    def quantile(probability: float) -> float:
        index = min(len(boot) - 1, max(0, round(probability * (len(boot) - 1))))
        return boot[index]

    return {
        "q025": quantile(0.025),
        "q500": quantile(0.5),
        "q975": quantile(0.975),
    }


def tao_tier_test(
    *,
    max_m: int = 20,
    random_count: int = 100,
    random_seed: int = 8675309,
    max_a: int = 50,
    max_admissible: int = 500_000,
    bootstrap_samples: int = 1000,
) -> dict[str, Any]:
    """Run the finite Littlewood-Offord tier discrepancy test."""

    pair_sets = _tier_pairs(
        max_m=max_m,
        random_count=random_count,
        random_seed=random_seed,
        max_a=max_a,
        max_admissible=max_admissible,
    )
    tiers: dict[str, Any] = {}
    medians: dict[str, float | None] = {}
    computed_values: dict[str, list[float]] = {}
    for tier, pairs in pair_sets.items():
        rows = [
            tao_discrepancy(a, m, max_admissible=max_admissible)
            for a, m in pairs
        ]
        values = [
            float(row["discrepancy"])
            for row in rows
            if row["status"] == "computed_exact" and row["discrepancy"] is not None
        ]
        computed_values[tier] = values
        medians[tier] = median(values) if values else None
        tiers[tier] = {
            "candidate_count": len(pairs),
            "computed_count": len(values),
            "skipped_count": len(rows) - len(values),
            "median_discrepancy": medians[tier],
            "median_discrepancy_bootstrap_ci": _bootstrap_median_interval(
                values,
                samples=bootstrap_samples,
                seed=random_seed + len(tiers) + 10,
            ),
            "rows": rows,
        }
    ordered = (
        medians["cf_convergent"] is not None
        and medians["intermediate_fraction"] is not None
        and medians["random_rational"] is not None
        and medians["cf_convergent"]
        < medians["intermediate_fraction"]
        < medians["random_rational"]
    )
    p_value = _bootstrap_order_p_value(
        computed_values["cf_convergent"],
        computed_values["intermediate_fraction"],
        computed_values["random_rational"],
        samples=bootstrap_samples,
        seed=random_seed + 1,
    )
    return {
        "tiers": tiers,
        "median_order_cf_lt_intermediate_lt_random": ordered,
        "bootstrap_one_sided_p_value": p_value,
        "tao_tier_hypothesis_supported": (
            bool(ordered) and p_value is not None and p_value < 0.05
        ),
        "method_note": (
            "The discrepancy is exact for candidate pairs below the admissible "
            "combination cap. Degenerate moduli and pairs above the cap are "
            "recorded as skipped to keep the finite audit bounded."
        ),
    }


def six_reduction_cross_tabulation() -> dict[str, Any]:
    """Return the structural six-reduction table requested by the audit."""

    reductions = {
        "Tao_2019": {
            "state_space": "log_density_measure_on_N",
            "condition": "Syrac_distribution_decay",
            "our_evidence": [
                "docs/reports/tao_syrac_empirical.json",
                "docs/reports/tao_characteristic_function_decay.json",
            ],
            "core_2_adic_3_adic_parameter": (
                "decay of characteristic functions for affine 3x+1/2^a "
                "increments, indexed by 2-adic residue frequencies"
            ),
            "stern_brocot_cross_reference": (
                "convergents of log2(3) identify near-resonant a/m windows "
                "where anti-concentration is hardest"
            ),
        },
        "Chang_2603_25753": {
            "state_space": "burst_ending_subsequence",
            "condition": "bit_4_balance_delta_lt_delta_max",
            "our_evidence": ["docs/reports/chang_bit4_balance_audit.json"],
            "core_2_adic_3_adic_parameter": (
                "phantom-gain run length K and primitive-necklace weights "
                "for powers of 2 competing with powers of 3"
            ),
            "stern_brocot_cross_reference": (
                "local R(K) oscillation is tested at numerator K=p of "
                "log2(3) convergents"
            ),
        },
        "Mori_2411_08084": {
            "state_space": "C_star_T_1_T_2",
            "condition": "no_nontrivial_reducing_subspace",
            "our_evidence": ["docs/reports/unified_collatz_operator.json"],
            "core_2_adic_3_adic_parameter": (
                "mixed 2/3-adic operator orbits and reducing subspace tests"
            ),
            "stern_brocot_cross_reference": (
                "near-resonant 2^a versus 3^m scales are the finite "
                "projection levels where operator mixing is most delicate"
            ),
        },
        "Santana_2601_03297": {
            "state_space": "custom_topology_continuous_potentials",
            "condition": "unique_equilibrium_state",
            "our_evidence": [],
            "core_2_adic_3_adic_parameter": (
                "thermodynamic weights for Collatz-compatible potentials"
            ),
            "stern_brocot_cross_reference": (
                "candidate pressure plateaus should be compared against "
                "Stern-Brocot approximation tiers; no framework artifact yet"
            ),
        },
        "Siegel_2412_02902": {
            "state_space": "chi_H_image_in_Q_intersect_Z_p",
            "condition": "dense_Fourier_translate_span",
            "our_evidence": ["docs/reports/tao_siegel_chi_h_correspondence.md"],
            "core_2_adic_3_adic_parameter": (
                "Fourier translate span for p-adic images of Collatz coding"
            ),
            "stern_brocot_cross_reference": (
                "Tao characteristic decay is the visible 2-adic shadow of "
                "Siegel's Fourier-span condition"
            ),
        },
        "this_framework": {
            "state_space": "residue_Markov_quotient_mod_2_k",
            "condition": "m_step_Foster_drift_uniform_negative",
            "our_evidence": ["docs/reports/m_step_foster_drift_k8.json"],
            "core_2_adic_3_adic_parameter": (
                "valuation-word slope A/m and realizability in finite "
                "LTE-closed tail quotients"
            ),
            "stern_brocot_cross_reference": (
                "CF convergents match realizable slope survivors, while "
                "intermediate and non-convergent fractions produce boundary "
                "and high-growth ghosts in the tested scan"
            ),
        },
    }
    has_evidence_for_all = all(row["our_evidence"] for row in reductions.values())
    return {
        "reductions": reductions,
        "common_structural_parameter": (
            "near-resonance between 2-adic valuation sums A and 3-adic "
            "multiplication length m, organized by Stern-Brocot approximation "
            "tiers of log2(3)"
        ),
        "six_reduction_unification_meta_claim": False,
        "meta_claim_reason": (
            "The table surfaces a shared candidate parameter, but Santana has "
            "no local artifact yet and the cross-paper identification remains "
            "a structural hypothesis rather than a verified theorem."
        )
        if not has_evidence_for_all
        else (
            "All six entries have local evidence, but equality of the limiting "
            "characteristic measures is still not proved."
        ),
    }


def stern_brocot_megasynthesis_report(
    *,
    q_values: tuple[int, ...] = DEFAULT_Q_VALUES,
    cf_depth: int = 20,
    tao_max_m: int = 20,
    tao_random_count: int = 100,
    tao_bootstrap_samples: int = 1000,
    tao_max_admissible: int = 500_000,
    rozier_n_max: int = 500,
    chang_max_K: int = 80,
    artifact_paths: tuple[str, ...] = DEFAULT_SLOPE_ARTIFACT_PATHS,
) -> SternBrocotMegasynthesisReport:
    """Build the combined finite Stern-Brocot megasynthesis artifact."""

    cf_by_q = {
        q: cf_convergents_log2(q, cf_depth)
        for q in q_values
    }
    alignment = stern_brocot_alignment_table(
        cf_depth=cf_depth,
        artifact_paths=artifact_paths,
        rozier_n_max=rozier_n_max,
        chang_max_K=chang_max_K,
    )
    tao = tao_tier_test(
        max_m=tao_max_m,
        random_count=tao_random_count,
        max_admissible=tao_max_admissible,
        bootstrap_samples=tao_bootstrap_samples,
    )
    six_table = six_reduction_cross_tabulation()
    triple_alignment_count = sum(
        int(row["triple_alignment_detected"]) for row in alignment
    )
    stern_supported = triple_alignment_count >= 3
    verdict = {
        "stern_brocot_alignment_supported": stern_supported,
        "stern_brocot_alignment_distinct_convergents": triple_alignment_count,
        "tao_tier_hypothesis_supported": tao["tao_tier_hypothesis_supported"],
        "six_reduction_unification_meta_claim": six_table[
            "six_reduction_unification_meta_claim"
        ],
        "overall": (
            "strong_empirical_megasynthesis_supported"
            if stern_supported
            and tao["tao_tier_hypothesis_supported"]
            and six_table["six_reduction_unification_meta_claim"]
            else "partial_or_negative_empirical_megasynthesis"
        ),
        "interpretation": (
            "The finite synthesis preserves the Stern-Brocot tier hierarchy as "
            "a candidate organizing skeleton, while separating computed "
            "alignment from structural cross-paper hypotheses."
        ),
    }
    return SternBrocotMegasynthesisReport(
        type="stern_brocot_megasynthesis",
        status="finite_empirical_synthesis_complete",
        caveat=MEGASYNTHESIS_CAVEAT,
        cf_convergents_log_2_3=cf_by_q.get(3, ()),
        cf_convergents_log_2_5=cf_by_q.get(5, ()),
        cf_convergents_log_2_7=cf_by_q.get(7, ()),
        cf_convergents_log_2_9=cf_by_q.get(9, ()),
        stern_brocot_alignment_table=alignment,
        tao_tier_test_results=tao,
        six_reduction_table=six_table,
        verdict=verdict,
        scan_policy={
            "q_values": list(q_values),
            "cf_depth": cf_depth,
            "tao_max_m": tao_max_m,
            "tao_random_count": tao_random_count,
            "tao_bootstrap_samples": tao_bootstrap_samples,
            "tao_max_admissible": tao_max_admissible,
            "rozier_n_max": rozier_n_max,
            "chang_max_K": chang_max_K,
            "slope_artifact_paths": list(artifact_paths),
            "publication_grade_caveat": MEGASYNTHESIS_CAVEAT,
        },
    )


def megasynthesis_executive_summary(report: SternBrocotMegasynthesisReport) -> str:
    """Render a short human-readable summary for the JSON artifact."""

    verdict = report.verdict
    tao = report.tao_tier_test_results
    medians = {
        tier: data["median_discrepancy"]
        for tier, data in tao["tiers"].items()
    }
    triple_rows = [
        row for row in report.stern_brocot_alignment_table
        if row["triple_alignment_detected"]
    ]
    slope_rows = [
        row for row in report.stern_brocot_alignment_table
        if row["slope_realizability_matches"]
    ]
    return "\n".join(
        [
            "# Stern-Brocot Megasynthesis Executive Summary",
            "",
            "This artifact tests whether the Stern-Brocot tier hierarchy of "
            "`log2(3)` may be a universal skeleton organizing several recent "
            "Collatz reductions. It is a finite empirical synthesis, not a "
            "proof claim.",
            "",
            "## What Was Computed",
            "",
            "- Continued-fraction convergents of `log2(q)` for `q = 3, 5, 7, 9` "
            "to the configured depth.",
            "- A per-convergent alignment table joining Chang-style `R(K)` "
            "oscillation proxies, this framework's exact slope-realizability "
            "survivors, and small Rozier-style low-`mu` searches.",
            "- A bounded Tao Littlewood-Offord congruence discrepancy test on "
            "CF convergents, Stern-Brocot intermediate fractions, and random "
            "rationals.",
            "- A structural six-reduction cross-tabulation for Tao, Chang, "
            "Mori, Santana, Siegel, and this framework.",
            "",
            "## Verdict",
            "",
            f"- Stern-Brocot triple alignment supported: "
            f"{verdict['stern_brocot_alignment_supported']} "
            f"({verdict['stern_brocot_alignment_distinct_convergents']} "
            "distinct convergents met the strict triple criterion).",
            f"- Tao tier hypothesis supported: "
            f"{verdict['tao_tier_hypothesis_supported']} "
            f"(median discrepancies: {medians}).",
            f"- Six-reduction unification meta-claim: "
            f"{verdict['six_reduction_unification_meta_claim']}.",
            f"- Overall finite-audit result: `{verdict['overall']}`.",
            "",
            "## Structural Reading",
            "",
            "The slope-realizability side remains the cleanest signal: exact "
            "`A/m` slopes at CF convergents recover the known realizable "
            "survivors in the saved artifacts, while intermediate and "
            "non-convergent rationals mark boundary or high-growth ghost "
            "cycles. The Chang and Rozier columns expose plausible arithmetic "
            "interfaces to the same near-resonance problem, but the strict "
            "three-way alignment criterion is intentionally conservative.",
            "",
            f"The alignment table found {len(slope_rows)} convergent rows with "
            "at least one exact slope-realizability match and "
            f"{len(triple_rows)} rows satisfying the stricter Chang+slope+Rozier "
            "criterion. This should be read as evidence about the tested "
            "finite artifacts only.",
            "",
            "## Caveat",
            "",
            report.caveat,
        ]
    )


def save_megasynthesis_executive_summary(
    report: SternBrocotMegasynthesisReport,
    path: str | Path,
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(megasynthesis_executive_summary(report) + "\n")
