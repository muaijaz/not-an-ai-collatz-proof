from collatz_exp.post_exit_baker import (
    baker_lower_bound,
    dpe_baker_certification_report,
    dpe_continued_fraction_certification_report,
    dpe_convergent_atlas_report,
    continued_fraction_lower_bound,
    realizability_structural_exclusion_report,
)


def test_baker_lower_bound_smoke():
    bound = baker_lower_bound(12, 19)
    assert bound > 0.0
    assert bound < abs(19 - 12 * 1.58)


def test_dpe_baker_certification_smoke():
    report = dpe_baker_certification_report(
        configurations=((4, 2),),
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
    )
    assert report.type == "d_pe_baker_certification"
    assert len(report.levels) == 1
    assert report.levels[0].reentry_edges > 0
    assert report.levels[0].min_observed_to_baker_ratio is not None


def test_dpe_convergent_atlas_smoke():
    report = dpe_convergent_atlas_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        max_denominator=50,
    )
    assert report.type == "d_pe_convergent_atlas"
    assert any(entry.A == 19 and entry.m == 12 for entry in report.entries)


def test_continued_fraction_bound_is_sharp_for_19_12():
    bound, relation, reference = continued_fraction_lower_bound(
        12,
        19,
        max_denominator=1000,
    )
    assert relation == "convergent"
    assert reference == "19/12"
    assert 0.018 < bound < 0.019


def test_dpe_continued_fraction_certification_smoke():
    report = dpe_continued_fraction_certification_report(
        configurations=((4, 2),),
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        max_denominator=1000,
    )
    assert report.type == "d_pe_continued_fraction_certification"
    assert len(report.levels) == 1
    assert report.levels[0].min_observed_to_cf_ratio is not None


def test_realizability_structural_exclusion_smoke():
    report = realizability_structural_exclusion_report(
        mod2_power=4,
        mod3_power=2,
        R_values=(2, 3, 4),
        sample_lift_power=1,
        max_steps=50,
        targets=((19, 12),),
    )
    assert report.type == "realizability_structural_exclusion"
    assert report.targets[0].candidates_checked > 0
