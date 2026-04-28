from collatz_exp.branch_table import branch_table_report, terminal_power_exponent_before_one
from collatz_exp.champions import champion_report, orbit_stats
from collatz_exp.compact_trace import compact_trace_report
from collatz_exp.graph_tree import odd_tree_sibling_report, right_sibling
from collatz_exp.power_ratio import power_ratio_report
from collatz_exp.sensitivity import sensitivity_report
from collatz_exp.tuple_merges import merge_witness, tuple_merge_report


def test_tuple_merge_final_pair_family():
    witness = merge_witness((4, 5), max_steps=3)
    assert witness is not None
    assert witness.value == 4
    assert witness.max_time == 3
    report = tuple_merge_report(samples=3)
    assert report.type == "local_tuple_merge_report"
    assert report.families[0].passed


def test_power_ratio_report_reaches_one_for_27():
    report = power_ratio_report(start=27, max_steps=200)
    assert report.type == "power_ratio_orbit_report"
    assert report.reached_one
    assert {summary.base for summary in report.summaries} == {2.0, 3.0, 6.0}


def test_branch_table_and_compact_trace_invariants():
    table = branch_table_report(7)
    assert table.reached_one
    assert terminal_power_exponent_before_one(5) == 4
    trace = compact_trace_report(19)
    assert trace.reached_one
    assert trace.invariant_valid


def test_inverse_tree_sibling_formula():
    report = odd_tree_sibling_report(parent=5, count=3)
    assert report.type == "odd_inverse_tree_sibling_report"
    assert all(child.verified for child in report.children)
    assert right_sibling(report.children[0].child) == report.children[1].child


def test_champions_and_sensitivity_smoke():
    assert orbit_stats(27, max_steps=200).reached_one
    champions = champion_report(stop=32)
    assert champions.checked == 32
    sensitivity = sensitivity_report(count=8, steps=8, width=16)
    assert sensitivity.type == "collatz_sensitivity_report"
    assert sensitivity.max_hamming_distance >= 0
