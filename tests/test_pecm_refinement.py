from fractions import Fraction

import pytest

from collatz_exp.pecm_refinement import (
    ConditionalExpectationIntertwiningDiagnostic,
    MixedAdicLevel,
    MixedAdicRefinement,
    RefinementError,
    StateOrderError,
    UniformTargetOperator,
    decode_state_index,
    diagnose_conditional_expectation_intertwining,
    diagnose_galerkin_coarsening,
    diagnose_operator_intertwining,
    diagnose_target_array_intertwining,
    encode_state_index,
    galerkin_coarsen,
    iter_canonical_states,
    validate_state_order,
)
from collatz_exp.post_exit_map import (
    PostExitState,
    _build_post_exit_target_array,
    post_exit_states,
)


def _binary_refinement() -> MixedAdicRefinement:
    return MixedAdicRefinement(
        coarse=MixedAdicLevel(2, 0, (2,)),
        fine=MixedAdicLevel(3, 0, (2,)),
    )


def _compatible_operators() -> tuple[UniformTargetOperator, UniformTargetOperator]:
    coarse = UniformTargetOperator(
        rows=((0, 1), (1, None)),
        label="coarse_fixture",
    )
    fine = UniformTargetOperator(
        rows=(
            (0, 1),
            (1, None),
            (2, 3),
            (3, None),
        ),
        label="fine_fixture",
    )
    return coarse, fine


def test_mixed_adic_fibers_are_complete_disjoint_and_natural():
    refinement = MixedAdicRefinement(
        coarse=MixedAdicLevel(2, 1, (2, 4)),
        fine=MixedAdicLevel(4, 2, (2, 4)),
    )

    assert refinement.mod2_degree == 4
    assert refinement.mod3_degree == 3
    assert refinement.fiber_size == 12

    fibers = refinement.fibers()
    assert all(len(fiber) == 12 for fiber in fibers)
    assert sorted(child for fiber in fibers for child in fiber) == list(
        range(refinement.fine.state_count)
    )
    for coarse_index, children in enumerate(fibers):
        assert tuple(sorted(children)) == children
        assert all(
            refinement.restrict_index(child) == coarse_index
            for child in children
        )
        coarse_state = decode_state_index(refinement.coarse, coarse_index)
        for child in children:
            fine_state = decode_state_index(refinement.fine, child)
            assert refinement.restrict_state(fine_state) == coarse_state


def test_restriction_is_transitive_across_three_levels():
    low = MixedAdicLevel(2, 0, (2, 3))
    middle = MixedAdicLevel(3, 1, (2, 3))
    high = MixedAdicLevel(5, 2, (2, 3))
    high_to_middle = MixedAdicRefinement(middle, high)
    middle_to_low = MixedAdicRefinement(low, middle)
    high_to_low = MixedAdicRefinement(low, high)

    for high_index in range(high.state_count):
        middle_index = high_to_middle.restrict_index(high_index)
        assert middle_to_low.restrict_index(middle_index) == (
            high_to_low.restrict_index(high_index)
        )


def test_prolongation_and_conditional_average_are_exact_left_inverses():
    refinement = MixedAdicRefinement(
        coarse=MixedAdicLevel(2, 1, (2,)),
        fine=MixedAdicLevel(4, 2, (2,)),
    )
    coarse_values = tuple(range(refinement.coarse.state_count))

    prolonged = refinement.prolong(coarse_values)
    assert refinement.conditional_average(prolonged) == tuple(
        Fraction(value) for value in coarse_values
    )

    fine_values = tuple(range(refinement.fine.state_count))
    averages = refinement.conditional_average(fine_values)
    for coarse_index, children in enumerate(refinement.fibers()):
        assert averages[coarse_index] == Fraction(
            sum(fine_values[child] for child in children),
            refinement.fiber_size,
        )


def test_state_index_codec_and_order_validation_match_existing_pecm_order():
    level = MixedAdicLevel(3, 1, (4, 6))
    existing = post_exit_states(
        mod2_power=level.mod2_power,
        mod3_power=level.mod3_power,
        R_values=level.R_values,
    )

    validate_state_order(existing, level)
    assert tuple(iter_canonical_states(level)) == existing
    for index, state in enumerate(existing):
        assert decode_state_index(level, index) == state
        assert encode_state_index(level, state) == index

    reordered = list(existing)
    reordered[0], reordered[1] = reordered[1], reordered[0]
    with pytest.raises(StateOrderError, match="row 0"):
        validate_state_order(reordered, level)

    with pytest.raises(StateOrderError, match="expected"):
        validate_state_order(existing[:-1], level)


