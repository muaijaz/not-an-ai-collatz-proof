import json
from fractions import Fraction

import pytest

from collatz_exp.core import affine_from_word, apply_word
from collatz_exp.symbolic_branch_certificate import (
    CylinderBudgetExceeded,
    ExactBranch,
    ExactMixedCylinder,
    RationalDifferenceCertificate,
    exact_selected_cylinder_pilot_report,
    exact_word_residue,
    post_word_u_residue,
    solve_rational_difference_constraints,
    trace_post_exit_macro,
    verify_rational_difference_certificate,
)


def test_exact_word_residue_uses_the_final_valuation_bit():
    assert exact_word_residue((1,)) == (3, 2)
    assert exact_word_residue((2,)) == (1, 3)
    assert exact_word_residue((1, 1)) == (7, 3)
    assert post_word_u_residue(2, (2,)) == (3, 2)


def test_small_post_exit_stopping_order_and_precision_fixtures():
    reentry = trace_post_exit_macro(2, 7)
    assert reentry.status == "tail_reentry"
    assert reentry.post_word == (2,)
    assert reentry.full_word == (1, 2)
    assert reentry.n0 == 27
    assert reentry.landing == 31
    assert reentry.landing_tail_depth == 5
    reentry_affine = affine_from_word(reentry.full_word)
    assert (
        reentry_affine.A,
        reentry_affine.B,
        reentry_affine.m,
    ) == (3, 5, 2)

    descent = trace_post_exit_macro(2, 5)
    assert descent.status == "descended"
    assert descent.n0 == 19
    assert descent.landing == 11
    assert descent.landing_tail_depth == 2

    multi_step = trace_post_exit_macro(2, 3)
    assert multi_step.status == "descended"
    assert multi_step.post_word == (2, 3)
    assert multi_step.full_word == (1, 2, 3)
    assert multi_step.landing == 5


def test_reentry_event_precision_does_not_already_fix_target_precision():
    low = trace_post_exit_macro(2, 7)
    high = trace_post_exit_macro(2, 135)
    assert 7 % 128 == 135 % 128
    assert low.post_word == high.post_word == (2,)
    assert low.landing_tail_depth == high.landing_tail_depth == 5
    low_target_u = (low.landing + 1) >> low.landing_tail_depth
    high_target_u = (high.landing + 1) >> high.landing_tail_depth
    assert low_target_u % 4 == 1
    assert high_target_u % 4 == 3


def test_max_steps_is_an_unresolved_status_not_a_descent():
    trace = trace_post_exit_macro(2, 3, max_post_steps=1)
    assert trace.status == "max_steps_exceeded"
    assert trace.post_word == (2,)
    assert trace.landing == 13


def test_exact_word_residue_realizes_small_words_on_every_lift():
    words = (
        (1,),
        (2,),
        (3,),
        (1, 2),
        (2, 1),
        (1, 1, 2),
        (3, 2, 1),
    )
    for word in words:
        residue, power = exact_word_residue(word)
        modulus = 1 << power
        for lift in range(4):
            n = residue + lift * modulus
            assert apply_word(n, word) > 0


def test_adversarial_seed_has_the_exact_expanding_affine_word():
    trace = trace_post_exit_macro(9, 4151)
    assert trace.status == "tail_reentry"
    assert trace.post_word == (3, 2, 4)
    assert trace.full_word == (1,) * 8 + (3, 2, 4)
    assert trace.n0 == 2_125_311
    assert trace.landing == 2_872_411
    assert trace.landing_tail_depth == 2
    affine = affine_from_word(trace.full_word)
    assert (affine.m, affine.A, affine.B) == (11, 17, 186_875)
    assert 3**affine.m > 1 << affine.A
    assert exact_word_residue(trace.full_word) == (28_159, 18)
    assert apply_word(trace.n0, trace.full_word) == trace.landing


def test_exact_pilot_partitions_root_and_covers_the_target_fiber():
    report = exact_selected_cylinder_pilot_report()
    data = report.to_json_dict()
    assert report.status.endswith("open_frontier_not_global_proof")
    assert report.provenance["input_artifact_snapshot_match"] is True
    assert report.provenance["reported_max_ratio_match"] is True
    assert len(report.edges) == 128
    partition = data["root"]["partition"]
    assert partition["expected_child_count"] == 128
    assert partition["actual_child_count"] == 128
    assert partition["unique_child_count"] == 128
    assert partition["partition_verified"] is True
    assert partition["full_odd_2adic_target_fiber_covered"] is True

    targets = {
        (edge["target"]["u_mod2"], edge["target"]["u_mod3"])
        for edge in report.edges
    }
    assert targets == {(residue, 2) for residue in range(1, 256, 2)}
    witness = next(
        edge for edge in report.edges if edge["least_positive_u"] == "4151"
    )
    assert witness["source"]["u_mod2"] == 4151
    assert witness["target"]["u_mod2"] == 23
    assert witness["least_n"] == "2125311"
    assert witness["landing"] == "2872411"


