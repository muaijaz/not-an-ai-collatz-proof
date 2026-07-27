import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from collatz_exp.core import apply_word, v2
from collatz_exp.symbolic_branch_certificate import (
    ExactMixedCylinder,
    least_positive_mixed_representative,
)
from collatz_exp.symbolic_higher_r_certificate import (
    affine_ghost_certificate,
    affine_ghost_chart_transition,
    higher_r_affine_ghost_report,
    higher_r_event_residue,
    higher_r_first_post_stage,
    higher_r_phase_factor,
    higher_r_reentry_source_residue,
    higher_r_reentry_target_mod3,
    higher_r_source_residue,
    higher_r_target_mod3,
    higher_r_transfer_instance,
    verify_higher_r_transfer_instance,
)


def _fraction(data: dict[str, str]) -> Fraction:
    return Fraction(int(data["numerator"]), int(data["denominator"]))


def test_higher_r_source_residue_fixes_depth_and_target_bits():
    target_power = 5
    for block_count in range(1, 4):
        for target_R in range(3, 9):
            for target_unit in range(1, 1 << target_power, 2):
                source_u, source_power = higher_r_source_residue(
                    block_count,
                    target_R,
                    target_unit,
                    target_power,
                )
                assert source_power == (3 * block_count + target_R + target_power - 2)
                assert v2(source_u + 1) == 3 * block_count
                source_w = (source_u + 1) >> (3 * block_count)
                target_numerator = 9**block_count * source_w - 1
                assert v2(target_numerator) == target_R - 2
                assert (target_numerator >> (target_R - 2)) % (
                    1 << target_power
                ) == target_unit


def test_higher_r_event_residue_fixes_only_the_exact_depth():
    for block_count in range(1, 6):
        for target_R in range(3, 12):
            source_u, source_power = higher_r_event_residue(
                block_count,
                target_R,
            )
            assert source_power == 3 * block_count + target_R - 1
            assert v2(source_u + 1) == 3 * block_count
            source_w = (source_u + 1) >> (3 * block_count)
            assert v2(9**block_count * source_w - 1) == target_R - 2


def test_canonical_higher_r_phase_transfer_fixtures():
    first = higher_r_transfer_instance(1, 3, 67)
    second = higher_r_transfer_instance(2, 3, 121)

    assert first.least_positive_u == 119
    assert first.source_n == 475
    assert first.valuation_word == (1, 2)
    assert first.target_n == 535
    assert first.target_unit == 67
    assert first.intermediate_tail_depths == (3,)
    assert first.phase_ratio == Fraction(11979, 12167)

    assert second.least_positive_u == 191
    assert second.source_n == 763
    assert second.valuation_word == (1, 2, 1, 2)
    assert second.target_n == 967
    assert second.target_unit == 121
    assert second.intermediate_tail_depths == (2, 3)
    assert second.phase_ratio == Fraction(11979, 12167) ** 2
    assert verify_higher_r_transfer_instance(first)
    assert verify_higher_r_transfer_instance(second)


def test_higher_r_transfer_reaches_every_target_residue_and_preserves_lifts():
    target_power = 4
    expected = set(range(1, 1 << target_power, 2))
    for block_count in (1, 2):
        for target_R in (3, 4, 7):
            reached = set()
            for target_unit in expected:
                instance = higher_r_transfer_instance(
                    block_count,
                    target_R,
                    target_unit,
                    target_mod2_power=target_power,
                )
                reached.add(instance.target.u_mod2)
                for lift in range(3):
                    source_u = (
                        instance.least_positive_u + lift * instance.source_lift_modulus
                    )
                    target_n = apply_word(
                        4 * source_u - 1,
                        instance.valuation_word,
                    )
                    assert v2(target_n + 1) == target_R
                    target_v = (target_n + 1) >> target_R
                    assert target_v % (1 << target_power) == target_unit
                    assert (
                        target_v % (3**instance.target.mod3_power)
                        == instance.target.u_mod3
                    )
            assert reached == expected


def test_higher_r_target_mod3_gains_exactly_two_digits_per_block():
    for block_count in range(1, 5):
        for target_R in range(3, 8):
            residue, power = higher_r_target_mod3(
                block_count,
                target_R,
                2,
                2,
            )
            assert power == 2 + 2 * block_count
            instance = higher_r_transfer_instance(
                block_count,
                target_R,
                1,
                target_mod2_power=1,
            )
            assert instance.target.mod3_power == power
            assert instance.target.u_mod3 == residue


def test_transfer_verifier_rejects_mutated_certificate_fields():
    instance = higher_r_transfer_instance(2, 5, 37)
    assert not verify_higher_r_transfer_instance(
        replace(instance, target_n=instance.target_n + 2)
    )
    assert not verify_higher_r_transfer_instance(
        replace(instance, intermediate_tail_depths=(9, 9))
    )
    assert not verify_higher_r_transfer_instance(
        replace(
            instance,
            target=replace(
                instance.target,
                mod2_power=instance.target.mod2_power + 1,
            ),
        )
    )
    assert not verify_higher_r_transfer_instance(
        replace(instance, phase_base=Fraction(0))
    )


