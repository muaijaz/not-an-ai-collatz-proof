from collatz_exp.cohomology import cohomology_report, first_betti_number
from collatz_exp.core import accelerated_step
from collatz_exp.density_lp import transition_matrix_artifact
from collatz_exp.sos_lyapunov import (
    feature_names,
    lyapunov_template_artifact,
    monomial_features,
)


def test_first_betti_number_known_graphs():
    assert first_betti_number(vertices=3, undirected_edges=2, components=1) == 0
    assert first_betti_number(vertices=3, undirected_edges=3, components=1) == 1
    assert first_betti_number(vertices=4, undirected_edges=2, components=2) == 0


def test_cohomology_report_shape_and_formula():
    report = cohomology_report(modulus_power=4, sample_lift_power=1)
    assert report.type == "truncated_residue_graph_cohomology"
    assert "not_global_proof" in report.status
    assert report.first_betti == first_betti_number(
        report.vertices,
        report.undirected_edges,
        report.components,
    )
    assert report.to_json_dict()["cycle_witnesses"] == [
        list(cycle) for cycle in report.cycle_witnesses
    ]


def test_cohomology_cycle_witnesses_use_support_edges():
    report = cohomology_report(modulus_power=4, sample_lift_power=2)
    artifact = transition_matrix_artifact(modulus_power=4, sample_lift_power=2)
    residues = artifact.residues
    support = set()
    for i, row in enumerate(artifact.row_counts):
        for j, count in enumerate(row):
            if count:
                edge = tuple(sorted((residues[i], residues[j])))
                support.add(edge)

    for cycle in report.cycle_witnesses:
        assert len(cycle) >= 1
        for source, target in zip(cycle, (*cycle[1:], cycle[0])):
            assert tuple(sorted((source, target))) in support


def test_sos_lyapunov_scaffold_has_no_proof_claim():
    artifact = lyapunov_template_artifact(
        modulus_power=4,
        mod3_power=1,
        degree=2,
        max_sample_constraints=4,
    )
    data = artifact.to_json_dict()
    assert data["type"] == "finite_polynomial_lyapunov_template"
    assert "no_proof" in data["status"]
    assert data["proof_claim"] is False
    assert data["solver"] == "none"
    assert "basis" in data
    assert "constraints" in data
    assert "normalization" in data
    assert "theorem" not in data
    assert data == artifact.to_json_dict()


def test_sos_constraint_sampling_integrity():
    artifact = lyapunov_template_artifact(
        modulus_power=4,
        mod3_power=1,
        degree=2,
        max_sample_constraints=8,
    )
    assert monomial_features(2)
    assert len(feature_names(2)) == len(artifact.basis)
    for constraint in artifact.sample_constraints:
        target, valuation = accelerated_step(constraint.source2)
        assert constraint.valuation == valuation
        assert constraint.target2 == target % (1 << artifact.modulus_power)
        assert len(constraint.delta_coefficients) == len(artifact.basis)
