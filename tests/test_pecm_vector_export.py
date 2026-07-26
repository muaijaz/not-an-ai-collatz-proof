import json

import numpy as np
import pytest

from collatz_exp.pecm_vector_export import (
    _graph_roles,
    positive_resolvent_vector,
    post_exit_common_alpha_vector_exports,
    post_exit_vector_export,
)


def test_positive_resolvent_vector_accepts_target_arrays():
    targets = np.array([[1], [-1]], dtype=np.int32)
    solution = positive_resolvent_vector(
        targets,
        1,
        alpha=0.75,
        iterations=10,
        tolerance=1e-12,
    )

    assert solution.converged
    assert solution.fixed_point_residual == 0.0
    assert solution.vector.tolist() == pytest.approx([7.0 / 3.0, 1.0])
    assert solution.ratios.tolist() == pytest.approx([3.0 / 7.0, 0.0])


def test_positive_resolvent_vector_accepts_state_count_operator():
    class FixtureOperator:
        state_count = 2

        @staticmethod
        def apply(values):
            return np.array([values[1], 0.0])

    solution = positive_resolvent_vector(
        FixtureOperator(),
        alpha=0.75,
        iterations=10,
        tolerance=1e-12,
    )

    assert solution.converged
    assert solution.vector.tolist() == pytest.approx([7.0 / 3.0, 1.0])


def test_graph_roles_separate_core_basin_off_support_and_closed_recurrence():
    targets = np.array(
        [
            [1, -1],
            [1, -1],
            [0, -1],
            [-1, -1],
            [4, 4],
        ],
        dtype=np.int32,
    )

    roles, recurrent = _graph_roles(targets)

    assert roles.tolist() == [1, 2, 1, 0, 2]
    assert recurrent.tolist() == [False, False, False, False, True]


def test_post_exit_vector_export_is_deterministic_and_machine_readable():
    kwargs = {
        "alpha": 0.9,
        "R_values": (2, 3, 4, 5, 6),
        "sample_lift_power": 1,
        "max_steps": 50,
        "extension_iterations": 100,
        "tolerance": 1e-12,
    }
    first = post_exit_vector_export(2, 0, **kwargs)
    second = post_exit_vector_export(2, 0, **kwargs)

    assert first.converged
    assert first.states == 10
    assert first.complete_transition_window
    assert first.proof_facing_input_complete
    assert first.certificate_kind == "floating_point_super_eigenvector_diagnostic"
    assert not first.exact_inequality_verified
    assert not first.proof_eligible
    assert "float64_inequality_not_exactly_verified" in (
        first.proof_ineligibility_reasons
    )
    assert not first.global_collatz_proof
    assert first.state_order_hash == second.state_order_hash
    assert len(first.state_order_hash) == 64
    assert [record.to_json_dict() for record in first.records] == [
        record.to_json_dict() for record in second.records
    ]
    assert [record.state_id for record in first.records] == list(range(first.states))
    assert first.descended_samples + first.reentry_samples + (
        first.unresolved_or_out_of_window_samples
    ) == first.states * first.row_denominator
    assert first.lambda_super < first.alpha
    assert first.alpha_minus_lambda > 0.0
    assert first.cyclic_core_states + first.cyclic_basin_states + (
        first.transient_off_support_states
    ) == first.states
    geometric_mean = float(
        np.exp(np.mean(np.log([record.h for record in first.records])))
    )
    assert geometric_mean == pytest.approx(1.0)
    payload = json.loads(first.to_json())
    assert payload["records"][0]["state_id"] == 0
    assert payload["state_order_hash"] == first.state_order_hash


def test_common_alpha_export_uses_identical_alpha_at_every_level():
    exports = post_exit_common_alpha_vector_exports(
        ((2, 0), (3, 0)),
        alpha=0.9,
        R_values=(2, 3, 4, 5, 6),
        sample_lift_power=1,
        max_steps=50,
        extension_iterations=100,
        tolerance=1e-12,
    )

    assert [export.alpha for export in exports] == [0.9, 0.9]


def test_common_alpha_export_applies_budget_to_all_retained_levels():
    with pytest.raises(ValueError, match="would retain 6 states"):
        post_exit_common_alpha_vector_exports(
            ((2, 0), (2, 0), (2, 0)),
            alpha=0.9,
            R_values=(2,),
            max_materialized_states=5,
        )


def test_unresolved_samples_are_rejected_by_default_and_marked_if_allowed():
    kwargs = {
        "alpha": 0.9,
        "R_values": (2, 3, 4),
        "sample_lift_power": 1,
        "max_steps": 50,
        "extension_iterations": 40,
        "tolerance": 1e-12,
    }
    with pytest.raises(ValueError, match="transition window is incomplete"):
        post_exit_vector_export(2, 0, **kwargs)

    export = post_exit_vector_export(
        2,
        0,
        require_resolved=False,
        **kwargs,
    )
    assert export.unresolved_or_out_of_window_samples == 1
    assert not export.complete_transition_window
    assert not export.proof_facing_input_complete
    assert not export.proof_eligible
    assert (
        "unresolved_or_out_of_window_samples_share_the_cemetery_sentinel"
        in export.proof_ineligibility_reasons
    )
    assert not export.exact_inequality_verified


def test_materialized_export_guard_rejects_oversized_levels_before_building():
    with pytest.raises(ValueError, match="chunked/streaming"):
        post_exit_vector_export(
            12,
            4,
            alpha=0.55,
            max_materialized_states=1_000_000,
        )

    with pytest.raises(ValueError, match="target entries"):
        post_exit_vector_export(
            2,
            0,
            alpha=0.9,
            R_values=(2,),
            sample_lift_power=10,
            max_materialized_states=100,
            max_materialized_transitions=100,
        )


def test_require_convergence_rejects_alpha_below_spectral_radius():
    with pytest.raises(ValueError, match="did not converge"):
        post_exit_vector_export(
            2,
            1,
            alpha=0.9,
            R_values=(2, 3, 4, 5, 6),
            sample_lift_power=1,
            max_steps=80,
            extension_iterations=20,
            tolerance=1e-12,
            require_resolved=False,
            require_convergence=True,
        )
