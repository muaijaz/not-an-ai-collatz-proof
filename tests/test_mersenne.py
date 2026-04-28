from collatz_exp.mersenne import (
    analyze_mersenne_tails,
    classify_mersenne_tail_cylinder,
    discharge_mersenne_tail_cylinder,
    initial_mersenne_run,
    mersenne_tail_defect,
    profile_mersenne,
    representative_descent_from_cylinder,
    verify_initial_mersenne_run,
)
from collatz_exp.cover import CoverFrontierNode, run_certificate_cover


def test_initial_mersenne_run_formula():
    run = initial_mersenne_run(32)
    assert run.run_length == 31
    assert run.post_run_value == 2 * 3**31 - 1
    assert run.next_valuation == 8
    assert verify_initial_mersenne_run(32)


def test_mersenne_profiles_reproduce_handoff_rows():
    expected = {
        32: (38, 79),
        40: (36, 80),
        56: (28, 77),
        64: (64, 141),
        72: (98, 198),
        80: (62, 145),
        88: (151, 296),
        90: (155, 298),
    }
    for R, row in expected.items():
        profile = profile_mersenne(R)
        assert (profile.post_run_steps, profile.post_run_valuation) == row
        assert profile.landing < (1 << R) - 1
        assert profile.spikes


def test_mersenne_tail_defect_and_frontier_classification():
    node = CoverFrontierNode(residue=(1 << 16) - 1, modulus_power=16)
    tail = classify_mersenne_tail_cylinder(node)
    assert mersenne_tail_defect(node.residue, node.modulus_power) == 0
    assert tail.run_length == 15
    assert tail.m == 16
    assert tail.A == 22


def test_representative_descent_for_mersenne_tail():
    result = representative_descent_from_cylinder((1 << 16) - 1, 16)
    assert result is not None
    m, A, landing = result
    assert m > 0
    assert A > 0
    assert landing < (1 << 17) - 1


def test_mersenne_tail_report_from_cover_frontier():
    cover = run_certificate_cover(max_depth=16, max_nodes=20_000)
    report = analyze_mersenne_tails(
        cover,
        min_run_length=8,
        top_n=3,
        discharge_top_n=1,
        max_extra_bits=2,
    )
    assert report.type == "mersenne_tail_frontier_report"
    assert report.tail_classes > 0
    assert report.top_tails[0].run_length >= 8
    assert len(report.discharges) == 1


def test_discharge_attempt_is_honest_finite_artifact():
    node = CoverFrontierNode(residue=(1 << 16) - 1, modulus_power=16)
    discharge = discharge_mersenne_tail_cylinder(node, max_extra_bits=1)
    assert discharge.status in {
        "all_subcylinders_certified_at_extra_precision",
        "not_discharged_within_extra_precision",
    }
    assert discharge.subcylinders_checked >= discharge.subcylinders_certified
