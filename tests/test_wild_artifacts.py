from collatz_exp.constrained_jsr import (
    christoffel_filtered_jsr_report,
    constrained_projective_jsr_report,
    constrained_jsr_report,
    legal_residue_edges,
    legal_word_closes,
    tail_aware_markov_lyapunov_report,
    tail_aware_lte_closed_projective_jsr_report,
    tail_aware_projective_jsr_report,
)
from collatz_exp.christoffel import (
    is_christoffel_compatible,
    is_cyclically_balanced,
    valuation_word_to_parity_bits,
)
from collatz_exp.core import accelerated_step
from collatz_exp.graph_curvature import ollivier_ricci_report, wasserstein_1_lp
from collatz_exp.hodge import hodge_report
from collatz_exp.lll_cycles import cycle_lattice_report, lll_reduce
from collatz_exp.magnitude import magnitude_report
from collatz_exp.mixed_tensor import mixed_tensor_rank_report
from collatz_exp.newton_polygons import newton_polygon_report
from collatz_exp.snf_invariants import snf_invariant_report
from collatz_exp.spike_dpp import spike_correlation_report
from collatz_exp.thermodynamic import pressure_report
from collatz_exp.walsh_transfer import fwht, walsh_transfer_report
from collatz_exp.cover import run_certificate_cover


def test_constrained_jsr_edges_are_witnessed():
    edges = legal_residue_edges(4, 6)
    assert edges
    for edge in edges[:20]:
        landing, valuation = accelerated_step(edge.witness)
        assert valuation == edge.valuation
        assert edge.witness % 16 == edge.source
        assert landing % 16 == edge.target
    report = constrained_jsr_report(4, 6)
    assert report.type == "constrained_residue_jsr_cycle_mean"
    assert report.all_one_self_loop_detected
    assert legal_word_closes((1,), 4)
    projective = constrained_projective_jsr_report(
        modulus_powers=(4,),
        max_valuation=6,
        tail_depth_cutoffs=(2, 3),
    )
    level = projective.levels[0]
    assert projective.type == "constrained_projective_jsr"
    assert level.obstruction_kind == "negative_integer_cycle"
    assert level.affine_quotient_jsr_upper > 1.0
    assert level.tail_filtered[0].affine_quotient_jsr < 1.0
    tail = tail_aware_projective_jsr_report(
        levels=((5, 4),),
        max_valuation=8,
    )
    tail_level = tail.levels[0]
    assert tail.type == "tail_aware_projective_jsr"
    assert not tail_level.all_one_self_loop_detected
    assert tail_level.affine_quotient_jsr is not None
    closed = tail_aware_lte_closed_projective_jsr_report(
        levels=((5, 4),),
        max_valuation=8,
    )
    closed_level = closed.levels[0]
    assert closed.type == "tail_aware_lte_closed_projective_jsr"
    assert not closed_level.all_one_self_loop_detected
    assert closed_level.closed_overflow_edges >= tail_level.overflow_edges
    markov = tail_aware_markov_lyapunov_report(
        levels=((5, 4),),
        max_valuation=8,
    )
    markov_level = markov.levels[0]
    assert markov.type == "tail_aware_markov_lyapunov"
    assert markov_level.worst_case_jsr_factor is not None
    assert markov_level.worst_case_jsr_factor > 1.0
    assert markov_level.largest_component_average_log2_growth_per_accelerated_step < 0.0
    assert valuation_word_to_parity_bits((2, 1, 3)) == (1, 0, 1, 1, 0, 0)
    assert is_cyclically_balanced((1, 0, 1, 0))
    assert is_christoffel_compatible((1, 0))
    assert not is_christoffel_compatible((1, 1, 0, 0))
    christoffel = christoffel_filtered_jsr_report(
        levels=((5, 4),),
        max_valuation=8,
        max_cycle_edges=6,
        max_cycles_scanned=2000,
    )
    assert christoffel.type == "christoffel_filtered_tail_jsr"
    christoffel_level = christoffel.levels[0]
    assert christoffel_level.cycles_scanned > 0
    assert christoffel_level.exact_karp_factor is not None


def test_lll_cycle_lattice_smoke():
    reduced = lll_reduce(((1, 0, 100), (0, 1, 141), (0, 0, 1000)))
    assert len(reduced) == 3
    report = cycle_lattice_report(m_max=4, valuation_max=4)
    assert report.words_scanned > 0
    assert report.relations


def test_walsh_transfer_smoke():
    values = [1, 2, 3, 4]
    fwht(values)
    assert values == [10, -2, -4, 0]
    report = walsh_transfer_report(modulus_power=4, sample_lift_power=2)
    assert report.dimension == 8


def test_mixed_tensor_and_graph_artifacts_smoke():
    tensor = mixed_tensor_rank_report(mod2_power=4, mod3_power=1)
    assert tensor.nonzero_entries > 0
    hodge = hodge_report(modulus_power=4, sample_lift_power=2)
    assert hodge.harmonic_dimension >= 0
    snf = snf_invariant_report(modulus_power=4, sample_lift_power=2)
    assert snf.vertices == 8


def test_curvature_and_misc_artifacts_smoke():
    assert wasserstein_1_lp({1: 1}, {1: 1}, {(1, 1): 0}) == 0.0
    curvature = ollivier_ricci_report(modulus_power=4, sample_lift_power=2, max_edges=4)
    assert curvature.edges_checked <= 4
    assert pressure_report().type == "toy_valuation_pressure_report"
    assert newton_polygon_report(m_max=4).words_scanned > 0
    assert spike_correlation_report(start_max=31, steps=8).starts_checked > 0
    cover = run_certificate_cover(max_depth=6, max_nodes=100)
    assert magnitude_report(cover, max_points=8).sampled_points <= 8
