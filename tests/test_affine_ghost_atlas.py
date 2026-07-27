import json
from fractions import Fraction
from pathlib import Path

import pytest

from collatz_exp.affine_ghost_atlas import (
    CANONICAL_FULL_WORD,
    CANONICAL_SOURCE,
    C322,
    DEFAULT_OUTPUT_PATH,
    K1123,
    V2112,
    W112,
    W1122,
    affine_ghost_atlas_report,
    chart_switch_resonance,
    exact_descent_cylinder,
    exact_word_residue,
    expanding_ghost_chart,
    ghost_exit_haar_masses,
    maximal_ghost_repeat_run,
    same_point_ghost_gap_threshold,
    w112_exit_stage,
    word_is_exact,
)
from collatz_exp.core import affine_from_word, apply_word, valuation_word, v2


def _fraction(data: dict[str, str]) -> Fraction:
    return Fraction(int(data["numerator"]), int(data["denominator"]))


@pytest.mark.parametrize(
    "word",
    (
        (1,),
        (2,),
        (1, 2),
        W112,
        W1122,
        V2112,
        C322,
    ),
)
def test_exact_word_residue_is_the_unique_full_precision_cylinder(word):
    affine = affine_from_word(word)
    residue, modulus = exact_word_residue(word)
    assert modulus == 1 << (affine.A + 1)
    assert residue % 2 == 1

    exact_residues = []
    for n in range(1, modulus, 2):
        by_orbit = valuation_word(n, len(word)) == word
        by_linear = word_is_exact(word, n)
        assert by_orbit == by_linear
        if by_linear:
            exact_residues.append(n)
    assert exact_residues == [residue]

    for lift in range(5):
        n = residue + lift * modulus
        assert valuation_word(n, len(word)) == word
        assert word_is_exact(word, n) is True


def test_zero_linear_form_uses_the_terminal_congruence():
    # The contracting fixed point n=1 has L_(2)(1)=0.  It still realizes
    # the exact word; theorem statements interpret v2(0) as infinity.
    assert affine_from_word((2,)).B == 1
    assert word_is_exact((2,), 1) is True
    assert apply_word(1, (2,)) == 1


def test_canonical_expanding_charts_are_exact():
    w = expanding_ghost_chart(W112)
    u = expanding_ghost_chart(W1122)
    v = expanding_ghost_chart(V2112)

    assert (w.M, w.A, w.B, w.D, w.ghost) == (
        3,
        4,
        19,
        11,
        Fraction(-19, 11),
    )
    assert (u.M, u.A, u.B, u.D, u.ghost) == (
        4,
        6,
        73,
        17,
        Fraction(-73, 17),
    )
    assert (v.M, v.A, v.B, v.D, v.ghost) == (
        4,
        6,
        103,
        17,
        Fraction(-103, 17),
    )
    with pytest.raises(ValueError, match="expanding"):
        expanding_ghost_chart(K1123)


def test_repeat_count_has_the_exact_off_by_one():
    run = maximal_ghost_repeat_run((1,), 3)
    assert run.source_linear_v2 == 2
    assert run.repeat_count == 1
    assert run.landing_n == 5
    assert run.residual_depth == 1

    canonical = maximal_ghost_repeat_run(W112, CANONICAL_SOURCE)
    assert canonical.source_linear_v2 == 9
    assert canonical.repeat_count == 2
    assert canonical.landing_n == 108553
    assert canonical.residual_depth == 1
    assert apply_word(CANONICAL_SOURCE, W112) == 64327


def test_repeat_formula_matches_direct_runs_on_small_exact_sources():
    for word in ((1,), (1, 2), W112, W1122, V2112):
        residue, modulus = exact_word_residue(word)
        for lift in range(20):
            n = residue + lift * modulus
            run = maximal_ghost_repeat_run(word, n)
            x = n
            count = 0
            while valuation_word(x, len(word)) == word:
                x = apply_word(x, word)
                count += 1
            assert count == run.repeat_count
            assert x == run.landing_n
            assert 1 <= run.residual_depth <= run.chart.A


def test_conditional_haar_exit_law_is_normalized_and_exact():
    assert ghost_exit_haar_masses(3) == (
        Fraction(4, 7),
        Fraction(2, 7),
        Fraction(1, 7),
    )
    assert ghost_exit_haar_masses(4) == (
        Fraction(8, 15),
        Fraction(4, 15),
        Fraction(2, 15),
        Fraction(1, 15),
    )
    assert sum(ghost_exit_haar_masses(6), Fraction()) == 1


