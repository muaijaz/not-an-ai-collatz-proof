from collatz_exp.cf_convergent_slope import (
    cf_convergent_slope_hypothesis_report,
    continued_fraction_convergents_log2_3,
)


def test_log2_3_convergents_include_elementary_collatz_slope():
    convergents = continued_fraction_convergents_log2_3(6)
    fractions = {item["fraction"] for item in convergents}
    assert "2/1" in fractions
    assert "3/2" in fractions


def test_cf_slope_hypothesis_report_classifies_8_7_obstruction():
    report = cf_convergent_slope_hypothesis_report()
    obstruction = next(
        cycle for cycle in report.cycles if cycle["valuation_word"] == [2, 1, 1, 1]
    )
    assert obstruction["level"] == [8, 7]
    assert obstruction["classification"] == "noninteger_2adic_only"
    assert obstruction["slope_A_over_m"] == "5/4"
    assert obstruction["non_convergent_rational"]


def test_cf_slope_hypothesis_is_partially_supported_on_current_artifacts():
    report = cf_convergent_slope_hypothesis_report()
    assert report.verdict == "cf_convergent_hypothesis_partially_supported"
    assert report.hypothesis_tests["hypothesis_supported_at_(5,4)..(7,6)"]
    assert not report.hypothesis_tests["hypothesis_supported_at_(8,7)"]
    assert report.hypothesis_tests[
        "high_growth_obstruction_variant_supported_at_(8,7)"
    ]
