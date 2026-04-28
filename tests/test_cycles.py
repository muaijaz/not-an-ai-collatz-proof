from collatz_exp.cycles import (
    classify_cycle_word,
    scan_cycle_words,
    scan_near_balanced_cycles,
)


def test_cycle_classifier_checklist():
    assert classify_cycle_word((2,)).kind == "positive_integer_cycle"
    assert classify_cycle_word((1,)).kind == "negative_integer_cycle"
    assert classify_cycle_word((3,)).kind == "noninteger_2adic_only"


def test_cycle_scan_separates_trivial_from_nontrivial_positive_cycles():
    report = scan_cycle_words(((2,), (1,), (1, 2)))
    assert len(report.positive_integer_cycles) == 1
    assert len(report.nontrivial_positive_integer_cycles) == 0
    assert report.by_kind["positive_integer_cycle"] == 1


def test_near_balanced_cycle_smoke_scan():
    report = scan_near_balanced_cycles(m_max=4, valuation_max=5, slack=1)
    assert report.words_scanned > 0
    assert len(report.nontrivial_positive_integer_cycles) == 0
