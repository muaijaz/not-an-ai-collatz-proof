from collatz_exp.core import accelerated_step, affine_from_word, apply_word, valuation_word
from collatz_exp.cycles import classify_cycle_word
from collatz_exp.qnp1_audit import qnp1_realizability_report
from collatz_exp.qnp1_family import (
    accelerated_step_q,
    affine_from_word_q,
    apply_word_q,
    classify_cycle_word_q,
    valuation_word_q,
)


def test_q3_family_primitives_match_existing_core():
    for n, length in ((1, 1), (3, 2), (7, 4), (27, 5)):
        word = valuation_word(n, length)
        assert valuation_word_q(n, length, 3) == word
        assert apply_word_q(n, word, 3) == apply_word(n, word)
        assert accelerated_step_q(n, 3) == accelerated_step(n)[0]


def test_q3_affine_and_cycle_classifier_match_existing_cycles():
    for word in ((1,), (2,), (3,), (1, 2), (1, 4), (2, 1, 2)):
        q_affine = affine_from_word_q(word, 3)
        affine = affine_from_word(word)
        assert q_affine.A == affine.A
        assert q_affine.B == affine.B
        assert q_affine.m == affine.m
        assert classify_cycle_word_q(word, 3) == classify_cycle_word(word)


def test_q5_known_accelerated_cycle_and_negative_word_classify_exactly():
    assert valuation_word_q(1, 2, 5) == (1, 4)
    assert apply_word_q(1, (1, 4), 5) == 1
    positive = classify_cycle_word_q((1, 4), 5)
    assert positive.kind == "positive_integer_cycle"
    assert positive.value == 1

    negative = classify_cycle_word_q((2,), 5)
    assert negative.kind == "negative_integer_cycle"
    assert negative.value == -1


def test_q5_realizability_audit_recovers_small_positive_cycle():
    report = qnp1_realizability_report(
        q_param=5,
        levels=((5, 4),),
        max_valuation=8,
        max_cycle_edges=4,
        max_cycles_scanned=20_000,
    )
    assert report.q_param == 5
    assert report.known_cycles_recovered
    assert any(cycle.orbit == (1, 3) for cycle in report.known_cycles_recovered)
    assert report.realizable_karp_factor_q5_positive_max is not None
    assert report.realizable_karp_factor_q5_positive_max >= 25 / 32
