from collatz_exp.squeeze_bounds import rigorous_squeeze_report


def test_rigorous_squeeze_report_smoke():
    report = rigorous_squeeze_report()
    assert report.type == "rigorous_bound_squeeze"
    assert len(report.entries) >= 6
    names = {entry.name for entry in report.entries}
    assert "diophantine_gap_19_over_12" in names
    assert "renewal_mean_delta_log2" in names
    diophantine = next(
        entry for entry in report.entries if entry.name == "diophantine_gap_19_over_12"
    )
    assert diophantine.lower_bound < diophantine.empirical_value < diophantine.upper_bound
