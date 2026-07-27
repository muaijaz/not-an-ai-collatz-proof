import json
from dataclasses import replace
from fractions import Fraction

import pytest

from collatz_exp.core import v2
from collatz_exp.symbolic_branch_certificate import trace_post_exit_macro
from collatz_exp.symbolic_frontier_certificate import (
    finite_state_self_loop_witness,
    nested_cusp_factor,
    r2_exact_frontier_report,
    r2_floor_loop_run_length,
    r2_floor_loop_target_unit,
    r2_induced_floor_loop_exit,
    r2_reentry_event_residue,
    r2_reentry_instance,
    r2_reentry_source_residue,
    r2_reentry_target_mod3,
    r2_source_class,
    verify_r2_reentry_instance,
)


def _fraction(data: dict[str, str]) -> Fraction:
    return Fraction(int(data["numerator"]), int(data["denominator"]))


def test_r2_mod8_partition_is_exact_and_exhaustive():
    expected = {
        1: "first_post_descent_u_mod8_1",
        5: "first_post_descent_u_mod8_5",
        3: "second_post_descent_u_mod8_3",
        7: "first_post_reentry_u_mod8_7",
    }
    counts = {name: 0 for name in expected.values()}
    for u in range(1, 256, 2):
        branch_class = r2_source_class(u)
        assert branch_class == expected[u % 8]
        counts[branch_class] += 1
    assert set(counts.values()) == {32}

    with pytest.raises(ValueError, match="positive odd"):
        r2_source_class(2)


def test_r2_mod8_boundary_traces_include_second_step_valuation_two():
    first_high = trace_post_exit_macro(2, 1)
    first_exact = trace_post_exit_macro(2, 5)
    second_high = trace_post_exit_macro(2, 3)
    second_boundary = trace_post_exit_macro(2, 11)
    reentry = trace_post_exit_macro(2, 7)

    assert first_high.status == first_exact.status == "descended"
    assert first_high.post_word == (4,)
    assert first_exact.post_word == (3,)
    assert second_high.status == second_boundary.status == "descended"
    assert second_high.post_word == (2, 3)
    assert second_boundary.post_word == (2, 2)
    assert reentry.status == "tail_reentry"
    assert reentry.post_word == (2,)


def test_parametric_reentry_event_residue_fixes_exact_depth():
    for target_R in range(2, 16):
        residue, power = r2_reentry_event_residue(target_R)
        assert power == target_R + 2
        assert v2(9 * residue + 1) == target_R + 1
        assert residue % 8 == 7


def test_target_fixed_reentry_formula_reaches_every_odd_mod256_class():
    for target_R in range(2, 10):
        targets = set()
        for target_u_mod2 in range(1, 256, 2):
            source_residue, source_power = r2_reentry_source_residue(
                target_R,
                target_u_mod2,
            )
            assert source_power == target_R + 9
            assert source_residue % 8 == 7
            instance = r2_reentry_instance(target_R, target_u_mod2)
            assert verify_r2_reentry_instance(instance)
            assert instance.source.u_mod2 == source_residue
            assert instance.target.R == target_R
            targets.add(instance.target.u_mod2)
        assert targets == set(range(1, 256, 2))


def test_reentry_3adic_transport_gains_two_digits_and_cycles_mod9():
    transported = [
        r2_reentry_target_mod3(target_R, 2, 2)
        for target_R in range(2, 8)
    ]
    assert all(power == 4 for _, power in transported)
    assert [residue % 9 for residue, _ in transported] == [8, 4, 2, 1, 5, 7]

    instance = r2_reentry_instance(7, 101)
    expected_mod3, expected_power = r2_reentry_target_mod3(7, 2, 2)
    for lift in range(5):
        u = instance.least_positive_u + lift * instance.source_lift_modulus
        trace = trace_post_exit_macro(2, u, max_post_steps=3)
        target_unit = (trace.landing + 1) >> 7
        assert target_unit % (3**expected_power) == expected_mod3


def test_reentry_event_has_persistent_mod256_spine():
    for target_R in range(7, 20):
        residue, _ = r2_reentry_event_residue(target_R)
        assert residue % 256 == 199


def test_same_R_witness_exactly_refutes_outer_tail_only_candidate():
    witness = r2_reentry_instance(2, 53)
    assert witness.least_positive_u == 47
    assert witness.n0 == 187
    assert witness.landing == 211
    assert witness.target_R == 2
    assert witness.least_lift_size_ratio_upper == Fraction(211, 187) > 1
    assert not verify_r2_reentry_instance(
        replace(witness, target_unit=witness.target_unit + 2)
    )


def test_finite_resolution_obstruction_is_a_real_expanding_self_loop():
    witness = finite_state_self_loop_witness(4, 2)
    assert witness["least_positive_u"] == "1151"
    assert witness["n0"] == "4603"
    assert witness["landing"] == "5179"
    assert witness["target_unit"] == "1295"
    assert witness["source_coarse_state"] == witness["target_coarse_state"]
    assert witness["same_coarse_state"] is True
    assert witness["size_expands"] is True

    for mod2_power, mod3_power in ((1, 0), (2, 1), (7, 3), (12, 5)):
        general = finite_state_self_loop_witness(mod2_power, mod3_power)
        assert general["source_coarse_state"] == general["target_coarse_state"]
        assert general["size_expands"] is True


