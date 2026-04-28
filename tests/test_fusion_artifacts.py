from collatz_exp.cohomology_tower import cohomology_tower_report
from collatz_exp.cycle_tower import cycle_exclusion_tower_report
from collatz_exp.spectral_fingerprint import spectral_fingerprint_report


def test_cycle_exclusion_tower_smoke():
    report = cycle_exclusion_tower_report(
        max_m=5,
        valuation_max=4,
        lift_modulus_power=4,
        lift_max_period=4,
    )
    assert report.type == "cycle_exclusion_tower"
    assert report.words_scanned > 0
    assert report.lattice.words_scanned > 0
    assert report.lift_realizability.checks


def test_cohomology_tower_smoke():
    report = cohomology_tower_report(k_min=4, k_max=5, sample_lift_power=2)
    assert report.type == "profinite_cohomology_sandpile_tower"
    assert len(report.levels) == 2
    assert report.levels[-1].vertices >= report.levels[0].vertices
    assert report.levels[-1].sandpile_forest_count >= 1


def test_spectral_fingerprint_smoke():
    report = spectral_fingerprint_report(k_min=4, k_max=5, sample_lift_power=2)
    assert report.type == "mixed_spectral_fingerprint"
    assert len(report.levels) == 2
    assert report.levels[0].transfer_second_abs is None or report.levels[0].transfer_second_abs >= 0
    assert report.levels[-1].harmonic_dimension >= 0
