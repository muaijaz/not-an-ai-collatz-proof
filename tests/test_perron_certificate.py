import json
from fractions import Fraction

from collatz_exp.perron_certificate import (
    certify_level,
    format_perron_certificate_report,
    perron_certificate_report,
)


def test_certify_tiny_level_contraction():
    level = certify_level(4, 1, R_values=(2, 3, 4), power_iterations=100)
    assert level.states == 72
    assert level.certified_contraction
    bound = Fraction(
        int(level.certified_upper_numerator),
        int(level.certified_upper_denominator),
    )
    assert 0 < bound < 1
    # The certified upper bound must dominate the float Perron estimate.
    assert float(bound) >= level.float_scale_estimate - 1e-9


def test_certify_level_8_2_matches_float_scale():
    level = certify_level(8, 2, power_iterations=200)
    assert level.certified_contraction
    assert level.certified_block_count >= 1
    assert level.largest_block_states >= 1
    # Bound should be tight: within 1e-3 of the float estimate.
    assert abs(level.certified_upper_float - level.float_scale_estimate) < 1e-3
    assert level.worst_row_state is not None


def test_certificate_report_json_round_trip():
    report = perron_certificate_report(
        configurations=((4, 1),),
        R_values=(2, 3, 4),
        power_iterations=50,
    )
    payload = json.loads(report.to_json())
    assert payload["configurations"] == [[4, 1]]
    assert len(payload["levels"]) == 1
    level = payload["levels"][0]
    assert level["certified_contraction"] is True
    text = format_perron_certificate_report(report)
    assert "certified_upper" in text
    assert "contraction=True" in text


def test_certificate_deterministic():
    first = perron_certificate_report(
        configurations=((4, 1),), R_values=(2, 3, 4), power_iterations=50
    )
    second = perron_certificate_report(
        configurations=((4, 1),), R_values=(2, 3, 4), power_iterations=50
    )
    assert first.to_json() == second.to_json()
