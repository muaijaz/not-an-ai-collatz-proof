"""Phase-transition diagnostics for positive qn+1 cycle factors."""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .qnp1_audit import QPositiveCycle, qnp1_realizability_report


Q_GRID = (3, 5, 7, 9, 11, 13, 17, 19, 21, 25, 27, 31)


@dataclass(frozen=True)
class QNP1PhaseTransitionReport:
    type: str
    status: str
    caveat: str
    q_grid: tuple[int, ...]
    m_max: int
    levels: tuple[tuple[int, int], ...]
    entries: tuple[dict[str, Any], ...]
    diophantine_max_factor_by_q: dict[str, float]
    gap_to_1_by_q: dict[str, float]
    argmax_m_by_q: dict[str, int]
    argmax_m_vs_log_2_q_correlation: dict[str, Any]
    scan_policy: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "caveat": self.caveat,
            "q_grid": list(self.q_grid),
            "m_max": self.m_max,
            "levels": [list(level) for level in self.levels],
            "entries": list(self.entries),
            "diophantine_max_factor_by_q": dict(self.diophantine_max_factor_by_q),
            "gap_to_1_by_q": dict(self.gap_to_1_by_q),
            "argmax_m_by_q": dict(self.argmax_m_by_q),
            "argmax_m_vs_log_2_q_correlation": dict(
                self.argmax_m_vs_log_2_q_correlation
            ),
            "scan_policy": dict(self.scan_policy),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json() + "\n")


def _fraction_to_json(factor: Fraction) -> dict[str, Any]:
    return {
        "fraction": f"{factor.numerator}/{factor.denominator}",
        "numerator": factor.numerator,
        "denominator": factor.denominator,
        "float": float(factor),
    }


def diophantine_max_factor(q: int, m_max: int = 100) -> dict[str, Any]:
    """Bound positive cycle factors by ``q^m / 2^A`` for ``m <= m_max``."""

    if q <= 1 or q % 2 == 0:
        raise ValueError("q must be an odd integer greater than one")
    if m_max < 1:
        raise ValueError("m_max must be positive")

    best_factor = Fraction(0, 1)
    best_m = 0
    best_A = 0
    log_2_q = math.log2(q)
    values: list[dict[str, Any]] = []
    for m in range(1, m_max + 1):
        numerator = q**m
        A = numerator.bit_length()
        factor = Fraction(numerator, 1 << A)
        distance = A / m - log_2_q
        values.append(
            {
                "m": m,
                "A_min": A,
                "factor": _fraction_to_json(factor),
                "diophantine_distance": distance,
            }
        )
        if factor > best_factor:
            best_factor = factor
            best_m = m
            best_A = A

    return {
        "q": q,
        "m_max": m_max,
        "log_2_q": log_2_q,
        "max_factor": best_factor,
        "max_factor_json": _fraction_to_json(best_factor),
        "argmax_m": best_m,
        "argmax_A": best_A,
        "diophantine_distance": best_A / best_m - log_2_q,
        "gap_to_1": float(1 - best_factor),
        "values": tuple(values),
    }


def continued_fraction_convergents_log2(
    q: int,
    count: int = 10,
) -> tuple[dict[str, Any], ...]:
    """Return the first continued-fraction convergents of ``log2(q)``."""

    if count < 1:
        raise ValueError("count must be positive")
    x = math.log2(q)
    coefficients: list[int] = []
    convergents: list[dict[str, Any]] = []
    p_minus_2, p_minus_1 = 0, 1
    q_minus_2, q_minus_1 = 1, 0
    current = x
    for index in range(count):
        coefficient = math.floor(current)
        coefficients.append(coefficient)
        numerator = coefficient * p_minus_1 + p_minus_2
        denominator = coefficient * q_minus_1 + q_minus_2
        convergents.append(
            {
                "index": index,
                "partial_quotient": coefficient,
                "numerator": numerator,
                "denominator": denominator,
                "value": numerator / denominator,
                "distance": numerator / denominator - x,
            }
        )
        p_minus_2, p_minus_1 = p_minus_1, numerator
        q_minus_2, q_minus_1 = q_minus_1, denominator
        fractional = current - coefficient
        if fractional == 0:
            break
        current = 1 / fractional
    return tuple(convergents)


def _best_positive_cycle(cycles: tuple[QPositiveCycle, ...]) -> QPositiveCycle | None:
    best: QPositiveCycle | None = None
    for cycle in cycles:
        if best is None or cycle.edge_factor > best.edge_factor:
            best = cycle
    return best


