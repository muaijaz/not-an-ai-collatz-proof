import json
from fractions import Fraction
from pathlib import Path

import pytest

from collatz_exp.affine_ghost_atlas import (
    W112,
    expanding_ghost_chart,
    word_is_exact,
)
from collatz_exp.core import affine_from_word, apply_word, v2, valuation_word
from collatz_exp.recursive_ghost_atlas import (
    DEFAULT_OUTPUT_PATH,
    J4,
    SEED_WORDS,
    W12,
    W1112,
    W1113,
    derive_first_free_exit_template,
    first_free_exit_stage,
    first_free_expanding_edges,
    instantiate_first_free_branch,
    ladder_prefix_certificate,
    ladder_partial_theta_residue,
    ladder_prefix_word,
    mersenne_chart,
    one_two_chart,
    p_chart_coefficients,
    p_expanding_a_max,
    p_word,
    post_source_copy_lift,
    resonance_depth_witness,
    recursive_ghost_atlas_report,
    resonant_ladder_edges,
    shortest_parser_component,
    shortest_parser_expanding_edges,
)


EXPECTED_TEMPLATES = {
    (W12, 1): ((), 1, 3, -7, ()),
    (W12, 2): ((1, 1), 0, 27, -29, (1, 2)),
    (W12, 3): ((1,), 2, 9, -5, ()),
    (J4, 1): ((), 1, 3, -65, ()),
    (J4, 2): ((1,), 1, 9, -65, (1,)),
    (J4, 3): ((1, 1), 1, 27, -65, (1,)),
    (J4, 4): ((1, 1, 1), 1, 81, -65, (1, 2)),
    (W1112, 1): ((), 1, 3, -73, ()),
    (W1112, 2): ((1,), 1, 9, -85, (1,)),
    (W1112, 3): ((1, 1), 1, 27, -103, (1,)),
    (W1112, 4): ((1, 1, 1, 1), 0, 243, -341, (1, 2, 3)),
    (W1112, 5): ((1, 1, 1), 2, 81, -65, (1,)),
    (W1113, 1): ((), 1, 3, -89, ()),
    (W1113, 2): ((1,), 1, 9, -125, (1,)),
    (W1113, 3): ((1, 1), 1, 27, -179, (1,)),
    (W1113, 4): ((1, 1, 1, 1), 0, 243, -763, (1, 2, 3)),
    (W1113, 5): ((1, 1, 1, 2), 0, 243, -373, (1, 2)),
    (W1113, 6): ((1, 1, 1), 3, 81, -65, ()),
}


EXPECTED_EXPANDING_EDGES = {
    (W12, 2, 1): ((1, 1, 1), -76),
    (W12, 2, 2): ((1, 1, 2), -36),
    (J4, 2, 1): ((1, 2), 260),
    (J4, 3, 1): ((1, 1, 2), 520),
    (J4, 4, 1): ((1, 1, 1, 2), 1040),
    (J4, 4, 2): ((1, 1, 1, 3), 3120),
    (W1112, 2, 1): ((1, 2), 180),
    (W1112, 3, 1): ((1, 1, 2), 216),
    (W1112, 4, 1): ((1, 1, 1, 1, 1), -3376),
    (W1112, 4, 2): ((1, 1, 1, 1, 2), -1296),
    (W1112, 4, 3): ((1, 1, 1, 1, 3), 2864),
    (W1112, 5, 1): ((1, 1, 1, 3), 2080),
    (W1113, 2, 1): ((1, 2), 20),
    (W1113, 3, 1): ((1, 1, 2), -392),
    (W1113, 4, 1): ((1, 1, 1, 1, 1), -10128),
    (W1113, 4, 2): ((1, 1, 1, 1, 2), -8048),
    (W1113, 4, 3): ((1, 1, 1, 1, 3), -3888),
    (W1113, 5, 1): ((1, 1, 1, 2, 1), -7776),
    (W1113, 5, 2): ((1, 1, 1, 2, 2), -3616),
}


