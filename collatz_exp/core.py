"""Exact arithmetic primitives for the accelerated odd Collatz map."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, log2
from typing import Iterable


@dataclass(frozen=True)
class AffineWord:
    """Affine expansion for a fixed accelerated valuation word."""

    word: tuple[int, ...]
    A: int
    B: int
    m: int


@dataclass(frozen=True)
class FirstDescent:
    """First descent data for one odd integer."""

    n: int
    m: int
    A: int
    word: tuple[int, ...]
    landing: int


def v2(x: int) -> int:
    """Return the 2-adic valuation of a positive integer."""

    if x <= 0:
        raise ValueError("v2 expects a positive integer")
    return (x & -x).bit_length() - 1


def accelerated_step(n: int) -> tuple[int, int]:
    """Return ``(S(n), a)`` for odd positive ``n`` and ``a = v2(3*n + 1)``."""

    if n <= 0 or n % 2 == 0:
        raise ValueError("accelerated_step expects an odd positive integer")
    a = v2(3 * n + 1)
    return (3 * n + 1) // (1 << a), a


def affine_from_word(word: Iterable[int]) -> AffineWord:
    """Compute ``S^m(n) = (3^m*n + B) / 2^A`` for a valuation word."""

    values = tuple(word)
    A = 0
    B = 0
    for a in values:
        if a <= 0:
            raise ValueError("valuation words must contain positive integers")
        B = 3 * B + (1 << A)
        A += a
    return AffineWord(word=values, A=A, B=B, m=len(values))


def power_balance(A: int, m: int) -> int:
    """Compare ``2^A`` and ``3^m`` exactly.

    Returns ``1`` when ``2^A > 3^m``, ``0`` when equal, and ``-1`` otherwise.
    """

    if A < 0 or m < 0:
        raise ValueError("A and m must be nonnegative")
    left = 1 << A
    right = 3**m
    return (left > right) - (left < right)


def is_shrink_favorable(A: int, m: int) -> bool:
    """Return whether a word with total valuation ``A`` beats ``3^m``."""

    return power_balance(A, m) > 0


def debt_bucket(A: int, m: int, scale: int = 100) -> int:
    """Bucket ``m*log2(3) - A`` for exploration ordering only."""

    if scale <= 0:
        raise ValueError("scale must be positive")
    return floor((m * log2(3) - A) * scale)


def valuation_word(n: int, steps: int) -> tuple[int, ...]:
    """Return the first ``steps`` accelerated valuations for one odd ``n``."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")
    x = n
    word: list[int] = []
    for _ in range(steps):
        x, a = accelerated_step(x)
        word.append(a)
    return tuple(word)


def apply_word(n: int, word: Iterable[int]) -> int:
    """Apply a known valuation word to ``n``, verifying each valuation."""

    x = n
    for expected in word:
        x, actual = accelerated_step(x)
        if actual != expected:
            raise ValueError(f"valuation mismatch: expected {expected}, got {actual}")
    return x


def first_descent(n: int, max_steps: int = 10_000) -> FirstDescent | None:
    """Return the first accelerated step where ``S^m(n) < n``."""

    if n <= 1 or n % 2 == 0:
        raise ValueError("first_descent expects an odd integer greater than 1")

    start = n
    x = n
    A = 0
    word: list[int] = []

    for m in range(1, max_steps + 1):
        x, a = accelerated_step(x)
        word.append(a)
        A += a
        if x < start:
            return FirstDescent(n=start, m=m, A=A, word=tuple(word), landing=x)
    return None


def hardest_first_descent_under_power(
    K: int, max_steps: int = 10_000
) -> FirstDescent:
    """Search odd ``n < 2^K`` and return the largest first-descent step count."""

    if K < 2:
        raise ValueError("K must be at least 2")

    best: FirstDescent | None = None
    for n in range(3, 1 << K, 2):
        candidate = first_descent(n, max_steps=max_steps)
        if candidate is None:
            raise RuntimeError(f"no descent found for n={n}")
        if best is None or candidate.m > best.m:
            best = candidate

    if best is None:
        raise RuntimeError("empty search range")
    return best


def iter_odd_residue_values(residue: int, modulus_power: int, limit: int) -> list[int]:
    """Return positive odd values in one ``mod 2^k`` class below ``limit``."""

    if modulus_power < 1:
        raise ValueError("modulus_power must be positive")
    modulus = 1 << modulus_power
    r = residue % modulus
    if r % 2 == 0:
        raise ValueError("residue must be odd modulo a power of two")

    values: list[int] = []
    n = r if r > 0 else modulus
    while n < limit:
        values.append(n)
        n += modulus
    return values
