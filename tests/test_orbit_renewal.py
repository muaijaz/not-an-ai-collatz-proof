from collatz_exp.orbit_renewal import (
    orbit_renewal_descent_report,
    orbit_renewal_markov_cramer_report,
    orbit_renewal_n0_stability_report,
    orbit_renewal_per_k_mgf_report,
    orbit_renewal_spike_decomposition_report,
    renewal_drift_phase_decomposed_report,
    renewal_drift_phase_decomposed_n0_stability_report,
    renewal_drift_per_step_report,
)
from collatz_exp.orbit_renewal_tda import orbit_renewal_tda_report
from collatz_exp.valuation_mi import valuation_mi_lag_report


def test_orbit_renewal_descent_smoke():
    report = orbit_renewal_descent_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "orbit_renewal_descent"
    assert report.completed_orbits == 10
    assert report.total_excursions > 0


def test_renewal_drift_per_step_smoke():
    report = renewal_drift_per_step_report(
        sample_count=20,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        bootstrap_resamples=25,
        max_steps_per_orbit=1000,
    )
    assert report.type == "renewal_drift_per_step"
    assert report.total_excursions > 0
    assert report.mean_drift_per_step.estimate is not None
    assert report.mean_drift_per_step.ci_low is not None
    assert report.mean_valuation_per_step.estimate is not None
    assert report.verdict in {
        "both_consistent",
        "only_valuation_consistent",
        "only_drift_consistent",
        "neither_consistent",
    }


def test_renewal_drift_phase_decomposed_smoke():
    report = renewal_drift_phase_decomposed_report(
        sample_count=20,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        bootstrap_resamples=25,
        max_steps_per_orbit=1000,
    )
    assert report.type == "renewal_drift_phase_decomposed"
    assert report.total_excursions > 0
    assert report.tail_internal_steps + report.post_exit_steps == (
        report.total_excursion_steps
    )
    assert report.tail_valuation_exact_check
    assert report.w_tail.estimate is not None
    assert report.mean_drift_per_step_post_exit.ci_low is not None
    assert report.verdict in {
        "phase_mixing_explains_deviation",
        "post_exit_drift_only_consistent",
        "post_exit_valuation_only_consistent",
        "neither_post_exit_consistent",
    }


def test_renewal_drift_phase_decomposed_n0_stability_smoke():
    report = renewal_drift_phase_decomposed_n0_stability_report(
        ranges=((101, 1000), (1001, 10_000), (10_001, 100_000)),
        sample_count_per_range=10,
        random_seed=1,
        bootstrap_resamples=25,
        max_steps_per_orbit=1000,
    )
    assert report.type == "renewal_drift_phase_decomposed_n0_stability"
    assert len(report.range_reports) == 3
    assert report.range_reports[0].total_excursions > 0
    assert report.post_exit_valuation_deviations
    assert report.total_drift_deviations
    assert report.verdict in {
        "asymptotic_identity_supported",
        "converging_but_not_yet_at_target",
        "non_monotone_or_flat",
        "diverging",
    }


def test_orbit_renewal_spike_decomposition_smoke():
    report = orbit_renewal_spike_decomposition_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
        histogram_bin_width=0.01,
    )
    assert report.type == "orbit_renewal_spike_decomposition"
    assert report.completed_orbits == 10
    assert report.total_excursions > 0
    assert report.cramer_rate_method == "positive_tail_mgf_histogram_golden_section"
    assert report.segments


def test_orbit_renewal_per_k_mgf_smoke():
    report = orbit_renewal_per_k_mgf_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "orbit_renewal_per_k_mgf"
    assert report.completed_orbits == 10
    assert report.total_excursions > 0
    assert report.aggregate_mgf_positive_tail
    assert report.segments


def test_orbit_renewal_tda_smoke_without_ripser():
    report = orbit_renewal_tda_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
        max_points=50,
        null_replicates=1,
        run_tda=False,
    )
    assert report.type == "orbit_renewal_tda"
    assert report.completed_orbits == 10
    assert report.total_excursions > 0
    assert report.r_drop_h1.status == "tda_not_requested"


def test_orbit_renewal_markov_cramer_smoke():
    report = orbit_renewal_markov_cramer_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "orbit_renewal_markov_cramer"
    assert report.completed_orbits == 10
    assert report.total_excursions > 0
    assert report.markov_pairs > 0
    assert report.lambda_reports
    assert report.transition_reports


def test_orbit_renewal_n0_stability_smoke():
    report = orbit_renewal_n0_stability_report(
        sample_count_per_range=5,
        ranges=((101, 1000), (1001, 10_000)),
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "orbit_renewal_n0_stability"
    assert len(report.range_reports) == 2
    assert report.range_reports[0].total_excursions > 0


def test_valuation_mi_lag_report_smoke():
    report = valuation_mi_lag_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
        max_lag=4,
    )
    assert report.type == "valuation_mi_lags"
    assert report.completed_orbits == 10
    assert report.total_accelerated_steps > 0
    assert len(report.lag_reports) == 4