def test_first_free_template_table_covers_all_eighteen_residuals():
    actual = {}
    for source_word in SEED_WORDS:
        chart = expanding_ghost_chart(source_word)
        for residual in range(1, chart.A + 1):
            template = derive_first_free_exit_template(source_word, residual)
            actual[(source_word, residual)] = (
                template.fixed_prefix,
                template.free_offset,
                template.q_coefficient,
                template.q_constant,
                template.expanding_q,
            )
            assert template.fixed_valuation_total == residual
            assert template.q_coefficient % 2 == 1
            assert template.q_constant % 2 == 1
            for q in range(1, template.first_contracting_q + 2):
                word = template.exit_word(q)
                assert affine_from_word(word).A == residual + q

    assert actual == EXPECTED_TEMPLATES
    assert len(actual) == 18


def test_every_q_branch_is_one_exact_source_cylinder_and_is_resonant():
    for (source_word, residual), expected in EXPECTED_TEMPLATES.items():
        template = derive_first_free_exit_template(source_word, residual)
        q_limit = template.first_contracting_q + 3
        for q in range(1, q_limit + 1):
            branch = instantiate_first_free_branch(template, q)
            n = branch.target_residue
            source = expanding_ghost_chart(source_word)
            source_linear = source.D * n + source.B
            z = source_linear >> residual

            assert v2(source_linear) == residual
            assert (
                v2(
                    abs(
                        template.q_coefficient * z
                        + template.q_constant
                    )
                )
                == q
            )
            assert valuation_word(n, branch.target_M) == branch.target_word
            assert word_is_exact(branch.target_word, n) is True
            assert branch.target_modulus == 1 << (residual + q + 1)
            assert branch.gap_v2 == residual
            assert branch.is_resonant is True
            assert (
                branch.is_expanding
                == (q in expected[4])
            )
            lift = branch.post_source_copy_lift
            assert lift.source_landing_n % branch.target_modulus == (
                branch.target_residue
            )
            assert valuation_word(
                lift.source_predecessor_n,
                len(source_word),
            ) == source_word
            assert apply_word(
                lift.source_predecessor_n,
                source_word,
            ) == lift.source_landing_n
            lifted_linear = (
                source.D * lift.source_landing_n + source.B
            )
            assert v2(lifted_linear) == residual
            assert (
                (lifted_linear >> residual)
                % (3 ** len(source_word))
                == 0
            )


def test_seed_expanding_edge_atlas_has_the_exact_nineteen_edges():
    actual = {}
    for source_word in SEED_WORDS:
        for branch in first_free_expanding_edges(source_word):
            key = (
                source_word,
                branch.template.residual_depth,
                branch.q,
            )
            actual[key] = (branch.target_word, branch.gap_G)
            assert branch.gap_v2 == branch.template.residual_depth
            assert branch.classification == "expanding_chart"
            assert branch.target_D > 0

    assert actual == EXPECTED_EXPANDING_EDGES
    assert len(actual) == 19


def test_resonance_target_depth_and_repeat_budget_are_unbounded():
    for source_word in SEED_WORDS:
        for branch in first_free_expanding_edges(source_word):
            for repeat_count in (1, 3, 7):
                target_depth = repeat_count * branch.target_A + 1
                witness = resonance_depth_witness(
                    source_word,
                    branch.target_word,
                    branch.template.residual_depth,
                    target_depth,
                )
                assert witness.source_linear_v2 == (
                    branch.template.residual_depth
                )
                assert witness.target_linear_v2 == target_depth
                assert witness.target_repeat_count == repeat_count
                assert witness.gap_G == branch.gap_G
                assert witness.source_n % 2 == 1
                assert word_is_exact(branch.target_word, witness.source_n)
                assert not word_is_exact(source_word, witness.source_n)
                lift = witness.post_source_copy_lift
                source = expanding_ghost_chart(source_word)
                target = expanding_ghost_chart(branch.target_word)
                assert v2(
                    source.D * lift.source_landing_n + source.B
                ) == branch.template.residual_depth
                assert v2(
                    target.D * lift.source_landing_n + target.B
                ) == target_depth


def test_contracting_seed_branches_descend_with_only_terminal_one():
    terminal = []
    for source_word in SEED_WORDS:
        chart = expanding_ghost_chart(source_word)
        for residual in range(1, chart.A + 1):
            template = derive_first_free_exit_template(source_word, residual)
            # Once 2^(e+q)-3^M exceeds B, every positive source descends.
            q = template.first_contracting_q
            while True:
                branch = instantiate_first_free_branch(template, q)
                if branch.classification == "contracting_terminal_equality_at_one":
                    terminal.append((source_word, residual, q))
                else:
                    assert branch.classification == (
                        "contracting_all_positive_sources_descend"
                    )
                    assert branch.contracting_non_descent_count == 0
                contraction_gap = -branch.target_D
                if contraction_gap > branch.target_B:
                    break
                q += 1
            assert q < template.first_contracting_q + 8

    assert terminal == [
        (W12, 1, 1),
        (J4, 1, 1),
        (W1112, 1, 1),
        (W1113, 1, 1),
    ]


