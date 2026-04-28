from collatz_exp.cover import load_cover_report, run_certificate_cover
from collatz_exp.tail_family import (
    analyze_cover_tail_frontier,
    analyze_tail_family,
    analyze_tail_parameter_sample,
    canonical_tail_coordinate,
    tail_renormalization_family_report,
    tail_renormalization_report,
    tail_renormalization_step,
    tail_prefix_formula,
    tail_residue,
)


def test_tail_prefix_formula_and_residue_coordinate():
    formula = tail_prefix_formula(6)
    assert formula.forced_steps == 5
    assert formula.input_expression == "2^6*u - 1"
    residue, power = tail_residue(6, u_residue=3, u_mod_power=4)
    assert power == 10
    assert residue == (64 * 3 - 1)
    assert canonical_tail_coordinate(20, 128, 8) == (27, 1, 1)
    assert canonical_tail_coordinate(20, 0, 8) == (28, 0, 0)


def test_tail_parameter_sample_for_pure_tail():
    sample = analyze_tail_parameter_sample(
        R=8,
        u_residue=0,
        u_mod_power=0,
        representative_max_steps=1000,
    )
    assert sample.residue == (1 << 8) - 1
    assert sample.modulus_power == 8
    assert sample.forced_initial_ones == 7
    assert sample.m >= 7
    assert sample.representative_descent_m is not None


def test_tail_family_split_smoke():
    report = analyze_tail_family(R=10, u_mod_power=3, top_n=4)
    assert report.type == "mersenne_tail_parameter_family_report"
    assert report.samples == 8
    assert 0 <= report.certified_count <= report.samples
    assert len(report.top_dangerous) <= 4
    odd_report = analyze_tail_family(R=10, u_mod_power=3, top_n=4, odd_u_only=True)
    assert odd_report.samples == 4


def test_tail_renormalization_step_matches_tail_coordinate():
    step = tail_renormalization_step(R=8, u=1)
    assert step.n == 255
    assert step.block_m == 8
    assert step.block_A == 8 + step.c
    assert step.next_n % 2 == 1
    assert (1 << step.next_R) * step.next_u - 1 == step.next_n
    assert step.next_n < step.n


def test_tail_renormalization_report_smoke():
    report = tail_renormalization_report(R=20, u=143, max_blocks=10)
    assert report.type == "tail_renormalization_report"
    assert report.steps >= 1
    assert report.total_m == sum(step.block_m for step in report.path)
    assert report.total_A == sum(step.block_A for step in report.path)
    assert report.path[0].R == 20
    assert report.path[0].u == 143


def test_tail_renormalization_family_report_smoke():
    report = tail_renormalization_family_report(
        R=10,
        u_mod_power=3,
        max_blocks=5,
        top_n=3,
    )
    assert report.type == "tail_renormalization_family_report"
    assert report.samples == 4
    assert len(report.top_dangerous) <= 3
    assert report.max_steps >= 1


def test_cover_tail_frontier_smoke():
    cover = run_certificate_cover(max_depth=12, max_nodes=4_000)
    report = analyze_cover_tail_frontier(cover, min_initial_ones=6, top_n=3)
    assert report.type == "cover_tail_frontier_report"
    assert report.frontier_classes == len(cover.frontier)
    assert len(report.top_tails) <= 3
