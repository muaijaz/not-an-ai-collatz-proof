import json
import math

from collatz_exp.foster_drift import (
    CHANG_BIT4_BALANCE_CAVEAT,
    CHANG_BIT4_BALANCE_VERDICTS,
    FOSTER_DRIFT_CAVEAT,
    M_STEP_FOSTER_DRIFT_CAVEAT,
    M_STEP_VERDICTS,
    POINTWISE_DESCENT_CAVEAT,
    POINTWISE_DESCENT_VERDICTS,
    VERDICTS,
    chang_bit4_balance_audit_report,
    foster_drift_report,
    m_step_foster_drift_k8_report,
    m_step_foster_drift_report,
    pointwise_descent_audit_report,
)
from collatz_exp.orbit_lyapunov import orbit_lyapunov_beta_sweep_report
from collatz_exp.phase_lyapunov import (
    LOG2_3_OVER_2,
    PhaseLyapunovParams,
    collect_phase_lyapunov_orbits,
    evaluate_phase_lyapunov,
    phase_lyapunov_search_report,
    search_phase_lyapunov,
)


def _assert_ci_halfwidths_finite(value):
    if isinstance(value, dict):
        if "ci_halfwidth" in value:
            halfwidth = value["ci_halfwidth"]
            assert halfwidth is not None, "CI half-width should be recorded"
            assert math.isfinite(halfwidth), "CI half-width should be finite"
            assert halfwidth >= 0.0, "CI half-width should be non-negative"
        for child in value.values():
            _assert_ci_halfwidths_finite(child)
    elif isinstance(value, list):
        for child in value:
            _assert_ci_halfwidths_finite(child)


def test_orbit_lyapunov_beta_sweep_smoke():
    report = orbit_lyapunov_beta_sweep_report(
        sample_count=10,
        beta_values=(1.0, 2.0),
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "actual_orbit_lyapunov_beta_sweep"
    assert report.completed_orbits == 10
    assert report.total_accelerated_steps > 0
    assert len(report.results) == 4


def test_phase_lyapunov_search_smoke():
    report = phase_lyapunov_search_report(
        sample_count=12,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
        alpha_grid=(0.0, LOG2_3_OVER_2),
        beta_grid=(0.0, 16.0),
        gamma_diff_grid=(-0.5, 0.0),
    )
    assert report.type == "phase_lyapunov_search"
    assert report.completed_orbits == 12
    assert report.total_accelerated_steps > 0
    assert report.grid_candidates_evaluated == 8
    assert report.V5_baseline.total.fraction_nondecrease is not None
    assert report.best_grid_candidate.total.fraction_nondecrease is not None
    assert len(report.worst_positive_events) <= 5


def test_phase_lyapunov_evaluate_and_search_shape():
    sample = collect_phase_lyapunov_orbits(
        sample_count=4,
        start_min=101,
        start_max=1000,
        random_seed=2,
        max_steps_per_orbit=500,
    )
    evaluated = evaluate_phase_lyapunov(
        sample,
        PhaseLyapunovParams(alpha=LOG2_3_OVER_2, beta=0.0, gamma_diff=0.0),
    )
    assert evaluated["total"]["total_steps"] == sample.total_accelerated_steps
    assert set(evaluated["phases"]) == {"tail_internal", "post_exit"}

    search = search_phase_lyapunov(
        sample,
        alpha_grid=(0.0, LOG2_3_OVER_2),
        beta_grid=(0.0,),
        gamma_diff_grid=(0.0,),
    )
    assert search["grid_candidates_evaluated"] == 2
    assert search["best"]["total"]["total_steps"] == sample.total_accelerated_steps


def test_foster_drift_smoke_artifact_shape():
    report = foster_drift_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=1000,
        residue_powers=(2, 3),
        tail_thresholds=(0.5, 1.0, 2.0),
        hitting_time_max_steps=1000,
        hitting_time_threshold=1.0,
        bootstrap_resamples=100,
        random_seed=0,
    )
    assert report["type"] == "phase_lyapunov_foster_drift"
    assert report["caveat"] == FOSTER_DRIFT_CAVEAT
    assert report["verdict"] in VERDICTS
    for key in (
        "definitions",
        "references",
        "numerics",
        "window_reports",
        "drift_residuals",
        "uniform_negative_drift",
        "uniform_negative_drift_by_residue",
        "uniform_subexponential_tail",
        "residue_obstruction_witnesses",
        "window_obstruction_witnesses",
    ):
        assert key in report
    assert report["window_reports"][0]["seeds"]["sample_seed"] == 101
    assert report["window_reports"][0]["distinct_draws"] > 0
    _assert_ci_halfwidths_finite(report)
    json.dumps(report, allow_nan=False)