@pytest.mark.parametrize(
    ("u", "expected_loops"),
    ((15, 1), (127, 2), (1023, 3)),
)
def test_nested_cusp_run_length_and_shift_identity(
    u: int,
    expected_loops: int,
):
    assert r2_floor_loop_run_length(u) == expected_loops
    current = u
    for _ in range(expected_loops):
        source_S = v2(current + 1)
        target = r2_floor_loop_target_unit(current)
        assert target + 1 == 9 * (current + 1) // 8
        assert v2(target + 1) == source_S - 3
        current = target
    assert current % 16 != 15


def test_nested_cusp_exact_factors_and_nearest_simple_base():
    assert nested_cusp_factor(Fraction(23, 22)) == Fraction(11979, 12167)
    assert nested_cusp_factor(Fraction(25, 24)) == Fraction(15552, 15625)
    assert nested_cusp_factor(Fraction(26, 25)) > 1

    report = r2_exact_frontier_report(
        verification_power=6,
        verification_target_R_max=4,
        verification_max_loops=3,
    )
    nearest = report.nested_cusp[
        "nearest_consecutive_base_with_numerator_at_most_64"
    ]
    assert _fraction(nearest["base"]) == Fraction(25, 24)
    assert _fraction(nearest["factor"]) == Fraction(15552, 15625)


def test_maximal_floor_loop_exit_has_exact_three_branch_grammar():
    statuses = {
        1: "descent_at_first_post_step",
        2: "descent_at_second_post_step",
        3: "higher_R_tail_reentry",
    }
    for u in range(1, 4096, 2):
        exit_result = r2_induced_floor_loop_exit(u)
        assert exit_result.exit_S == (
            exit_result.initial_S - 3 * exit_result.loops
        )
        assert exit_result.exit_S in {1, 2, 3}
        assert exit_result.next_status == statuses[exit_result.exit_S]
        assert exit_result.exit_u + 1 == (
            9**exit_result.loops * (u + 1) // (8**exit_result.loops)
        )
        if exit_result.exit_S == 3:
            assert exit_result.next_target_R is not None
            assert exit_result.next_target_R >= 3
        else:
            assert exit_result.next_target_R is None


def test_exact_frontier_report_is_complete_but_not_a_global_proof():
    report = r2_exact_frontier_report()
    data = report.to_json_dict()

    assert report.input_frontier["artifact_snapshot_match"] is True
    assert report.input_frontier["canonical_prior_frontier_verified"] is True
    validation = report.input_frontier["artifact_content_validation"]
    assert validation["fully_verified"] is True
    assert validation["actual_edge_count"] == 128
    assert validation["actual_distinct_target_count"] == 128
    assert report.source_partition["uniformly_descending_coarse_states"] == 96
    assert report.source_partition["live_family_coarse_states"] == 32
    assert report.source_partition["unresolved_positive_integer_sources"] == 0
    assert report.reentry_family["target_fixed_leaves_per_r"] == 128
    assert report.reentry_family["finite_refinement_terminates"] is False
    assert report.finite_verification["parametric_instances_verified"] == 2432
    assert report.frontier["source_cover_complete"] is True
    assert report.frontier["closed_transition_graph"] is False
    assert report.max_plus["finite_karp_run"] is False
    assert report.proof[
        "symbolic_finite_mixed_state_pointwise_no_go_derived"
    ] is True
    assert report.proof[
        "symbolic_nested_cusp_subfamily_contraction_derived"
    ] is True
    assert report.proof[
        "symbolic_maximal_floor_loop_exit_grammar_derived"
    ] is True
    assert report.proof["programmatically_exhausted_all_positive_integers"] is False
    assert report.proof["global_recursive_lyapunov_derived"] is False
    assert report.proof["global_collatz_proof"] is False
    masses = report.induced_exit_grammar[
        "conditional_odd_unit_aggregate_2adic_Haar_mass"
    ]
    assert _fraction(masses["descent"]) == Fraction(6, 7)
    assert _fraction(masses["higher_R_reentry"]) == Fraction(1, 7)
    assert json.loads(report.to_json()) == data
    assert "NaN" not in report.to_json()
    assert "Infinity" not in report.to_json()


def test_report_parameters_do_not_depend_on_the_default_outer_witness():
    report = r2_exact_frontier_report(
        target_mod2_power=3,
        source_u_mod3=0,
        source_mod3_power=0,
        verification_power=5,
        verification_target_R_max=4,
        verification_max_loops=2,
    )
    assert report.outer_tail_candidate_audit["witness_source_u"] == "15"
    assert report.outer_tail_candidate_audit["witness_transition"] == "59 -> 67"
    assert report.input_frontier["canonical_prior_frontier_verified"] is False
    assert report.input_frontier["scope_relation"] == (
        "artifact_does_not_verify_requested_scope"
    )
    assert report.input_frontier["artifact_content_validation"][
        "fully_verified"
    ] is False
    assert report.source_partition["scope"]["coarse_states"] == 4
    assert report.source_partition["uniformly_descending_coarse_states"] == 3
    assert report.source_partition["live_family_coarse_states"] == 1

    with pytest.raises(ValueError, match="at least three"):
        r2_exact_frontier_report(target_mod2_power=2)


def test_missing_input_artifact_is_explicitly_unverified(tmp_path):
    report = r2_exact_frontier_report(
        verification_power=4,
        verification_target_R_max=2,
        verification_max_loops=1,
        input_path=tmp_path / "missing.json",
    )
    validation = report.input_frontier["artifact_content_validation"]
    assert validation["exists"] is False
    assert validation["fully_verified"] is False
    assert report.input_frontier["canonical_prior_frontier_verified"] is False
    assert report.proof["canonical_input_frontier_link_verified"] is False