def test_exit_stage_replays_the_formula_on_each_configured_branch():
    for (source_word, residual), _ in EXPECTED_TEMPLATES.items():
        template = derive_first_free_exit_template(source_word, residual)
        for q in range(1, template.first_contracting_q + 2):
            branch = instantiate_first_free_branch(template, q)
            stage = first_free_exit_stage(source_word, branch.target_residue)
            assert stage.residual_depth == residual
            assert stage.q == q
            assert stage.branch.target_word == branch.target_word
            assert stage.landing_n == apply_word(
                stage.source_n,
                branch.target_word,
            )
            if branch.is_expanding:
                assert stage.outcome == "switch_to_expanding_chart"
                assert stage.landing_n > stage.source_n
            elif stage.source_n == 1:
                assert stage.outcome == "terminal_equality"
            else:
                assert stage.outcome == "descent_below_exhausted_source"
                assert stage.landing_n < stage.source_n


def test_w112_seed_link_reaches_the_parametric_ladder_exactly():
    template = derive_first_free_exit_template(W112, 3)
    branch = instantiate_first_free_branch(template, 1)
    assert branch.target_word == J4
    assert branch.gap_G == -520
    assert branch.gap_v2 == 3


def test_every_finite_ladder_prefix_composes_with_a_positive_w112_predecessor():
    source = expanding_ghost_chart(W112)
    for rounds in range(1, 7):
        certificate = ladder_prefix_certificate(4, rounds)
        lift = post_source_copy_lift(
            W112,
            certificate.residue,
            certificate.modulus,
        )
        assert valuation_word(
            lift.source_predecessor_n,
            len(W112),
        ) == W112
        assert apply_word(lift.source_predecessor_n, W112) == (
            lift.source_landing_n
        )
        assert v2(
            source.D * lift.source_landing_n + source.B
        ) == 3
        stage = first_free_exit_stage(W112, lift.source_landing_n)
        assert stage.q == 1
        assert stage.branch.target_word == J4
        assert valuation_word(
            lift.source_landing_n,
            certificate.M,
        ) == certificate.word


@pytest.mark.parametrize("m", range(2, 25))
def test_parametric_j_and_k_chart_formulas_and_exit_templates(m):
    c_m = 3**m - 2**m
    e_m = 3**m - 2 ** (m + 1)
    j = mersenne_chart(m)
    k = one_two_chart(m)

    assert (j.M, j.A, j.B, j.D, j.ghost) == (
        m,
        m,
        c_m,
        c_m,
        -1,
    )
    assert (k.M, k.A, k.B, k.D, k.ghost) == (
        m,
        m + 1,
        c_m,
        e_m,
        Fraction(-c_m, e_m),
    )

    j_exit = derive_first_free_exit_template(j.word, m)
    assert j_exit.fixed_prefix == (1,) * (m - 1)
    assert j_exit.free_offset == 1
    assert j_exit.q_coefficient == 3**m
    assert j_exit.q_constant == -c_m
    assert instantiate_first_free_branch(j_exit, 1).target_word == k.word

    k_exit = derive_first_free_exit_template(k.word, m)
    assert k_exit.fixed_prefix == (1,) * m
    assert k_exit.free_offset == 0
    assert k_exit.q_coefficient == 3 ** (m + 1)
    assert k_exit.q_constant == e_m - 6 * c_m
    assert (
        instantiate_first_free_branch(k_exit, 1).target_word
        == mersenne_chart(m + 1).word
    )


@pytest.mark.parametrize("m", range(2, 33))
def test_parametric_ladder_gap_identities_are_resonant(m):
    j_to_k, k_to_j = resonant_ladder_edges(m)
    c_m = 3**m - 2**m
    c_next = 3 ** (m + 1) - 2 ** (m + 1)

    assert j_to_k.gap_G == c_m * 2**m
    assert k_to_j.gap_G == -c_next * 2**m
    assert j_to_k.gap_v2 == k_to_j.gap_v2 == m
    assert j_to_k.target_word == one_two_chart(m).word
    assert k_to_j.target_word == mersenne_chart(m + 1).word


