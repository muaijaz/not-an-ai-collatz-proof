"""Finite Christoffel/Sturmian compatibility helpers.

The routines here are deliberately modest: they recognize the cyclic balanced
binary words that occur as conjugates of finite Christoffel words.  This is the
right finite proxy for the cycle-parity constraint used in Hercher-style
arguments, but it is not itself a replacement for the full arithmetic theorem.
"""

from __future__ import annotations

from math import gcd


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
