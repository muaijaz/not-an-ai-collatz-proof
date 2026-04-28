from collatz_exp.hercher import hercher_t_ni_report
from collatz_exp.paparella import paparella_nilpotency_report


def test_hercher_t_ni_smoke():
    report = hercher_t_ni_report(
        sample_count=20,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_steps_per_orbit=1000,
    )
    assert report.type == "hercher_t_ni_reciprocal_sum_diagnostic"
    assert report.completed_orbits == 20
    assert report.local_minimum_segments > 0
    assert report.universal_bound_3_passes


def test_paparella_nilpotency_smoke():
    report = paparella_nilpotency_report(n_values=(16, 32), p_max=32)
    assert report.type == "paparella_nilpotency_trace_diagnostic"
    assert len(report.levels) == 2
    assert all(level.all_traces_zero for level in report.levels)
    assert all(level.nilpotent_by_escape_depth for level in report.levels)
