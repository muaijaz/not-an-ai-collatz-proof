from fractions import Fraction

from collatz_exp.qnp1_phase_transition import (
    diophantine_max_factor,
    empirical_realizable_karp_q,
    qnp1_phase_transition_report,
)


def test_diophantine_bound_q3_improves_with_m_cap():
    small = diophantine_max_factor(3, m_max=1)
    assert small["max_factor"] == Fraction(3, 4)
    assert small["argmax_m"] == 1
    assert small["argmax_A"] == 2

    wider = diophantine_max_factor(3, m_max=5)
    assert wider["max_factor"] == Fraction(243, 256)
    assert wider["argmax_m"] == 5
    assert wider["argmax_A"] == 8


def test_q5_empirical_matches_m3_diophantine_bound_at_light_levels():
    bound = diophantine_max_factor(5, m_max=3)
    empirical = empirical_realizable_karp_q(
        5,
        [(5, 4), (6, 5)],
        max_valuation=8,
        max_cycle_edges=4,
        max_cycles_scanned=20_000,
    )
    assert bound["max_factor"] == Fraction(125, 128)
    assert empirical["empirical_realizable_karp_factor"] == 125 / 128
    assert empirical["empirical_argmax_word"] in ([1, 1, 5], [1, 3, 3])


def test_q9_diophantine_bound_is_strictly_less_than_one_and_report_smokes():
    bound = diophantine_max_factor(9, m_max=10)
    assert bound["max_factor"] < 1

    report = qnp1_phase_transition_report(
        q_grid=(3, 5),
        m_max=5,
        levels=((5, 4),),
        max_valuation=8,
        max_cycle_edges=4,
        max_cycles_scanned=20_000,
    )
    assert report.type == "qnp1_phase_transition"
    assert len(report.entries) == 2
