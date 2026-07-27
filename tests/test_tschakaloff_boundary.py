import json
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from collatz_exp.tschakaloff_boundary import (
    CANONICAL_ALPHA,
    CANONICAL_Q,
    CANONICAL_Z,
    DEFAULT_OUTPUT_PATH,
    SOURCE_DOI,
    SOURCE_SCAN_SHA256,
    boundary_affine_reduction,
    canonical_theorem_parameters,
    exact_cutoff_witness,
    repo_tschakaloff_term,
    tschakaloff_boundary_report,
    tschakaloff_f_term,
    verify_boundary_affine_reduction,
    verify_series_normalization,
    verify_theorem_hypotheses,
)


def _fraction(data: dict[str, str]) -> Fraction:
    return Fraction(int(data["numerator"]), int(data["denominator"]))


def test_repository_series_is_exactly_the_published_f_at_q_times_z():
    assert CANONICAL_Q == Fraction(9, 4)
    assert CANONICAL_Z == 2
    assert CANONICAL_ALPHA == Fraction(9, 2)
    assert repo_tschakaloff_term(0) == 1
    assert repo_tschakaloff_term(1) == 2
    assert repo_tschakaloff_term(2) == Fraction(16, 9)
    assert repo_tschakaloff_term(3) == Fraction(512, 729)
    assert verify_series_normalization(128)
    for n in range(128):
        assert tschakaloff_f_term(n) == repo_tschakaloff_term(n)


def test_published_theorem_parameters_satisfy_every_elementary_hypothesis():
    parameters = canonical_theorem_parameters()
    validation = verify_theorem_hypotheses(parameters)

    assert parameters.r == 9
    assert parameters.s == 4
    assert parameters.q == Fraction(9, 4)
    assert parameters.h == 9
    assert parameters.p == 2
    assert parameters.ell == 1
    assert parameters.sigma == 0
    assert parameters.alpha == Fraction(9, 2)
    assert validation["all_elementary_hypotheses_verified"] is True
    assert all(validation["checks"].values())

    invalid = replace(parameters, alpha=Fraction(0))
    assert (
        verify_theorem_hypotheses(invalid)["all_elementary_hypotheses_verified"]
        is False
    )


def test_gamma_cutoff_has_an_exact_integer_sandwich():
    witness = exact_cutoff_witness()

    gamma = witness["gamma_upper_bound"]
    paper = witness["paper_cutoff_lower_bound"]
    assert gamma["left"] == 256
    assert gamma["right"] == 243
    assert gamma["verified"] is True
    assert paper["left"] == 81
    assert paper["right"] == 80
    assert paper["verified"] is True
    assert _fraction(witness["separating_rational"]) == Fraction(3, 8)
    assert witness["strict_cutoff_verified_exactly"] is True
    assert witness["floating_point_used"] is False


