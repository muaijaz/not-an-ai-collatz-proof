from collatz_exp.constrained_karp import (
    BalancedWordAutomaton,
    constrained_karp_jsr,
    constrained_karp_jsr_report,
    lte_closed_tail_graph,
    product_graph,
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
