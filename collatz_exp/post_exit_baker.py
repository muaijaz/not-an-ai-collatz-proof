"""Diophantine diagnostics for PECM post-exit debt gaps."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from collections import Counter
from typing import Any

from .cycles_eliahou import log2_3_convergents
from .post_exit_map import _iter_post_exit_states, _sample_u_values, post_exit_transition_sample


@dataclass(frozen=True)
class BakerLevelReport:
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    transitions_checked: int
    reentry_edges: int
    descended_edges: int
    out_of_window_edges: int
    baker_C: float
    baker_kappa: float
    min_observed_gap: float | None
    min_baker_bound: float | None
    min_observed_to_baker_ratio: float | None
    max_signed_D_over_baker_ratio: float | None
    worst_ratio_edge: dict[str, Any] | None
    target_edge_m: int | None
    target_edge_A: int | None
    target_edge_observed_gap: float | None
    target_edge_baker_bound: float | None
    target_edge_ratio: float | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BakerCertificationReport:
    type: str
    status: str
    source_note: str
    levels: tuple[BakerLevelReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "source_note": self.source_note,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ConvergentAtlasEntry:
    A: int
    m: int
    D_PE: float
    abs_gap: float
    side: str
    appears_as_reentry_edge: bool
    matching_reentry_edges: int
    sample_edge: dict[str, Any] | None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConvergentAtlasReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    max_denominator: int
    reentry_edge_pairs: int
    entries: tuple[ConvergentAtlasEntry, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "max_denominator": self.max_denominator,
            "reentry_edge_pairs": self.reentry_edge_pairs,
            "entries": [entry.to_json_dict() for entry in self.entries],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class ContinuedFractionLevelReport:
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    transitions_checked: int
    reentry_edges: int
    descended_edges: int
    out_of_window_edges: int
    min_observed_gap: float | None
    min_cf_bound: float | None
    min_observed_to_cf_ratio: float | None
    worst_ratio_edge: dict[str, Any] | None
    convergent_edge_count: int
    nonconvergent_edge_count: int
    pair_summaries: tuple[dict[str, Any], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pair_summaries"] = [dict(item) for item in self.pair_summaries]
        return data


@dataclass(frozen=True)
class ContinuedFractionCertificationReport:
    type: str
    status: str
    source_note: str
    levels: tuple[ContinuedFractionLevelReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "source_note": self.source_note,
            "levels": [level.to_json_dict() for level in self.levels],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


@dataclass(frozen=True)
class RealizabilityTargetReport:
    A: int
    m: int
    candidates_checked: int
    status_counts: dict[str, int]
    examples: dict[str, dict[str, Any]]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealizabilityExclusionReport:
    type: str
    status: str
    mod2_power: int
    mod3_power: int
    R_min: int
    R_max: int
    sample_lift_power: int
    max_steps: int
    targets: tuple[RealizabilityTargetReport, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "mod2_power": self.mod2_power,
            "mod3_power": self.mod3_power,
            "R_min": self.R_min,
            "R_max": self.R_max,
            "sample_lift_power": self.sample_lift_power,
            "max_steps": self.max_steps,
            "targets": [target.to_json_dict() for target in self.targets],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def baker_lower_bound(
    m: int,
    A: int,
    *,
    C: float = 1e-9,
    kappa: float = 13.3,
) -> float:
    """Return a conservative Baker-style floor for ``|A - m*log2(3)|``.

    The default constants are intentionally configurable. They encode the
    proof-shape requested by the experiment, not a freshly formalized
    Laurent-Mignotte-Nesterenko specialization for ``log 2`` and ``log 3``.
    """

    if m <= 0 or A <= 0:
        raise ValueError("m and A must be positive")
    if C <= 0.0 or kappa <= 0.0:
        raise ValueError("C and kappa must be positive")
    return C / (max(m, A) ** kappa)


def _convergent_bound_table(max_denominator: int):
    witnesses = list(log2_3_convergents(max_denominator=max_denominator))
    if len(witnesses) < 2:
        raise RuntimeError("not enough convergents generated")
    by_pair = {
        (witness.numerator_A, witness.denominator_m): index
        for index, witness in enumerate(witnesses)
    }
    return witnesses, by_pair


def continued_fraction_lower_bound(
    m: int,
    A: int,
    *,
    max_denominator: int = 5000,
) -> tuple[float, str, str]:
    """Return a classical continued-fraction lower bound for ``|A-m log2(3)|``.

    For denominator ``m`` between consecutive convergent denominators
    ``m_n <= m < m_{n+1}``, the best-approximation property gives
    ``|A-m*alpha| >= |A_n-m_n*alpha|`` unless ``A/m`` is the convergent itself.
    The standard convergent estimate
    ``|A_n-m_n*alpha| > 1/(m_n+m_{n+1})`` supplies the reported lower bound.
    """

    if m <= 0 or A <= 0:
        raise ValueError("m and A must be positive")
    witnesses, by_pair = _convergent_bound_table(max_denominator=max_denominator)
    index = None
    for candidate_index, witness in enumerate(witnesses[:-1]):
        next_denominator = witnesses[candidate_index + 1].denominator_m
        if witness.denominator_m <= m < next_denominator:
            index = candidate_index
            break
    if index is None:
        raise ValueError("max_denominator did not cover the requested denominator")
    witness = witnesses[index]
    next_witness = witnesses[index + 1]
    bound = 1.0 / (witness.denominator_m + next_witness.denominator_m)
    relation = (
        "convergent"
        if by_pair.get((A, m)) == index
        else "nonconvergent_best_approximation_interval"
    )
    return bound, relation, witness.approximation


def _post_exit_edge_stats(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
):
    R_set = set(R_values)
    transitions = 0
    reentries = 0
    descended = 0
    out_of_window = 0
    edges: list[dict[str, Any]] = []
    for state in _iter_post_exit_states(mod2_power, mod3_power, R_values):
        for u in _sample_u_values(state, sample_lift_power):
            transitions += 1
            transition = post_exit_transition_sample(state, u, max_steps=max_steps)
            if transition.status.startswith("descended"):
                descended += 1
                continue
            if (
                transition.target is None
                or transition.target.R not in R_set
                or not transition.status.startswith("reentered_tail")
            ):
                out_of_window += 1
                continue
            reentries += 1
            m_pe = state.R - 1 + transition.steps
            A_pe = transition.total_A
            D_pe = A_pe - m_pe * math.log2(3)
            edges.append(
                {
                    "source": state.to_json_dict(),
                    "target": transition.target.to_json_dict(),
                    "u": u,
                    "n0": transition.n0,
                    "landing": transition.landing,
                    "m_PE": m_pe,
                    "A_PE": A_pe,
                    "D_PE": D_pe,
                    "abs_gap": abs(D_pe),
                    "steps": transition.steps,
                    "total_A": transition.total_A,
                }
            )
    return transitions, reentries, descended, out_of_window, edges


def _baker_level_report(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
    baker_C: float,
    baker_kappa: float,
    target_edge: tuple[int, int],
) -> BakerLevelReport:
    transitions, reentries, descended, out_of_window, edges = _post_exit_edge_stats(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
    )
    min_gap = None
    min_bound = None
    min_ratio = None
    max_signed_ratio = None
    worst_edge = None
    target_gap = target_bound = target_ratio = None
    for edge in edges:
        bound = baker_lower_bound(
            int(edge["m_PE"]),
            int(edge["A_PE"]),
            C=baker_C,
            kappa=baker_kappa,
        )
        ratio = edge["abs_gap"] / bound if bound > 0.0 else float("inf")
        signed_ratio = edge["D_PE"] / bound if bound > 0.0 else float("-inf")
        if min_gap is None or edge["abs_gap"] < min_gap:
            min_gap = float(edge["abs_gap"])
        if min_bound is None or bound < min_bound:
            min_bound = float(bound)
        if min_ratio is None or ratio < min_ratio:
            min_ratio = float(ratio)
            worst_edge = {
                **edge,
                "baker_bound": bound,
                "observed_to_baker_ratio": ratio,
                "signed_D_over_baker_ratio": signed_ratio,
            }
        if max_signed_ratio is None or signed_ratio > max_signed_ratio:
            max_signed_ratio = float(signed_ratio)
        if (edge["m_PE"], edge["A_PE"]) == target_edge and target_gap is None:
            target_gap = float(edge["abs_gap"])
            target_bound = float(bound)
            target_ratio = float(ratio)
    return BakerLevelReport(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        transitions_checked=transitions,
        reentry_edges=reentries,
        descended_edges=descended,
        out_of_window_edges=out_of_window,
        baker_C=baker_C,
        baker_kappa=baker_kappa,
        min_observed_gap=min_gap,
        min_baker_bound=min_bound,
        min_observed_to_baker_ratio=min_ratio,
        max_signed_D_over_baker_ratio=max_signed_ratio,
        worst_ratio_edge=worst_edge,
        target_edge_m=target_edge[0],
        target_edge_A=target_edge[1],
        target_edge_observed_gap=target_gap,
        target_edge_baker_bound=target_bound,
        target_edge_ratio=target_ratio,
    )


def dpe_baker_certification_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 3), (10, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    baker_C: float = 1e-9,
    baker_kappa: float = 13.3,
    target_edge: tuple[int, int] = (12, 19),
) -> BakerCertificationReport:
    """Compare finite PECM gaps to a configurable Baker-style lower bound."""

    levels = tuple(
        _baker_level_report(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            baker_C=baker_C,
            baker_kappa=baker_kappa,
            target_edge=target_edge,
        )
        for mod2_power, mod3_power in configurations
    )
    status = (
        "finite_reentry_gaps_respect_configured_baker_floor_not_structural_proof"
        if all(
            level.min_observed_to_baker_ratio is not None
            and level.min_observed_to_baker_ratio >= 1.0
            for level in levels
        )
        else "finite_reentry_gap_below_configured_baker_floor"
    )
    return BakerCertificationReport(
        type="d_pe_baker_certification",
        status=status,
        source_note=(
            "Uses configurable Baker-style constants for |A-m*log2(3)|. "
            "For published explicit two-logarithm bounds see Laurent, "
            "Mignotte, Nesterenko (JNT 1995) and Gouillon (JTNB 2006)."
        ),
        levels=levels,
    )


def _continued_fraction_level_report(
    mod2_power: int,
    mod3_power: int,
    R_values: tuple[int, ...],
    sample_lift_power: int,
    max_steps: int,
    max_denominator: int,
) -> ContinuedFractionLevelReport:
    transitions, reentries, descended, out_of_window, edges = _post_exit_edge_stats(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
    )
    pair_counts: dict[tuple[int, int], int] = {}
    pair_best: dict[tuple[int, int], dict[str, Any]] = {}
    min_gap = None
    min_bound = None
    min_ratio = None
    worst_edge = None
    convergent_edges = 0
    nonconvergent_edges = 0
    for edge in edges:
        pair = (int(edge["A_PE"]), int(edge["m_PE"]))
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        bound, relation, reference = continued_fraction_lower_bound(
            pair[1],
            pair[0],
            max_denominator=max_denominator,
        )
        ratio = edge["abs_gap"] / bound
        if relation == "convergent":
            convergent_edges += 1
        else:
            nonconvergent_edges += 1
        if pair not in pair_best or edge["abs_gap"] < pair_best[pair]["abs_gap"]:
            pair_best[pair] = {
                **edge,
                "cf_bound": bound,
                "observed_to_cf_ratio": ratio,
                "cf_relation": relation,
                "cf_reference": reference,
            }
        if min_gap is None or edge["abs_gap"] < min_gap:
            min_gap = float(edge["abs_gap"])
        if min_bound is None or bound < min_bound:
            min_bound = float(bound)
        if min_ratio is None or ratio < min_ratio:
            min_ratio = float(ratio)
            worst_edge = {
                **edge,
                "cf_bound": bound,
                "observed_to_cf_ratio": ratio,
                "cf_relation": relation,
                "cf_reference": reference,
            }
    summaries = []
    for (A, m), count in sorted(pair_counts.items(), key=lambda item: (item[0][1], item[0][0])):
        best = pair_best[(A, m)]
        summaries.append(
            {
                "A": A,
                "m": m,
                "count": count,
                "min_abs_gap": best["abs_gap"],
                "D_PE": best["D_PE"],
                "cf_bound": best["cf_bound"],
                "observed_to_cf_ratio": best["observed_to_cf_ratio"],
                "cf_relation": best["cf_relation"],
                "cf_reference": best["cf_reference"],
            }
        )
    return ContinuedFractionLevelReport(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        transitions_checked=transitions,
        reentry_edges=reentries,
        descended_edges=descended,
        out_of_window_edges=out_of_window,
        min_observed_gap=min_gap,
        min_cf_bound=min_bound,
        min_observed_to_cf_ratio=min_ratio,
        worst_ratio_edge=worst_edge,
        convergent_edge_count=convergent_edges,
        nonconvergent_edge_count=nonconvergent_edges,
        pair_summaries=tuple(summaries),
    )


def dpe_continued_fraction_certification_report(
    configurations: tuple[tuple[int, int], ...] = ((8, 3), (10, 4)),
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    max_denominator: int = 5000,
) -> ContinuedFractionCertificationReport:
    """Compare finite PECM gaps with classical continued-fraction bounds."""

    levels = tuple(
        _continued_fraction_level_report(
            mod2_power=mod2_power,
            mod3_power=mod3_power,
            R_values=R_values,
            sample_lift_power=sample_lift_power,
            max_steps=max_steps,
            max_denominator=max_denominator,
        )
        for mod2_power, mod3_power in configurations
    )
    status = (
        "finite_reentry_gaps_respect_continued_fraction_bounds_not_global_proof"
        if all(
            level.min_observed_to_cf_ratio is not None
            and level.min_observed_to_cf_ratio >= 1.0
            for level in levels
        )
        else "finite_reentry_gap_below_continued_fraction_bound"
    )
    return ContinuedFractionCertificationReport(
        type="d_pe_continued_fraction_certification",
        status=status,
        source_note=(
            "Uses the classical best-approximation property of continued "
            "fractions and the convergent lower bound "
            "|A_n-m_n*alpha| > 1/(m_n+m_{n+1}) for alpha=log2(3)."
        ),
        levels=levels,
    )


def dpe_convergent_atlas_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    R_values: tuple[int, ...] = tuple(range(2, 31)),
    sample_lift_power: int = 2,
    max_steps: int = 200,
    max_denominator: int = 1000,
) -> ConvergentAtlasReport:
    """Check which ``log2(3)`` convergents occur as PECM reentry edge pairs."""

    transitions, reentries, _descended, _out_of_window, edges = _post_exit_edge_stats(
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_values=R_values,
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
    )
    del transitions
    by_pair: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for edge in edges:
        pair = (int(edge["A_PE"]), int(edge["m_PE"]))
        by_pair.setdefault(pair, []).append(edge)
    entries: list[ConvergentAtlasEntry] = []
    for witness in log2_3_convergents(max_denominator=max_denominator):
        pair = (witness.numerator_A, witness.denominator_m)
        matches = by_pair.get(pair, [])
        D_pe = witness.numerator_A - witness.denominator_m * math.log2(3)
        entries.append(
            ConvergentAtlasEntry(
                A=witness.numerator_A,
                m=witness.denominator_m,
                D_PE=D_pe,
                abs_gap=abs(D_pe),
                side="valuation_rich" if D_pe < 0 else "valuation_poor",
                appears_as_reentry_edge=bool(matches),
                matching_reentry_edges=len(matches),
                sample_edge=None if not matches else matches[0],
            )
        )
    status = (
        "finite_convergent_atlas_built_not_scaling_proof"
        if entries
        else "no_convergents_generated"
    )
    return ConvergentAtlasReport(
        type="d_pe_convergent_atlas",
        status=status,
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        max_denominator=max_denominator,
        reentry_edge_pairs=len(by_pair),
        entries=tuple(entries),
    )


def realizability_structural_exclusion_report(
    mod2_power: int = 8,
    mod3_power: int = 3,
    R_values: tuple[int, ...] = tuple(range(2, 101)),
    sample_lift_power: int = 2,
    max_steps: int = 1000,
    targets: tuple[tuple[int, int], ...] = ((84, 53), (485, 306), (1054, 665)),
) -> RealizabilityExclusionReport:
    """Classify why selected ``(A,m)`` pairs are absent as PECM reentries."""

    target_reports: list[RealizabilityTargetReport] = []
    for A, m in targets:
        counts: Counter[str] = Counter()
        examples: dict[str, dict[str, Any]] = {}
        checked = 0
        for state in _iter_post_exit_states(mod2_power, mod3_power, R_values):
            if state.R > m + 1:
                continue
            for u in _sample_u_values(state, sample_lift_power):
                checked += 1
                transition = post_exit_transition_sample(state, u, max_steps=max_steps)
                m_pe = state.R - 1 + transition.steps
                if transition.status.startswith("descended"):
                    if m_pe < m:
                        label = "descended_before_target_m"
                    elif m_pe == m:
                        label = (
                            "descended_at_target_m_target_A"
                            if transition.total_A == A
                            else "descended_at_target_m_wrong_A"
                        )
                    else:
                        label = "descended_after_target_m"
                elif (
                    transition.target is not None
                    and transition.status.startswith("reentered_tail")
                ):
                    if m_pe < m:
                        label = "reentered_before_target_m"
                    elif m_pe == m and transition.total_A == A:
                        label = "realized_as_reentry_edge"
                    elif m_pe == m:
                        label = "reentered_at_target_m_wrong_A"
                    else:
                        label = "reentered_after_target_m"
                else:
                    label = "unresolved_or_out_of_window"
                counts[label] += 1
                if label not in examples:
                    examples[label] = {
                        "source": state.to_json_dict(),
                        "u": u,
                        "status": transition.status,
                        "m_PE": m_pe,
                        "A_PE": transition.total_A,
                        "D_PE": transition.total_A - m_pe * math.log2(3),
                        "landing": transition.landing,
                        "target": None
                        if transition.target is None
                        else transition.target.to_json_dict(),
                    }
        target_reports.append(
            RealizabilityTargetReport(
                A=A,
                m=m,
                candidates_checked=checked,
                status_counts=dict(sorted(counts.items())),
                examples=examples,
            )
        )
    status = (
        "finite_target_pairs_not_realized_as_reentry_edges"
        if all(
            target.status_counts.get("realized_as_reentry_edge", 0) == 0
            for target in target_reports
        )
        else "finite_some_target_pairs_realized"
    )
    return RealizabilityExclusionReport(
        type="realizability_structural_exclusion",
        status=status,
        mod2_power=mod2_power,
        mod3_power=mod3_power,
        R_min=min(R_values),
        R_max=max(R_values),
        sample_lift_power=sample_lift_power,
        max_steps=max_steps,
        targets=tuple(target_reports),
    )
