from collatz_exp.mersenne import profile_mersenne
from collatz_exp.mersenne_continuation import (
    analyze_mersenne_branches,
    analyze_mersenne_prefix_family,
    analyze_mersenne_progression,
    build_mersenne_continuation_graph,
    common_prefix,
    continuation_edges,
    post_run_word_for_mersenne,
    refine_mersenne_continuation_moduli,
    sample_from_profile,
    spike_positions,
    summarize_residue_class,
)


def test_mersenne_continuation_samples_profile_rows():
    profile = profile_mersenne(32)
    sample = sample_from_profile(32, 16, profile)
    assert sample.residue_class == 0
    assert sample.post_run_steps == 38
    assert sample.post_run_valuation == 79
    assert sample.landing_debt < 0
    assert len(post_run_word_for_mersenne(32)) == 38


def test_mersenne_residue_class_summary_tracks_worst_R():
    samples = tuple(
        sample_from_profile(R, 8, profile_mersenne(R))
        for R in (32, 40)
    )
    summary = summarize_residue_class(0, samples)
    assert summary.count == 2
    assert summary.max_post_run_steps == 38
    assert summary.min_post_run_valuation == 79
    assert summary.worst_R in {32, 40}


def test_mersenne_continuation_edges_are_grouped_by_R_mod_M():
    samples = tuple(
        sample_from_profile(R, 8, profile_mersenne(R))
        for R in range(16, 24)
    )
    edges = continuation_edges(8, samples)
    assert edges
    assert all(0 <= edge.source_class < 8 for edge in edges)
    assert all(0 <= edge.target_class < 8 for edge in edges)
    assert sum(edge.count for edge in edges) == len(samples)


def test_mersenne_continuation_graph_smoke():
    graph = build_mersenne_continuation_graph(R_min=2, R_max=40, modulus=8)
    assert graph.type == "mersenne_continuation_parameter_graph"
    assert graph.samples == 39
    assert graph.classes
    assert graph.edges
    assert graph.worst_samples
    assert all(sample.landing_debt < 0 for sample in graph.worst_samples)


def test_mersenne_refinement_report_parent_child_consistency():
    report = refine_mersenne_continuation_moduli(
        R_min=2,
        R_max=48,
        moduli=(8, 16, 32),
    )
    assert report.type == "mersenne_continuation_refinement_report"
    assert report.worst_by_modulus
    assert report.refinement_links
    for link in report.refinement_links:
        assert link.child_class % link.parent_modulus == link.parent_class
        assert link.child_modulus % link.parent_modulus == 0


def test_common_prefix_and_spike_positions():
    assert common_prefix(((1, 2, 3), (1, 2, 4), (1, 2))) == (1, 2)
    assert spike_positions((1, 4, 2, 7), threshold=4) == ((2, 4), (4, 7))


def test_mersenne_progression_report_smoke():
    report = analyze_mersenne_progression(
        base_R=6,
        modulus=16,
        t_max=2,
        prefix_length=20,
    )
    assert report.type == "mersenne_progression_word_report"
    assert len(report.samples) == 3
    assert report.worst_R in {6, 22, 38}
    assert report.distinct_prefixes >= 1


def test_mersenne_branch_report_splits_by_next_valuation():
    report = analyze_mersenne_branches(
        base_R=6,
        modulus=16,
        t_max=4,
        prefix_length=30,
        max_depth=2,
    )
    assert report.type == "mersenne_progression_branch_report"
    assert report.root.count == 5
    assert report.root.children
    assert all(child.count > 0 for child in report.root.children)


def test_mersenne_prefix_family_finds_known_hard_branch():
    report = analyze_mersenne_prefix_family(
        target_prefix=(4, 1, 2, 1, 1, 1, 6),
        t_max=16,
        prefix_length=20,
        max_steps=20_000,
    )
    assert report.type == "mersenne_prefix_family_report"
    assert any(sample.t == 12 and sample.R == 3206 for sample in report.hits)
    assert report.hit_count >= 1
    assert report.hit_residues_by_power