def test_chart_switch_law_covers_both_nonresonant_orders_and_zero_gap():
    below = chart_switch_resonance((1,), (1, 2), 3)
    equal = chart_switch_resonance((1,), (1, 2), 7)
    above = chart_switch_resonance((1,), (1, 2), 15)
    zero = chart_switch_resonance((1,), (1, 1), 3)

    assert (below.residual_depth, below.gap_v2) == (1, 2)
    assert below.valuation_case == "residual_below_gap"
    assert below.target_linear_v2 == 1

    assert (equal.residual_depth, equal.gap_v2) == (2, 2)
    assert equal.valuation_case == "resonance"
    assert equal.target_linear_v2 == 4
    assert equal.resonance_lift == 2
    assert equal.target_word_exact is True

    assert (above.residual_depth, above.gap_v2) == (3, 2)
    assert above.valuation_case == "gap_below_residual"
    assert above.target_linear_v2 == 2

    assert zero.gap_G == 0
    assert zero.gap_v2 is None
    assert zero.valuation_case == "zero_gap_no_resonance"
    assert zero.target_linear_v2 == zero.residual_depth


def test_canonical_chart_switches_are_valuation_resonances():
    regrouped = chart_switch_resonance(
        W112,
        W1122,
        CANONICAL_SOURCE,
    )
    assert regrouped.after_source_n == 64327
    assert regrouped.gap_G == 480
    assert regrouped.gap_v2 == regrouped.residual_depth == 5
    assert regrouped.target_linear_v2 == 12
    assert regrouped.resonance_lift == 7
    assert regrouped.target_word_exact is True

    maximal = chart_switch_resonance(W112, V2112, 64327)
    assert maximal.after_source_n == 108553
    assert maximal.gap_G == 810
    assert maximal.gap_v2 == maximal.residual_depth == 1
    assert maximal.target_linear_v2 == 8
    assert maximal.resonance_lift == 7
    assert maximal.target_word_exact is True
    assert maximal.target_chart.A > maximal.source_chart.A


def test_negative_gap_resonance_uses_absolute_2_adic_order():
    switch = chart_switch_resonance((1, 2), (1,), 27)
    assert switch.gap_G == -4
    assert switch.gap_v2 == switch.residual_depth == 2
    assert switch.valuation_case == "resonance"
    assert switch.target_linear_v2 == 5
    assert switch.target_word_exact is True


def test_same_point_gap_threshold_has_the_correct_equality_boundary():
    threshold = same_point_ghost_gap_threshold(
        W112,
        W1122,
        Fraction(2),
    )
    assert threshold == 96
    for n in (7, 9, 101):
        source_linear = 11 * n + 19
        target_linear = 17 * n + 73
        if source_linear >= threshold:
            assert Fraction(target_linear, source_linear) <= 2
    assert Fraction(17 * 5 + 73, 11 * 5 + 19) > 2


@pytest.mark.parametrize(
    ("n", "residual", "q", "word", "outcome"),
    (
        (1, 1, 1, (2,), "terminal_equality"),
        (108553, 1, 1, (2,), "descent_below_exhausted_source"),
        (3, 2, 3, (1, 4), "descent_below_exhausted_source"),
        (11, 2, 1, (1, 2), "switch_to_expanding_ghost"),
        (31, 3, 1, (1, 1, 1, 1), "switch_to_expanding_ghost"),
        (47, 3, 2, (1, 1, 1, 2), "switch_to_expanding_ghost"),
        (79, 3, 3, (1, 1, 1, 3), "switch_to_expanding_ghost"),
        (15, 3, 5, (1, 1, 1, 5), "descent_below_exhausted_source"),
        (23, 4, 3, (1, 1, 5), "descent_below_exhausted_source"),
    ),
)
def test_w112_exit_partition_covers_every_exact_branch_class(
    n,
    residual,
    q,
    word,
    outcome,
):
    stage = w112_exit_stage(n)
    assert stage.residual_depth == residual
    assert stage.branch_q == q
    assert stage.exit_word == word
    assert stage.outcome == outcome
    assert stage.landing_n == apply_word(n, word)
    if outcome == "descent_below_exhausted_source":
        assert stage.landing_n < n
    if outcome == "switch_to_expanding_ghost":
        assert stage.target_ghost is not None


def test_w112_exit_formulas_hold_without_orbit_assumptions():
    for n in range(1, 1 << 12, 2):
        linear = 11 * n + 19
        residual = v2(linear)
        if residual > 4:
            continue
        stage = w112_exit_stage(n)
        z = linear >> residual
        if residual == 1:
            assert stage.branch_q == v2(3 * z - 23)
        elif residual == 2:
            assert stage.branch_q == v2(9 * z - 29)
        elif residual == 3:
            assert stage.branch_q == v2(81 * z - 103)
        else:
            assert stage.branch_q == v2(27 * z - 19)


