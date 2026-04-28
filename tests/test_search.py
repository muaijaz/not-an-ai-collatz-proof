from collatz_exp.search import adaptive_cover, adaptive_cover_bfs, forced_trace_for_residue


def test_forced_trace_keeps_exact_m_and_A():
    trace = forced_trace_for_residue(27, 59)
    assert trace.m == 37
    assert trace.A == 59
    assert trace.word[:3] == (1, 2, 1)


def test_adaptive_cover_uses_fair_debt_priority():
    result = adaptive_cover(max_depth=8, max_nodes=200)
    assert result.strategy == "debt-priority"
    assert result.nodes_processed > 0
    assert result.dominated_pruned >= 0


def test_legacy_bfs_still_available_for_comparison():
    result = adaptive_cover_bfs(max_depth=8, max_nodes=200)
    assert result.strategy == "bfs"
    assert result.nodes_processed > 0