def test_refinement_rejects_resolution_and_R_order_mismatches():
    with pytest.raises(RefinementError, match="mod2_power"):
        MixedAdicRefinement(
            MixedAdicLevel(3, 0, (2,)),
            MixedAdicLevel(2, 1, (2,)),
        )
    with pytest.raises(RefinementError, match="ordered R_values"):
        MixedAdicRefinement(
            MixedAdicLevel(2, 0, (2, 3)),
            MixedAdicLevel(3, 1, (3, 2)),
        )

    refinement = _binary_refinement()
    wrong_power = PostExitState(
        R=2,
        u_mod2=1,
        u_mod2_power=2,
        u_mod3=0,
        u_mod3_power=0,
    )
    with pytest.raises(ValueError, match="u_mod2_power"):
        refinement.restrict_state(wrong_power)


def test_uniform_target_operator_has_exact_deterministic_semantics():
    operator = UniformTargetOperator.from_target_array(
        ((0, 1, -1, 1), (1, -1, -1, 0)),
        label="array_fixture",
    )

    assert operator.row_distribution(0) == (
        (None, Fraction(1, 4)),
        (0, Fraction(1, 4)),
        (1, Fraction(1, 2)),
    )
    assert operator.apply((2, 5)) == (Fraction(3), Fraction(7, 4))
    metadata = operator.to_json_dict()
    assert metadata == {
        "type": "uniform_target_operator",
        "label": "array_fixture",
        "state_count": 2,
        "sample_count": 4,
        "cemetery_sample_count": 3,
        "live_sample_count": 5,
    }
    assert operator.to_json_dict(include_rows=True)["rows"] == [
        [0, 1, -1, 1],
        [1, -1, -1, 0],
    ]


def test_exact_pointwise_intertwining_implies_galerkin_intertwining():
    refinement = _binary_refinement()
    coarse, fine = _compatible_operators()

    diagnostic = diagnose_operator_intertwining(refinement, coarse, fine)

    assert diagnostic.status == "exact_pointwise_intertwining"
    assert diagnostic.full_projective_identity_exact
    assert diagnostic.galerkin_identity_exact
    assert diagnostic.pointwise_max_augmented_row_l1 == 0
    assert diagnostic.galerkin_max_augmented_row_l1 == 0
    assert diagnostic.pointwise_max_cemetery_mass_defect == 0


def test_galerkin_coarsening_is_exact_but_does_not_claim_full_compatibility():
    refinement = _binary_refinement()
    fine = UniformTargetOperator(
        rows=(
            (0, 2),
            (1, None),
            (1, 3),
            (3, None),
        ),
        label="fiber_varying_fine_fixture",
    )

    galerkin = galerkin_coarsen(refinement, fine)
    assert galerkin.rows == (
        (0, 0, 1, 1),
        (1, None, 1, None),
    )
    assert galerkin.sample_count == fine.sample_count * refinement.fiber_size

    coarse_values = (Fraction(2), Fraction(5))
    left = galerkin.apply(coarse_values)
    right = refinement.conditional_average(
        fine.apply(refinement.prolong(coarse_values))
    )
    assert left == right

    diagnostic = diagnose_galerkin_coarsening(refinement, fine)
    assert diagnostic.status == "exact_galerkin_intertwining_only"
    assert diagnostic.galerkin_identity_exact
    assert not diagnostic.full_projective_identity_exact
    assert diagnostic.galerkin_max_augmented_row_l1 == 0
    assert diagnostic.pointwise_max_augmented_row_l1 == 1


def test_three_level_galerkin_coarsening_is_associative():
    low = MixedAdicLevel(2, 0, (2,))
    middle = MixedAdicLevel(3, 1, (2,))
    high = MixedAdicLevel(4, 2, (2,))
    fine = UniformTargetOperator(
        rows=tuple(
            (
                (source + 1) % high.state_count,
                None if source % 3 == 0 else (5 * source) % high.state_count,
            )
            for source in range(high.state_count)
        ),
        label="three_level_fixture",
    )

    high_to_middle = MixedAdicRefinement(middle, high)
    middle_to_low = MixedAdicRefinement(low, middle)
    high_to_low = MixedAdicRefinement(low, high)
    sequential = galerkin_coarsen(
        middle_to_low,
        galerkin_coarsen(high_to_middle, fine),
    )
    direct = galerkin_coarsen(high_to_low, fine)

    assert sequential.sample_count == direct.sample_count
    assert tuple(
        sequential.row_distribution(source)
        for source in range(low.state_count)
    ) == tuple(
        direct.row_distribution(source)
        for source in range(low.state_count)
    )


