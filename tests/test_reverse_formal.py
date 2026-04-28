from collatz_exp.certificates import certificate_from_residue
from collatz_exp.formal_artifacts import (
    certificate_artifact,
    formal_artifact_report,
    verify_certificate_artifact,
)
from collatz_exp.reverse_frontier import (
    accelerated_predecessors,
    reverse_frontier_probe,
    reverse_tree,
)
from collatz_exp.search import adaptive_cover


def test_accelerated_predecessors_include_trivial_preimage_of_one():
    predecessors = accelerated_predecessors(1, max_valuation=4)
    assert (1, 2) in predecessors
    assert all(value > 0 and value % 2 == 1 for value, _ in predecessors)


def test_reverse_tree_records_forward_words():
    tree = reverse_tree(reverse_depth=2, max_nodes=100, max_valuation=6)
    assert 1 in tree
    assert tree[1] == ()
    assert all(isinstance(word, tuple) for word in tree.values())


def test_reverse_frontier_probe_shape():
    cover = adaptive_cover(max_depth=8, max_nodes=200)
    report = reverse_frontier_probe(
        cover.unresolved,
        reverse_depth=2,
        max_nodes=100,
        max_valuation=6,
    )
    data = report.to_json_dict()
    assert data["type"] == "finite_reverse_frontier_probe"
    assert "not_certificate" in data["status"]
    assert report.unresolved_checked == len(cover.unresolved)
    assert len(report.hits) + len(report.misses) <= report.unresolved_checked


def test_formal_artifact_round_trip_and_mutation_rejection():
    certificate = certificate_from_residue(27, 59)
    assert certificate is not None

    artifact = certificate_artifact(certificate)
    data = artifact.to_json_dict()
    assert data["status"] == "machine_readable_certificate_verified_by_local_integer_checker"
    assert data["residue"] == "27"
    assert isinstance(data["B"], str)
    assert verify_certificate_artifact(data)

    mutated = dict(data)
    mutated["A"] = data["A"] + 1
    assert not verify_certificate_artifact(mutated)

    report = formal_artifact_report(certificate)
    assert report.verified
    assert "not_formal_proof" in report.lean_skeleton_status