def test_every_finite_ladder_prefix_has_a_nested_positive_exact_cylinder():
    certificates = [
        ladder_prefix_certificate(4, rounds)
        for rounds in range(1, 7)
    ]
    for rounds, certificate in enumerate(certificates, start=1):
        assert valuation_word(certificate.residue, certificate.M) == (
            certificate.word
        )
        assert certificate.D > 0
        assert certificate.boundary_values[0] == certificate.residue
        assert all(
            right > left
            for left, right in zip(
                certificate.boundary_values,
                certificate.boundary_values[1:],
            )
        )
        assert certificate.maximal_blocks_certified == 2 * rounds - 1
        assert v2(certificate.residue + 1) == 8
        assert ladder_partial_theta_residue(4, rounds) == (
            certificate.residue,
            certificate.modulus,
        )
        if rounds > 1:
            previous = certificates[rounds - 2]
            assert certificate.word[: len(previous.word)] == previous.word
            assert certificate.residue % previous.modulus == previous.residue


@pytest.mark.parametrize("m", range(2, 13))
def test_first_ladder_pair_has_the_closed_residue_formula(m):
    certificate = ladder_prefix_certificate(m, 1)
    assert certificate.word == p_word(2 * m, 2)
    assert certificate.residue == 3 * 2 ** (2 * m) - 1
    assert certificate.modulus == 2 ** (2 * m + 2)
    assert v2(certificate.residue + 1) == 2 * m


def test_ladder_pairing_is_the_exact_macro_renormalization():
    assert ladder_prefix_word(4, 3) == (
        p_word(8, 2) + p_word(10, 2) + p_word(12, 2)
    )
    for m in range(2, 15):
        for a in range(1, p_expanding_a_max(m) + 1):
            for repeats in (1, 2, 4):
                parsed = p_word(m, 1) * repeats + p_word(m, a)
                macro = p_word((repeats + 1) * m, a)
                assert parsed == macro
                assert affine_from_word(parsed) == affine_from_word(macro)


@pytest.mark.parametrize("m", range(1, 30))
def test_parametric_p_chart_coefficients_and_expansion_cutoff(m):
    a_max = p_expanding_a_max(m)
    for a in range(1, a_max + 3):
        A, B, D = p_chart_coefficients(m, a)
        affine = affine_from_word(p_word(m, a))
        assert A == m - 1 + a
        assert B == 3**m - 2**m
        assert D == 3**m - 2**A
        assert (D > 0) == (a <= a_max)
        assert (affine.A, affine.B) == (A, B)


def test_shortest_divergence_parser_closes_on_seven_resonant_nodes():
    nodes, edges = shortest_parser_component()
    assert nodes == (
        (2, 1),
        (2, 2),
        (3, 1),
        (3, 2),
        (4, 1),
        (4, 2),
        (4, 3),
    )
    assert len(edges) == 18
    assert all(edge.gap_v2 == edge.residual_depth for edge in edges)
    assert all(edge.target_m <= edge.source_m for edge in edges)
    assert {
        (edge.source_m, edge.source_a, edge.target_m, edge.target_a)
        for edge in edges
        if edge.source_m == 2
    } == {
        (2, 1, 2, 2),
        (2, 2, 2, 1),
    }


def test_shortest_parser_rows_match_direct_edge_enumeration():
    nodes, all_edges = shortest_parser_component()
    for node in nodes:
        expected = shortest_parser_expanding_edges(*node)
        actual = tuple(
            edge
            for edge in all_edges
            if (edge.source_m, edge.source_a) == node
        )
        assert actual == expected


