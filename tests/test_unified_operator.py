from collatz_exp.unified_operator import (
    mori_mixed_first_return_report,
    unified_collatz_operator_report,
)


def test_unified_operator_smoke():
    report = unified_collatz_operator_report(
        dyadic_powers=(4, 5),
        paparella_n_values=(16, 32),
    )
    assert report.type == "unified_collatz_operator_finite_projection"
    assert len(report.dyadic_levels) == 2
    assert len(report.paparella_levels) == 2
    assert all(level.dimension == 1 << level.modulus_power for level in report.dyadic_levels)
    assert all(not level.nontrivial_cycle_found for level in report.paparella_levels)


def test_mori_mixed_first_return_smoke():
    report = mori_mixed_first_return_report(
        levels=((3, 2), (4, 2)),
        lift_power=1,
        max_return_steps=50,
    )
    assert report.type == "mori_mixed_first_return_operator"
    assert len(report.levels) == 2
    assert all(level.row_sum_min == 1.0 for level in report.levels)
    assert all(level.unresolved_lifts == 0 for level in report.levels)
    assert report.levels[0].dimension == 32
