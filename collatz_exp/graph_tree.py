"""Exact inverse-tree formulas for the accelerated odd Collatz graph."""

from __future__ import annotations

from dataclasses import dataclass

from .core import accelerated_step


@dataclass(frozen=True)
class OddTreeChild:
    parent: int
    child: int
    exponent: int
    sibling_index: int
    verified: bool


@dataclass(frozen=True)
class OddTreeSiblingReport:
    type: str
    status: str
    parent: int
    children: tuple[OddTreeChild, ...]


def first_child_exponent_mod3(parent: int) -> int:
    """Smallest positive ``a`` with ``parent*2^a == 1 (mod 3)``."""

    if parent <= 0 or parent % 2 == 0:
        raise ValueError("parent must be odd and positive")
    if parent % 3 == 0:
        raise ValueError("multiples of 3 have no odd accelerated preimage")
    return 1 if parent % 3 == 2 else 2


def odd_tree_child(parent: int, sibling_index: int = 0) -> OddTreeChild:
    """Return the ``sibling_index`` child in the inverse odd Collatz tree."""

    if sibling_index < 0:
        raise ValueError("sibling_index must be nonnegative")
    exponent = first_child_exponent_mod3(parent) + 2 * sibling_index
    child = (parent * (1 << exponent) - 1) // 3
    image, valuation = accelerated_step(child)
    return OddTreeChild(
        parent=parent,
        child=child,
        exponent=exponent,
        sibling_index=sibling_index,
        verified=image == parent and valuation == exponent,
    )


def right_sibling(child: int) -> int:
    """Return the next right sibling in the ``3x+1`` odd inverse tree."""

    if child <= 0 or child % 2 == 0:
        raise ValueError("child must be odd and positive")
    return 4 * child + 1


def odd_tree_sibling_report(parent: int = 1, count: int = 8) -> OddTreeSiblingReport:
    """Build the first ``count`` odd inverse-tree children of ``parent``."""

    if count < 1:
        raise ValueError("count must be positive")
    children = tuple(odd_tree_child(parent, index) for index in range(count))
    return OddTreeSiblingReport(
        type="odd_inverse_tree_sibling_report",
        status="finite_inverse_tree_formula_not_collatz_proof",
        parent=parent,
        children=children,
    )
