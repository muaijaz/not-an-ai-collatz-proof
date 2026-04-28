from collatz_exp.orbit_renewal import (
    orbit_renewal_descent_report,
    orbit_renewal_markov_cramer_report,
    orbit_renewal_n0_stability_report,
    orbit_renewal_per_k_mgf_report,
    orbit_renewal_spike_decomposition_report,
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
