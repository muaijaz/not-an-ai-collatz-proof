from fractions import Fraction

from collatz_exp.tao_syrac import (
    tao_characteristic_decay_report,
    tao_syrac_distributions,
    tao_syrac_empirical_report,
)


def test_tao_syrac_distribution_smoke():
    distributions = tao_syrac_distributions(2)
    assert distributions[0] == [Fraction(1, 1)]
    assert sum(distributions[1]) == Fraction(1, 1)
    assert sum(distributions[2]) == Fraction(1, 1)
    assert len(distributions[2]) == 9


def test_tao_syrac_empirical_smoke():
    report = tao_syrac_empirical_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_n=3,
        max_steps_per_orbit=1000,
    )
    assert report.type == "tao_syrac_empirical"
    assert report.completed_orbits == 10
    assert len(report.level_reports) == 3
    assert report.level_reports[0].nth_iterate_samples == 10


def test_tao_characteristic_decay_smoke():
    report = tao_characteristic_decay_report(
        sample_count=10,
        start_min=101,
        start_max=10_000,
        random_seed=1,
        max_n=3,
    )
    assert report.type == "tao_characteristic_function_decay"
    assert len(report.level_reports) == 3
    assert report.level_reports[0].frequencies_checked == 2
