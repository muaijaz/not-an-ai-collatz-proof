from collatz_exp.harmonic_class import harmonic_class_identification_report


def test_harmonic_class_identification_smoke():
    report = harmonic_class_identification_report(
        modulus_power=5,
        sample_lift_power=2,
    )
    assert report.type == "harmonic_class_identification"
    assert report.projected_residue == 27 % (1 << 5)
    assert report.harmonic_dimension == report.first_betti
    assert report.indicator_norm >= 0.0
