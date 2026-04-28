from collatz_exp.cover import load_cover_report, run_certificate_cover
from collatz_exp.cover_mass import cover_mass_report, cylinder_mass
from collatz_exp.frontier_analysis import analyze_cover_frontier, initial_ones


def test_cylinder_mass_is_odd_relative_density():
    assert cylinder_mass(1) == 1
    assert cylinder_mass(2) == 1 / 2
    assert cylinder_mass(5) == 1 / 16


def test_cover_mass_report_partitions_root_for_finite_search():
    cover = run_certificate_cover(max_depth=10, max_nodes=2_000)
    mass = cover_mass_report(cover)
    assert mass.type == "binary_prefix_antichain_mass_report"
    assert "not_collatz_proof" in mass.status
    assert mass.antichain_valid
    assert mass.partition_valid
    assert mass.total_mass == 1
    assert mass.frontier_mass == cover.unresolved_odd_density


def test_frontier_analysis_ranks_by_debt():
    cover = run_certificate_cover(max_depth=10, max_nodes=2_000)
    analysis = analyze_cover_frontier(cover, top_n=5)
    assert analysis.type == "cover_frontier_analysis"
    assert analysis.frontier_classes == len(cover.frontier)
    assert 1 <= len(analysis.top) <= 5
    debt_buckets = [item.debt_bucket for item in analysis.top]
    assert debt_buckets == sorted(debt_buckets, reverse=True)


def test_initial_ones_helper():
    assert initial_ones(()) == 0
    assert initial_ones((1, 1, 2, 1)) == 2
    assert initial_ones((2, 1, 1)) == 0