def test_local_tail_cusp_candidate_is_exact_but_not_global():
    report = exact_selected_cylinder_pilot_report()
    candidate = report.symbolic_candidate
    assert candidate["tail_base"] == {"numerator": "23", "denominator": "22"}
    local_lambda = Fraction(
        int(candidate["lambda_scope"]["numerator"]),
        int(candidate["lambda_scope"]["denominator"]),
    )
    assert local_lambda == Fraction(
        7_164_821_035_427_968,
        7_236_312_975_589_017,
    )
    assert local_lambda < 1
    assert candidate["exact_scope_inequality_verified"] is True
    assert candidate["global_inequality_verified"] is False
    assert all(edge["local_symbolic_ratio_below_one"] for edge in report.edges)
    assert report.max_plus["karp_status"] == "not_applicable_open_frontier"
    assert report.proof["proof_eligible"] is False


def test_caller_supplied_root_report_has_no_default_root_claims():
    report = exact_selected_cylinder_pilot_report(
        root=ExactMixedCylinder(3, 9, 7, 0, 1),
        target_mod2_power=2,
        max_leaves=16,
    )
    assert report.provenance["sampling_used_for_root_selection"] is False
    assert report.frontier["open_target_nodes"] == 1
    assert report.frontier["reason"].startswith("The 1 exact retained targets")
    reasons = report.proof["proof_ineligibility_reasons"]
    assert reasons[0].startswith("The caller supplied one source root")
    assert any("1 exact retained target nodes" in reason for reason in reasons)


def test_partition_budget_failure_is_explicit():
    with pytest.raises(CylinderBudgetExceeded, match="needs 128 leaves"):
        exact_selected_cylinder_pilot_report(max_leaves=127)


def _solver_edges(
    second_ratio: Fraction,
) -> tuple[ExactBranch, ExactBranch]:
    return (
        ExactBranch(0, 0, 1, (1,), 3, Fraction(2, 1)),
        ExactBranch(1, 1, 0, (2,), 1, second_ratio),
    )


def test_exact_rational_difference_solver_constructs_a_potential():
    branches = _solver_edges(Fraction(1, 8))
    certificate = solve_rational_difference_constraints(
        2,
        branches,
        alpha=Fraction(1, 1),
        contraction=Fraction(3, 4),
    )
    assert certificate.feasible is True
    assert certificate.potential_powers is not None
    assert verify_rational_difference_certificate(certificate, 2, branches)


def test_exact_rational_difference_solver_returns_cycle_obstruction():
    branches = _solver_edges(Fraction(1, 2))
    certificate = solve_rational_difference_constraints(
        2,
        branches,
        alpha=Fraction(1, 1),
        contraction=Fraction(3, 4),
    )
    assert certificate.feasible is False
    assert set(certificate.witness_edge_ids) == {0, 1}
    assert certificate.witness_gain == Fraction(16, 9)
    assert verify_rational_difference_certificate(certificate, 2, branches)


def test_exact_rational_difference_solver_accepts_equality_cycle():
    branches = _solver_edges(Fraction(1, 8))
    certificate = solve_rational_difference_constraints(
        2,
        branches,
        alpha=Fraction(1, 1),
        contraction=Fraction(1, 2),
    )
    assert certificate.feasible is True
    assert verify_rational_difference_certificate(certificate, 2, branches)


def test_infeasible_certificate_verifier_rejects_out_of_range_witness():
    branch = ExactBranch(0, 5, 5, (1,), 3, Fraction(2, 1))
    certificate = RationalDifferenceCertificate(
        feasible=False,
        alpha=Fraction(1, 1),
        contraction=Fraction(3, 4),
        potential_powers=None,
        witness_edge_ids=(0,),
        witness_gain=Fraction(8, 3),
    )
    assert not verify_rational_difference_certificate(
        certificate,
        1,
        (branch,),
    )


def test_report_json_is_deterministic_and_has_no_nonfinite_tokens():
    first = exact_selected_cylinder_pilot_report().to_json()
    second = exact_selected_cylinder_pilot_report().to_json()
    assert first == second
    assert "NaN" not in first
    assert "Infinity" not in first
    parsed = json.loads(first)
    assert parsed["root"]["full_affine"]["B"] == "186875"
    assert parsed["proof"]["global_collatz_proof"] is False
