"""Finite reverse-frontier probes for the accelerated odd Collatz graph."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ReverseFrontierHit:
    unresolved_residue: int
    unresolved_modulus_power: int
    reverse_depth: int
    predecessor: int
    predecessor_word: tuple[int, ...]


@dataclass(frozen=True)
class ReverseFrontierReport:
    type: str
    status: str
    unresolved_checked: int
    reverse_depth: int
    nodes_generated: int
    hits: tuple[ReverseFrontierHit, ...]
    misses: tuple[tuple[int, int], ...]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["hits"] = [
            {
                **asdict(hit),
                "predecessor_word": list(hit.predecessor_word),
            }
            for hit in self.hits
        ]
        data["misses"] = [list(miss) for miss in self.misses]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, sort_keys=True)


def accelerated_predecessors(target: int, max_valuation: int) -> tuple[tuple[int, int], ...]:
    """Return ``(predecessor, valuation)`` pairs with ``S(predecessor)=target``."""

    if target <= 0 or target % 2 == 0:
        raise ValueError("target must be odd positive")
    if max_valuation < 1:
        raise ValueError("max_valuation must be positive")

    predecessors: list[tuple[int, int]] = []
    for valuation in range(1, max_valuation + 1):
        numerator = target * (1 << valuation) - 1
        if numerator % 3 != 0:
            continue
        predecessor = numerator // 3
        if predecessor > 0 and predecessor % 2 == 1:
            predecessors.append((predecessor, valuation))
    return tuple(predecessors)


def reverse_tree(
    reverse_depth: int = 4,
    max_nodes: int = 10_000,
    max_valuation: int = 12,
) -> dict[int, tuple[int, ...]]:
    """Grow a bounded inverse tree from ``1`` and record forward valuation words."""

    if reverse_depth < 0:
        raise ValueError("reverse_depth must be nonnegative")
    if max_nodes < 1:
        raise ValueError("max_nodes must be positive")

    seen: dict[int, tuple[int, ...]] = {1: ()}
    queue = deque([(1, 0)])
    while queue and len(seen) < max_nodes:
        value, depth = queue.popleft()
        if depth >= reverse_depth:
            continue
        for predecessor, valuation in accelerated_predecessors(value, max_valuation):
            if predecessor in seen:
                continue
            seen[predecessor] = (valuation, *seen[value])
            queue.append((predecessor, depth + 1))
            if len(seen) >= max_nodes:
                break
    return seen


def reverse_frontier_probe(
    unresolved: tuple[tuple[int, int], ...],
    reverse_depth: int = 4,
    max_nodes: int = 10_000,
    max_valuation: int = 12,
    max_hits: int = 64,
) -> ReverseFrontierReport:
    """Probe whether unresolved cylinders meet the bounded inverse tree of ``1``."""

    tree = reverse_tree(
        reverse_depth=reverse_depth,
        max_nodes=max_nodes,
        max_valuation=max_valuation,
    )
    hits: list[ReverseFrontierHit] = []
    misses: list[tuple[int, int]] = []

    for residue, modulus_power in unresolved:
        modulus = 1 << modulus_power
        match: tuple[int, tuple[int, ...]] | None = None
        for predecessor, word in tree.items():
            if predecessor % modulus == residue % modulus:
                match = (predecessor, word)
                break
        if match is None:
            misses.append((residue, modulus_power))
            continue
        if len(hits) < max_hits:
            predecessor, word = match
            hits.append(
                ReverseFrontierHit(
                    unresolved_residue=residue,
                    unresolved_modulus_power=modulus_power,
                    reverse_depth=len(word),
                    predecessor=predecessor,
                    predecessor_word=word,
                )
            )

    return ReverseFrontierReport(
        type="finite_reverse_frontier_probe",
        status="finite_inverse_graph_probe_not_certificate",
        unresolved_checked=len(unresolved),
        reverse_depth=reverse_depth,
        nodes_generated=len(tree),
        hits=tuple(hits),
        misses=tuple(misses),
    )
