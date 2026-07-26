import json
import math

import pytest

from collatz_exp.pecm_consistency import (
    format_pecm_cross_resolution_consistency_report,
    lift_consistency_profile,
    pecm_cross_resolution_consistency_report,
    sampled_branch_ratio_profile,
)
from collatz_exp.pecm_refinement import (
    MixedAdicLevel,
    MixedAdicRefinement,
    UniformTargetOperator,
)
from collatz_exp.experiments import build_parser


def _binary_refinement() -> MixedAdicRefinement:
    return MixedAdicRefinement(
        MixedAdicLevel(2, 0, (2,)),
        MixedAdicLevel(3, 0, (2,)),
    )


def test_lift_profile_uses_exact_minimax_shift_and_is_scale_invariant():
    refinement = _binary_refinement()
    coarse = (2.0, 8.0)
    fine = (1.0, 4.0, 9.0, 16.0)

    profile = lift_consistency_profile(refinement, coarse, fine)
    scaled = lift_consistency_profile(
        refinement,
        tuple(7.0 * value for value in coarse),
        tuple(11.0 * value for value in fine),
    )

    assert profile.errors == pytest.approx(scaled.errors)
    assert profile.errors["mean"] == pytest.approx(
        0.5 * abs(math.log(2.0 / 3.0))
    )
    assert profile.errors["min"] == pytest.approx(0.0)
    assert profile.optimal_additive_constants["mean"] == pytest.approx(
        0.5 * math.log(2.0 / 3.0)
    )
    assert profile.lift_spread_quantiles["1"] == pytest.approx(
        math.log(9.0)
    )
    assert {record["metric"] for record in profile.worst_coarse_states} == {
        "mean",
        "min",
        "max",
    }


def test_lift_profile_rejects_nonpositive_or_wrong_length_vectors():
    refinement = _binary_refinement()

    with pytest.raises(ValueError, match="shape"):
        lift_consistency_profile(refinement, (1.0,), (1.0,) * 4)
    with pytest.raises(ValueError, match="finite positive"):
        lift_consistency_profile(refinement, (1.0, 2.0), (1.0, 0.0, 1.0, 1.0))


def test_branch_ratio_bound_accounts_for_cemetery_survival_probability():
    refinement = _binary_refinement()
    operator = UniformTargetOperator(
        rows=(
            (2, None),
            (None, None),
            (None, None),
            (None, None),
        )
    )

    profile = sampled_branch_ratio_profile(
        refinement,
        operator,
        (1.0, 1.0, 4.0, 1.0),
        lambda_super=2.0,
    )

    assert profile["live_target_samples"] == 1
    assert profile["cemetery_or_descent_samples"] == 7
    assert profile["minimum_positive_row_survival_probability"] == 0.5
    assert profile["max_live_target_ratio"] == 4.0
    assert profile["rowwise_q_to_live_target_upper_bound"] == 4.0
    assert not profile["rowwise_q_bound_below_one"]
    assert profile["global_lambda_to_live_target_upper_bound"] == 4.0
    assert not profile["global_lambda_bound_below_one"]

    with pytest.raises(ValueError, match="does not bound"):
        sampled_branch_ratio_profile(
            refinement,
            operator,
            (1.0, 1.0, 4.0, 1.0),
            lambda_super=1.9,
        )


def test_branch_ratio_profile_serializes_empty_live_support_as_null():
    refinement = _binary_refinement()
    operator = UniformTargetOperator(rows=((None,),) * 4)

    profile = sampled_branch_ratio_profile(
        refinement,
        operator,
        (1.0, 1.0, 1.0, 1.0),
        lambda_super=0.0,
    )

    assert profile["status"] == "no_live_targets"
    assert profile["max_live_target_ratio"] is None
    assert profile["within_source_log_ratio_spread_quantiles"] is None
    assert "NaN" not in json.dumps(profile, allow_nan=False)


def test_tiny_report_builds_one_galerkin_ladder_and_is_deterministic():
    kwargs = {
        "configurations": ((2, 0), (3, 0)),
        "alpha": 0.9,
        "R_values": (2, 3, 4, 5, 6),
        "sample_lift_power": 1,
        "max_steps": 50,
        "extension_iterations": 200,
        "tolerance": 1e-10,
    }
    first = pecm_cross_resolution_consistency_report(**kwargs)
    second = pecm_cross_resolution_consistency_report(**kwargs)

    assert first.to_json() == second.to_json()
    assert first.primary_transition_window_complete
    assert first.legacy_transition_windows_complete
    assert first.proof_facing_input_complete
    assert not first.exact_lyapunov_inequality_verified
    assert not first.proof_eligible
    assert (
        "galerkin_compatibility_is_not_pointwise_projective_compatibility"
        in first.proof_ineligibility_reasons
    )
    assert not first.global_collatz_proof
    assert len(first.errors["mean"]) == 1
    assert len(first.level_summaries) == 2
    primary = first.operator_intertwining_defect[0]
    assert primary["pointwise_and_galerkin"]["galerkin_identity_exact"]
    assert (
        primary["pointwise_and_galerkin"]["galerkin_max_augmented_row_l1"]
        == {"numerator": 0, "denominator": 1}
    )
    assert (
        first.legacy_independently_sampled_operator_defects[0][
            "pointwise_and_galerkin"
        ]["status"]
        == "sampled_operators_not_refinement_compatible"
    )
    payload = json.loads(first.to_json())
    assert payload["levels"] == [[2, 0], [3, 0]]
    assert payload["errors"]["mean"] == [first.errors["mean"][0]]
    assert "not_global_proof" in payload["status"]
    formatted = format_pecm_cross_resolution_consistency_report(first)
    assert "E_mean=" in formatted
    assert "primary_transition_window_complete=True" in formatted


def test_report_rejects_unresolved_windows_and_oversized_levels():
    with pytest.raises(ValueError, match="transition window is incomplete"):
        pecm_cross_resolution_consistency_report(
            configurations=((2, 0), (3, 0)),
            alpha=0.9,
            R_values=(2, 3, 4),
            sample_lift_power=1,
            max_steps=50,
        )

    with pytest.raises(ValueError, match="chunked/streaming"):
        pecm_cross_resolution_consistency_report(
            configurations=((8, 2), (12, 4)),
            max_materialized_states=1_000_000,
        )

    with pytest.raises(ValueError, match="target entries"):
        pecm_cross_resolution_consistency_report(
            configurations=((2, 0), (3, 0)),
            alpha=0.9,
            R_values=(2,),
            sample_lift_power=10,
            max_materialized_states=100,
            max_materialized_transitions=100,
        )


def test_experiment_cli_exposes_safe_cross_resolution_controls():
    args = build_parser().parse_args(
        [
            "--pecm-cross-resolution",
            "--pecm-cross-resolution-configs",
            "2:0,3:0",
            "--pecm-common-alpha",
            "0.9",
            "--pecm-max-materialized-states",
            "1234",
            "--pecm-max-materialized-transitions",
            "5678",
            "--pecm-cross-resolution-output",
            "report.json",
        ]
    )

    assert args.pecm_cross_resolution
    assert args.pecm_cross_resolution_configs == "2:0,3:0"
    assert args.pecm_common_alpha == 0.9
    assert args.pecm_max_materialized_states == 1234
    assert args.pecm_max_materialized_transitions == 5678
    assert args.pecm_cross_resolution_output == "report.json"
