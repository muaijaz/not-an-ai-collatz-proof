"""CF-convergent diagnostics for slope-filtered cycle survivors."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .cycles import classify_cycle_word


DEFAULT_ARTIFACT_PATHS = (
    "docs/reports/karp_slope_joint_sweep.json",
    "docs/reports/karp_slope_joint_sweep_extended.json",
    "docs/reports/tail_cycle_realizability.json",
    "docs/reports/tail_cycle_realizability_extended.json",
    "docs/reports/tail_cycle_realizability_extended_deep.json",
)


@dataclass(frozen=True)
class CFConvergentSlopeReport:
    type: str
    status: str
    caveat: str
    artifact_paths: tuple[str, ...]
    cf_convergents: tuple[dict[str, Any], ...]
    intermediate_fractions: tuple[dict[str, Any], ...]
    cycles: tuple[dict[str, Any], ...]
    cross_tabulation: dict[str, Any]
    hypothesis_tests: dict[str, Any]
    verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "artifact_paths": list(self.artifact_paths),
            "cf_convergents": list(self.cf_convergents),
            "intermediate_fractions": list(self.intermediate_fractions),
            "cycles": list(self.cycles),
            "cross_tabulation": self.cross_tabulation,
            "hypothesis_tests": self.hypothesis_tests,
            "verdict": self.verdict,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json() + "\n")


def continued_fraction_convergents_log2_3(depth: int = 20) -> tuple[dict[str, Any], ...]:
    """Return continued-fraction convergents of log2(3)."""

    if depth < 1:
        raise ValueError("depth must be positive")
    target = math.log2(3)
    current = target
    p_minus_2, p_minus_1 = 0, 1
    q_minus_2, q_minus_1 = 1, 0
    rows: list[dict[str, Any]] = []
    for index in range(depth):
        partial = math.floor(current)
        p = partial * p_minus_1 + p_minus_2
        q = partial * q_minus_1 + q_minus_2
        frac = Fraction(p, q)
        residual = float(frac) - target
        rows.append(
            {
                "index": index,
                "partial_quotient": partial,
                "p": p,
                "q": q,
                "fraction": f"{frac.numerator}/{frac.denominator}",
                "residual": residual,
                "side": "above" if residual > 0 else "below" if residual < 0 else "exact",
            }
        )
        p_minus_2, p_minus_1 = p_minus_1, p
        q_minus_2, q_minus_1 = q_minus_1, q
        fractional = current - partial
        if fractional == 0:
            break
        current = 1.0 / fractional
    return tuple(rows)


def _intermediate_fractions(
    convergents: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], ...]:
    target = math.log2(3)
    seen: set[Fraction] = set()
    rows: list[dict[str, Any]] = []
    for left, right in zip(convergents, convergents[1:], strict=False):
        frac = Fraction(left["p"] + right["p"], left["q"] + right["q"])
        if frac in seen:
            continue
        seen.add(frac)
        rows.append(
            {
                "between_convergent_indices": [left["index"], right["index"]],
                "p": frac.numerator,
                "q": frac.denominator,
                "fraction": f"{frac.numerator}/{frac.denominator}",
                "residual": float(frac) - target,
            }
        )
    return tuple(rows)


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open() as handle:
        return json.load(handle)


def _word_tuple(value: Any) -> tuple[int, ...]:
    return tuple(int(item) for item in value)


def _cycle_slope(word: tuple[int, ...]) -> Fraction:
    if not word:
        raise ValueError("valuation word cannot be empty")
    return Fraction(sum(word), len(word))


def _classification_for_cycle(cycle: dict[str, Any], word: tuple[int, ...]) -> str:
    if "lift_classification" in cycle and cycle["lift_classification"] is not None:
        return str(cycle["lift_classification"])
    return classify_cycle_word(word).kind


def _collect_cycles(paths: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    collected: dict[tuple[int, int, tuple[int, ...], str], dict[str, Any]] = {}
    for path in paths:
        data = _load_json(path)
        for level in data.get("levels", []):
            tail_unit_power = int(level["tail_unit_power"])
            max_tail_depth = int(level["max_tail_depth"])
            source_cycles = []
            for survivor in level.get("survivors", []):
                source_cycles.append(("karp_survivor", survivor))
            for cycle in level.get("cycles", []):
                source_cycles.append(("tail_realizability_cycle", cycle))
            for source_kind, cycle in source_cycles:
                word = _word_tuple(cycle["valuation_word"])
                classification = _classification_for_cycle(cycle, word)
                key = (tail_unit_power, max_tail_depth, word, classification)
                slope = _cycle_slope(word)
                edge_factor = cycle.get("edge_factor")
                edge_mean = cycle.get("edge_mean_log2_slope")
                if key not in collected:
                    collected[key] = {
                        "level": [tail_unit_power, max_tail_depth],
                        "valuation_word": list(word),
                        "classification": classification,
                        "edge_factor": edge_factor,
                        "edge_mean_log2_slope": edge_mean,
                        "in_slope_window": bool(cycle.get("in_slope_window", False)),
                        "slope_filter_survivor": source_kind == "karp_survivor"
                        or bool(cycle.get("in_slope_window", False)),
                        "high_growth": edge_factor is not None and edge_factor >= 1.0,
                        "slope_A_over_m": f"{slope.numerator}/{slope.denominator}",
                        "slope_A": sum(word),
                        "slope_m": len(word),
                        "source_files": [],
                        "source_kinds": [],
                    }
                row = collected[key]
                if path not in row["source_files"]:
                    row["source_files"].append(path)
                if source_kind not in row["source_kinds"]:
                    row["source_kinds"].append(source_kind)
                if row["edge_factor"] is None and edge_factor is not None:
                    row["edge_factor"] = edge_factor
                if row["edge_mean_log2_slope"] is None and edge_mean is not None:
                    row["edge_mean_log2_slope"] = edge_mean
                row["in_slope_window"] = row["in_slope_window"] or bool(
                    cycle.get("in_slope_window", False)
                )
                row["slope_filter_survivor"] = row["slope_filter_survivor"] or (
                    source_kind == "karp_survivor"
                    or bool(cycle.get("in_slope_window", False))
                )
                row["high_growth"] = row["high_growth"] or (
                    edge_factor is not None and edge_factor >= 1.0
                )
    return tuple(
        sorted(
            collected.values(),
            key=lambda item: (
                item["level"][0],
                item["level"][1],
                item["classification"],
                item["valuation_word"],
            ),
        )
    )


def _annotate_cycle(
    cycle: dict[str, Any],
    convergent_set: dict[Fraction, dict[str, Any]],
    intermediate_set: dict[Fraction, dict[str, Any]],
    convergents: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    slope = Fraction(cycle["slope_A"], cycle["slope_m"])
    match = convergent_set.get(slope)
    intermediate = intermediate_set.get(slope)
    distances = [
        abs(slope - Fraction(item["p"], item["q"]))
        for item in convergents
    ]
    min_distance = min(distances) if distances else Fraction(0, 1)
    rational_class = (
        "cf_convergent"
        if match is not None
        else "intermediate_fraction"
        if intermediate is not None
        else "non_convergent_rational"
    )
    annotated = dict(cycle)
    annotated.update(
        {
            "cf_convergent_match": match is not None,
            "cf_convergent_index": None if match is None else match["index"],
            "intermediate_fraction_match": intermediate is not None,
            "intermediate_fraction": None
            if intermediate is None
            else intermediate["fraction"],
            "non_convergent_rational": rational_class == "non_convergent_rational",
            "rational_class": rational_class,
            "min_distance_to_convergent": f"{min_distance.numerator}/{min_distance.denominator}",
            "min_distance_to_convergent_float": float(min_distance),
        }
    )
    return annotated


def _increment(tab: dict[str, Any], keys: tuple[str, ...], rational_class: str) -> None:
    cursor = tab
    for key in keys:
        cursor = cursor.setdefault(key, {})
    cursor["total"] = cursor.get("total", 0) + 1
    cursor[rational_class] = cursor.get(rational_class, 0) + 1


def _cross_tabulate(cycles: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    by_classification: dict[str, Any] = {}
    by_level: dict[str, Any] = {}
    by_level_and_classification: dict[str, Any] = {}
    for cycle in cycles:
        level = f"({cycle['level'][0]},{cycle['level'][1]})"
        classification = cycle["classification"]
        rational_class = cycle["rational_class"]
        _increment(by_classification, (classification,), rational_class)
        _increment(by_level, (level,), rational_class)
        _increment(
            by_level_and_classification,
            (level, classification),
            rational_class,
        )
    slope_filtered = tuple(cycle for cycle in cycles if cycle["slope_filter_survivor"])
    slope_filtered_by_level_and_classification: dict[str, Any] = {}
    for cycle in slope_filtered:
        level = f"({cycle['level'][0]},{cycle['level'][1]})"
        _increment(
            slope_filtered_by_level_and_classification,
            (level, cycle["classification"]),
            cycle["rational_class"],
        )
    return {
        "by_classification": by_classification,
        "by_level": by_level,
        "by_level_and_classification": by_level_and_classification,
        "slope_filtered_by_level_and_classification": (
            slope_filtered_by_level_and_classification
        ),
    }


def _hypothesis_tests(cycles: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    small_levels = {(5, 4), (6, 5), (7, 6)}
    cycles_by_level = {
        level: [
            cycle
            for cycle in cycles
            if tuple(cycle["level"]) == level
            and cycle["slope_filter_survivor"]
        ]
        for level in (*sorted(small_levels), (8, 7))
    }
    small_supported = all(
        cycle["cf_convergent_match"]
        for level in sorted(small_levels)
        for cycle in cycles_by_level.get(level, [])
    )
    level_87 = cycles_by_level.get((8, 7), [])
    ghosts_87 = [
        cycle for cycle in level_87 if cycle["classification"] == "noninteger_2adic_only"
    ]
    high_growth_ghosts_87 = [
        cycle for cycle in ghosts_87 if cycle["high_growth"]
    ]
    positives_87 = [
        cycle for cycle in level_87 if cycle["classification"] == "positive_integer_cycle"
    ]
    ghosts_non_convergent = bool(ghosts_87) and all(
        cycle["non_convergent_rational"] for cycle in ghosts_87
    )
    positives_convergent_2 = bool(positives_87) and all(
        cycle["cf_convergent_match"] and cycle["slope_A_over_m"] == "2/1"
        for cycle in positives_87
    )
    word_2111 = next(
        (
            cycle
            for cycle in level_87
            if cycle["valuation_word"] == [2, 1, 1, 1]
        ),
        None,
    )
    level_87_supported = (
        ghosts_non_convergent
        and positives_convergent_2
        and word_2111 is not None
        and word_2111["non_convergent_rational"]
    )
    high_growth_level_87_supported = (
        bool(high_growth_ghosts_87)
        and all(cycle["non_convergent_rational"] for cycle in high_growth_ghosts_87)
        and positives_convergent_2
        and word_2111 is not None
        and word_2111["non_convergent_rational"]
    )
    return {
        "hypothesis_supported_at_(5,4)..(7,6)": small_supported,
        "hypothesis_supported_at_(8,7)": level_87_supported,
        "high_growth_obstruction_variant_supported_at_(8,7)": (
            high_growth_level_87_supported
        ),
        "small_level_cycle_count": sum(
            len(cycles_by_level.get(level, [])) for level in small_levels
        ),
        "level_(8,7)_ghost_count": len(ghosts_87),
        "level_(8,7)_high_growth_ghost_count": len(high_growth_ghosts_87),
        "level_(8,7)_positive_integer_cycle_count": len(positives_87),
        "level_(8,7)_ghosts_all_non_convergent": ghosts_non_convergent,
        "level_(8,7)_high_growth_ghosts_all_non_convergent": (
            bool(high_growth_ghosts_87)
            and all(cycle["non_convergent_rational"] for cycle in high_growth_ghosts_87)
        ),
        "level_(8,7)_positive_survivors_all_2_over_1_cf": positives_convergent_2,
        "word_[2,1,1,1]_classification": None
        if word_2111 is None
        else word_2111["rational_class"],
    }


def cf_convergent_slope_hypothesis_report(
    artifact_paths: tuple[str, ...] = DEFAULT_ARTIFACT_PATHS,
    cf_depth: int = 20,
) -> CFConvergentSlopeReport:
    """Analyze existing slope/realizability artifacts against CF convergents."""

    convergents = continued_fraction_convergents_log2_3(cf_depth)
    intermediates = _intermediate_fractions(convergents)
    convergent_set = {
        Fraction(item["p"], item["q"]): item for item in convergents
    }
    intermediate_set = {
        Fraction(item["p"], item["q"]): item for item in intermediates
    }
    raw_cycles = _collect_cycles(artifact_paths)
    cycles = tuple(
        _annotate_cycle(cycle, convergent_set, intermediate_set, convergents)
        for cycle in raw_cycles
    )
    cross_tab = _cross_tabulate(cycles)
    tests = _hypothesis_tests(cycles)
    if (
        tests["hypothesis_supported_at_(5,4)..(7,6)"]
        and tests["hypothesis_supported_at_(8,7)"]
    ):
        verdict = "cf_convergent_hypothesis_supported"
    elif (
        tests["hypothesis_supported_at_(5,4)..(7,6)"]
        or tests["hypothesis_supported_at_(8,7)"]
    ):
        verdict = "cf_convergent_hypothesis_partially_supported"
    else:
        verdict = "cf_convergent_hypothesis_falsified"
    return CFConvergentSlopeReport(
        type="cf_convergent_slope_hypothesis",
        status="finite_artifact_analysis_complete",
        caveat=(
            "This is a finite empirical diagnostic over existing JSON "
            "artifacts only. It tests a session-local structural hypothesis; "
            "it is not a proof about all Collatz slope filters or all "
            "realizability obstructions."
        ),
        artifact_paths=artifact_paths,
        cf_convergents=convergents,
        intermediate_fractions=intermediates,
        cycles=cycles,
        cross_tabulation=cross_tab,
        hypothesis_tests=tests,
        verdict=verdict,
    )