def test_full_phase_energy_factor_is_exact_and_uniform():
    single = Fraction(11979, 12167)
    for block_count in range(1, 10):
        assert higher_r_phase_factor(block_count) == single**block_count
        assert higher_r_phase_factor(block_count) <= single < 1


def test_first_higher_r_post_stage_matches_exact_cutoff():
    for source_R in range(3, 9):
        for source_unit in range(1, 128, 2):
            stage = higher_r_first_post_stage(source_R, source_unit)
            assert stage.source_n == (1 << source_R) * source_unit - 1
            assert stage.landing == (3**source_R * source_unit - 1) >> stage.post_q
            coefficient = (1 << (source_R + stage.post_q)) - 3**source_R
            descends = coefficient * source_unit > (1 << stage.post_q) - 1
            assert descends == (stage.classification == "descent_below_higher_R_source")

    assert higher_r_first_post_stage(3, 3).classification == (
        "descent_below_higher_R_source"
    )
    assert higher_r_first_post_stage(5, 37).classification == "tail_reentry"
    assert higher_r_first_post_stage(3, 1).classification == (
        "continuing_post_exit_branch"
    )


def test_first_post_target_fixed_residues_and_3adic_gain_are_exact():
    target_power = 4
    source_mod3_power = 2
    for source_R in (3, 5, 7):
        for post_q in (1, 2, 4):
            for reentry_depth in (1, 2, 4):
                for target_unit in range(1, 1 << target_power, 2):
                    source_residue, source_power = higher_r_reentry_source_residue(
                        source_R,
                        post_q,
                        reentry_depth,
                        target_unit,
                        target_power,
                    )
                    source = ExactMixedCylinder(
                        R=source_R,
                        u_mod2=source_residue,
                        mod2_power=source_power,
                        u_mod3=2,
                        mod3_power=source_mod3_power,
                    )
                    source_unit, _ = least_positive_mixed_representative(source)
                    stage = higher_r_first_post_stage(
                        source_R,
                        source_unit,
                    )
                    assert stage.post_q == post_q
                    assert stage.landing_tail_depth == reentry_depth
                    target_v = (stage.landing + 1) >> reentry_depth
                    assert target_v % (1 << target_power) == target_unit
                    target_mod3, target_mod3_power = higher_r_reentry_target_mod3(
                        source_R,
                        post_q,
                        reentry_depth,
                        2,
                        source_mod3_power,
                    )
                    assert target_mod3_power == (source_mod3_power + source_R)
                    assert target_v % (3**target_mod3_power) == target_mod3


@pytest.mark.parametrize(
    ("word", "source_n", "base", "D", "B", "target_n", "factor"),
    (
        (
            (1, 1, 1, 1, 2),
            1183,
            Fraction(5, 4),
            179,
            211,
            4495,
            Fraction(15552, 15625),
        ),
        (
            (1, 1, 2),
            38119,
            Fraction(8, 7),
            11,
            19,
            64327,
            Fraction(64827, 65536),
        ),
    ),
)
def test_affine_ghost_certificates_are_exact(
    word: tuple[int, ...],
    source_n: int,
    base: Fraction,
    D: int,
    B: int,
    target_n: int,
    factor: Fraction,
):
    certificate = affine_ghost_certificate(word, source_n, base)
    assert certificate.linear_D == D
    assert certificate.B == B
    assert certificate.ghost == Fraction(-B, D)
    assert certificate.target_n == target_n
    assert certificate.source_linear_v2 - certificate.target_linear_v2 == certificate.A
    assert certificate.potential_factor == factor < 1
    assert certificate.contracts is True


def test_simple_cusp_obstruction_is_independent_of_its_base():
    phase = higher_r_transfer_instance(1, 5, 37)
    assert phase.least_positive_u == 263
    assert phase.source_n == 1051
    assert phase.target_n == 1183
    target = apply_word(phase.target_n, (1, 1, 1, 1, 2))
    assert target == 4495
    assert v2(phase.target_n + 5) - 2 == 0
    assert v2(target + 5) - 2 == 0
    assert Fraction(target + 5, phase.target_n + 5) == Fraction(125, 33) > 1

    switch = affine_ghost_chart_transition(
        (1, 1, 1, 1, 2),
        (1, 1, 2),
    )
    assert switch.linear_multiplier == Fraction(2673, 11456)
    assert switch.additive_ghost_gap == Fraction(1080, 179)
    for source_n in (1, 1183, 4495):
        source_target = Fraction(243 * source_n + 211, 64)
        target_linear = 11 * source_target + 19
        transformed = (
            switch.linear_multiplier * (179 * source_n + 211)
            + switch.additive_ghost_gap
        )
        assert target_linear == transformed

    repeated = 38119
    repeated = apply_word(repeated, (1, 1, 2))
    repeated = apply_word(repeated, (1, 1, 2))
    assert repeated == 108553
    with pytest.raises(ValueError, match="valuation mismatch"):
        apply_word(repeated, (1, 1, 2))


