from fractions import Fraction

from collatz_exp.christoffel import (
    christoffel_slope,
    is_upper_christoffel,
    is_upper_christoffel_conjugate,
    slope_constrained_filter,
)


def test_upper_christoffel_representatives_are_exact():
    assert is_upper_christoffel((1, 0))
    assert is_upper_christoffel((1, 0, 0))
    assert is_upper_christoffel((1, 1, 0))
    assert not is_upper_christoffel((0, 1))
    assert is_upper_christoffel_conjugate((0, 1))
    assert not is_upper_christoffel_conjugate((1, 1, 0, 0))


def test_christoffel_slope_is_exact_valuation_per_step():
    assert christoffel_slope((1, 0)) == Fraction(2, 1)
    assert christoffel_slope((1, 0, 0)) == Fraction(3, 1)
    assert christoffel_slope((1, 1, 0)) == Fraction(3, 2)


def test_slope_constrained_filter_uses_upper_conjugacy_classes():
    words = ((1, 0), (0, 1), (1, 1, 0), (1, 0, 0), (1, 1, 0, 0))
    filtered = slope_constrained_filter(
        words,
        target=Fraction(3, 2),
        tolerance=Fraction(1, 10),
    )
    assert filtered == ((1, 1, 0),)
