from collatz_exp.core import (
    accelerated_step,
    affine_from_word,
    first_descent,
    hardest_first_descent_under_power,
    is_shrink_favorable,
    power_balance,
    v2,
)


def test_v2_and_accelerated_step():
    assert v2(1) == 0
    assert v2(40) == 3
    assert accelerated_step(7) == (11, 1)
    assert accelerated_step(11) == (17, 1)


def test_affine_from_word_matches_iteration():
    word = (1, 1, 2)
    affine = affine_from_word(word)
    n = 7
    assert affine.A == 4
    assert affine.B == 19
    assert (3**affine.m * n + affine.B) // (1 << affine.A) == 13


def test_first_descent_known_hard_cases():
    assert first_descent(703).m == 51
    case = first_descent(35_655)
    assert (case.m, case.A, case.landing) == (85, 135, 29_405)


def test_hardest_under_12():
    best = hardest_first_descent_under_power(12)
    assert (best.n, best.m, best.A, best.landing) == (703, 51, 83, 157)


def test_power_balance_is_exact_base2_gate():
    assert power_balance(2, 1) == 1
    assert power_balance(1, 1) == -1
    assert power_balance(0, 0) == 0
    assert is_shrink_favorable(59, 37)
