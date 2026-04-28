from collatz_exp.lift_realizability import (
    exact_word_closures_mod_power,
    lift_realizability_report,
    quotient_closed_words,
    word_cylinder_residues,
)


def test_word_cylinder_residues_detects_exact_all_ones():
    assert word_cylinder_residues((1,), precision_power=2) == (3,)
    assert word_cylinder_residues((1, 1), precision_power=3) == (7,)
    assert word_cylinder_residues((2,), precision_power=3) == (1,)


def test_exact_word_closure_separates_quotient_from_integer_cycle():
    closings = exact_word_closures_mod_power((1,), modulus_power=4)
    assert 31 in closings
    assert all(residue % 16 == 15 for residue in closings)
    assert exact_word_closures_mod_power((2,), modulus_power=4, precision_power=3) == (1,)


def test_quotient_closed_words_and_report_smoke():
    words = quotient_closed_words(
        modulus_power=4,
        max_valuation=4,
        max_period=4,
        max_words=20,
    )
    assert words
    report = lift_realizability_report(
        modulus_power=4,
        max_valuation=4,
        max_period=4,
        top_n=4,
    )
    assert report.type == "quotient_cycle_lift_realizability"
    assert report.quotient_words_found >= len(report.checks)
    assert len(report.checks) <= 4
    assert report.checks[0].cycle_classification
