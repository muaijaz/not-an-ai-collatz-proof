import math

from collatz_exp.chang_phantom_gain import (
    chang_R_K_identity_report,
    compute_chang_R_K,
)
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


def test_chang_R_K_identity_report_smoke():
    values = compute_chang_R_K(K_max=10)
    assert math.isclose(values[3], 0.01062031259014451)
    assert values[5] > 0.010
    report = chang_R_K_identity_report(
        K_max=10,
        comparison_K_max=12,
        target_renewal_excursions=1000,
        bootstrap_resamples=20,
        random_seed=0,
    )
    assert report["type"] == "jazz_constant_chang_R_K_identity"
    assert report["chang_R_K_values"]
    assert report["chang_sigma_R_K"]["sum_3_to_K_max"] > 0.0
    assert "j_renewal_high_precision" in report
    assert report["alternate_definitions"]["J_per_burst_end"]["sample_count"] >= 0
    assert report["verdict"] in {
        "identity_supported",
        "identity_supported_under_alternate_definition",
        "distinct_quantities_5_percent_gap_structural",
    }
