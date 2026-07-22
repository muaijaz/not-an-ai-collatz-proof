"""Proof-search frontier dashboard assembled from saved artifacts.

The dashboard is deliberately conservative: it reads existing finite reports
and turns their statuses into ranked engineering/research next steps. It does
not create new Collatz claims.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FrontierItem:
    priority: int
    name: str
    status: str
    evidence: tuple[str, ...]
    next_action: str
    source_reports: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        data["source_reports"] = list(self.source_reports)
        return data


@dataclass(frozen=True)
class FrontierDashboardReport:
    type: str
    status: str
    reports_dir: str
    items: tuple[FrontierItem, ...]
    missing_reports: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "status": self.status,
            "reports_dir": self.reports_dir,
            "items": [item.to_json_dict() for item in self.items],
            "missing_reports": list(self.missing_reports),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def _load_report(reports_dir: Path, name: str) -> tuple[dict[str, Any] | None, str | None]:
    path = reports_dir / name
    if not path.exists():
        return None, str(path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle), None


def _fmt_int(value: Any) -> str:
    return f"{int(value):,}"


def _add_compressed_operator_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    requested = data.get("requested_extended_levels") or []
    if not requested:
        return
    evidence = []
    for level in requested[:2]:
        label = f"({level.get('mod2_power')},{level.get('mod3_power')})"
        states = _fmt_int(level.get("states", 0))
        transitions = _fmt_int(level.get("sample_transitions", 0))
        cache_gib = float(level.get("target_cache_gib_int32", 0.0))
        evidence.append(
            f"{label}: {states} states, {transitions} sampled transitions, "
            f"{cache_gib:.2f} GiB int32 target cache"
        )
    items.append(
        FrontierItem(
            priority=1,
            name="Compressed PECM operator scaling",
            status=str(data.get("status", "capacity_unknown")),
            evidence=tuple(evidence),
            next_action=(
                "Run the streaming PECM transition operator on (14,5), then "
                "(16,6), without materializing the full target cache."
            ),
            source_reports=("post_exit_pecm_perron_extended.json",),
        )
    )


def _add_state_debt_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    worst = data.get("worst_constraint_state") or {}
    evidence = [
        f"LP success: {bool(data.get('lp_success'))}",
        f"epsilon: {data.get('epsilon')}",
        f"constraints: {_fmt_int(data.get('reentry_constraints', 0))}",
    ]
    if worst:
        evidence.append(
            "worst edge: "
            f"R {worst.get('source', {}).get('R')} -> {worst.get('target', {}).get('R')}, "
            f"steps={worst.get('steps')}, total_A={worst.get('total_A')}, "
            f"D_PE={worst.get('D_PE')}"
        )
    items.append(
        FrontierItem(
            priority=2,
            name="Promote finite state-debt certificate",
            status=str(data.get("status", "state_debt_status_unknown")),
            evidence=tuple(evidence),
            next_action=(
                "Replace the finite bucketed debt LP with exact symbolic "
                "inequalities: rational buckets, continued-fraction debt "
                "floors, and an explicit recurrence-state convention."
            ),
            source_reports=("unified_lyapunov_state_debt.json",),
        )
    )


def _add_dpe_cf_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    levels = data.get("levels") or []
    if not levels:
        return
    best = min(
        levels,
        key=lambda level: float(level.get("min_observed_gap") or float("inf")),
    )
    evidence = (
        f"best level: ({best.get('mod2_power')},{best.get('mod3_power')})",
        f"min observed gap: {best.get('min_observed_gap')}",
        f"observed/CF ratio: {best.get('min_observed_to_cf_ratio')}",
        f"convergent edges: {_fmt_int(best.get('convergent_edge_count', 0))}",
    )
    items.append(
        FrontierItem(
            priority=3,
            name="D_PE continued-fraction realizability theorem",
            status=str(data.get("status", "cf_certification_finite")),
            evidence=evidence,
            next_action=(
                "Turn the observed PECM debt floor into a theorem by combining "
                "continued-fraction separation from log2(3) with exact "
                "realizability constraints on post-exit cylinders."
            ),
            source_reports=("d_pe_continued_fraction_certification.json",),
        )
    )


def _add_chang_foster_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    evidence = (
        f"k<=8 Foster at m=16, eps=0.1: "
        f"{bool(data.get('foster_holds_at_chang_resolution_m16_eps_0p1'))}",
        f"obstructions at max m: {data.get('obstruction_count_at_max_m')}",
        str(data.get("cross_check_status", "no_cross_check_status")),
    )
    items.append(
        FrontierItem(
            priority=4,
            name="Chang/Tao pointwise bridge",
            status="distributional_to_pointwise_gap",
            evidence=evidence,
            next_action=(
                "Instrument deterministic orbit-level bit-balance against the "
                "PECM renewal classes; search for persistent exceptional "
                "families that evade the residue-Markov Foster drift."
            ),
            source_reports=("m_step_foster_drift_k8.json",),
        )
    )


def _add_christoffel_scaling_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    deferred = data.get("deferred_levels") or []
    if not deferred:
        return
    first = deferred[0]
    evidence = (
        f"classifications: {data.get('classification_counts')}",
        f"deferred ({first.get('tail_unit_power')},{first.get('max_tail_depth')}): "
        f"{first.get('bound')}",
        str(first.get("suggested_next_run")),
    )
    items.append(
        FrontierItem(
            priority=5,
            name="Memory-bounded Christoffel/Karp scaling",
            status=str(first.get("reason", "deferred_scaling")),
            evidence=evidence,
            next_action=(
                "Rewrite the product-graph cycle audit as a memory-bounded "
                "Karp/DFS pass so the Hercher-style integrality filter can be "
                "tested beyond the current memory wall."
            ),
            source_reports=("tail_cycle_realizability_extended_deep.json",),
        )
    )


def _add_finite_to_infinite_item(
    items: list[FrontierItem],
    data: dict[str, Any] | None,
) -> None:
    if not data:
        return
    observations = data.get("observations") or []
    evidence = tuple(
        f"{obs.get('name')}: {obs.get('next_test')}"
        for obs in observations[:3]
    )
    items.append(
        FrontierItem(
            priority=6,
            name="Finite-to-infinite falsifier",
            status=str(data.get("status", "finite_bridge_status_unknown")),
            evidence=evidence,
            next_action=str(data.get("falsifiable_next_step", "")),
            source_reports=("finite_to_infinite_bridge_audit.json",),
        )
    )


def frontier_dashboard_report(
    reports_dir: str | Path = "docs/reports",
) -> FrontierDashboardReport:
    """Rank the next proof-search work from saved JSON artifacts."""

    reports_path = Path(reports_dir)
    missing: list[str] = []
    loaded: dict[str, dict[str, Any] | None] = {}
    for name in (
        "post_exit_pecm_perron_extended.json",
        "unified_lyapunov_state_debt.json",
        "d_pe_continued_fraction_certification.json",
        "m_step_foster_drift_k8.json",
        "tail_cycle_realizability_extended_deep.json",
        "finite_to_infinite_bridge_audit.json",
    ):
        data, missing_path = _load_report(reports_path, name)
        loaded[name] = data
        if missing_path is not None:
            missing.append(missing_path)

    items: list[FrontierItem] = []
    _add_compressed_operator_item(items, loaded["post_exit_pecm_perron_extended.json"])
    _add_state_debt_item(items, loaded["unified_lyapunov_state_debt.json"])
    _add_dpe_cf_item(items, loaded["d_pe_continued_fraction_certification.json"])
    _add_chang_foster_item(items, loaded["m_step_foster_drift_k8.json"])
    _add_christoffel_scaling_item(items, loaded["tail_cycle_realizability_extended_deep.json"])
    _add_finite_to_infinite_item(items, loaded["finite_to_infinite_bridge_audit.json"])
    items.sort(key=lambda item: item.priority)

    status = "frontier_items_ranked" if items else "no_frontier_items_available"
    if missing:
        status += "_with_missing_reports"
    return FrontierDashboardReport(
        type="frontier_dashboard",
        status=status,
        reports_dir=str(reports_path),
        items=tuple(items),
        missing_reports=tuple(missing),
    )


def format_frontier_dashboard_report(report: FrontierDashboardReport) -> str:
    lines = [
        f"frontier dashboard: {report.status}",
        f"reports_dir={report.reports_dir}",
    ]
    if report.missing_reports:
        lines.append("missing_reports=" + ", ".join(report.missing_reports))
    for item in report.items:
        lines.append("")
        lines.append(f"{item.priority}. {item.name} [{item.status}]")
        for evidence in item.evidence:
            lines.append(f"   evidence: {evidence}")
        lines.append(f"   next: {item.next_action}")
        lines.append(f"   sources: {', '.join(item.source_reports)}")
    return "\n".join(lines)
