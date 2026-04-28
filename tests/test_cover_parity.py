from collatz_exp.cover import CoverFrontierNode, run_certificate_cover
from collatz_exp.cover_parity import analyze_cover_parity, analyze_frontier_parity_node


def test_frontier_parity_node_matches_cylinder_bits():
    node = CoverFrontierNode(residue=7, modulus_power=4)
    analysis = analyze_frontier_parity_node(node)
    assert analysis.residue == 7
    assert analysis.modulus_power == 4
    assert analysis.bits == (1, 1, 1, 0)
    assert analysis.coefficient_den == 16


def test_cover_parity_overlay_smoke():
    cover = run_certificate_cover(max_depth=10, max_nodes=2_000)
    report = analyze_cover_parity(cover, top_n=5)
    assert report.type == "cover_parity_overlay_report"
    assert report.frontier_classes == len(cover.frontier)
    assert 0 <= report.parity_certified_classes <= report.frontier_classes
    assert 1 <= len(report.top) <= 5
