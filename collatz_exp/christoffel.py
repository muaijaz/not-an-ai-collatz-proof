"""Finite Christoffel/Sturmian compatibility helpers.

The routines here are deliberately modest: they recognize the cyclic balanced
binary words that occur as conjugates of finite Christoffel words.  This is the
right finite proxy for the cycle-parity constraint used in Hercher-style
arguments, but it is not itself a replacement for the full arithmetic theorem.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd
from math import log2


LOG2_3 = log2(3)


def valuation_word_to_parity_bits(valuations: tuple[int, ...]) -> tuple[int, ...]:
    """Expand accelerated valuations to Terras parity bits.

    One accelerated odd step with valuation ``a`` corresponds to the parity
    block ``1 0^(a-1)``: one odd ``3n+1`` move followed by ``a`` divisions by
    two in the unaccelerated map, with the last division landing on the next odd
    integer.
    """

    bits: list[int] = []
    for valuation in valuations:
        if valuation < 1:
            raise ValueError("valuations must be positive")
        bits.append(1)
        bits.extend(0 for _ in range(valuation - 1))
    return tuple(bits)


def is_primitive_word(bits: tuple[int, ...]) -> bool:
    """Return whether ``bits`` is not a repetition of a shorter block."""

    length = len(bits)
    if length == 0:
        return False
    for period in range(1, length):
        if length % period != 0:
            continue
        if all(bits[index] == bits[index % period] for index in range(length)):
            return False
    return True


def is_cyclically_balanced(bits: tuple[int, ...]) -> bool:
    """Check the finite balanced-word condition on cyclic factors.

    For every factor length, the number of ``1`` bits in any two cyclic factors
    differs by at most one.  This is the standard finite Sturmian/Christoffel
    balance condition, checked directly because the diagnostic cycle words are
    intentionally short.
    """

    length = len(bits)
    if length <= 1:
        return True
    doubled = bits + bits
    for window in range(1, length + 1):
        counts = [
            sum(doubled[start : start + window])
            for start in range(length)
        ]
        if max(counts) - min(counts) > 1:
            return False
    return True


def is_christoffel_compatible(bits: tuple[int, ...]) -> bool:
    """Finite proxy for Christoffel compatibility.

    A non-trivial cycle parity word must contain both symbols.  Primitive,
    cyclically balanced binary words are conjugates of Christoffel words when
    the numbers of zeros and ones are coprime; the gcd check records that
    primitivity arithmetically as well as combinatorially.
    """

    if len(bits) < 2:
        return False
    ones = sum(bits)
    zeros = len(bits) - ones
    if ones == 0 or zeros == 0:
        return False
    if gcd(ones, zeros) != 1:
        return False
    return is_primitive_word(bits) and is_cyclically_balanced(bits)


def _upper_mechanical_word(ones: int, length: int) -> tuple[int, ...]:
    return tuple(
        ((index + 1) * ones + length - 1) // length
        - (index * ones + length - 1) // length
        for index in range(length)
    )


def is_upper_christoffel(word: tuple[int, ...]) -> bool:
    """Return whether ``word`` is the upper Christoffel representative."""

    length = len(word)
    if length < 2:
        return False
    if any(bit not in (0, 1) for bit in word):
        return False
    ones = sum(word)
    zeros = length - ones
    if ones == 0 or zeros == 0:
        return False
    if gcd(ones, zeros) != 1:
        return False
    return word == _upper_mechanical_word(ones, length)


def is_upper_christoffel_conjugate(word: tuple[int, ...]) -> bool:
    """Return whether a cyclic rotation of ``word`` is upper Christoffel."""

    return any(
        is_upper_christoffel(word[offset:] + word[:offset])
        for offset in range(len(word))
    )


def christoffel_slope(word: tuple[int, ...]) -> Fraction:
    """Return the exact valuation-per-accelerated-step slope ``A/m``."""

    ones = sum(word)
    if ones <= 0:
        raise ValueError("Christoffel slope requires at least one one-bit")
    return Fraction(len(word), ones)


def slope_constrained_filter(
    words: tuple[tuple[int, ...], ...],
    target: float | Fraction = LOG2_3,
    tolerance: float | Fraction = Fraction(1, 2),
) -> tuple[tuple[int, ...], ...]:
    """Filter upper-Christoffel conjugacy classes by slope proximity."""

    target_value = float(target)
    tolerance_value = float(tolerance)
    return tuple(
        word
        for word in words
        if is_upper_christoffel_conjugate(word)
        and abs(float(christoffel_slope(word)) - target_value) <= tolerance_value
    )
