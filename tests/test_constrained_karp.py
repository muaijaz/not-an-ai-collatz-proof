from collatz_exp.constrained_karp import (
    BalancedWordAutomaton,
    constrained_karp_jsr,
    constrained_karp_jsr_report,
    karp_slope_joint_sweep_report,
    lte_closed_tail_graph,
    product_graph,
    tail_cycle_realizability_report,
)


def test_balanced_word_automaton_recognizes_bounded_patterns():
    automaton = BalancedWordAutomaton(max_imbalance=1, max_period=4)
    assert automaton.pattern_count > 0
    assert automaton.accepts_cyclic_word((1, 0))
    assert automaton.accepts_cyclic_word((1, 0, 0))
    assert not automaton.accepts_cyclic_word((1, 1, 0, 0))


def test_product_graph_uses_integer_indexed_edges():
    automaton = BalancedWordAutomaton(max_imbalance=1, max_period=2)
    tail_graph = lte_closed_tail_graph(5, 4, 8)
    graph = product_graph(tail_graph, automaton)
    assert graph.states == len(tail_graph.states) * automaton.state_count
    assert graph.edges
    first = graph.edges[0]
    assert isinstance(first.source, int)
    assert isinstance(first.target, int)
    assert first.numerator > 0
    assert first.denominator > 0


def test_constrained_karp_report_stays_below_cycle_filter_bound():
    report = constrained_karp_jsr_report(
        levels=((5, 4),),
        max_valuation=8,
        max_period=2,
        christoffel_cycle_filter_bounds={(5, 4): 0.75},
    )
    level = report.levels[0]
    assert report.type == "constrained_karp_tail_jsr"
    assert level.constrained_karp_factor is not None
    assert level.constrained_karp_factor <= 0.75 + 1e-12
    assert level.within_cycle_filter_bound


def test_constrained_karp_jsr_returns_rational_when_visible():
    automaton = BalancedWordAutomaton(max_imbalance=1, max_period=2)
    graph = product_graph(lte_closed_tail_graph(5, 4, 8), automaton)
    result = constrained_karp_jsr(graph)
    assert result.constrained_factor is not None
    assert result.exact_rational_factor is not None


def test_karp_slope_joint_sweep_records_every_survivor():
    report = karp_slope_joint_sweep_report(
        levels=((5, 4),),
        max_valuation=8,
        automaton_max_periods=(2,),
        slope_tolerances=(0.5,),
        max_cycle_edges=4,
        max_cycles_scanned=10_000,
    )
    level = report.levels[0]
    assert report.type == "karp_slope_joint_sweep"
    assert level.survivor_count == len(level.survivors)
    assert level.survivor_count >= 1
    assert all(survivor.edge_factor is not None for survivor in level.survivors)
    assert not level.non_elementary_factor_ge_one


def test_tail_cycle_realizability_audits_high_growth_cycles():
    report = tail_cycle_realizability_report(
        5,
        4,
        max_cycle_edges=10,
        max_cycles_scanned=10_000,
        factor_threshold=1.0,
        max_valuation=12,
    )
    level = report.levels[0]
    assert report.type == "tail_cycle_realizability"
    assert report.obstruction is None
    assert level.high_growth_cycles == len(level.cycles)
    assert level.classification_counts["noninteger_2adic_only"] >= 1
    assert all(cycle.edge_factor >= 1.0 for cycle in level.cycles)
    assert all(cycle.cycle_value is None for cycle in level.cycles)


def test_tail_cycle_realizability_all_cycle_mode_reports_realizable_karp():
    report = tail_cycle_realizability_report(
        5,
        4,
        max_cycle_edges=10,
        max_cycles_scanned=10_000,
        factor_threshold=1.0,
        max_valuation=12,
        lift_max_scan_power=32,
        audit_all_cycles=True,
    )
    level = report.levels[0]
    assert report.realizable_karp_factor == 0.75
    assert level.realizable_karp_factor == 0.75
    assert level.realizable_karp_cycle is not None
    assert level.realizable_karp_cycle.valuation_word == (2,)
    assert level.closure_skipped_count == 0
