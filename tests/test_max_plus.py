from collatz_exp.max_plus import max_plus_debt_report


def test_max_plus_debt_report_smoke():
    report = max_plus_debt_report(modulus_power=4, sample_lift_power=2)
    assert report.type == "truncated_max_plus_debt_cycle_mean"
    assert report.states == 8
    assert report.edges > 0
    assert report.max_cycle_mean_debt is not None
    assert report.witness_residue is not None
