import math

from collatz_exp.jazz_constant import (
    jazz_constant_closed_form_report,
    jazz_constant_decomposition_report,
)


def test_jazz_constant_closed_form_report_smoke():
    report = jazz_constant_closed_form_report(horizons=(10,), max_exact_fft_length=100_000)
    assert report.type == "jazz_constant_closed_form_test"
    assert math.isclose(report.candidate_value, math.log(4.0 / 3.0) ** 2)
    assert report.tail_comparisons
    assert report.absolute_difference > 0


def test_jazz_constant_decomposition_report_smoke():
    report = jazz_constant_decomposition_report()
    assert report.type == "jazz_constant_spike_decomposition"
    assert report.spike_contributions
    assert report.dominant_segment == "1"
    assert report.dominant_segment_percent_of_mgf > 50.0
    assert report.heavy_tail_correction > 0