def test_full_conditional_expectation_intertwining_is_distinct_from_galerkin():
    refinement = _binary_refinement()
    coarse_identity = UniformTargetOperator(rows=((0,), (1,)))
    fine_identity = UniformTargetOperator(rows=((0,), (1,), (2,), (3,)))

    exact = diagnose_conditional_expectation_intertwining(
        refinement,
        coarse_identity,
        fine_identity,
    )
    assert isinstance(exact, ConditionalExpectationIntertwiningDiagnostic)
    assert exact.exact
    assert exact.max_augmented_row_l1 == 0

    varying_fine = UniformTargetOperator(
        rows=((0,), (1,), (0,), (1,)),
        label="nonuniform_inside_target_fibers",
    )
    galerkin = galerkin_coarsen(refinement, varying_fine)
    assert diagnose_galerkin_coarsening(
        refinement,
        varying_fine,
    ).galerkin_identity_exact
    full = diagnose_conditional_expectation_intertwining(
        refinement,
        galerkin,
        varying_fine,
    )
    assert not full.exact
    assert full.max_augmented_row_l1 == 1


def test_incompatibility_reports_live_and_cemetery_defects_exactly():
    refinement = _binary_refinement()
    coarse, _fine = _compatible_operators()
    incompatible_fine = UniformTargetOperator(
        rows=(
            (0, 2),
            (1, None),
            (1, 3),
            (None, None),
        ),
        label="incompatible_sampled_fixture",
    )

    diagnostic = diagnose_operator_intertwining(
        refinement,
        coarse,
        incompatible_fine,
    )

    assert diagnostic.status == "sampled_operators_not_refinement_compatible"
    assert not diagnostic.full_projective_identity_exact
    assert not diagnostic.galerkin_identity_exact
    assert diagnostic.pointwise_max_augmented_row_l1 == 1
    assert diagnostic.pointwise_max_cemetery_mass_defect == Fraction(1, 2)
    assert diagnostic.galerkin_max_live_row_l1 == Fraction(1, 4)
    assert diagnostic.galerkin_max_augmented_row_l1 == Fraction(1, 2)
    assert diagnostic.galerkin_max_cemetery_mass_defect == Fraction(1, 4)
    assert "sampling schemes" in diagnostic.interpretation
    assert "underlying Collatz map" in diagnostic.interpretation


def test_target_array_adapter_preserves_cemetery_mass():
    refinement = _binary_refinement()
    coarse, fine = _compatible_operators()

    diagnostic = diagnose_target_array_intertwining(
        refinement,
        coarse.to_target_rows(),
        fine.to_target_rows(),
    )

    assert diagnostic.status == "exact_pointwise_intertwining"
    report = diagnostic.to_json_dict()
    assert report["pointwise_max_total_variation"] == {
        "numerator": 0,
        "denominator": 1,
    }
    assert report["fiber_size"] == 2


def test_current_independent_pecm_samples_are_not_a_projective_ladder():
    R_values = (2, 3, 4)
    refinement = MixedAdicRefinement(
        MixedAdicLevel(2, 0, R_values),
        MixedAdicLevel(3, 0, R_values),
    )
    coarse_targets = _build_post_exit_target_array(
        mod2_power=2,
        mod3_power=0,
        R_values=R_values,
        sample_lift_power=1,
        max_steps=50,
        tail_reentry_min_R=2,
    )[0]
    fine_targets = _build_post_exit_target_array(
        mod2_power=3,
        mod3_power=0,
        R_values=R_values,
        sample_lift_power=1,
        max_steps=50,
        tail_reentry_min_R=2,
    )[0]

    diagnostic = diagnose_target_array_intertwining(
        refinement,
        coarse_targets,
        fine_targets,
    )

    assert diagnostic.status == "sampled_operators_not_refinement_compatible"
    assert diagnostic.pointwise_mismatched_fine_rows > 0
    assert diagnostic.galerkin_mismatched_coarse_rows > 0
    assert "sampling schemes" in diagnostic.interpretation


def test_current_sampled_mixed_adic_defect_matches_exact_tiny_fixture():
    R_values = (2, 3, 4)
    refinement = MixedAdicRefinement(
        MixedAdicLevel(2, 0, R_values),
        MixedAdicLevel(4, 1, R_values),
    )
    coarse_targets = _build_post_exit_target_array(
        mod2_power=2,
        mod3_power=0,
        R_values=R_values,
        sample_lift_power=1,
        max_steps=50,
        tail_reentry_min_R=2,
    )[0]
    fine_targets = _build_post_exit_target_array(
        mod2_power=4,
        mod3_power=1,
        R_values=R_values,
        sample_lift_power=1,
        max_steps=50,
        tail_reentry_min_R=2,
    )[0]
    coarse = UniformTargetOperator.from_target_array(coarse_targets)
    fine = UniformTargetOperator.from_target_array(fine_targets)

    diagnostic = diagnose_conditional_expectation_intertwining(
        refinement,
        coarse,
        fine,
    )

    assert not diagnostic.exact
    assert diagnostic.max_live_row_l1 == Fraction(5, 4)
    assert diagnostic.max_augmented_row_l1 == Fraction(5, 3)