def test_default_report_records_the_exact_result_and_open_gap():
    report = higher_r_affine_ghost_report()
    data = report.to_json_dict()

    assert report.provenance["canonical_prior_frontier_verified"] is True
    assert report.provenance["scope_relation"] == ("canonical_prior_frontier_verified")
    assert report.higher_r_transfer["full_word"] == "(1,2)^m"
    assert _fraction(report.phase_energy["single_block_factor"]) == Fraction(
        11979,
        12167,
    )
    assert report.phase_energy["contracts_entire_higher_R_handoff"] is True
    assert report.phase_energy["global_lyapunov"] is False
    assert report.simple_cusp_obstruction["candidate_ratio_value"] == ("125/33 > 1")
    assert len(report.affine_ghost_theorem["canonical_certificates"]) == 2
    assert report.finite_verification["transfer_instances_verified"] == 4096
    assert report.frontier["full_post_exit_stopping_grammar_closed"] is False
    assert report.max_plus["finite_karp_run"] is False
    assert report.proof["symbolic_finite_repeat_budget_derived"] is True
    assert report.proof["symbolic_chart_switch_identity_derived"] is True
    assert report.proof["global_cross_chart_lyapunov_derived"] is False
    assert report.proof["global_collatz_proof"] is False
    assert json.loads(report.to_json()) == data
    assert "NaN" not in report.to_json()
    assert "Infinity" not in report.to_json()


def test_custom_report_scope_keeps_canonical_witnesses_separate():
    report = higher_r_affine_ghost_report(
        target_mod2_power=3,
        source_u_mod3=0,
        source_mod3_power=0,
        verification_block_count_max=1,
        verification_target_R_max=4,
        verification_first_post_unit_power=4,
    )
    assert report.provenance["canonical_prior_frontier_verified"] is False
    assert report.provenance["scope_relation"] == (
        "requested_scope_differs_from_canonical"
    )
    chain = report.simple_cusp_obstruction["canonical_source_chain"]
    assert chain["R2_source_n"] == "1051"
    assert chain["phase_target_n"] == "1183"
    assert chain["next_target_n"] == "4495"
    assert report.finite_verification["transfer_instances_verified"] == 8


def test_missing_prior_artifact_is_explicitly_unverified(tmp_path):
    report = higher_r_affine_ghost_report(
        target_mod2_power=2,
        verification_block_count_max=1,
        verification_target_R_max=3,
        verification_first_post_unit_power=3,
        input_path=tmp_path / "missing.json",
    )
    validation = report.provenance["artifact_content_validation"]
    assert validation["exists"] is False
    assert validation["fully_verified"] is False
    assert report.provenance["canonical_prior_frontier_verified"] is False
    assert report.proof["canonical_input_frontier_link_verified"] is False


def test_valid_but_changed_prior_snapshot_is_distinguished(tmp_path):
    changed = tmp_path / "changed.json"
    changed.write_text(
        Path("docs/reports/pecm_r2_recursive_tail_cusp.json").read_text(
            encoding="utf-8"
        )
        + "\n",
        encoding="utf-8",
    )
    report = higher_r_affine_ghost_report(
        target_mod2_power=8,
        verification_block_count_max=1,
        verification_target_R_max=3,
        verification_first_post_unit_power=3,
        input_path=changed,
    )
    assert report.provenance["artifact_content_validation"]["fully_verified"] is True
    assert report.provenance["artifact_snapshot_match"] is False
    assert report.provenance["scope_relation"] == (
        "canonical_artifact_snapshot_mismatch"
    )
    assert report.provenance["canonical_prior_frontier_verified"] is False


@pytest.mark.parametrize(
    "call",
    (
        lambda: higher_r_source_residue(0, 3, 1, 1),
        lambda: higher_r_event_residue(1, 2),
        lambda: higher_r_reentry_source_residue(3, 0, 2, 1, 1),
        lambda: higher_r_reentry_target_mod3(3, 1, 0, 0, 0),
        lambda: higher_r_transfer_instance(
            1,
            3,
            1,
            target_mod2_power=1,
            phase_base=Fraction(0),
        ),
        lambda: affine_ghost_certificate((2,), 3, Fraction(5, 4)),
    ),
)
def test_invalid_certificate_inputs_are_rejected(call):
    with pytest.raises(ValueError):
        call()