def empirical_realizable_karp_q(
    q: int,
    levels: list[tuple[int, int]] | tuple[tuple[int, int], ...],
    *,
    max_valuation: int = 12,
    max_cycle_edges: int = 12,
    max_cycles_scanned: int = 200_000,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Run the bounded qn+1 realizability audit and return the best positive cycle."""

    started = time.perf_counter()
    try:
        report = qnp1_realizability_report(
            q_param=q,
            levels=tuple(levels),
            max_valuation=max_valuation,
            max_cycle_edges=max_cycle_edges,
            max_cycles_scanned=max_cycles_scanned,
        )
    except Exception as exc:
        return {
            "q": q,
            "empirical_realizable_karp_factor": None,
            "empirical_argmax_word": None,
            "empirical_argmax_cycle_value": None,
            "empirical_argmax_orbit": None,
            "elapsed_seconds": time.perf_counter() - started,
            "status": "empirical_audit_failed",
            "reason": str(exc),
        }

    elapsed = time.perf_counter() - started
    best: QPositiveCycle | None = None
    best_level_index: int | None = None
    for level in report.levels:
        candidate = _best_positive_cycle(level.positive_integer_cycles)
        if candidate is None:
            continue
        if best is None or candidate.edge_factor > best.edge_factor:
            best = candidate
            best_level_index = level.level_index

    status = "bounded_tail_graph_scan_complete"
    reason = None
    if elapsed > timeout_seconds:
        status = "timeout_budget_exceeded_after_completion"
        reason = f"completed in {elapsed:.3f}s, above {timeout_seconds:.3f}s budget"
    if best is None:
        status = "no_positive_integer_cycle_found_in_bounded_scan"

    return {
        "q": q,
        "empirical_realizable_karp_factor": None if best is None else best.edge_factor,
        "empirical_argmax_word": None if best is None else list(best.word),
        "empirical_argmax_cycle_value": None if best is None else best.cycle_value,
        "empirical_argmax_orbit": None if best is None else list(best.orbit),
        "empirical_argmax_level_index": best_level_index,
        "elapsed_seconds": elapsed,
        "status": status,
        "reason": reason,
        "level_summaries": [
            {
                "level_index": level.level_index,
                "tail_unit_power": level.tail_unit_power,
                "max_tail_depth": level.max_tail_depth,
                "tail_edges": level.tail_edges,
                "cycles_scanned": level.cycles_scanned,
                "classification_counts": level.classification_counts,
                "realizable_karp_factor_positive": (
                    level.realizable_karp_factor_positive
                ),
                "status": level.status,
            }
            for level in report.levels
        ],
    }


def _pearson(xs: tuple[float, ...], ys: tuple[float, ...]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return numerator / (denom_x * denom_y)


def qnp1_phase_transition_report(
    q_grid: tuple[int, ...] = Q_GRID,
    m_max: int = 100,
    levels: tuple[tuple[int, int], ...] = ((5, 4), (6, 5)),
    max_valuation: int = 12,
    max_cycle_edges: int = 12,
    max_cycles_scanned: int = 200_000,
    timeout_seconds: float = 30.0,
) -> QNP1PhaseTransitionReport:
    """Compare Diophantine upper bounds with bounded empirical realizability."""

    entries: list[dict[str, Any]] = []
    by_q: dict[str, float] = {}
    gap_by_q: dict[str, float] = {}
    argmax_by_q: dict[str, int] = {}

    for q in q_grid:
        dio = diophantine_max_factor(q, m_max=m_max)
        empirical = empirical_realizable_karp_q(
            q,
            levels,
            max_valuation=max_valuation,
            max_cycle_edges=max_cycle_edges,
            max_cycles_scanned=max_cycles_scanned,
            timeout_seconds=timeout_seconds,
        )
        dio_float = float(dio["max_factor"])
        empirical_factor = empirical["empirical_realizable_karp_factor"]
        matches = (
            empirical_factor is not None
            and abs(empirical_factor - dio_float) <= 1e-12
        )
        entry = {
            "q": q,
            "log_2_q": dio["log_2_q"],
            "diophantine_max_factor": dio_float,
            "diophantine_max_factor_exact": dio["max_factor_json"]["fraction"],
            "diophantine_argmax_m": dio["argmax_m"],
            "diophantine_argmax_A": dio["argmax_A"],
            "diophantine_distance": dio["diophantine_distance"],
            "diophantine_gap_to_1": dio["gap_to_1"],
            "empirical_realizable_karp_factor": empirical[
                "empirical_realizable_karp_factor"
            ],
            "empirical_argmax_word": empirical["empirical_argmax_word"],
            "empirical_argmax_cycle_value": empirical[
                "empirical_argmax_cycle_value"
            ],
            "empirical_argmax_orbit": empirical["empirical_argmax_orbit"],
            "empirical_status": empirical["status"],
            "empirical_reason": empirical["reason"],
            "empirical_elapsed_seconds": empirical["elapsed_seconds"],
            "empirical_matches_diophantine_bound": matches,
            "cf_log_2_q_convergents": list(
                continued_fraction_convergents_log2(q, count=10)
            ),
            "empirical_level_summaries": empirical["level_summaries"],
        }
        entries.append(entry)
        by_q[str(q)] = dio_float
        gap_by_q[str(q)] = dio["gap_to_1"]
        argmax_by_q[str(q)] = dio["argmax_m"]

    argmax_values = tuple(float(argmax_by_q[str(q)]) for q in q_grid)
    proxy_values = tuple(-math.log10(max(gap_by_q[str(q)], 1e-300)) for q in q_grid)
    return QNP1PhaseTransitionReport(
        type="qnp1_phase_transition",
        status="finite_empirical_diagnostic_complete",
        caveat=(
            "The Diophantine column is an upper bound on positive integer cycle "
            "factor at bounded m. The empirical column records only positive "
            "integer cycles found in bounded tail-graph scans; it is not a "
            "proof of cycle absence or global qn+1 behavior."
        ),
        q_grid=q_grid,
        m_max=m_max,
        levels=levels,
        entries=tuple(entries),
        diophantine_max_factor_by_q=by_q,
        gap_to_1_by_q=gap_by_q,
        argmax_m_by_q=argmax_by_q,
        argmax_m_vs_log_2_q_correlation={
            "method": "pearson_argmax_m_vs_negative_log10_gap_proxy",
            "value": _pearson(argmax_values, proxy_values),
            "note": (
                "The true irrationality measure of log2(q) is not computed; "
                "this finite proxy correlates argmax m with the bounded "
                "Diophantine gap depth."
            ),
        },
        scan_policy={
            "max_valuation": max_valuation,
            "max_cycle_edges": max_cycle_edges,
            "max_cycles_scanned": max_cycles_scanned,
            "timeout_seconds": timeout_seconds,
            "generic_q_tail_model": (
                "exact LTE closure when q-1 is a power of two; otherwise a "
                "finite witnessed residue-lift graph"
            ),
        },
    )
