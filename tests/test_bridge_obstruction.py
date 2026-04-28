from pathlib import Path

from collatz_exp.bridge_obstruction import (
    finite_to_infinite_bridge_audit,
    mersenne_post_run_report,
)


def test_mersenne_post_run_report_records_descent_rows():
    report = mersenne_post_run_report(sample_R=(32, 40))
    assert report.type == "mersenne_post_run_descent"
    assert len(report.samples) == 2
    assert all(sample.landing_below_start for sample in report.samples)
    assert report.samples[0].post_run_steps_to_descent == 38
    assert report.samples[0].post_run_valuation_to_descent == 79


def test_bridge_audit_names_missing_implication():
    report = finite_to_infinite_bridge_audit(Path("docs/reports"))
    assert report.type == "finite_to_infinite_bridge_audit"
    assert report.observations
    assert any(
        observation.name == "mersenne_bypass_vs_post_run"
        for observation in report.observations
    )
    assert "infinite compatible tail schedule" in report.candidate_bridge_statement
