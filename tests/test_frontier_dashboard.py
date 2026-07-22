import json

from collatz_exp.frontier_dashboard import (
    format_frontier_dashboard_report,
    frontier_dashboard_report,
)


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_frontier_dashboard_ranks_saved_artifact_gates(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    _write_json(
        reports / "post_exit_pecm_perron_extended.json",
        {
            "status": "extended_levels_require_compressed_or_distributed_operator",
            "requested_extended_levels": [
                {
                    "mod2_power": 14,
                    "mod3_power": 5,
                    "states": 1000,
                    "sample_transitions": 4000,
                    "target_cache_gib_int32": 0.1,
                }
            ],
        },
    )
    _write_json(
        reports / "unified_lyapunov_state_debt.json",
        {
            "status": "finite_bucketed_state_debt_lyapunov_feasible_not_global_proof",
            "lp_success": True,
            "epsilon": 0.3,
            "reentry_constraints": 12,
            "worst_constraint_state": {
                "source": {"R": 11},
                "target": {"R": 2},
                "steps": 2,
                "total_A": 19,
                "D_PE": -0.01955,
            },
        },
    )
    _write_json(
        reports / "d_pe_continued_fraction_certification.json",
        {
            "status": "finite_cf_certificate",
            "levels": [
                {
                    "mod2_power": 8,
                    "mod3_power": 3,
                    "min_observed_gap": 0.01955,
                    "min_observed_to_cf_ratio": 1.036,
                    "convergent_edge_count": 613,
                }
            ],
        },
    )
    _write_json(
        reports / "m_step_foster_drift_k8.json",
        {
            "foster_holds_at_chang_resolution_m16_eps_0p1": True,
            "obstruction_count_at_max_m": 0,
            "cross_check_status": "compared",
        },
    )
    _write_json(
        reports / "tail_cycle_realizability_extended_deep.json",
        {
            "classification_counts": {"noninteger_2adic_only": 3},
            "deferred_levels": [
                {
                    "tail_unit_power": 9,
                    "max_tail_depth": 8,
                    "bound": "memory_bound",
                    "reason": "memory pressure",
                    "suggested_next_run": "stream it",
                }
            ],
        },
    )
    _write_json(
        reports / "finite_to_infinite_bridge_audit.json",
        {
            "status": "finite_obstruction_ledger_no_global_arithmetic_step",
            "falsifiable_next_step": "search compatible product paths",
            "observations": [{"name": "split", "next_test": "track exits"}],
        },
    )

    report = frontier_dashboard_report(reports)

    assert report.type == "frontier_dashboard"
    assert report.status == "frontier_items_ranked"
    assert [item.priority for item in report.items] == [1, 2, 3, 4, 5, 6]
    assert report.items[0].name == "Compressed PECM operator scaling"
    assert "state-debt" in report.items[1].name
    assert not report.missing_reports
    assert "frontier dashboard" in format_frontier_dashboard_report(report)


def test_frontier_dashboard_reports_missing_artifacts(tmp_path):
    report = frontier_dashboard_report(tmp_path)

    assert report.status == "no_frontier_items_available_with_missing_reports"
    assert len(report.missing_reports) == 6
