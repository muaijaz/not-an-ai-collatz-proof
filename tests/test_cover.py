from fractions import Fraction

from collatz_exp.certificates import certificate_from_residue
from collatz_exp.cover import (
    CertificateCover,
    CoverFrontierNode,
    cover_report_from_json_dict,
    frontier_density,
    load_cover_report,
    run_certificate_cover,
)


def test_certificate_cover_trie_detects_parent_cylinder():
    certificate = certificate_from_residue(27, 59)
    assert certificate is not None

    cover = CertificateCover()
    assert cover.add(certificate)
    assert not cover.add(certificate)
    assert cover.is_covered(27, 59)
    assert cover.is_covered(27 + (1 << 59), 60)
    assert not cover.is_covered(27 + (1 << 58), 59)


def test_frontier_density_is_exact():
    frontier = (
        CoverFrontierNode(residue=1, modulus_power=3),
        CoverFrontierNode(residue=5, modulus_power=3),
    )
    assert frontier_density(frontier) == Fraction(1, 2)
    assert frontier_density(()) == Fraction(0, 1)


def test_certificate_cover_report_json_round_trip(tmp_path):
    report = run_certificate_cover(max_depth=8, max_nodes=200)
    data = report.to_json_dict()
    assert data["type"] == "certificate_cover_search_report"
    assert "not_collatz_proof" in data["status"] or data["complete"]
    assert data["certificates"]
    assert data["frontier"]

    restored = cover_report_from_json_dict(data)
    assert restored.nodes_processed == report.nodes_processed
    assert restored.unresolved_odd_density == report.unresolved_odd_density

    path = tmp_path / "cover.json"
    report.save(path)
    loaded = load_cover_report(path)
    assert loaded.nodes_processed == report.nodes_processed
    assert len(loaded.certificates) == len(report.certificates)


def test_certificate_cover_resume_increases_or_preserves_progress():
    first = run_certificate_cover(max_depth=10, max_nodes=50)
    resumed = run_certificate_cover(max_depth=10, max_nodes=120, initial_report=first)
    assert resumed.nodes_processed >= first.nodes_processed
    assert len(resumed.certificates) >= len(first.certificates)
    assert resumed.unresolved_odd_density <= first.unresolved_odd_density
