from collatz_exp.renewal_bootstrap import renewal_bootstrap_calibration_report


def test_renewal_bootstrap_calibration_smoke():
    report = renewal_bootstrap_calibration_report(
        sample_count=100,
        start_min=10**3,
        start_max=10**5,
        bootstrap_repetitions=10,
        random_seed=0,
        bootstrap_seed=1,
    )
    assert report.type == "renewal_bootstrap_calibration"
    assert report.total_excursions > 0
    assert len(report.bootstrap_intervals) == 4
    assert len(report.saddlepoint_tail_estimates) == 3