def test_default_report_is_proof_calibrated_and_records_both_parsers():
    report = recursive_ghost_atlas_report()
    data = report.to_json_dict()

    assert report.provenance["canonical_prior_frontier_verified"] is True
    assert (
        report.selection_rules["source_relative_first_free"]
        ["globally_intrinsic_parsing_claim"]
        is False
    )
    assert (
        report.universal_induced_resonance
        ["every_seed_first_free_edge_resonant"]
        is True
    )
    assert report.seed_exit_grammar["residual_template_count"] == 18
    assert report.seed_exit_grammar["expanding_edge_count"] == 19
    assert report.shortest_parser["node_count"] == 7
    assert report.shortest_parser["every_edge_resonant"] is True
    assert (
        report.parametric_ladder
        ["arbitrarily_long_finite_positive_paths_derived"]
        is True
    )
    assert (
        report.parametric_ladder
        ["each_edge_forces_the_next_edge_for_every_lift"]
        is False
    )
    assert report.infinite_boundary["positive_integer_realizability"] == "open"
    assert (
        report.infinite_boundary
        ["positive_integer_infinite_ladder_realizability_derived"]
        is False
    )
    assert (
        report.infinite_boundary["tschakaloff_reduction"]
        ["irrationality_derived"]
        is False
    )
    assert (
        report.infinite_boundary["divergent_positive_collatz_orbit_constructed"]
        is False
    )
    assert report.frontier["full_recursive_grammar_derived"] is False
    assert report.max_plus["finite_karp_proves_global_contraction"] is False
    assert report.proof["global_collatz_proof"] is False
    assert json.loads(report.to_json()) == data
    assert "NaN" not in report.to_json()
    assert "Infinity" not in report.to_json()


def test_missing_invalid_and_changed_prior_artifacts_are_not_canonical(tmp_path):
    missing = recursive_ghost_atlas_report(
        input_path=tmp_path / "missing.json",
        verification_m_max=8,
        prefix_rounds=2,
    )
    assert missing.provenance["scope_relation"] == "input_artifact_missing"
    assert missing.proof["canonical_input_frontier_link_verified"] is False

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{}\n", encoding="utf-8")
    invalid = recursive_ghost_atlas_report(
        input_path=invalid_path,
        verification_m_max=8,
        prefix_rounds=2,
    )
    assert invalid.provenance["scope_relation"] == (
        "input_artifact_structurally_invalid"
    )

    changed_path = tmp_path / "changed.json"
    changed_path.write_text(
        Path("docs/reports/pecm_affine_ghost_atlas.json").read_text(
            encoding="utf-8"
        )
        + "\n",
        encoding="utf-8",
    )
    changed = recursive_ghost_atlas_report(
        input_path=changed_path,
        verification_m_max=8,
        prefix_rounds=2,
    )
    assert (
        changed.provenance["artifact_content_validation"]["fully_verified"]
        is True
    )
    assert changed.provenance["artifact_snapshot_match"] is False
    assert changed.provenance["scope_relation"] == (
        "canonical_artifact_snapshot_mismatch"
    )


def test_committed_recursive_artifact_is_deterministic():
    report = recursive_ghost_atlas_report()
    assert DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8") == (
        report.to_json() + "\n"
    )


@pytest.mark.parametrize(
    "call",
    (
        lambda: derive_first_free_exit_template((), 1),
        lambda: derive_first_free_exit_template((2,), 1),
        lambda: derive_first_free_exit_template(W12, 0),
        lambda: derive_first_free_exit_template(W12, 4),
        lambda: instantiate_first_free_branch(
            derive_first_free_exit_template(W12, 2),
            0,
        ),
        lambda: first_free_exit_stage(W12, 2),
        lambda: first_free_exit_stage(W12, 11),
        lambda: post_source_copy_lift(W12, 1, 3),
        lambda: post_source_copy_lift(W12, 2, 4),
        lambda: resonance_depth_witness(W12, (1, 1, 1), 1, 4),
        lambda: resonance_depth_witness(W12, (1, 1, 1), 2, 3),
        lambda: p_word(0, 1),
        lambda: p_word(1, 0),
        lambda: p_expanding_a_max(0),
        lambda: p_chart_coefficients(0, 1),
        lambda: shortest_parser_expanding_edges(2, 3),
        lambda: shortest_parser_component(2, 3),
        lambda: mersenne_chart(1),
        lambda: one_two_chart(1),
        lambda: resonant_ladder_edges(1),
        lambda: ladder_prefix_word(1, 1),
        lambda: ladder_prefix_word(2, 0),
        lambda: ladder_partial_theta_residue(1, 1),
        lambda: ladder_partial_theta_residue(2, 0),
        lambda: recursive_ghost_atlas_report(verification_m_max=7),
        lambda: recursive_ghost_atlas_report(prefix_rounds=1),
    ),
)
def test_invalid_recursive_atlas_inputs_are_rejected(call):
    with pytest.raises(ValueError):
        call()