def test_m_step_foster_drift_smoke_artifact_shape():
    report = m_step_foster_drift_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=1000,
        residue_powers=(2, 3),
        m_steps_grid=(1, 2, 4),
        foster_epsilon=0.1,
        random_seed=0,
    )
    assert report["type"] == "m_step_foster_drift"
    assert report["caveat"] == M_STEP_FOSTER_DRIFT_CAVEAT
    assert report["verdict"] in M_STEP_VERDICTS
    for key in (
        "definitions",
        "references",
        "numerics",
        "window_reports",
        "smallest_m_uniform_negative_drift_by_residue",
        "smallest_m_uniform_negative_drift_by_residue_eps_0p1",
        "smallest_m_uniform_negative_marginal_drift",
        "m_step_drift_residual_table",
        "residue_obstruction_witnesses_at_smallest_m",
        "m1_cross_check_passes",
        "m1_max_disagreement",
    ):
        assert key in report
    assert report["m_steps_grid"][0] == 1
    assert report["window_reports"][0]["seeds"]["sample_seed"] == 101
    assert report["m1_cross_check_passes"] is True
    _assert_ci_halfwidths_finite(report)
    json.dumps(report, allow_nan=False)


def test_m_step_foster_drift_k8_smoke_artifact_shape(tmp_path):
    reference = m_step_foster_drift_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=1000,
        residue_powers=(2, 3, 4, 5, 6),
        m_steps_grid=(1, 2, 4),
        foster_epsilon=0.1,
        random_seed=0,
    )
    reference_path = tmp_path / "m_step_foster_drift.json"
    reference_path.write_text(json.dumps(reference, sort_keys=True) + "\n")
    report = m_step_foster_drift_k8_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=1000,
        residue_powers=(2, 3, 4, 5, 6, 7, 8),
        m_steps_grid=(1, 2, 4),
        foster_epsilon=0.1,
        random_seed=0,
        cross_check_reference_path=str(reference_path),
    )
    assert report["type"] == "m_step_foster_drift_k8"
    assert report["caveat"] == M_STEP_FOSTER_DRIFT_CAVEAT
    assert report["verdict"] in M_STEP_VERDICTS
    assert report["residue_powers"] == [2, 3, 4, 5, 6, 7, 8]
    assert report["cross_check_against_k_le_6_passes"] is True
    assert report["cross_check_max_disagreement"] == 0.0
    assert report["foster_holds_at_chang_resolution_m16_eps_0p1"] in (True, False)
    assert report["chang_resolution"]["fiber_refinement_power_256"] == 8
    assert report["window_reports"][0]["seeds"]["sample_seed"] == 101
    _assert_ci_halfwidths_finite(report)
    json.dumps(report, allow_nan=False)


def test_pointwise_descent_audit_smoke_artifact_shape():
    report = pointwise_descent_audit_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=250,
        m_max_values=(10, 100),
        random_seed=0,
    )
    assert report["type"] == "pointwise_descent_audit"
    assert report["caveat"] == POINTWISE_DESCENT_CAVEAT
    assert report["verdict"] in POINTWISE_DESCENT_VERDICTS
    for key in (
        "definitions",
        "references",
        "numerics",
        "window_reports",
        "largest_t_descent_observed",
        "largest_t_descent_witness",
        "offending_witness",
        "cross_window_scaling",
        "all_windows_empirical_uniform_bound",
    ):
        assert key in report
    window = report["window_reports"][0]
    assert window["seeds"]["sample_seed"] == 101
    assert window["m_max_values"] == [10, 100]
    assert set(window["truncation_counts_by_m_max"]) == {"10", "100"}
    dist = window["hitting_time_distribution"]
    for key in (
        "min",
        "mean",
        "median",
        "quantile_0_99",
        "quantile_0_999",
        "quantile_0_9999",
        "quantile_0_99999",
        "max",
    ):
        assert key in dist
    witness = report["offending_witness"]
    assert witness is None or {"n", "R", "n_mod_64", "status"} <= set(witness)
    json.dumps(report, allow_nan=False)


def test_chang_bit4_balance_audit_smoke_artifact_shape():
    report = chang_bit4_balance_audit_report(
        ranges=((10**4, 10**6),),
        sample_count_per_range=250,
        random_seed=0,
        bootstrap_resamples=8,
        max_steps_per_orbit=1000,
    )
    assert report["type"] == "chang_bit4_balance_audit"
    assert report["caveat"] == CHANG_BIT4_BALANCE_CAVEAT
    assert report["verdict"] in CHANG_BIT4_BALANCE_VERDICTS
    for key in (
        "definitions",
        "references",
        "numerics",
        "foster_rate_reference",
        "window_reports",
        "empirical_max_delta_at_window",
        "empirical_max_delta_decreasing_with_window",
        "foster_rate_envelope_holds",
        "global_max_delta_witness",
    ):
        assert key in report
    window = report["window_reports"][0]
    assert window["seeds"]["sample_seed"] == 101
    assert window["seeds"]["bootstrap_seed"] == 404
    assert window["sample_count"] == 250
    assert window["defined_delta_orbits"] + window["zero_denominator_orbits"] == 250
    for key in (
        "mean",
        "median",
        "quantile_0_99",
        "max",
        "mean_ci",
        "median_ci",
        "quantile_0_99_ci",
    ):
        assert key in window["delta_distribution"]
    assert "median" in window["chang_m_distribution"]
    assert window["delta_by_orbit_length_T_quantile"]
    witness = report["global_max_delta_witness"]
    assert witness is None or {"start", "chang_m", "delta"} <= set(witness)
    json.dumps(report, allow_nan=False)
