from collatz_exp.mixed_harmonic_class import (
    mixed_harmonic_class_report,
    obstruction_lyapunov_correction_report,
)


def test_mixed_harmonic_class_smoke():
    report = mixed_harmonic_class_report(
        mod2_power=4,
        mod3_power=2,
        sample_lift_power=1,
    )
    assert report.type == "mixed_harmonic_class_identification"
    assert report.vertices == 8 * 9
    assert report.harmonic_dimension == report.first_betti
    assert len(report.obstruction_vertices) == 1
    assert report.indicator_norm >= 0.0


def test_obstruction_lyapunov_correction_smoke():
    report = obstruction_lyapunov_correction_report(
        mod2_power=4,
        mod3_power=2,
        sample_lift_power=1,
        trajectory_samples=4,
    )
    assert report.type == "obstruction_lyapunov_correction"
    assert report.residual_norm >= 0.0
    assert report.trajectory_check.samples == 4