def test_refined_full_cylinder_has_exact_first_descent_at_step_13():
    certificate = exact_descent_cylinder(
        CANONICAL_FULL_WORD,
        CANONICAL_SOURCE,
    )
    assert certificate.M == 13
    assert certificate.A == 21
    assert certificate.B == 3563675
    assert certificate.contraction_gap == 502829
    assert certificate.fixed_point == Fraction(3563675, 502829)
    assert certificate.residue == 38119
    assert certificate.modulus == 1 << 22
    assert certificate.landing_n == 28981
    assert certificate.all_positive_members_descend is True

    lifted = exact_descent_cylinder(
        CANONICAL_FULL_WORD,
        CANONICAL_SOURCE + (1 << 22),
    )
    lifted_data = lifted.to_json_dict()
    assert lifted_data["witness_source_n"] == str(CANONICAL_SOURCE + (1 << 22))
    assert lifted_data["witness_landing_n"] == str(28981 + 2 * 3**13)
    assert "canonical_source_n" not in lifted_data

    for lift in range(8):
        source = 38119 + (1 << 22) * lift
        x = source
        for step, a in enumerate(CANONICAL_FULL_WORD, start=1):
            x = apply_word(x, (a,))
            if step < 13:
                assert x > source
        assert x == 28981 + 2 * 3**13 * lift
        assert x < source


def test_default_report_records_the_signal_and_the_open_global_gap():
    report = affine_ghost_atlas_report()
    data = report.to_json_dict()

    assert report.provenance["canonical_prior_frontier_verified"] is True
    assert report.universal_word_cylinder["status"] == "exact_theorem"
    assert report.repeat_grammar["maximal_repeat_count"] == ("floor((v2(L_W(n))-1)/A)")
    assert report.haar_exit_law["iid_or_orbit_independence_claim"] is False
    resonance = report.chart_switch_resonance
    assert resonance["canonical_maximal_W112_to_V2112"]["valuation_case"] == "resonance"
    assert (
        resonance["maximal_exit_complexity_corollary"]["global_termination_consequence"]
        is False
    )
    assert report.w112_exit_partition["status"] == ("exact_complete_residual_partition")
    assert report.atlas_path_fixtures["lands_below_original_source"] is True
    assert report.refined_descent_cylinder["first_descent_is_exactly_step"] == 13
    assert report.frontier["every_maximal_chart_cycle_requires_a_resonance"] is True
    assert report.frontier["closed_transition_graph"] is False
    assert report.frontier["all_expanding_exit_charts_recursively_closed"] is False
    assert report.frontier["induced_chart_selection_rule_complete"] is False
    assert report.frontier["edge_composability_verified"] is False
    assert report.max_plus["finite_karp_run"] is False
    assert report.proof["global_chart_atlas_closed"] is False
    assert report.proof["global_cross_chart_lyapunov_derived"] is False
    assert report.proof["global_collatz_proof"] is False
    assert json.loads(report.to_json()) == data
    assert "NaN" not in report.to_json()
    assert "Infinity" not in report.to_json()


def test_missing_and_changed_prior_artifacts_are_not_canonical(tmp_path):
    missing = affine_ghost_atlas_report(
        verification_power=7,
        input_path=tmp_path / "missing.json",
    )
    assert missing.provenance["artifact_content_validation"]["fully_verified"] is False
    assert missing.provenance["canonical_prior_frontier_verified"] is False
    assert missing.provenance["scope_relation"] == "input_artifact_missing"
    assert missing.proof["canonical_input_frontier_link_verified"] is False

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{}\n", encoding="utf-8")
    invalid = affine_ghost_atlas_report(
        verification_power=7,
        input_path=invalid_path,
    )
    assert invalid.provenance["scope_relation"] == (
        "input_artifact_structurally_invalid"
    )
    assert invalid.provenance["canonical_prior_frontier_verified"] is False

    changed_path = tmp_path / "changed.json"
    changed_path.write_text(
        Path("docs/reports/pecm_higher_r_affine_ghost.json").read_text(encoding="utf-8")
        + "\n",
        encoding="utf-8",
    )
    changed = affine_ghost_atlas_report(
        verification_power=7,
        input_path=changed_path,
    )
    assert changed.provenance["artifact_content_validation"]["fully_verified"] is True
    assert changed.provenance["artifact_snapshot_match"] is False
    assert changed.provenance["canonical_prior_frontier_verified"] is False
    assert changed.provenance["scope_relation"] == (
        "canonical_artifact_snapshot_mismatch"
    )


def test_committed_artifact_is_deterministic():
    report = affine_ghost_atlas_report()
    assert DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8") == (report.to_json() + "\n")


@pytest.mark.parametrize(
    "call",
    (
        lambda: exact_word_residue(()),
        lambda: word_is_exact((1,), 2),
        lambda: expanding_ghost_chart((2,)),
        lambda: maximal_ghost_repeat_run(W112, 2),
        lambda: ghost_exit_haar_masses(0),
        lambda: chart_switch_resonance(W112, W1122, 5),
        lambda: same_point_ghost_gap_threshold(W112, W1122, Fraction(3, 2)),
        lambda: w112_exit_stage(38119),
        lambda: exact_descent_cylinder(W112, 38119),
        lambda: affine_ghost_atlas_report(verification_power=6),
        lambda: affine_ghost_atlas_report(verification_power=3),
    ),
)
def test_invalid_atlas_inputs_are_rejected(call):
    with pytest.raises(ValueError):
        call()