@pytest.mark.parametrize("start_m", range(2, 65))
def test_every_boundary_is_a_nonconstant_affine_form_in_the_master_value(
    start_m: int,
):
    reduction = boundary_affine_reduction(start_m)
    expected_coefficient = -(CANONICAL_Q ** (start_m * (start_m - 1) // 2)) / (
        CANONICAL_Z ** (start_m + 1)
    )

    assert reduction.shifted_argument == (CANONICAL_Z * CANONICAL_Q ** (-(start_m + 1)))
    assert reduction.master_coefficient == expected_coefficient
    assert reduction.master_coefficient != 0
    assert verify_boundary_affine_reduction(reduction)


def test_boundary_verifier_rejects_mutated_reductions():
    reduction = boundary_affine_reduction(4)
    assert not verify_boundary_affine_reduction(
        replace(
            reduction,
            master_coefficient=reduction.master_coefficient + 1,
        )
    )
    assert not verify_boundary_affine_reduction(
        replace(reduction, shifted_argument=Fraction(1))
    )


def test_default_report_closes_only_the_explicit_infinite_ladder():
    report = tschakaloff_boundary_report()
    data = report.to_json_dict()

    assert report.provenance["canonical_recursive_atlas_verified"] is True
    assert report.provenance["scope_relation"] == ("canonical_recursive_atlas_verified")
    assert report.published_source["doi"] == SOURCE_DOI
    assert report.published_source["research_scan_sha256"] == SOURCE_SCAN_SHA256
    assert report.published_source["paper_proof_formalized_in_repository"] is False
    assert (
        report.theorem_instantiation["elementary_hypotheses"][
            "all_elementary_hypotheses_verified"
        ]
        is True
    )
    assert report.series_normalization["identity_verified"] is True
    assert report.master_value["irrational_over_Q"] is True
    assert report.boundary_family["every_boundary_irrational_over_Q_in_Q_2"] is True
    assert (
        report.boundary_family["nonnegative_integer_infinite_ladder_realizability"]
        == "excluded"
    )
    assert (
        report.boundary_family["finite_positive_prefix_cylinders_invalidated"] is False
    )
    assert report.proof["positive_integer_infinite_ladder_excluded"] is True
    assert report.proof["global_recursive_grammar_closed"] is False
    assert report.proof["global_collatz_proof"] is False
    assert json.loads(report.to_json()) == data
    assert "NaN" not in report.to_json()
    assert "Infinity" not in report.to_json()


def test_missing_and_changed_prior_artifacts_are_not_canonical(tmp_path):
    missing = tschakaloff_boundary_report(
        input_path=tmp_path / "missing.json",
        normalization_term_count=4,
        boundary_start_m_max=4,
    )
    assert missing.provenance["artifact_content_validation"]["exists"] is False
    assert missing.provenance["canonical_recursive_atlas_verified"] is False
    assert missing.proof["canonical_input_atlas_link_verified"] is False

    changed = tmp_path / "changed.json"
    changed.write_text(
        Path("docs/reports/pecm_recursive_ghost_atlas.json").read_text(encoding="utf-8")
        + "\n",
        encoding="utf-8",
    )
    changed_report = tschakaloff_boundary_report(
        input_path=changed,
        normalization_term_count=4,
        boundary_start_m_max=4,
    )
    assert (
        changed_report.provenance["artifact_content_validation"]["fully_verified"]
        is True
    )
    assert changed_report.provenance["artifact_snapshot_match"] is False
    assert changed_report.provenance["canonical_recursive_atlas_verified"] is False


def test_mutated_prior_boundary_claim_is_rejected(tmp_path):
    payload = json.loads(
        Path("docs/reports/pecm_recursive_ghost_atlas.json").read_text(encoding="utf-8")
    )
    payload["infinite_boundary"]["tschakaloff_reduction"]["functional_equation"] = (
        "mutated"
    )
    mutated = tmp_path / "mutated.json"
    mutated.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    report = tschakaloff_boundary_report(
        input_path=mutated,
        normalization_term_count=4,
        boundary_start_m_max=4,
    )
    validation = report.provenance["artifact_content_validation"]
    assert validation["tschakaloff_reduction_present"] is False
    assert validation["fully_verified"] is False
    assert report.proof["canonical_input_atlas_link_verified"] is False


def test_committed_tschakaloff_artifact_is_deterministic():
    report = tschakaloff_boundary_report()
    assert DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8") == report.to_json() + "\n"


@pytest.mark.parametrize(
    "call",
    (
        lambda: tschakaloff_f_term(-1),
        lambda: repo_tschakaloff_term(-1),
        lambda: verify_series_normalization(0),
        lambda: boundary_affine_reduction(1),
        lambda: tschakaloff_boundary_report(normalization_term_count=0),
        lambda: tschakaloff_boundary_report(boundary_start_m_max=1),
    ),
)
def test_invalid_inputs_are_rejected(call):
    with pytest.raises(ValueError):
        call()
